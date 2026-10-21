# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
import tempfile
from pathlib import Path
import unittest
from rdflib import Graph, URIRef
from scripts.migration.sao.audit_inverses import audit

class LegacyInverseAuditTests(unittest.TestCase):
    def run_audit(self, extra=""):
        text = """id: https://example.org/audit/
name: inverse-audit-fixture
version: 1.0.0
prefixes:
  ex: https://example.org/audit/
default_prefix: ex
classes:
  A:
    attributes:
      forward:
        range: B
        inverse: backward
  B:
    attributes:
      backward:
        range: A
        inverse: forward
""" + extra
        from rdflib import RDF
        graph=Graph()
        for name in ("forward","backward"):
            graph.add((URIRef("https://example.org/audit/"+name),RDF.type,RDF.Property))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"schema.yaml";path.write_text(text)
            return audit(path,graph)

    def test_consistent_pair_is_accepted(self):
        report=self.run_audit()
        self.assertEqual(report["counts"]["accepted_pairs"],1)
        self.assertEqual(report["counts"]["unresolved_groups"],0)

    def test_class_local_range_mismatch_is_withheld(self):
        report=self.run_audit("""  C:
    attributes:
      forward:
        range: B
        inverse: backward
""")
        self.assertEqual(report["counts"]["accepted_pairs"],0)
        reasons=report["unresolved_groups"][0]["reasons"]
        self.assertTrue(any("cannot point back to C" in reason for reason in reasons))

    def test_global_inverse_checks_uses_without_local_annotations(self):
        report=self.run_audit("""  C:
    attributes:
      forward:
        range: B
""")
        self.assertEqual(report["counts"]["accepted_pairs"],0)
        self.assertTrue(any("Global inverse" in reason for reason in report["unresolved_groups"][0]["reasons"]))
