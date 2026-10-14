# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import sys
import tempfile
from pathlib import Path
import unittest
from rdflib import Graph, URIRef
from rdflib.namespace import OWL
from owlrl import DeductiveClosure, OWLRL_Semantics
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "scripts"))
from validate_axioms import check_axioms, check_shape_ranges
sys.path.insert(0,str(ROOT / "scripts/migration"))
from audit_inverses import audit

class InverseAxiomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocabulary,cls.axioms,cls.pairs=check_axioms()

    def test_all_accepted_pairs_infer_reverse_edges_in_both_directions(self):
        graph=Graph()
        graph+=self.axioms
        expected=[]
        for index,(a,b) in enumerate(sorted(self.pairs)):
            left=URIRef(f"urn:inverse-test:{index}:left")
            right=URIRef(f"urn:inverse-test:{index}:right")
            other=URIRef(f"urn:inverse-test:{index}:other")
            graph.add((left,a,right));expected.append((right,b,left))
            graph.add((other,b,left));expected.append((left,a,other))
        # Exercise an actual OWL-RL implementation rather than a hand-written inversion.
        DeductiveClosure(OWLRL_Semantics).expand(graph)
        for triple in expected:
            self.assertIn(triple,graph)

    def test_retired_predicates_have_no_inverse_axioms(self):
        from rdflib import Literal
        excluded=set(self.vocabulary.subjects(OWL.deprecated,Literal(True)))
        endpoints={p for a,b in self.axioms.subject_objects(OWL.inverseOf) for p in (a,b)}
        self.assertTrue(excluded)
        self.assertFalse(excluded & endpoints)

    def test_authored_shape_range_conflicts_are_rejected(self):
        from rdflib import Namespace
        from build_rdf import assemble
        sh=Namespace("http://www.w3.org/ns/shacl#")
        shapes=assemble(ROOT / "rdf/manifests/shapes.json")
        participating={property for pair in self.pairs for property in pair}
        for node,path in shapes.subject_objects(sh.path):
            if path in participating and shapes.value(node,sh["class"]) is not None:
                shapes.set((node,sh["class"],URIRef("urn:unknown:Class")))
                break
        with self.assertRaisesRegex(ValueError,"range mismatch"):
            check_shape_ranges(self.vocabulary,shapes,self.pairs)

    def test_unrelated_properties_do_not_get_reverse_edges(self):
        graph=Graph();graph+=self.axioms
        source,target=URIRef("urn:test:source"),URIRef("urn:test:target")
        graph.add((source,URIRef("https://ontologies.corestory.ai/sao/has_file_operations"),target))
        DeductiveClosure(OWLRL_Semantics).expand(graph)
        for name in ("operates_on_file","performed_in_callable"):
            self.assertNotIn((target,URIRef("https://ontologies.corestory.ai/sao/"+name),source),graph)



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

if __name__ == "__main__":
    unittest.main()
