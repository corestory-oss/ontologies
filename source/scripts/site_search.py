# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, read-only search records for the rendered site and Garden view."""
from html.parser import HTMLParser
import json
from urllib.parse import quote

from scripts.site_projection import SAO, SPEC, compact


class PlainText(HTMLParser):
    """Read rendered text, not Markdown syntax or raw HTML, into search fields."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.headings = []
        self.heading = None
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.ignored += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.heading = {"level": int(tag[1]), "id": dict(attrs).get("id", ""), "parts": []}
        if tag in ("p", "li", "br", "pre", "tr", "td", "th", "div") or tag.startswith("h"):
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.ignored = max(0, self.ignored - 1)
        if self.heading and tag == "h" + str(self.heading["level"]):
            self.headings.append({"level": self.heading["level"], "id": self.heading["id"],
                                  "title": " ".join("".join(self.heading["parts"]).split())})
            self.heading = None
        if tag in ("p", "li", "pre", "tr", "td", "th", "div") or tag.startswith("h"):
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.ignored:
            self.parts.append(data)
            if self.heading:
                self.heading["parts"].append(data)

    @property
    def text(self):
        return " ".join("".join(self.parts).split())


def plain_text(html):
    parser = PlainText()
    parser.feed(html)
    return parser.text


def excerpt(text, limit=240):
    if len(text) <= limit:
        return text
    boundary = text.rfind(" ", 0, limit)
    return text[:boundary if boundary > 0 else limit].rstrip() + "…"


def guide_record(body, target, source, fallback):
    parser = PlainText()
    parser.feed(body)
    title = next((h["title"] for h in parser.headings if h["level"] == 1), fallback)
    text = parser.text
    summary = text[len(title):].lstrip() if text.startswith(title) else text
    return {"kind": "Guide", "title": title, "id": source, "url": target,
            "description": excerpt(summary), "text": text,
            "headings": [h for h in parser.headings if h["level"] in (2, 3)]}


def search_index(payload, guide_records, metadata):
    """Index only local projected terms; external RDF standards stay in Garden."""
    entries = []
    for group in payload:
        if group["type"] not in ("Classes", "Properties"):
            continue
        for term in group["concepts"]:
            iri = term["id"]
            if not iri.startswith((str(SAO), str(SPEC))):
                continue
            name = compact(iri)
            title = term.get("label", {}).get("en") or name.split(":", 1)[-1]
            # Projection definitions are plain RDF text, unlike rendered remarks.
            # HTML parsing would discard generic type notation such as List<T>.
            definition = " ".join(term.get("definition", {}).get("en", "").split())
            remarks = plain_text(term.get("remarks", {}).get("en", ""))
            ontology = "sao" if iri.startswith(str(SAO)) else "specspec"
            entries.append({"kind": term["type"], "title": title, "id": name, "iri": iri,
                            "url": "reference/#" + quote(name, safe=":/"),
                            "description": excerpt(definition),
                            "text": " ".join((name, iri, title, definition, remarks)),
                            "ontology": ontology, "version": metadata["ontologies"][ontology]["version"],
                            "deprecated": bool(term.get("deprecated", False))})
    entries.extend(guide_records)
    entries.sort(key=lambda item: (item["kind"], item["id"]))
    return {"version": 1, "entries": entries}


def serialize_index(index):
    return json.dumps(index, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
