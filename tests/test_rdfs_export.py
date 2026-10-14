# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
import sys
import tempfile
from pathlib import Path
import unittest
from rdflib import Graph, Namespace, RDF, RDFS
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/migration"))
from export_rdfs import build_graph, validate_projection, partition_graph, write_or_check, load_manifest, SCHEMA

FIXTURE = """
id: https://example.org/test/
name: rdfs-export-fixture
title: Export fixture
description: Exercise shared properties and mixins.
version: 1.0.0
prefixes:
  test: https://example.org/test/
  linkml: https://w3id.org/linkml/
default_prefix: test
imports:
  - linkml:types
enums:
  State:
    permissible_values:
      ready:
        description: Ready for use.
classes:
  Mixin:
    mixin: true
  A:
    mixins: [Mixin]
    attributes:
      shared:
        range: string
      unique:
        range: State
  B:
    attributes:
      shared:
        range: integer
"""

class RdfsProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "schema.yaml"
        self.path.write_text(FIXTURE)
        self.graph = build_graph(self.path)
        self.ns = Namespace("https://example.org/test/")

    def test_shared_property_does_not_assert_intersection(self):
        self.assertEqual(list(self.graph.objects(self.ns.shared, RDFS.domain)), [])
        self.assertEqual(list(self.graph.objects(self.ns.shared, RDFS.range)), [])
        self.assertEqual(set(self.graph.objects(self.ns.shared, SCHEMA.domainIncludes)), {self.ns.A, self.ns.B})
        self.assertEqual(len(set(self.graph.objects(self.ns.shared, SCHEMA.rangeIncludes))), 2)

    def test_unique_property_and_mixin(self):
        self.assertIn((self.ns.unique, RDFS.domain, self.ns.A), self.graph)
        self.assertIn((self.ns.unique, RDFS.range, self.ns.State), self.graph)
        self.assertIn((self.ns.A, RDFS.subClassOf, self.ns.Mixin), self.graph)
        self.assertIn((self.ns.State, RDF.type, RDFS.Datatype), self.graph)

    def test_modular_export_assembles_exactly(self):
        pieces = partition_graph(self.graph, self.path)
        directory = Path(self.temp.name) / "rdf"
        output = Path(self.temp.name) / "complete.ttl"
        write_or_check(self.graph, pieces, output, directory, check=False)
        self.assertEqual(set(load_manifest(directory / "manifest.json")), set(self.graph))
        write_or_check(self.graph, pieces, output, directory, check=True)
        target = directory / "common.ttl"
        target.write_text(target.read_text() + '\n<urn:extra:s> <urn:extra:p> <urn:extra:o> .\n')
        with self.assertRaisesRegex(ValueError, "stale"):
            write_or_check(self.graph, pieces, output, directory, check=True)

    def test_shared_property_is_owned_by_common_across_modules(self):
        self.path.write_text(FIXTURE.split("enums:")[0] + "imports: [linkml:types, schema/a, schema/b]\n")
        # Replace the first imports declaration rather than retaining duplicate keys.
        text = self.path.read_text().replace("imports:\n  - linkml:types\n", "")
        self.path.write_text(text)
        directory = self.path.parent / "schema"
        directory.mkdir()
        for name, range_name in (("a", "string"), ("b", "integer")):
            (directory / (name + ".yaml")).write_text(
                "id: https://example.org/test/schema/" + name + "\nname: " + name +
                "\nprefixes:\n  test: https://example.org/test/\ndefault_prefix: test\nclasses:\n  " +
                name.upper() + ":\n    attributes:\n      shared:\n        range: " + range_name + "\n")
        graph = build_graph(self.path)
        pieces = partition_graph(graph, self.path)
        self.assertIn((self.ns.shared, RDF.type, RDF.Property), pieces["common.ttl"])
        self.assertNotIn((self.ns.shared, RDF.type, RDF.Property), pieces["a.ttl"])
        self.assertNotIn((self.ns.shared, RDF.type, RDF.Property), pieces["b.ttl"])
        self.assertEqual(set().union(*(set(piece) for piece in pieces.values())), set(graph))
        triples = sum(len(piece) for piece in pieces.values())
        self.assertEqual(triples, len(graph))

    def test_turtle_roundtrip_and_rdfs_projection(self):
        validate_projection(self.graph, self.path)
        parsed = Graph().parse(data=self.graph.serialize(format="turtle"), format="turtle")
        self.assertEqual(set(parsed), set(self.graph))

if __name__ == "__main__":
    unittest.main()
