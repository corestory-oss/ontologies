# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import sys
import tempfile
from pathlib import Path
import unittest
from rdflib import Graph, Namespace, RDF, Literal
from scripts.build_rdf import assemble, same_graph
from scripts.validators.sao import sources, check_data

SAO = Namespace("https://ontologies.corestory.ai/sao/")
EX = Namespace("https://example.org/test/")

class TurtleSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocabulary, cls.shapes = sources()

    def system(self):
        graph = Graph()
        graph.add((EX.system, RDF.type, SAO.System))
        graph.add((EX.system, SAO.id, Literal("system")))
        graph.add((EX.system, SAO.name, Literal("System")))
        return graph

    def valid(self, graph):
        return check_data(graph, self.vocabulary, self.shapes)[0]

    def test_valid_system(self):
        self.assertTrue(self.valid(self.system()))

    def test_missing_required_name(self):
        graph = self.system();graph.remove((EX.system, SAO.name, None))
        self.assertFalse(self.valid(graph))

    def test_single_value_cardinality(self):
        graph = self.system();graph.add((EX.system, SAO.name, Literal("Second name")))
        self.assertFalse(self.valid(graph))

    def test_enum_constraint(self):
        graph = self.system()
        graph.add((EX.call, RDF.type, SAO.CallableUnit))
        graph.add((EX.call, SAO.id, Literal("call")))
        graph.add((EX.call, SAO.name, Literal("Call")))
        graph.add((EX.call, SAO.callable_type, Literal("method")))
        self.assertTrue(self.valid(graph))
        graph.set((EX.call, SAO.callable_type, Literal("not-a-callable-type")))
        self.assertFalse(self.valid(graph))

    def test_class_range(self):
        graph = self.system()
        graph.add((EX.system, SAO.metadata, Literal("not a Metadata node")))
        self.assertFalse(self.valid(graph))

    def test_scalar_pattern(self):
        graph = self.system()
        graph.add((EX.metadata, RDF.type, SAO.Metadata))
        graph.add((EX.metadata, SAO.version, Literal("2.1.0")))
        self.assertTrue(self.valid(graph))
        graph.set((EX.metadata, SAO.version, Literal("not-semver")))
        self.assertFalse(self.valid(graph))

    def test_anonymous_shape_roundtrip(self):
        text = '<urn:shape> <http://www.w3.org/ns/shacl#property> [ <http://www.w3.org/ns/shacl#path> <urn:property> ] .'
        left = Graph().parse(data=text, format="turtle")
        right = Graph().parse(data=left.serialize(format="turtle"), format="turtle")
        self.assertTrue(same_graph(left, right))

    def test_manifest_escape_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manifests").mkdir()
            manifest = root / "manifests/vocabulary.json"
            manifest.write_text(json.dumps({"format":"turtle", "files":["../outside.ttl"]}))
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                assemble(manifest)

    def test_authored_turtle_change_drives_assembly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manifests").mkdir()
            source = root / "source.ttl"
            source.write_text('<urn:subject> <urn:property> "before" .')
            manifest = root / "manifests/vocabulary.json"
            manifest.write_text(json.dumps({"format":"turtle", "files":["source.ttl"]}))
            before = assemble(manifest)
            source.write_text('<urn:subject> <urn:property> "after" .')
            after = assemble(manifest)
            self.assertNotEqual(set(before), set(after))

if __name__ == "__main__":
    unittest.main()
