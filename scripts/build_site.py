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
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import markdown
from scripts.catalog import ROOT
from scripts.site_projection import project, SAO, SPEC


def render_page(title, body, home):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · CoreStory Ontologies</title>
<style>body{{font:17px/1.65 system-ui,sans-serif;max-width:1000px;margin:42px auto;padding:0 24px;color:#18232c}}a{{color:#17629a}}pre{{overflow:auto;background:#f3f5f7;padding:18px;border-radius:8px}}code{{font-size:.88em}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;border:1px solid #dce2e7;padding:9px}}img{{max-width:100%}}nav{{margin-bottom:32px}}blockquote{{border-left:3px solid #abc;padding-left:18px;color:#506070}}</style>
</head><body><nav><a href="{home}">Ontology explorer</a></nav>{body}</body></html>'''


def guides(output):
    """Render existing prose; rewrite local links to HTML or bundled source files."""
    documents = [ROOT / name for name in ("README.md", "CONTRIBUTING.md", "CHANGELOG.md")]
    documents += sorted((ROOT / "docs").rglob("*.md"))
    documents += sorted((ROOT / "examples").rglob("*.md"))
    documents += [ROOT / "legacy/sao/README.md"]
    destination = {p.resolve(): Path("guides") / p.relative_to(ROOT).with_suffix(".html") for p in documents}
    # Raw downloads support the code, schema, manifest and PDF links in guides.
    source = output / "source"
    for directory in ("ontologies", "scripts", "tests", "examples", "legacy", "docs", "dist"):
        shutil.copytree(ROOT / directory, source / directory,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for name in ("README.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE", "NOTICE"):
        shutil.copy2(ROOT / name, source / name)
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
            to = destination.get(resolved, Path("source") / resolved.relative_to(ROOT))
            if resolved.is_dir():
                to /= "index.html"
            relative = posixpath.relpath(to.as_posix(), target.parent.as_posix())
            return opening + relative + (separator + anchor if separator else "") + ")"
        text = re.sub(r"(!?\[[^\]]*\]\()([^\s)]+)\)", rewrite, path.read_text())
        body = markdown.markdown(text, extensions=["fenced_code", "tables", "toc"])
        title = next((line.lstrip("# ") for line in text.splitlines() if line.startswith("# ")), path.stem)
        html = render_page(title, body, posixpath.relpath("index.html", target.parent.as_posix()))
        (output / target).parent.mkdir(parents=True, exist_ok=True)
        (output / target).write_text(html)
    for directory in sorted(source.rglob("*")):
        if directory.is_dir():
            entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            links = "".join(f'<li><a href="{escape(p.name, quote=True)}{ "/index.html" if p.is_dir() else ""}">{escape(p.name)}</a></li>' for p in entries)
            relative = posixpath.relpath("index.html", directory.relative_to(output).as_posix())
            (directory / "index.html").write_text(render_page("Source files", "<h1>Source files</h1><ul>" + links + "</ul>", relative))
    links = "".join(f'<li><a href="{escape(posixpath.relpath(target.as_posix(), "guides"))}">{escape(str(path.relative_to(ROOT)))}</a></li>' for path, target in sorted(destination.items(), key=lambda item: str(item[0])))
    (output / "guides/index.html").write_text(render_page("Guides", "<h1>Guides</h1><ul>" + links + "</ul>", "../index.html"))
    return len(documents)


def copy_garden(directory, output):
    manifest = json.loads((ROOT / "web/garden-assets.json").read_text())
    for asset in manifest["assets"]:
        path = directory / asset["path"]
        blob = path.read_bytes()
        digest = "sha256-" + base64.b64encode(hashlib.sha256(blob).digest()).decode()
        if digest != asset["hash"]:
            raise ValueError(f"Garden asset checksum mismatch: {asset['path']}")
        destination = output / "vendor" / asset["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(blob)
    bootstrap = output / "vendor/v2/explorer.js"
    text = bootstrap.read_text()
    # Plain JSON works with ordinary CDN HTTP compression. The browser handles
    # Content-Encoding; Garden should not attempt a second gzip decompression.
    old = 'new Response(O.pipeThrough(new DecompressionStream("gzip"))).json()'
    if old not in text:
        raise ValueError("Pinned Garden bootstrap no longer matches the documented adapter")
    text = text.replace(old, 'new Response(O).json()')
    text = text.replace("https://the.rdf.garden/api/errors", "/__disabled-garden-errors")
    bootstrap.write_text(text)


def build(output, assets, distributions):
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Output must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    payload, metadata = project()
    dataset = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    (output / "ecosystem.json").write_text(dataset)
    dataset_hash = hashlib.sha256(dataset.encode()).hexdigest()
    copy_garden(Path(assets), output)
    (output / "dist").mkdir()
    for path in sorted(Path(distributions).glob("*.ttl")):
        shutil.copy2(path, output / "dist" / path.name)
    metadata["guide_pages"] = guides(output)
    # No wall-clock time or machine paths: identical inputs produce identical files.
    (output / "snapshot.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    config = {
        "sources": [{"href": "./ecosystem.json?sha256=" + dataset_hash}], "logoUrl": "./logo.svg",
        "menuTitle": "SAO + SpecSpec", "apiUrl": "",
        "enableConceptFeedback": False, "enableSiteFeedback": False, "enableFiles": False,
        "hideStandardClasses": True,
        "namespaceColors": {str(SAO): "var(--bl)", str(SPEC): "var(--gr)", str(SPEC) + "sao/": "var(--or)"},
    }
    csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'"
    (output / "index.html").write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light">
<meta http-equiv="Content-Security-Policy" content="''' + csp + '''">
<title>CoreStory · SAO + SpecSpec</title>
<link rel="icon" type="image/svg+xml" href="./logo.svg">
<link rel="external" href="./guides/index.html" title="Guides and model notes">
<link rel="external" href="./snapshot.json" title="Versions and source snapshot">
<link rel="external" href="./dist/sao.ttl" title="SAO Turtle">
<link rel="external" href="./dist/specspec.ttl" title="SpecSpec Turtle">
<script type="module" src="./vendor/v2/explorer.js"></script>
<script type="application/json">''' + json.dumps(config) + '''</script></head><body></body></html>''')
    (output / "logo.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 80"><g fill="white" font-family="system-ui,sans-serif"><text x="6" y="36" font-size="32" font-weight="700">CoreStory</text><text x="6" y="65" font-size="18">SAO + SpecSpec</text></g></svg>''')
    # Cloudflare Pages understands this static response-header file. It is not a function.
    (output / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n\n/ecosystem.json\n  Content-Type: application/json; charset=utf-8\n")
    print(f"Static site: {output}; {metadata['classes']} classes, {metadata['properties']} properties, {metadata['guide_pages']} guides.")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/site")
    parser.add_argument("--garden-assets", type=Path, required=True)
    parser.add_argument("--distributions", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    build(args.output, args.garden_assets, args.distributions)


if __name__ == "__main__":
    main()
