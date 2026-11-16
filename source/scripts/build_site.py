#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Build a self-contained static Garden explorer and HTML guides, without a server."""
import argparse
import base64
import hashlib
from html import escape
import json
from pathlib import Path
import posixpath
import re
import shutil
import sys
from string import Template
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import markdown
from scripts.catalog import ROOT
from scripts.site_projection import project, SAO, SPEC
from scripts.site_search import excerpt, guide_record, search_index, serialize_index
from scripts.site_publication import (SOURCE_MANIFEST, copy_public_sources, publication_head,
                                      regular_source_file, source_indexes, source_manifest, validate_source_inputs,
                                      write_crawl_files)


def search_panel(root=""):
    """One ordinary form and link list; no custom keyboard widget is needed."""
    return '''<section id="search" class="site-search" aria-labelledby="search-title" data-search>
<h2 id="search-title">Find a term or guide</h2>
<form role="search" data-search-form>
<label for="search-query">Search the ontologies and documentation</label>
<div class="search-controls"><input id="search-query" name="q" type="search" maxlength="200"
 autocomplete="off" placeholder="Try CallableUnit, evidence, or validation"
 aria-describedby="search-help" aria-controls="search-results" data-search-input>
<button type="submit">Search</button><button type="button" data-search-clear>Clear</button></div>
</form>
<p id="search-help" class="search-help">Search term names, definitions, guide headings, and guide text. Results link to Garden or a guide.</p>
<p class="search-status" role="status" aria-live="polite" aria-atomic="true" data-search-status>Enter a term or topic to begin.</p>
<button type="button" data-search-retry hidden>Retry loading search</button>
<ol id="search-results" class="search-results" data-search-results></ol>
<noscript><p>Search needs JavaScript. <a href="''' + root + '''guides/">Browse all guides</a> or <a href="''' + root + '''reference/">open the ontology explorer</a>.</p></noscript>
</section>'''


def render_guide(text, target, source):
    """Use the same Markdown pass for stable anchors, navigation and search."""
    renderer = markdown.Markdown(extensions=["fenced_code", "tables", "toc"])
    body = renderer.convert(text)
    record = guide_record(body, target.as_posix(), source, Path(source).stem)
    # Wide source tables scroll inside the reading column, including by keyboard.
    body = body.replace('<table>', '<div class="table-scroll" role="region" aria-label="Scrollable table" tabindex="0"><table>')
    body = body.replace('</table>', '</table></div>')
    root = posixpath.relpath(".", target.parent.as_posix()) + "/"
    extra_head = ""
    if source == "docs/start-here.md":
        marker = "<!-- corestory-explainer -->"
        if target.as_posix() != "guides/docs/start-here.html" or body.count(marker) != 1:
            raise ValueError("Beginner guide must have one explainer at its approved route")
        body = body.replace(marker, '<div class="explainer-video" data-explainer-video>'
                            '<div id="explainer-player" class="video-stage" data-video-stage>'
                            f'<img src="{root}assets/brand/corestory-logo-gold.svg" width="172" height="60" alt="CoreStory">'
                            '<button type="button" aria-describedby="explainer-privacy" '
                            'aria-controls="explainer-player" data-video-load hidden>Load YouTube player</button>'
                            '</div><p class="video-status" role="status" aria-live="polite" '
                            'data-video-status></p></div>')
        extra_head = f'<script defer src="{root}assets/guide-video.js"></script>'
    breadcrumbs = ('<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'
                   f'<li><a href="{root}index.html">Home</a></li>'
                   f'<li><a href="{root}guides/">Guides</a></li>'
                   f'<li aria-current="page">{escape(record["title"])}</li></ol></nav>')
    toc = []
    for heading in record["headings"]:
        toc.append(f'<li class="toc-level-{heading["level"]}"><a href="#{escape(heading["id"], quote=True)}">'
                   + escape(heading["title"]) + '</a></li>')
    sidebar = ('<aside class="guide-sidebar"><details class="guide-toc" open>'
               '<summary>On this page</summary><nav aria-label="On this page"><ul>'
               + "".join(toc) + '</ul></nav></details></aside>') if toc else ""
    article = '<article class="guide-article">' + body + '</article>'
    body = breadcrumbs + '<div class="guide-layout">' + sidebar + article + '</div>'
    scope = next((name for prefix, name in (("docs/sao/", "SAO"), ("docs/specspec/", "SpecSpec"),
                                           ("legacy/sao/", "Legacy SAO"))
                  if source.startswith(prefix)), "")
    title = record["title"]
    if source == "README.md":
        title += " · Repository guide"
    if scope and not title.startswith(scope):
        title += " · " + scope
    description = title + ": " + excerpt(record["description"], 165)
    return render_page(title, body, root + "index.html", target=target,
                       description=description, extra_head=extra_head), record


