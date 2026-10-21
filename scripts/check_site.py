#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Check generated static files, links and ontology term coverage without a server."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdflib import RDF, RDFS
from scripts.build_rdf import assemble
from scripts.catalog import ROOT, catalog


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and key in ("href", "src", "data-href"):
                self.targets.append(value)


def check(directory):
    directory = Path(directory).resolve()
    failures = []
    pages = directory.rglob("*.html")
    for path in pages:
        parser = Links()
        parser.feed(path.read_text())
        for url in parser.targets:
            if url.startswith("#") or ":" in url.split("/")[0]:
                continue
            filename = unquote(url.split("#")[0].split("?")[0])
            target = directory / filename.lstrip("/") if url.startswith("/") else path.parent / filename
            if filename and not target.exists():
                failures.append(f"{path.relative_to(directory)} → {url}")
    dataset = directory / "ecosystem.json"
    digest = hashlib.sha256(dataset.read_bytes()).hexdigest()
    if "./ecosystem.json?sha256=" + digest not in (directory / "index.html").read_text():
        failures.append("Dataset URL is missing its current content hash")
    payload = json.loads(dataset.read_text())
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
    bootstrap = (directory / "vendor/v2/explorer.js").read_text()
    if 'DecompressionStream("gzip")' in bootstrap:
        failures.append("Bootstrap still expects compressed data instead of CDN-friendly JSON")
    if failures:
        raise ValueError("\n".join(failures))
    print(f"Static site checks pass: ontology term coverage and inspected local HTML links resolve.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    check(args.directory)
