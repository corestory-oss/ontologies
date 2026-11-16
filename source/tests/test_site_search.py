# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Contracts for local search, guide navigation and build-time discovery checks."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import markdown

from scripts.build_site import guides, render_guide, search_panel
from scripts.catalog import ROOT, catalog
from scripts.check_site import Links, check_search
from scripts.site_publication import source_manifest
from scripts.site_projection import SAO, SPEC, compact, project
from scripts.site_search import excerpt, plain_text, search_index, serialize_index


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

    def select(self, tag):
        return [attrs for name, attrs in self.nodes if name == tag]


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.metadata = project()
        cls.index = search_index(cls.payload, [], cls.metadata)
        cls.entries = {entry['id']: entry for entry in cls.index['entries']}

    def test_every_local_projected_term_is_searchable(self):
        expected = {compact(term['id']) for group in self.payload[:2] for term in group['concepts']
                    if term['id'].startswith((str(SAO), str(SPEC)))}
        self.assertEqual(set(self.entries), expected)
        self.assertEqual(len(self.entries), len(self.index['entries']))
        self.assertFalse(any(key.startswith(('rdf:', 'rdfs:', 'xsd:', 'owl:')) for key in self.entries))

    def test_garden_fragments_use_actual_prefixes(self):
        for name in ('sao:CallableUnit', 'spec:Requirement', 'specsao:RequirementImplementationLink'):
            self.assertEqual(self.entries[name]['url'], 'reference/#' + name)
        for entry in self.index['entries']:
            self.assertEqual(entry['version'], catalog()[entry['ontology']]['version'])

    def test_definition_enum_and_deprecation_are_searchable(self):
        self.assertIn('normative', self.entries['spec:Requirement']['text'])
        self.assertIn('document_db', self.entries['sao:DataStoreType']['text'])
        retired = [entry for entry in self.entries.values() if entry['deprecated']]
        projected = [term for group in self.payload[:2] for term in group['concepts'] if term.get('deprecated')]
        self.assertEqual(len(retired), len(projected))

    def test_definitions_preserve_plain_projected_text(self):
        for group in self.payload:
            if group['type'] not in ('Classes', 'Properties'):
                continue
            for term in group['concepts']:
                if not term['id'].startswith((str(SAO), str(SPEC))):
                    continue
                with self.subTest(iri=term['id']):
                    entry = self.entries[compact(term['id'])]
                    definition = ' '.join(term.get('definition', {}).get('en', '').split())
                    self.assertEqual(entry['iri'], term['id'])
                    self.assertEqual(entry['description'], excerpt(definition))
                    self.assertIn(definition, entry['text'])

    def test_real_generic_type_notation_survives_in_search_records(self):
        for name, notation in (('sao:has_type_parameters', 'List<T>'),
                               ('sao:nullability_model', 'Option<T>')):
            with self.subTest(name=name):
                self.assertIn(notation, self.entries[name]['description'])
                self.assertIn(notation, self.entries[name]['text'])

    def test_only_rendered_remarks_are_parsed_as_html(self):
        definition = '  List<T> and\n Map<K, Option<T>> &lt;T&gt; <b>literal</b>  '
        term = {'id': str(SAO) + 'GenericExample', 'type': 'Class',
                'label': {'en': 'Generic example'}, 'definition': {'en': definition},
                'remarks': {'en': '<p>Use <code>List&lt;T&gt;</code> &amp; Option&lt;T&gt;.</p>'
                                  '<script>not_searchable()</script>'}}
        entry = search_index([{'type': 'Classes', 'concepts': [term]}], [], self.metadata)['entries'][0]
        self.assertEqual(entry['description'], 'List<T> and Map<K, Option<T>> &lt;T&gt; <b>literal</b>')
        self.assertIn(entry['description'], entry['text'])
        self.assertIn('Use List<T> & Option<T>.', entry['text'])
        self.assertNotIn('<code>', entry['text'])
        self.assertNotIn('not_searchable', entry['text'])

    def test_index_is_deterministic_without_machine_paths(self):
        reversed_payload = [dict(group, concepts=list(reversed(group['concepts']))) for group in reversed(self.payload)]
        self.assertEqual(serialize_index(self.index), serialize_index(search_index(reversed_payload, [], self.metadata)))
        self.assertNotIn(str(ROOT), serialize_index(self.index))

    def test_text_extraction_decodes_entities_and_excludes_scripts(self):
        self.assertEqual(plain_text('<p>A &amp; <code>B</code></p><script>bad()</script><p>C</p>'), 'A & B C')

    def test_excerpts_end_at_word_boundaries_and_mark_truncation(self):
        self.assertEqual(excerpt('Short description.'), 'Short description.')
        self.assertEqual(excerpt('Keep the whole word here.', 16), 'Keep the whole…')
        self.assertEqual(excerpt('VeryLongIdentifier', 8), 'VeryLong…')

    @unittest.skipUnless(shutil.which('node'), 'Node is optional; the browser matcher has a separate Node test entrypoint')
    def test_browser_matcher_against_real_projection(self):
        result = subprocess.run(['node', str(ROOT / 'tests/site_search.test.cjs')],
                                input=serialize_index(self.index), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class GuideNavigationTests(unittest.TestCase):
    def test_toc_anchors_match_markdown_including_duplicate_headings(self):
        text = '# A & B\n\n## Same heading\n\nText.\n\n### `exact_name`\n\n## Same heading\n\n## Café\n'
        html, record = render_guide(text, Path('guides/docs/nested/test.html'), 'docs/nested/test.md')
        parser = Links()
        parser.feed(html)
        self.assertEqual(record['title'], 'A & B')
        self.assertEqual([h['id'] for h in record['headings']], ['same-heading', 'exact_name', 'same-heading_1', 'cafe'])
        for heading in record['headings']:
            self.assertIn('#' + heading['id'], parser.targets)
            self.assertIn(heading['id'], parser.ids)
        self.assertIn('../../../index.html', parser.targets)
        self.assertIn('../../../guides/', parser.targets)
        self.assertIn('aria-label="Breadcrumb"', html)
        self.assertIn('aria-label="On this page"', html)
        self.assertIn('class="guide-article"', html)
        self.assertIn('script-src \'self\'', html)

    def test_existing_markdown_heading_ids_are_preserved(self):
        text = '# Guide\n\n## Deploy & verify\n\n### 2. Known_limits\n'
        original = Links()
        original.feed(markdown.markdown(text, extensions=['fenced_code', 'tables', 'toc']))
        html, _ = render_guide(text, Path('guides/test.html'), 'test.md')
        result = Links()
        result.feed(html)
        self.assertTrue(original.ids.issubset(result.ids))

    def test_no_empty_toc_and_no_raw_html_in_search_fields(self):
        html, record = render_guide('# Only <em>title</em>\n\nA <b>short</b> page.', Path('guides/test.html'), 'test.md')
        self.assertNotIn('On this page', html)
        self.assertEqual(record['title'], 'Only title')
        self.assertEqual(record['description'], 'A short page.')
        self.assertEqual(record['headings'], [])

    def test_search_has_native_controls_status_and_fallback(self):
        panel = search_panel('../')
        for expected in ('role="search"', 'for="search-query"', 'type="search"', 'role="status"',
                         'type="submit"', 'maxlength="200"', 'data-search-clear', 'data-search-retry', '<noscript>', '../guides/'):
            self.assertIn(expected, panel)

    def test_tables_have_keyboard_scroll_regions(self):
        html, _ = render_guide('# Data\n\n| A | B |\n|---|---|\n| C | D |', Path('guides/test.html'), 'test.md')
        self.assertIn('aria-label="Scrollable table" tabindex="0"><table>', html)

    def test_explainer_requires_one_marker_and_approved_route(self):
        for text, target in [('# Missing', 'guides/docs/start-here.html'),
                             ('<!-- corestory-explainer -->\n\n<!-- corestory-explainer -->',
                              'guides/docs/start-here.html'),
                             ('<!-- corestory-explainer -->', 'guides/other.html')]:
            with self.subTest(text=text, target=target), self.assertRaisesRegex(ValueError, 'one explainer'):
                render_guide(text, Path(target), 'docs/start-here.md')


class GuideBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='ontology-guides-')
        cls.output = Path(cls.temp.name)
        cls.records = guides(cls.output)
        cls.payload, cls.metadata = project()
        cls.index = search_index(cls.payload, cls.records, cls.metadata)
        cls.serialized = serialize_index(cls.index)
        (cls.output / 'search-index.json').write_text(cls.serialized)
        snapshot = dict(cls.metadata, guide_pages=len(cls.records), search_index={
            'path': 'search-index.json', 'entries': len(cls.index['entries']),
            'sha256': hashlib.sha256(cls.serialized.encode()).hexdigest()})
        (cls.output / 'snapshot.json').write_text(json.dumps(snapshot))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_reviewed_documents_are_indexed_once(self):
        expected = {str(path.relative_to(ROOT)) for folder in ('docs', 'examples') for path in (ROOT / folder).rglob('*.md')}
        expected.update(('README.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'legacy/sao/README.md'))
        expected.intersection_update(source_manifest(ROOT)['files'])
        self.assertEqual({record['id'] for record in self.records}, expected)
        self.assertEqual(len(self.records), len(expected))
        self.assertNotIn('docs/sao/whitepaper.md', expected)
        self.assertFalse(any(entry['id'] == 'docs/sao/whitepaper.md'
                             or entry['url'] == 'guides/docs/sao/whitepaper.html'
                             for entry in self.index['entries']))
        self.assertTrue(all((self.output / record['url']).is_file() for record in self.records))

    def test_beginner_path_precedes_commands_and_patterns(self):
        html = (self.output / 'guides/index.html').read_text()
        section = html.split('<h2>Start here</h2>', 1)[1].split('</ul>', 1)[0]
        parser = Links()
        parser.feed(section)
        self.assertEqual(parser.targets, [
            'docs/start-here.html', 'docs/start-here.html#watch-the-explainer',
            'docs/getting-started.html', 'docs/modeling-patterns.html',
        ])

    def test_explainer_initial_markup_is_local_accessible_and_searchable(self):
        html = (self.output / 'guides/docs/start-here.html').read_text()
        parser = Elements(html)
        self.assertEqual(parser.select('iframe'), [])
        buttons = [attrs for attrs in parser.select('button') if 'data-video-load' in attrs]
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0]['type'], 'button')
        self.assertIn('hidden', buttons[0], 'no inert button when JavaScript is off')
        ids = {attrs['id'] for _, attrs in parser.nodes if 'id' in attrs}
        self.assertIn(buttons[0]['aria-describedby'], ids)
        self.assertIn(buttons[0]['aria-controls'], ids)
        self.assertIn('watch-the-explainer', ids)
        self.assertEqual(sum(attrs.get('href') == 'https://youtu.be/gQVNWIBSrEY'
                             for attrs in parser.select('a')), 1)
        self.assertIn('If the player is unavailable or JavaScript is off', html)
        self.assertIn('YouTube may collect usage data', html)
        self.assertEqual([attrs['src'] for attrs in parser.select('script')],
                         ['../../assets/guide-video.js', '../../assets/site-search.js'])
        for tag, attrs in parser.nodes:
            with self.subTest(tag=tag, attrs=attrs):
                self.assertFalse(any(key.startswith('on') for key in attrs))
                self.assertNotIn(attrs.get('rel'), ('preconnect', 'dns-prefetch', 'prefetch'))
                for name in ('src', 'srcset', 'poster', 'data'):
                    self.assertNotIn('://', attrs.get(name, ''))
                    self.assertFalse(attrs.get(name, '').startswith('//'))
        record = next(record for record in self.records if record['id'] == 'docs/start-here.md')
        self.assertIn({'id': 'watch-the-explainer', 'title': 'Watch the explainer', 'level': 2},
                      record['headings'])
        self.assertIn('Tell the CoreStory of your system - Ontologies Explainer', record['text'])
        self.assertNotIn('corestory-explainer', record['text'])

    def test_only_beginner_guide_gets_frame_permission_and_video_script(self):
        default = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'"
        checked = 0
        for path in self.output.rglob('*.html'):
            parser = Elements(path.read_text())
            csp = [attrs['content'] for attrs in parser.select('meta')
                   if attrs.get('http-equiv') == 'Content-Security-Policy']
            video = path.relative_to(self.output).as_posix() == 'guides/docs/start-here.html'
            with self.subTest(path=path.relative_to(self.output)):
                self.assertEqual(csp, [default + ('; frame-src https://www.youtube-nocookie.com' if video else '')])
                self.assertEqual(sum(attrs.get('src', '').endswith('/guide-video.js')
                                     for attrs in parser.select('script')), int(video))
            checked += 1
        self.assertGreater(checked, len(self.records))

    def test_search_integrity_and_all_guide_anchors(self):
        failures = []
        check_search(self.output, self.payload, failures)
        self.assertEqual(failures, [])

    def test_checker_rejects_changed_index_and_bad_heading(self):
        damaged = json.loads(self.serialized)
        guide = next(entry for entry in damaged['entries'] if entry['kind'] == 'Guide' and entry['headings'])
        guide['headings'][0]['id'] = 'nonexistent-anchor'
        try:
            (self.output / 'search-index.json').write_text(serialize_index(damaged))
            failures = []
            check_search(self.output, self.payload, failures)
            self.assertIn('Search snapshot hash or entry count differs', failures)
            self.assertTrue(any('heading does not resolve' in failure for failure in failures))
        finally:
            (self.output / 'search-index.json').write_text(self.serialized)


if __name__ == '__main__':
    unittest.main()