def render_page(title, body, home, *, target, description, page_class="guide", extra_head="", noindex=False):
    root = posixpath.dirname(home)
    if root:
        root += "/"
    template = Template((ROOT / "web/templates/page.html").read_text())
    document_title = title if title == "CoreStory Ontologies" else title + " · CoreStory Ontologies"
    return template.substitute(title=escape(document_title), body=body, root=root,
                               page_class=escape(page_class, quote=True),
                               extra_head=extra_head,
                               frame_src=("; frame-src https://www.youtube-nocookie.com"
                                          if str(target) == "guides/docs/start-here.html" else ""),
                               publication_head=publication_head(document_title, description, target, noindex=noindex))


def prose(output, metadata):
    """Render editable website prose separately from repository documentation."""
    versions = metadata["ontologies"]
    for page in sorted((ROOT / "web/pages").glob("*.md")):
        text = page.read_text()
        for name in ("sao", "specspec"):
            text = text.replace("{{" + name + "_version}}", versions[name]["version"])
        text = text.replace("{{site_search}}", search_panel())
        body = markdown.markdown(text, extensions=["fenced_code", "tables", "toc", "attr_list", "md_in_html"])
        target = output / "index.html" if page.stem == "index" else output / page.stem / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        home = posixpath.relpath("index.html", target.parent.relative_to(output).as_posix())
        extra = '<script defer src="assets/legacy-reference.js"></script>' if page.stem == "index" else ""
        identity = guide_record(body, target.relative_to(output).as_posix(), page.name, page.stem)
        title = "CoreStory Ontologies" if page.stem == "index" else identity["title"]
        description = ("Explore SAO and SpecSpec: shared vocabularies for software structures, specifications, and evidence. Read guides and download RDF distributions."
                       if page.stem == "index" else title + ": " + excerpt(identity["description"], 165))
        target.write_text(render_page(title, body, home, target=target.relative_to(output),
                                      description=description, page_class="landing", extra_head=extra))


