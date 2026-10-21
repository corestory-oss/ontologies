# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Contracts for the Garden display projection and deterministic output."""
from collections import Counter
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import unittest

from rdflib import Graph, RDF, RDFS
from scripts.build_rdf import ROOT, assemble, turtle
from scripts.catalog import catalog
from scripts.site_projection import project


class SiteProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.metadata = project()
        cls.classes = {c["id"]: c for c in cls.payload[0]["concepts"]}
        cls.properties = {p["id"]: p for p in cls.payload[1]["concepts"]}

    def test_requirement_definition_is_normative(self):
        node = self.classes["https://ontologies.corestory.ai/specspec/Requirement"]
        constraint = next(p for p in node["shape"][0] if p["property"].endswith("/statement_mode"))
        self.assertEqual(constraint["min"], 1)
        self.assertEqual(constraint["max"], 1)
        self.assertEqual(constraint["shape"], [{"@value": "normative"}])
        self.assertIn("reviewer", node["remarks"]["en"])

    def test_bridge_points_to_both_ontologies(self):
        node = self.classes["https://ontologies.corestory.ai/specspec/sao/RequirementImplementationLink"]
        ranges = {r for p in node["shape"][0] for option in p.get("shape", [])
                  if isinstance(option, list) for r in option}
        self.assertIn("https://ontologies.corestory.ai/specspec/Requirement", ranges)
        self.assertIn("https://ontologies.corestory.ai/sao/CallableUnit", ranges)

    def test_inverse_and_retirement_explanations_are_present(self):
        prop = self.properties["https://ontologies.corestory.ai/sao/invokes_callables"]
        self.assertIn("OWL inverse:", prop["remarks"]["en"])
        retired = [p for p in self.properties.values() if p.get("deprecated")]
        self.assertEqual(len(retired), 9)
        self.assertTrue(all(p.get("remarks") for p in retired))

    def test_datastore_allowed_values_appear_once(self):
        node = self.classes["https://ontologies.corestory.ai/sao/DataStoreType"]
        remarks = node["remarks"]["en"]
        self.assertEqual(remarks.count("<li>"), 14)
        self.assertEqual(remarks.count("<code>document_db</code>"), 1)
        self.assertEqual(remarks.count("<code>flat_file</code>"), 1)

    def test_every_enum_glossary_matches_turtle_once(self):
        class Items(HTMLParser):
            def __init__(self):
                super().__init__()
                self.items = []
            def handle_starttag(self, tag, attrs):
                if tag == "li":
                    self.items.append("")
            def handle_data(self, data):
                if self.items:
                    self.items[-1] += data

        checked = 0
        for entry in catalog().values():
            for product in entry["products"]:
                if not product.endswith("vocabulary"):
                    continue
                graph = assemble(ROOT / entry["source"] / "manifests" / (product + ".json"))
                for datatype in graph.subjects(RDF.type, RDFS.Datatype):
                    values = {value for predicate, value in graph.predicate_objects(datatype)
                              if str(predicate).endswith("/permissibleValue")}
                    if not values:
                        continue
                    with self.subTest(datatype=str(datatype)):
                        remarks = self.classes[str(datatype)]["remarks"]["en"]
                        glossary = remarks.split("<h3>Allowed values</h3><ul>", 1)[1].split("</ul>", 1)[0]
                        parser = Items()
                        parser.feed(glossary)
                        expected = []
                        for value in values:
                            label = str(graph.value(value, RDF.value))
                            description = graph.value(value, RDFS.comment)
                            expected.append(label + (": " + str(description) if description else ""))
                        self.assertEqual(Counter(parser.items), Counter(expected))
                    checked += 1
        self.assertGreater(checked, 0)

    def test_source_manifest_hashes_and_portability(self):
        expected = set()
        for entry in catalog().values():
            for name in entry["products"]:
                manifest = ROOT / entry["source"] / "manifests" / (name + ".json")
                expected.update(str(Path(entry["source"]) / p) for p in json.loads(manifest.read_text())["files"])
        self.assertEqual({item["path"] for item in self.metadata["inputs"]}, expected)
        for item in self.metadata["inputs"]:
            self.assertFalse(Path(item["path"]).is_absolute())
            self.assertEqual(item["sha256"], hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest())
        self.assertNotIn("built_at", self.metadata)

    def test_projection_is_reproducible(self):
        payload, metadata = project()
        self.assertEqual(json.dumps(payload, sort_keys=True), json.dumps(self.payload, sort_keys=True))
        self.assertEqual(metadata, self.metadata)

    def test_rdf_anonymous_nodes_serialize_reproducibly(self):
        text = '<urn:shape> <urn:property> [ <urn:path> <urn:field> ] .'
        left = Graph().parse(data=text, format="turtle")
        right = Graph().parse(data=text, format="turtle")
        self.assertEqual(turtle(left), turtle(right))


if __name__ == "__main__":
    unittest.main()
