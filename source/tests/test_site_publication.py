# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Public-site contracts; the real pinned Garden build is checked separately."""
import contextlib
import io
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.metadata
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urljoin
from urllib.request import urlopen

from scripts.build_site import build, render_page
from scripts.catalog import ROOT
from scripts.check_site import Links, Publication, check_publication
from scripts.site_publication import (SITE_ORIGIN, SOURCE_MANIFEST, canonical_url,
                                      copy_public_sources, source_indexes, source_manifest)

# Full-profile meta-validation is CPU-heavy on shared CI runners. Keep a finite
# per-process budget without imposing a 60-second performance requirement.
ONBOARDING_VALIDATION_TIMEOUT = 180


class PublicationUnitTests(unittest.TestCase):
    def source_fixture(self, root):
        files = ('LICENSE', 'NOTICE', 'docs/guide.md')
        for name in files:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('reviewed fixture: ' + name)
        return {'version': 1, 'files': list(files), 'excluded': {'docs/internal.pdf': 'Withheld'}}

    def test_copy_is_exact_and_preserves_excluded_original(self):
        with tempfile.TemporaryDirectory(prefix='ontology-source-test-') as temp:
            root, output = Path(temp) / 'repo', Path(temp) / 'source'
            manifest = self.source_fixture(root)
            private = root / 'docs/internal.pdf'
            private.write_bytes(b'private fixture, must survive unchanged')
            # A newly added repository-root file is never implicitly published.
            (root / 'unreviewed.txt').write_text('not public')
            copy_public_sources(root, output, manifest)
            self.assertEqual({p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}, set(manifest['files']))
            self.assertEqual(private.read_bytes(), b'private fixture, must survive unchanged')
            self.assertFalse((output / 'docs/internal.pdf').exists())

    def test_new_nested_payload_refuses_before_copying(self):
        with tempfile.TemporaryDirectory(prefix='ontology-source-test-') as temp:
            root, output = Path(temp) / 'repo', Path(temp) / 'source'
            manifest = self.source_fixture(root)
            extra = root / 'docs/nested/unreviewed.md'
            extra.parent.mkdir()
            extra.write_text('not reviewed')
            with self.assertRaisesRegex(ValueError, 'Unreviewed public source input: docs/nested/unreviewed.md'):
                copy_public_sources(root, output, manifest)
            self.assertFalse(output.exists())

    def test_source_symlinks_fail_closed_even_when_excluded_or_dangling(self):
        for kind in ('file', 'ancestor', 'excluded', 'dangling', 'cache'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory(prefix='ontology-source-test-') as temp:
                root, output = Path(temp) / 'repo', Path(temp) / 'source'
                manifest = self.source_fixture(root)
                if kind == 'file':
                    (root / 'docs/guide.md').unlink()
                    (root / 'docs/guide.md').symlink_to(root / 'LICENSE')
                elif kind == 'ancestor':
                    (root / 'docs').rename(root / 'real-docs')
                    (root / 'docs').symlink_to(root / 'real-docs', target_is_directory=True)
                else:
                    name = {'excluded': 'internal.pdf', 'dangling': 'missing', 'cache': '__pycache__'}[kind]
                    (root / 'docs' / name).symlink_to(root / ('LICENSE' if kind == 'excluded' else 'absent'))
                with self.assertRaisesRegex(ValueError, 'Symlink in public source'):
                    copy_public_sources(root, output, manifest)
                self.assertFalse(output.exists())

    def test_manifest_rejects_duplicates_paths_globs_and_exclusion_overlap(self):
        cases = [('LICENSE', 'LICENSE'), ('../escape',), ('/absolute',), ('docs/*.md',),
                 ('docs//guide.md',), ('docs/internal.pdf',), ('index.html',)]
        with tempfile.TemporaryDirectory(prefix='ontology-manifest-test-') as temp:
            root = Path(temp)
            baseline = self.source_fixture(root)
            path = root / SOURCE_MANIFEST
            path.parent.mkdir()
            for names in cases:
                with self.subTest(names=names):
                    manifest = dict(baseline, files=sorted([*baseline['files'], *names]))
                    path.write_text(json.dumps(manifest))
                    with self.assertRaises(ValueError):
                        source_manifest(root)

    def test_canonical_paths_are_independent_of_preview_mount(self):
        for path, suffix in (("index.html", "/"), ("sao/index.html", "/sao/"),
                             ("guides/docs/start-here.html", "/guides/docs/start-here.html")):
            self.assertEqual(canonical_url(path), SITE_ORIGIN + suffix)

    def test_metadata_escapes_authored_text_once(self):
        html = render_page('A & "B"', '<h1>Test</h1>', '../index.html', target='sao/index.html',
                           description='Use <terms> & "evidence".')
        parser = Publication()
        parser.feed(html)
        self.assertEqual(parser.meta['description'], ['Use <terms> & "evidence".'])
        self.assertEqual(parser.meta['og:title'], [parser.title])
        self.assertEqual(parser.meta['twitter:title'], [parser.title])
        self.assertIn('content="Use &lt;terms&gt; &amp; &quot;evidence&quot;."', html)

    def test_normal_pages_preserve_relative_runtime_links(self):
        html = render_page('Guide', '<h1>Guide</h1>', '../../../index.html',
                           target='guides/docs/nested/test.html', description='A nested guide.')
        parser = Publication()
        parser.feed(html)
        self.assertIsNone(parser.base)
        for prefix in ('/', '/preview/ontologies/'):
            page = 'https://preview.invalid' + prefix + 'guides/docs/nested/test.html'
            for resource in parser.resources:
                self.assertTrue(urljoin(page, resource).startswith('https://preview.invalid' + prefix + 'assets/'))

    def test_invalid_error_base_refuses_before_writing(self):
        with tempfile.TemporaryDirectory(prefix='ontology-base-test-') as temp:
            target = Path(temp) / 'candidate'
            for base in ('//evil.invalid/', '/prefix', '/a/../', '/a/"/', 'https://host/'):
                with self.subTest(base=base), self.assertRaisesRegex(ValueError, 'Base path'):
                    build(target, '/unused', ROOT / 'dist', base_path=base)
                self.assertFalse(target.exists())


    def test_unreviewed_or_symlinked_distribution_refuses_before_writing(self):
        with tempfile.TemporaryDirectory(prefix='ontology-distribution-test-') as temp:
            root = Path(temp)
            distributions = root / 'dist'
            distributions.mkdir()
            for path in (ROOT / 'dist').glob('*.ttl'):
                (distributions / path.name).write_bytes(path.read_bytes())
            extra = distributions / 'unreviewed.ttl'
            extra.write_text('not reviewed')
            with self.assertRaisesRegex(ValueError, 'distributions differ'):
                build(root / 'candidate', '/unused', distributions)
            self.assertFalse((root / 'candidate').exists())
            extra.unlink()
            (distributions / 'sao.ttl').unlink()
            (distributions / 'sao.ttl').symlink_to(ROOT / 'dist/sao.ttl')
            with self.assertRaisesRegex(ValueError, 'Symlink in public source'):
                build(root / 'candidate', '/unused', distributions)
            self.assertFalse((root / 'candidate').exists())


class PublicationBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='ontology-publication-test-')
        cls.output = Path(cls.temp.name) / 'site'
        # Only the external Garden-byte copy is excluded from this unit fixture.
        # Real build/check_site runs verify the pinned runtime and term coverage.
        with patch('scripts.build_site.copy_garden'), contextlib.redirect_stdout(io.StringIO()):
            build(cls.output, '/unused-unit-fixture', ROOT / 'dist', base_path='/preview/ontologies/')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def failures(self):
        failures = []
        check_publication(self.output, failures)
        return failures

    def test_all_publication_contracts(self):
        self.assertEqual(self.failures(), [])

    def test_source_root_navigation_and_attribution(self):
        html = (self.output / 'source/index.html').read_text()
        parser = Links()
        parser.feed(html)
        for target in ('ontologies/index.html', 'scripts/index.html', 'docs/index.html', 'LICENSE', 'NOTICE'):
            self.assertIn(target, parser.targets)
        self.assertNotIn('github.com/corestory-oss', html)
        for name in ('LICENSE', 'NOTICE'):
            self.assertEqual((self.output / 'source' / name).read_bytes(), (ROOT / name).read_bytes())
        self.assertFalse((self.output / 'source/documents').exists())

    def test_exact_source_inventory_excludes_all_whitepaper_representations(self):
        manifest = source_manifest(ROOT)
        self.assertEqual(len(manifest['files']), 250)
        expected = set(manifest['files']) | source_indexes(manifest['files'])
        actual = {p.relative_to(self.output / 'source').as_posix()
                  for p in (self.output / 'source').rglob('*') if p.is_file()}
        self.assertEqual(actual, expected)
        self.assertEqual((self.output / 'source-manifest.json').read_bytes(), (ROOT / SOURCE_MANIFEST).read_bytes())
        for extension in ('pdf', 'docx', 'md'):
            name = 'docs/sao/whitepaper.' + extension
            self.assertIn(name, manifest['excluded'])
            self.assertTrue((ROOT / name).is_file())
            self.assertFalse((self.output / 'source' / name).exists())
        self.assertFalse((self.output / 'guides/docs/sao/whitepaper.html').exists())
        self.assertNotIn('whitepaper.html', (self.output / 'search-index.json').read_text())
        for name in ('docs/sao/README', 'docs/sao/guide', 'docs/sao/extraction/00-overview'):
            self.assertTrue((self.output / ('guides/' + name + '.html')).is_file())

    def test_checker_rejects_nested_payload_and_output_symlinks(self):
        for name in ('source/docs/sao/private.json', 'source/docs/sao/whitepaper.pdf', 'source/docs/sao/whitepaper.md'):
            with self.subTest(name=name):
                path = self.output / name
                try:
                    path.write_bytes(b'not a reviewed output')
                    self.assertIn('Unexpected public source file: ' + name.removeprefix('source/'), self.failures())
                finally:
                    path.unlink()
        for name in ('source/docs/sao/symlink', 'source/docs/sao/dangling'):
            with self.subTest(name=name):
                path = self.output / name
                try:
                    path.symlink_to(ROOT / ('docs' if name.endswith('/symlink') else 'absent'))
                    self.assertTrue(any('Symlink in public source output' in failure for failure in self.failures()))
                finally:
                    path.unlink()

    def test_checker_rejects_modified_copied_bytes(self):
        path = self.output / 'source/examples/sao/rdf/system.ttl'
        original = path.read_bytes()
        try:
            path.write_bytes(original + b'\n# changed\n')
            self.assertIn('Changed public source bytes: examples/sao/rdf/system.ttl', self.failures())
        finally:
            path.write_bytes(original)

    def test_checker_rejects_unreviewed_rendered_guide_and_distribution(self):
        path = self.output / 'guides/docs/sao/whitepaper.html'
        try:
            path.write_text('<!doctype html><title>Withheld fixture</title>')
            self.assertIn('Rendered guide inventory differs from reviewed public sources', self.failures())
        finally:
            path.unlink()
        path = self.output / 'dist/unreviewed.ttl'
        try:
            path.write_text('not reviewed')
            self.assertIn('Public distribution inventory differs from reviewed sources', self.failures())
        finally:
            path.unlink()

    def test_public_onboarding_files_and_validation_work_over_http(self):
        # Exercise the published paths and documented flags without network package
        # installation in CI. The real uv block is also run against a candidate.
        document = (self.output / 'source/docs/getting-started.md').read_text()
        match = re.search(r'<!-- public-quickstart:start -->\s*```sh\n(.*?)```', document, re.S)
        assert match is not None, 'Published quickstart command block is missing'
        block = match[1]
        command = shlex.split(block.replace('\\\n', '').split('uv tool run ', 1)[1])
        self.assertEqual(command[:3], ['--from', 'pyshacl==0.30.1', 'pyshacl'])
        self.assertEqual(importlib.metadata.version('pyshacl'), '0.30.1')
        self.assertIn('repository access required', document)
        self.assertIn('not a complete build checkout', (self.output / 'source/index.html').read_text())
        downloads = re.findall(r'curl --fail --silent --show-error "\$SITE_BASE([^\"]+)" -o (\S+)', block)
        self.assertEqual(len(downloads), 5)

        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(self.output)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory(prefix='ontology-onboarding-test-') as temp:
                for path, name in downloads:
                    with urlopen(f'http://127.0.0.1:{server.server_port}' + path) as response:
                        self.assertEqual(response.status, 200)
                        (Path(temp) / name).write_bytes(response.read())
                result = subprocess.run([sys.executable, '-m', 'pyshacl', *command[3:]], cwd=temp,
                                        text=True, capture_output=True, timeout=ONBOARDING_VALIDATION_TIMEOUT)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertIn('Conforms: True', result.stdout)
                (Path(temp) / 'system.ttl').write_text('@prefix sao: <https://ontologies.corestory.ai/sao/> .\n<urn:invalid> a sao:System .\n')
                failed = subprocess.run([sys.executable, '-m', 'pyshacl', *command[3:]], cwd=temp,
                                        text=True, capture_output=True, timeout=ONBOARDING_VALIDATION_TIMEOUT)
                self.assertEqual(failed.returncode, 1, failed.stderr + failed.stdout)
                self.assertIn('Conforms: False', failed.stdout)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_namespace_pages_explain_static_html_and_offer_turtle(self):
        for name, prefix in (('sao', 'sao'), ('specspec', 'spec')):
            html = (self.output / name / 'index.html').read_text()
            self.assertIn('not an RDF content-negotiation endpoint', html)
            self.assertIn(SITE_ORIGIN + '/' + name + '/', html)
            parser = Links()
            parser.feed(html)
            for target in (f'../reference/#{prefix}:', f'../dist/{name}.ttl',
                           f'../dist/{name}.shacl.ttl', f'../dist/{name}.owl.ttl'):
                self.assertIn(target, parser.targets)

    def test_deep_error_recovery_and_noindex(self):
        html = (self.output / '404.html').read_text()
        parser = Publication()
        parser.feed(html)
        self.assertEqual(parser.meta['robots'], ['noindex, follow'])
        self.assertEqual(parser.base, '/preview/ontologies/')
        self.assertLess(html.index('<base '), html.index('rel="stylesheet"'))
        base = urljoin('https://preview.invalid/preview/ontologies/missing/deep/path', parser.base)
        for resource in parser.resources:
            self.assertTrue(urljoin(base, resource).startswith('https://preview.invalid/preview/ontologies/assets/'))
        self.assertEqual(urljoin(base, 'reference/index.html'), 'https://preview.invalid/preview/ontologies/reference/index.html')
        self.assertNotIn('/404.html', (self.output / 'sitemap.xml').read_text())

    def test_garden_remains_local_with_feedback_disabled(self):
        html = (self.output / 'reference/index.html').read_text()
        for expected in ('"apiUrl": ""', '"enableConceptFeedback": false', '"enableSiteFeedback": false',
                         '"enableFiles": false', "connect-src 'self'", 'src="../assets/vendor/v2/explorer.js"'):
            self.assertIn(expected, html)

    def test_checker_rejects_missing_or_corrupted_artifacts(self):
        cases = [('healthz', b'not healthy\n', 'Invalid static health'),
                 ('robots.txt', b'User-agent: *\nDisallow: /\n', 'Robots policy'),
                 ('sitemap.xml', b'<broken', 'Invalid sitemap'),
                 ('assets/ontology-social.png', b'not a PNG', 'actual 1200'),
                 ('source/LICENSE', b'wrong license', 'source attribution')]
        for name, damaged, expected in cases:
            with self.subTest(name=name):
                path = self.output / name
                original = path.read_bytes()
                try:
                    path.write_bytes(damaged)
                    self.assertTrue(any(expected in failure for failure in self.failures()))
                finally:
                    path.write_bytes(original)
        path = self.output / 'source/index.html'
        original = path.read_bytes()
        try:
            path.unlink()
            self.assertIn('Missing publication artifact: source/index.html', self.failures())
        finally:
            path.write_bytes(original)

    def test_checker_rejects_duplicate_metadata_and_external_runtime(self):
        path = self.output / 'sao/index.html'
        original = path.read_text()
        try:
            # Rejection fixture only: never served and no network request is made.
            path.write_text(original.replace('</head>', '<script src="https://telemetry.invalid/sdk.js"></script>'
                                            '<meta name="description" content="duplicate"></head>'))
            failures = self.failures()
            self.assertTrue(any('publication metadata' in failure for failure in failures))
            self.assertTrue(any('Nonlocal runtime resource' in failure for failure in failures))
        finally:
            path.write_text(original)


if __name__ == '__main__':
    unittest.main()