def guides(output, manifest=None):
    """Render existing prose; rewrite local links to HTML or bundled source files."""
    if manifest is None:
        manifest = source_manifest(ROOT)
    documents = [ROOT / name for name in manifest["files"] if name.endswith(".md")]
    destination = {p.resolve(): Path("guides") / p.relative_to(ROOT).with_suffix(".html") for p in documents}
    # Rendering and downloads share the same reviewed, exact file inventory.
    source = output / "source"
    copy_public_sources(ROOT, source, manifest)
    shutil.copyfile(ROOT / SOURCE_MANIFEST, output / "source-manifest.json")
    public_directories = {str(Path(name).parent) for name in source_indexes(manifest["files"])}
    records = []
    for path in documents:
        target = destination[path.resolve()]
        def rewrite(match):
            opening, url = match.groups()
            if ":" in url.split("/")[0] or url.startswith(("#", "/")):
                return match[0]
            filename, separator, anchor = url.partition("#")
            resolved = (path.parent / unquote(filename)).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                raise ValueError(f"Broken guide link: {path.relative_to(ROOT)} → {url}")
            relative_source = resolved.relative_to(ROOT).as_posix()
            if relative_source in manifest["excluded"]:
                # Keep authored source bytes; don't expose a withheld document via a rendered link.
                return opening.removeprefix("!").removeprefix("[").removesuffix("](") + " (not included in this public snapshot)"
            if relative_source not in manifest["files"] and relative_source not in public_directories:
                raise ValueError(f"Guide links to unreviewed public source: {path.relative_to(ROOT)} → {url}")
            to = destination.get(resolved, Path("source") / resolved.relative_to(ROOT))
            if resolved.is_dir():
                to /= "index.html"
            relative = posixpath.relpath(to.as_posix(), target.parent.as_posix())
            return opening + relative + (separator + anchor if separator else "") + ")"
        text = re.sub(r"(!?\[[^\]]*\]\()([^\s)]+)\)", rewrite, path.read_text())
        html, record = render_guide(text, target, path.relative_to(ROOT).as_posix())
        records.append(record)
        (output / target).parent.mkdir(parents=True, exist_ok=True)
        (output / target).write_text(html)
    # Include the source root itself; rglob alone leaves /source/ without an index.
    directories = [source] + sorted(path for path in source.rglob("*") if path.is_dir())
    for directory in directories:
        entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        links = "".join(f'<li><a href="{escape(p.name, quote=True)}{ "/index.html" if p.is_dir() else ""}">{escape(p.name)}</a></li>' for p in entries)
        relative = posixpath.relpath("index.html", directory.relative_to(output).as_posix())
        name = directory.relative_to(source).as_posix()
        title = "Source files" if name == "." else "Source files · " + name
        intro = ('<p>Reviewed reference source files, not a complete build checkout. '
                 'For a runnable public example, follow <a href="../guides/docs/getting-started.html">Getting started</a>. '
                 'The <a href="../source-manifest.json">versioned file inventory</a> records the publication scope. '
                 'Published ontology sources, documentation, examples, and tooling are licensed under Apache 2.0. '
                 '<a href="LICENSE">Read the license</a> and <a href="NOTICE">notices</a>.</p>'
                 if name == "." else '<p><a href="../index.html">Parent directory</a></p>')
        body = "<h1>" + escape(title) + "</h1>" + intro + "<ul>" + links + "</ul>"
        (directory / "index.html").write_text(render_page(
            title, body, relative, target=directory.relative_to(output) / "index.html",
            description="Browse the bundled public source " + ("snapshot" if name == "." else "directory " + name) + " for CoreStory Ontologies."))
    sections = []
    groups = [("Start here", ("docs/start-here.md", "docs/getting-started.md", "docs/modeling-patterns.md")),
              ("SAO · Software structures", "docs/sao/"),
              ("SpecSpec · Specification & evidence", "docs/specspec/"),
              ("Examples", "examples/"), ("Repository & development", None)]
    used = set()
    for label, prefix in groups:
        links = []
        for path, target in sorted(destination.items(), key=lambda item: str(item[0])):
            relative = str(path.relative_to(ROOT))
            if path in used or (prefix is not None and not relative.startswith(prefix)):
                continue
            used.add(path)
            title = next((line.lstrip("# ") for line in path.read_text().splitlines() if line.startswith("# ")), path.stem)
            href = escape(posixpath.relpath(target.as_posix(), "guides"), quote=True)
            video = (f' · <a href="{href}#watch-the-explainer">Watch the explainer</a>'
                     if relative == "docs/start-here.md" else "")
            links.append((relative, f'<li><a href="{href}">{escape(title)}</a>{video}</li>'))
        if isinstance(prefix, tuple):
            links.sort(key=lambda item: prefix.index(item[0]))
        sections.append(f'<h2>{escape(label)}</h2><ul class="guide-index">' + "".join(link for _, link in links) + '</ul>')
    body = '<h1>Guides & examples</h1><p>Read the models, follow worked examples, or explore the repository tooling.</p>' + search_panel("../") + "".join(sections)
    (output / "guides/index.html").write_text(render_page(
        "Guides", body, "../index.html", target="guides/index.html",
        description="Learn SAO and SpecSpec with introductions, modeling patterns, worked examples, and reference guides for software structures and evidence."))
    return records


