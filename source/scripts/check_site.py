#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Check generated static files, links and ontology term coverage without a server."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdflib import RDF, RDFS
from scripts.build_rdf import assemble
from scripts.catalog import ROOT, catalog
from scripts.site_projection import SAO, SPEC, compact
from scripts.site_publication import (SITE_NAME, SITE_ORIGIN, SOCIAL_IMAGE,
                                      canonical_url, check_public_sources, source_manifest)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id":
                self.ids.add(value)
            if tag != "base" and value and key in ("href", "src", "data-href"):
                self.targets.append(value)


def check_search(directory, payload, failures):
    """Check search coverage, content hash, local routes and generated anchors."""
    directory = Path(directory).resolve()
    index_path = directory / "search-index.json"
    if not index_path.is_file():
        failures.append("Missing local search index")
        return
    index = json.loads(index_path.read_text())
    entries = index.get("entries", [])
    snapshot = json.loads((directory / "snapshot.json").read_text())
    expected = {(term["type"], compact(term["id"]))
                for group in payload if group["type"] in ("Classes", "Properties")
                for term in group["concepts"] if term["id"].startswith((str(SAO), str(SPEC)))}
    actual = {(entry["kind"], entry["id"]) for entry in entries if entry["kind"] != "Guide"}
    if index.get("version") != 1 or expected != actual:
        failures.append("Search term coverage differs from the local Garden projection")
    if len({(entry["kind"], entry["id"]) for entry in entries}) != len(entries):
        failures.append("Duplicate search records")
    metadata = snapshot.get("search_index", {})
    if metadata != {"path": "search-index.json", "entries": len(entries),
                    "sha256": hashlib.sha256(index_path.read_bytes()).hexdigest()}:
        failures.append("Search snapshot hash or entry count differs")
    guide_urls = {entry["url"] for entry in entries if entry["kind"] == "Guide"}
    expected_guides = {p.relative_to(directory).as_posix() for p in (directory / "guides").rglob("*.html")
                       if p != directory / "guides/index.html"}
    if guide_urls != expected_guides or len(guide_urls) != snapshot["guide_pages"]:
        failures.append("Search guide coverage differs from rendered guides")
    for entry in entries:
        url = entry["url"]
        if entry["kind"] != "Guide":
            if url != "reference/#" + entry["id"]:
                failures.append(f"Search term has an invalid Garden fragment: {url}")
            continue
        target = (directory / url).resolve()
        if not target.is_relative_to(directory) or not target.is_file():
            failures.append(f"Search guide does not resolve locally: {url}")
            continue
        parser = Links()
        parser.feed(target.read_text())
        for heading in entry.get("headings", []):
            if heading["id"] not in parser.ids:
                failures.append(f"Search guide heading does not resolve: {url}#{heading['id']}")
        for anchor in (link[1:] for link in parser.targets if link.startswith("#")):
            if unquote(anchor) not in parser.ids:
                failures.append(f"Guide anchor does not resolve: {url}#{anchor}")


