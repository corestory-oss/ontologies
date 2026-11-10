# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Glossary terms: SKOS-aligned labels, bindings, and no merging by label."""
from pathlib import Path
import unittest

from owlrl import DeductiveClosure, OWLRL_Semantics
from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import OWL, SKOS

from scripts.validators.sao import sources, check_data
from scripts.validators.sao_axioms import check_axioms

ROOT = Path(__file__).resolve().parents[2]
S = Namespace("https://ontologies.corestory.ai/sao/")
EX = Namespace("https://example.org/sao/glossary/")


class GlossaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocabulary, cls.shapes = sources()
        _, cls.axioms, _ = check_axioms()
        cls.example = Graph().parse(ROOT / "examples/sao/rdf/glossary.ttl", format="turtle")

    def graph(self):
        g = Graph()
        g += self.example
        return g

    def report(self, g):
        conforms, _, text = check_data(g, self.vocabulary, self.shapes)
        return conforms, text

    def assertRejected(self, g, component):
        conforms, text = self.report(g)
        self.assertFalse(conforms)
        self.assertIn(component, text)

    def reason(self, g):
        data = Graph()
        data += g
        data += self.vocabulary
        data += self.axioms
        DeductiveClosure(OWLRL_Semantics).expand(data)
        return data

    def test_example_conforms(self):
        conforms, text = self.report(self.graph())
        self.assertTrue(conforms, text)

    def test_preferred_label_required(self):
        g = self.graph()
        g.remove((EX["retail-account-balance"], S.preferred_label, None))
        self.assertRejected(g, "MinCountConstraintComponent")

    def test_one_preferred_label_per_language(self):
        g = self.graph()
        g.add((EX["retail-balance"], S.preferred_label, Literal("Current balance", lang="en")))
        self.assertRejected(g, "UniqueLangConstraintComponent")

    def test_one_untagged_preferred_label(self):
        g = self.graph()
        term = EX["retail-account-balance"]
        g.set((term, S.preferred_label, Literal("Account balance")))
        self.assertTrue(self.report(g)[0])
        g.add((term, S.preferred_label, Literal("Balance of account")))
        self.assertRejected(g, "QualifiedMaxCountConstraintComponent")

    def test_preferred_labels_in_several_languages(self):
        g = self.graph()
        g.add((EX["retail-balance"], S.preferred_label, Literal("Saldo", lang="de")))
        self.assertTrue(self.report(g)[0])

    def test_label_kinds_are_disjoint(self):
        term = EX["retail-balance"]
        for prop, value in ((S.alternative_labels, Literal("Balance", lang="en")),
                            (S.hidden_labels, Literal("Balance", lang="en")),
                            (S.short_codes, Literal("AVBL"))):
            with self.subTest(prop=prop):
                g = self.graph()
                if prop == S.short_codes:
                    g.add((term, S.preferred_label, value))
                else:
                    g.add((term, prop, value))
                self.assertRejected(g, "DisjointConstraintComponent")

    def test_label_must_be_text(self):
        g = self.graph()
        g.add((EX["retail-balance"], S.alternative_labels, EX["available-balance-field"]))
        self.assertRejected(g, "OrConstraintComponent")

    def test_term_belongs_to_exactly_one_glossary(self):
        g = self.graph()
        g.remove((EX["finance-balance"], S.contained_in_glossary, None))
        self.assertRejected(g, "MinCountConstraintComponent")
        g = self.graph()
        g.add((EX["finance-balance"], S.contained_in_glossary, EX.retail))
        self.assertRejected(g, "MaxCountConstraintComponent")

    def test_glossary_must_be_a_glossary(self):
        g = self.graph()
        g.set((EX["finance-balance"], S.contained_in_glossary, EX["ledger-balance-field"]))
        self.assertRejected(g, "ClassConstraintComponent")

    def test_binding_targets_a_system_entity_not_a_term_or_text(self):
        g = self.graph()
        g.add((EX["retail-balance"], S.describes_entities, EX["finance-balance"]))
        self.assertRejected(g, "NotConstraintComponent")
        g = self.graph()
        g.add((EX["retail-balance"], S.describes_entities, Literal("available_balance")))
        self.assertRejected(g, "ClassConstraintComponent")

    def test_hierarchy_stays_between_terms(self):
        g = self.graph()
        g.add((EX["retail-balance"], S.has_broader_terms, EX["available-balance-field"]))
        self.assertRejected(g, "ClassConstraintComponent")
        g = self.graph()
        g.add((EX["retail-balance"], S.has_narrower_terms, EX["retail-account-balance"]))
        self.assertRejected(g, "DisjointConstraintComponent")

    def test_same_label_terms_stay_distinct(self):
        retail, finance = EX["retail-balance"], EX["finance-balance"]
        expanded = self.reason(self.graph())
        self.assertEqual(set(expanded.objects(retail, S.preferred_label)),
                         set(expanded.objects(finance, S.preferred_label)))
        self.assertNotIn((retail, OWL.sameAs, finance), expanded)
        self.assertNotEqual(set(expanded.objects(retail, S.describes_entities)),
                            set(expanded.objects(finance, S.describes_entities)))

    def test_inverses_symmetry_and_skos_projection(self):
        g = self.graph()
        g.add((EX["retail-balance"], S.related_to_terms, EX["retail-account-balance"]))
        g.remove((EX.finance, S.contains_terms, None))
        g.remove((EX["retail-account-balance"], S.has_narrower_terms, None))
        expanded = self.reason(g)
        self.assertIn((EX.finance, S.contains_terms, EX["finance-balance"]), expanded)
        self.assertIn((EX["retail-account-balance"], S.has_narrower_terms, EX["retail-balance"]), expanded)
        self.assertIn((EX["retail-account-balance"], S.related_to_terms, EX["retail-balance"]), expanded)
        # SKOS consumers can read the same graph without a custom mapping.
        self.assertIn((EX["retail-balance"], RDF.type, SKOS.Concept), expanded)
        self.assertIn((EX.retail, RDF.type, SKOS.ConceptScheme), expanded)
        self.assertIn((EX["retail-balance"], SKOS.prefLabel, Literal("Balance", lang="en")), expanded)
        self.assertIn((EX["retail-balance"], SKOS.altLabel, Literal("AVBL")), expanded)
        self.assertIn((EX["retail-balance"], SKOS.inScheme, EX.retail), expanded)
        self.assertIn((EX["retail-balance"], SKOS.broader, EX["retail-account-balance"]), expanded)
        self.assertTrue(self.report(g)[0])


if __name__ == "__main__":
    unittest.main()