def copy_garden(directory, output):
    manifest = json.loads((ROOT / "web/garden-assets.json").read_text())
    for asset in manifest["assets"]:
        path = directory / asset["path"]
        blob = path.read_bytes()
        digest = "sha256-" + base64.b64encode(hashlib.sha256(blob).digest()).decode()
        if digest != asset["hash"]:
            raise ValueError(f"Garden asset checksum mismatch: {asset['path']}")
        destination = output / "assets/vendor" / asset["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(blob)
    bootstrap = output / "assets/vendor/v2/explorer.js"
    text = bootstrap.read_text()
    # Plain JSON works with ordinary CDN HTTP compression. The browser handles
    # Content-Encoding; Garden should not attempt a second gzip decompression.
    old = 'new Response(O.pipeThrough(new DecompressionStream("gzip"))).json()'
    if old not in text:
        raise ValueError("Pinned Garden bootstrap no longer matches the documented adapter")
    text = text.replace(old, 'new Response(O).json()')
    text = text.replace("https://the.rdf.garden/api/errors", "/__disabled-garden-errors")
    bootstrap.write_text(text)


def build(output, assets, distributions, *, base_path="/"):
    if not re.fullmatch(r"/(?:[A-Za-z0-9_-]+/)*", base_path):
        raise ValueError("Base path must be / or a slash-terminated path such as /ontologies/")
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Output must be empty: {output}")
    manifest = source_manifest(ROOT)
    validate_source_inputs(ROOT, manifest)
    distributions = Path(distributions)
    distribution_names = {Path(name).name for name in manifest["files"] if name.startswith("dist/")}
    if {path.name for path in distributions.glob("*.ttl")} != distribution_names:
        raise ValueError("Turtle distributions differ from the reviewed public inventory")
    for name in sorted(distribution_names):
        regular_source_file(distributions, name)
    output.mkdir(parents=True, exist_ok=True)
    payload, metadata = project()
    dataset = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    (output / "reference").mkdir()
    (output / "reference/ecosystem.json").write_text(dataset)
    provenance = json.loads((ROOT / "web/assets/provenance.json").read_text())
    for asset in provenance["files"]:
        path = ROOT / "web/assets" / asset["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != asset["sha256"]:
            raise ValueError(f"Brand/font asset checksum mismatch: {asset['path']}")
    shutil.copytree(ROOT / "web/assets", output / "assets", dirs_exist_ok=True)
    shutil.copytree(ROOT / "web/styles", output / "assets/styles")
    dataset_hash = hashlib.sha256(dataset.encode()).hexdigest()
    copy_garden(Path(assets), output)
    (output / "dist").mkdir()
    for name in sorted(distribution_names):
        shutil.copyfile(regular_source_file(distributions, name), output / "dist" / name, follow_symlinks=False)
    records = guides(output, manifest)
    metadata["public_source"] = {"manifest": "source-manifest.json", "version": manifest["version"],
                                 "files": len(manifest["files"])}
    metadata["guide_pages"] = len(records)
    index = serialize_index(search_index(payload, records, metadata))
    (output / "search-index.json").write_text(index)
    metadata["search_index"] = {"path": "search-index.json", "sha256": hashlib.sha256(index.encode()).hexdigest(),
                                "entries": len(json.loads(index)["entries"])}
    # No wall-clock time or machine paths: identical inputs produce identical files.
    (output / "snapshot.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    config = {
        "sources": [{"href": "./ecosystem.json?sha256=" + dataset_hash}], "logoUrl": "../assets/brand/corestory-logo-black.svg",
        "menuTitle": "CoreStory Ontologies", "apiUrl": "",
        "enableConceptFeedback": False, "enableSiteFeedback": False, "enableFiles": False,
        "hideStandardClasses": True,
        "namespaceColors": {str(SAO): "var(--bl)", str(SPEC): "var(--gr)", str(SPEC) + "sao/": "var(--or)"},
    }
    csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'"
    (output / "reference/index.html").write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light">
<meta http-equiv="Content-Security-Policy" content="''' + csp + '''">
<title>CoreStory · SAO + SpecSpec</title>
''' + publication_head("CoreStory · SAO + SpecSpec", "Explore SAO and SpecSpec classes, properties, definitions, and relationships in the interactive Garden reference browser.", "reference/index.html") + '''
<link rel="icon" type="image/svg+xml" href="../assets/brand/corestory-symbol-black.svg">
<link rel="external" href="../index.html" title="CoreStory Ontologies home">
<link rel="external" href="../guides/index.html" title="Guides and model notes">
<link rel="external" href="../source/index.html" title="Bundled public source files">
<link rel="external" href="../sao/index.html" title="SAO namespace and downloads">
<link rel="external" href="../specspec/index.html" title="SpecSpec namespace and downloads">
<link rel="external" href="../snapshot.json" title="Versions and source snapshot">
<link rel="external" href="../dist/sao.ttl" title="SAO Turtle">
<link rel="external" href="../dist/specspec.ttl" title="SpecSpec Turtle">
<script type="module" src="../assets/vendor/v2/explorer.js"></script>
<script type="application/json">''' + json.dumps(config) + '''</script></head><body></body></html>''')
    prose(output, metadata)
    # This file is an error body, not an SPA fallback. The host must return 404.
    # A known base keeps assets and recovery links valid on deep unknown paths.
    # Only the error page needs it; normal pages retain source-relative links.
    (output / "404.html").write_text(render_page(
        "Page not found", '<h1>Page not found</h1><p>This path is not a published page. If you followed an ontology term IRI, use the explorer to find its definition.</p>'
        '<p><a href="reference/index.html">Open the ontology explorer</a> · <a href="guides/index.html">Browse guides</a> · <a href="index.html#search">Search the library</a></p>',
        "index.html", target="404.html", description="This page was not found in the CoreStory Ontologies reference library. Find a guide, namespace, or term in the explorer.",
        extra_head='<base href="' + base_path + '">', noindex=True))
    write_crawl_files(output)
    # Cloudflare Pages understands this static response-header file. It is not a function.
    (output / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n\n/reference/ecosystem.json\n  Content-Type: application/json; charset=utf-8\n")
    print(f"Static site: {output}; {metadata['classes']} classes, {metadata['properties']} properties, {metadata['guide_pages']} guides.")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/site")
    parser.add_argument("--garden-assets", type=Path, required=True)
    parser.add_argument("--distributions", type=Path, default=ROOT / "dist")
    parser.add_argument("--base-path", default="/", help="Hosting prefix for deep 404 recovery links; e.g. /ontologies/")
    args = parser.parse_args()
    build(args.output, args.garden_assets, args.distributions, base_path=args.base_path)


if __name__ == "__main__":
    main()
