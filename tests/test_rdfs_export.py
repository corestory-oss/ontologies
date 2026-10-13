# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
import sys
import tempfile
from pathlib import Path
import unittest
from rdflib import Graph, Namespace, RDF, RDFS
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from export_rdfs import build_graph, validate_projection, SCHEMA

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

    def test_turtle_roundtrip_and_rdfs_projection(self):
        validate_projection(self.graph, self.path)
        parsed = Graph().parse(data=self.graph.serialize(format="turtle"), format="turtle")
        self.assertEqual(set(parsed), set(self.graph))

if __name__ == "__main__":
    unittest.main()