class Publication(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.canonicals = []
        self.title = ""
        self.in_title = False
        self.lang = None
        self.resources = []
        self.base = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "title":
            self.in_title = True
        if tag == "base":
            self.base = attrs.get("href")
        if tag == "meta":
            key = attrs.get("name", attrs.get("property", attrs.get("http-equiv")))
            self.meta.setdefault(key, []).append(attrs.get("content", ""))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag in ("script", "img", "iframe", "video", "audio", "source"):
            self.resources.append(attrs.get("src", ""))
        if tag == "link" and attrs.get("rel") in ("stylesheet", "icon", "preload", "modulepreload"):
            self.resources.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def check_publication(directory, failures):
    """Fail closed on missing publication artifacts and repeated page identities."""
    directory = Path(directory)
    required = ("index.html", "reference/index.html", "guides/index.html", "source/index.html",
                "sao/index.html", "specspec/index.html", "404.html", "healthz", "robots.txt", "sitemap.xml", SOCIAL_IMAGE)
    missing = [name for name in required if not (directory / name).is_file()]
    failures.extend("Missing publication artifact: " + name for name in missing)
    if missing:
        return
    source_failures = []
    check_public_sources(ROOT, directory, source_failures)
    if source_failures:
        failures.extend(source_failures)
        return  # Do not parse unexpected payloads or follow output symlinks.
    manifest = source_manifest(ROOT)
    distribution_names = {Path(name).name for name in manifest["files"] if name.startswith("dist/")}
    distributions = directory / "dist"
    if distributions.is_symlink() or not distributions.is_dir():
        failures.append("Missing regular public distribution directory")
        return
    if {path.name for path in distributions.iterdir()} != distribution_names:
        failures.append("Public distribution inventory differs from reviewed sources")
    for name in distribution_names:
        path = distributions / name
        if path.is_symlink() or not path.is_file() or path.read_bytes() != (directory / "source/dist" / name).read_bytes():
            failures.append("Missing or changed public distribution: " + name)
    expected_guides = {str(Path("guides") / Path(name).with_suffix(".html"))
                       for name in manifest["files"] if name.endswith(".md")} | {"guides/index.html"}
    actual_guides = {path.relative_to(directory).as_posix() for path in (directory / "guides").rglob("*.html")}
    if actual_guides != expected_guides:
        failures.append("Rendered guide inventory differs from reviewed public sources")
    titles, descriptions = set(), set()
    expected_urls = set()
    for path in sorted(directory.rglob("*.html")):
        relative = path.relative_to(directory).as_posix()
        parser = Publication()
        parser.feed(path.read_text())
        description = parser.meta.get("description", [""])[0]
        expected = {"description": description, "og:type": "website", "og:site_name": SITE_NAME,
                    "og:title": parser.title, "og:description": description, "og:url": canonical_url(relative),
                    "og:image": SITE_ORIGIN + "/" + SOCIAL_IMAGE, "og:image:type": "image/png",
                    "og:image:width": "1200", "og:image:height": "630",
                    "twitter:card": "summary_large_image", "twitter:title": parser.title,
                    "twitter:description": description, "twitter:image": SITE_ORIGIN + "/" + SOCIAL_IMAGE}
        if any(parser.meta.get(key) != [value] for key, value in expected.items()):
            failures.append("Incomplete or inconsistent publication metadata: " + relative)
        if not parser.meta.get("og:image:alt", [""])[0] or not parser.meta.get("twitter:image:alt", [""])[0]:
            failures.append("Missing social image alternative text: " + relative)
        if not parser.title or parser.title in titles or not description or description in descriptions:
            failures.append("Missing or duplicate page title/description: " + relative)
        titles.add(parser.title)
        descriptions.add(description)
        if parser.lang != "en" or parser.canonicals != [canonical_url(relative)]:
            failures.append("Invalid language or canonical URL: " + relative)
        if any(url.startswith("//") or ":" in url.split("/")[0] for url in parser.resources if url):
            failures.append("Nonlocal runtime resource: " + relative)
        if "connect-src 'self'" not in parser.meta.get("Content-Security-Policy", [""])[0]:
            failures.append("Missing same-origin connection policy: " + relative)
        if relative == "404.html":
            if parser.meta.get("robots") != ["noindex, follow"] or not re.fullmatch(r"/(?:[A-Za-z0-9_-]+/)*", parser.base or ""):
                failures.append("404 must be noindex with a hosting-base recovery path")
        else:
            expected_urls.add(canonical_url(relative))
    try:
        # Parse only our local build artifact, never untrusted remote XML.
        sitemap = ET.parse(directory / "sitemap.xml")
        locations = [node.text for node in sitemap.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        if set(locations) != expected_urls or len(locations) != len(set(locations)):
            failures.append("Sitemap coverage differs from canonical HTML pages")
    except ET.ParseError:
        failures.append("Invalid sitemap XML")
    if (directory / "robots.txt").read_text() != "User-agent: *\nAllow: /\nSitemap: " + SITE_ORIGIN + "/sitemap.xml\n":
        failures.append("Robots policy differs from the public library policy")
    if (directory / "healthz").read_text() != "ok\n":
        failures.append("Invalid static health response")
    image = (directory / SOCIAL_IMAGE).read_bytes()
    if len(image) < 24 or image[:8] != b"\x89PNG\r\n\x1a\n" or image[12:16] != b"IHDR" or struct.unpack(">II", image[16:24]) != (1200, 630):
        failures.append("Social image must be an actual 1200×630 PNG")
    source = directory / "source"
    for folder in ("documents", ".git", "creds"):
        if (directory / folder).exists() or (source / folder).exists():
            failures.append("Unexpected private/operational directory: " + folder)


def check(directory):
    directory = Path(directory).resolve()
    failures = []
    check_publication(directory, failures)
    if failures:
        raise ValueError("\n".join(failures))
    pages = directory.rglob("*.html")
    for path in pages:
        parser = Links()
        parser.feed(path.read_text())
        for url in parser.targets:
            if url.startswith(("#", "//")) or ":" in url.split("/")[0]:
                continue
            filename = unquote(url.split("#")[0].split("?")[0])
            target = directory / filename.lstrip("/") if url.startswith("/") else path.parent / filename
            if target.is_dir():
                target /= "index.html"
            if filename and not target.exists():
                failures.append(f"{path.relative_to(directory)} → {url}")
    for css in directory.glob("assets/styles/*.css"):
        for url in re.findall(r"url\(['\"]?([^)'\"]+)", css.read_text()):
            if not (css.parent / url).is_file():
                failures.append(f"{css.relative_to(directory)} → {url}")
    homepage = (directory / "index.html").read_text()
    if "{{sao_version}}" in homepage or "{{specspec_version}}" in homepage:
        failures.append("Homepage contains unresolved ontology versions")
    if not (directory / "assets/legacy-reference.js").is_file():
        failures.append("Missing compatibility redirect for old Garden bookmarks")
    dataset = directory / "reference/ecosystem.json"
    digest = hashlib.sha256(dataset.read_bytes()).hexdigest()
    if "./ecosystem.json?sha256=" + digest not in (directory / "reference/index.html").read_text():
        failures.append("Dataset URL is missing its current content hash")
    payload = json.loads(dataset.read_text())
    check_search(directory, payload, failures)
    terms = {kind: {item["id"] for item in payload[index]["concepts"]}
             for index, kind in enumerate(("class", "property"))}
    def covered(node, kind):
        return str(node) in terms[kind]
    for entry in catalog().values():
        for name in entry["products"]:
            if not name.endswith("vocabulary"):
                continue
            graph = assemble(ROOT / entry["source"] / "manifests" / (name + ".json"))
            for node in graph.subjects(RDF.type, RDFS.Class):
                if not covered(node, "class"):
                    failures.append(f"Missing class: {node}")
            for node in graph.subjects(RDF.type, RDF.Property):
                if not covered(node, "property"):
                    failures.append(f"Missing property: {node}")
    bootstrap = (directory / "assets/vendor/v2/explorer.js").read_text()
    if 'DecompressionStream("gzip")' in bootstrap:
        failures.append("Bootstrap still expects compressed data instead of CDN-friendly JSON")
    if failures:
        raise ValueError("\n".join(failures))
    print("Static site checks pass: public artifacts, canonical/social metadata, sitemap, source scope, ontology/search coverage, guide anchors, snapshot hash and local HTML links resolve.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    check(args.directory)
