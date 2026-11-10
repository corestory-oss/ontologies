# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Cross-glossary term mappings carry a basis claim and never merge terms."""
import unittest

from rdflib import Literal, URIRef

from scripts.validate_rdf import example, sources, validate_graph
from scripts.validators.specspec import BRIDGE, SAO

LINK = URIRef("urn:specspec:demo:glossary:balance-match")
GLOSSARY = "https://example.org/sao/glossary/"


class GlossaryMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocabulary, cls.shapes = sources("ecosystem")

    def check(self, data):
        conforms, _, report = validate_graph(data, "ecosystem", vocabulary=self.vocabulary, shapes=self.shapes)
        return conforms, report

    def assertRejected(self, data, component):
        conforms, report = self.check(data)
        self.assertFalse(conforms)
        self.assertIn(component, report)

    def test_example_mapping_is_validated(self):
        data = example("ecosystem")
        self.assertIn((LINK, BRIDGE.mapping_relation, Literal("exact_match")), data)
        conforms, report = self.check(data)
        self.assertTrue(conforms, report)

    def test_basis_claim_required(self):
        data = example("ecosystem")
        data.remove((LINK, BRIDGE.basis_claim, None))
        self.assertRejected(data, "MinCountConstraintComponent")

    def test_relation_must_be_a_skos_mapping_kind(self):
        data = example("ecosystem")
        data.set((LINK, BRIDGE.mapping_relation, Literal("same_as")))
        self.assertRejected(data, "InConstraintComponent")

    def test_term_cannot_match_itself(self):
        data = example("ecosystem")
        data.set((LINK, BRIDGE.matched_term, URIRef(GLOSSARY + "retail-balance")))
        self.assertRejected(data, "DisjointConstraintComponent")

    def test_endpoints_must_be_glossary_terms(self):
        data = example("ecosystem")
        data.set((LINK, BRIDGE.matched_term, URIRef(GLOSSARY + "available-balance-field")))
        self.assertRejected(data, "ClassConstraintComponent")

    def test_mapping_keeps_both_terms(self):
        data = example("ecosystem")
        for key in ("retail-balance", "finance-spendable-funds"):
            term = URIRef(GLOSSARY + key)
            self.assertEqual(len(set(data.objects(term, SAO.contained_in_glossary))), 1)


if __name__ == "__main__":
    unittest.main()
