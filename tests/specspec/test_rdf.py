# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Contracts for the RDF migration, including failures the old validator caught."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD
from rdflib.namespace import OWL
from rdflib.collection import Collection
from owlrl import DeductiveClosure, RDFS_Semantics

from scripts.build_rdf import ROOT, assemble, same_graph
from scripts.validators.specspec import SPEC, BRIDGE, SAO, SH, check_data, check_evidence, core_sources, sources

DEMO = Namespace("urn:specspec:demo:")
EXPORT = Namespace(str(SPEC) + "export/")


class RDFContractTests(unittest.TestCase):
    def setUp(self):
        self.directory = ROOT / "examples/specspec/modernization"
        self.graph = Graph().parse(self.directory / "graph.ttl")

    def replace(self, node, predicate, value):
        self.graph.set((node, predicate, value))

    def assert_valid(self, expected=True, message=None, vocabulary=None, shapes=None):
        conforms, _, report = check_data(self.graph, vocabulary, shapes)
        self.assertEqual(conforms, expected, report)
        if message:
            self.assertIn(message, report)

    def test_connected_example_and_fixture_integrity(self):
        self.assert_valid()
        manifest = json.loads((self.directory / "sources.json").read_text())
        self.assertEqual(check_evidence(self.graph, manifest, self.directory), [])

    def test_required_fields_and_normative_restrictions(self):
        mutations = [
            (DEMO["legacy-behavior"], SPEC.origin, None),
            (DEMO["no-overdraft"], SPEC.statement_mode, Literal("descriptive")),
            (DEMO["overdraft-criterion"], SPEC.statement_mode, Literal("descriptive")),
            (DEMO.analyst, SPEC.title, None),
            (DEMO.analyst, SPEC.id, None),
            (DEMO.analyst, SPEC.agent_kind, Literal("robot")),
        ]
        original = set(self.graph)
        for node, predicate, value in mutations:
            with self.subTest(predicate=predicate, value=value):
                self.graph = Graph()
                for triple in original:
                    self.graph.add(triple)
                self.graph.remove((node, predicate, None))
                if value is not None:
                    self.graph.add((node, predicate, value))
                self.assert_valid(False)

    def test_unresolved_and_wrong_class_references(self):
        for target in (URIRef("urn:missing:anchor"), DEMO.analyst):
            with self.subTest(target=target):
                self.replace(DEMO["legacy-behavior"], SPEC.supporting_anchors, target)
                self.assert_valid(False, "ClassConstraintComponent")

    def test_observed_support(self):
        self.graph.remove((DEMO["legacy-behavior"], SPEC.supporting_anchors, None))
        self.assert_valid(False, "observed claim needs")

    def test_inferred_support(self):
        self.graph.remove((DEMO["scope-gap"], SPEC.supporting_anchors, None))
        self.assert_valid()
        self.graph.remove((DEMO["scope-gap"], SPEC.derived_from_claims, None))
        self.assert_valid(False, "inferred claim needs")

    def test_confidence_bounds_and_basis(self):
        self.replace(DEMO["legacy-behavior"], SPEC.confidence, Literal(1.5, datatype=XSD.float))
        self.assert_valid(False, "MaxInclusiveConstraintComponent")
        self.replace(DEMO["legacy-behavior"], SPEC.confidence, Literal(0.8, datatype=XSD.float))
        self.assert_valid(False, "confidence_basis")
        self.replace(DEMO["legacy-behavior"], SPEC.confidence_basis, Literal("Analyst estimate"))
        self.assert_valid()

    def test_review_requires_reviewer(self):
        for status in ("accepted", "rejected"):
            self.replace(DEMO["legacy-behavior"], SPEC.review_status, Literal(status))
            self.assert_valid(False, "need a reviewer")
        self.replace(DEMO["legacy-behavior"], SPEC.reviewed_by, DEMO.analyst)
        self.assert_valid()

    def test_cycle_across_multiple_claims(self):
        self.graph.add((DEMO["legacy-behavior"], SPEC.derived_from_claims, DEMO["scope-gap"]))
        self.assert_valid(False, "must not be cyclic")

    def test_coordinates_pair_order_and_minimum(self):
        anchor = DEMO["legacy-guard"]
        self.graph.remove((anchor, SPEC.line_end, None))
        self.assert_valid(False, "coordinates must occur together")
        self.replace(anchor, SPEC.line_end, Literal(1))
        self.assert_valid(False, "coordinates must occur together")
        self.replace(anchor, SPEC.line_start, Literal(0))
        self.assert_valid(False, "MinInclusiveConstraintComponent")

    def test_chosen_option_membership(self):
        self.graph.remove((DEMO["modernization-decision"], SPEC.options, DEMO["java-option"]))
        self.assert_valid(False, "one of the considered options")

    def test_step_positions_are_ordered_by_value(self):
        self.replace(DEMO["request-step"], SPEC.position, Literal(2))
        self.assert_valid(False, "unique and consecutive")
        self.replace(DEMO["request-step"], SPEC.position, Literal(1))
        second = DEMO["second-step"]
        for predicate, value in list(self.graph.predicate_objects(DEMO["request-step"])):
            self.graph.add((second, predicate, value))
        self.replace(second, SPEC.id, Literal(str(second), datatype=XSD.anyURI))
        self.graph.add((DEMO["excessive-withdrawal"], SPEC.steps, second))
        self.assert_valid(False, "unique and consecutive")
        self.replace(second, SPEC.position, Literal(2))
        self.assert_valid()

    def test_baseline_membership_for_removals(self):
        self.graph.add((DEMO.change, SPEC.removes_requirements, DEMO["no-overdraft"]))
        self.assert_valid(False, "Removed requirements must belong")
        self.graph.add((DEMO.baseline, SPEC.requirements, DEMO["no-overdraft"]))
        self.assert_valid()

    def test_baseline_membership_for_replacements(self):
        replacement = DEMO.replacement
        self.graph.add((replacement, RDF.type, SPEC.RequirementReplacement))
        self.graph.add((replacement, SPEC.id, Literal(str(replacement), datatype=XSD.anyURI)))
        self.graph.add((replacement, SPEC.title, Literal("Replacement")))
        self.graph.add((replacement, SPEC.previous_requirement, DEMO["no-overdraft"]))
        self.graph.add((replacement, SPEC.replacement_requirement, DEMO["no-overdraft"]))
        self.graph.add((DEMO.change, SPEC.replacements, replacement))
        self.assert_valid(False, "Replaced requirements must belong")
        self.graph.add((DEMO.baseline, SPEC.requirements, DEMO["no-overdraft"]))
        self.assert_valid()

    def test_distinct_nodes_cannot_reuse_identity(self):
        duplicate = DEMO["duplicate-analyst"]
        for predicate, value in list(self.graph.predicate_objects(DEMO.analyst)):
            self.graph.add((duplicate, predicate, value))
        self.assert_valid(False, "id must match the node IRI")

    def test_unknown_leaf_property_and_scalar_cardinality(self):
        self.graph.add((DEMO.analyst, SPEC.typo, Literal("Unexpected")))
        self.assert_valid(False, "ClosedConstraintComponent")
        self.graph.remove((DEMO.analyst, SPEC.typo, None))
        self.graph.add((DEMO.analyst, SPEC.title, Literal("Second title")))
        self.assert_valid(False, "MaxCountConstraintComponent")

    def test_vacuous_validation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "vacuous"):
            check_data(Graph())

    def test_evidence_digest_bounds_and_path_escape(self):
        manifest = json.loads((self.directory / "sources.json").read_text())
        self.replace(DEMO["legacy-snapshot"], SPEC.revision, Literal("sha256:incorrect"))
        self.assertTrue(any("digest" in e for e in check_evidence(self.graph, manifest, self.directory)))
        self.replace(DEMO["legacy-guard"], SPEC.line_end, Literal(10000))
        self.assertTrue(any("source length" in e for e in check_evidence(self.graph, manifest, self.directory)))
        manifest[str(DEMO["legacy-snapshot"])] = "../../README.md"
        self.assertTrue(any("escapes" in e for e in check_evidence(self.graph, manifest, self.directory)))

    def test_optional_bridge_and_wrong_external_type(self):
        vocabulary, shapes = sources(ROOT / "tests/specspec/fixtures/sao.ttl")
        self.graph.parse(self.directory / "sao-links.ttl")
        self.assert_valid(vocabulary=vocabulary, shapes=shapes)
        target = next(self.graph.objects(None, BRIDGE.callable))
        self.replace(target, RDF.type, SAO.TestCase)
        self.assert_valid(False, "ClassConstraintComponent", vocabulary, shapes)

    def test_bridge_requires_descriptive_basis(self):
        vocabulary, shapes = sources(ROOT / "tests/specspec/fixtures/sao.ttl")
        self.graph.parse(self.directory / "sao-links.ttl")
        link = self.graph.value(None, RDF.type, BRIDGE.RequirementImplementationLink)
        self.replace(link, BRIDGE.basis_claim, DEMO["no-overdraft"])
        self.assert_valid(False, "descriptive basis claim", vocabulary, shapes)


class SourceAssemblyTests(unittest.TestCase):
    def test_migration_inventory_and_enum_values(self):
        baseline = json.loads((ROOT / "docs/specspec/rdf-migration-baseline.json").read_text())
        vocabulary, shapes, axioms = core_sources()
        classes = set(vocabulary.subjects(RDF.type, RDFS.Class))
        self.assertEqual(classes, {URIRef(v) for v in baseline["core_classes"].values()})
        for name, enum in baseline["enums"].items():
            entries = vocabulary.objects(URIRef(enum["iri"]), EXPORT.permissibleValue)
            values = {str(vocabulary.value(entry, RDF.value)) for entry in entries}
            self.assertEqual(values, set(enum["values"]), name)
            head = URIRef(str(SPEC) + "shapes/" + name + "Values")
            self.assertEqual({str(v) for v in Collection(shapes, head)}, values)
        bridge = assemble(ROOT / "ontologies/specspec/manifests/sao-vocabulary.json")
        # The migration baseline stays a historical record; later bridge classes are listed explicitly.
        post_migration = {BRIDGE.TermMappingLink}
        self.assertEqual(set(bridge.subjects(RDF.type, RDFS.Class)),
                         {URIRef(v) for v in baseline["bridge_classes"].values()} | post_migration)
        data = Graph().parse(ROOT / "examples/specspec/modernization/graph.ttl")
        self.assertEqual(len(set(data.subjects(RDF.type, None))) - 1, baseline["example_records"])
        self.assertEqual(len(data), baseline["example_triples"])
        for graph in (vocabulary, shapes, axioms):
            self.assertFalse(any(isinstance(term, URIRef) and str(term).startswith(str(SAO))
                                 for triple in graph for term in triple))
            self.assertFalse(list(graph.objects(None, OWL.imports)))

    def test_all_original_class_property_contracts(self):
        baseline = json.loads((ROOT / "docs/specspec/rdf-migration-baseline.json").read_text())
        vocabulary, shapes, _ = core_sources()
        for name, contracts in baseline["core_property_contracts"].items():
            node = URIRef(baseline["core_classes"][name])
            self.assertIn((node, RDFS.comment, Literal(baseline["class_descriptions"][name])), vocabulary)
            if name in baseline["class_parents"]:
                parent = URIRef(baseline["core_classes"][baseline["class_parents"][name]])
                self.assertIn((node, RDFS.subClassOf, parent), vocabulary)
            shape = URIRef(str(SPEC) + "shapes/" + name + "Shape")
            properties = {shapes.value(p, SH.path): p for p in shapes.objects(shape, SH.property)}
            self.assertEqual(set(properties), {URIRef(c["path"]) for c in contracts}, name)
            for contract in contracts:
                prop = properties[URIRef(contract["path"])]
                with self.subTest(cls=name, path=contract["path"]):
                    self.assertEqual(shapes.value(prop, SH.minCount), Literal(1) if contract["required"] else None)
                    self.assertEqual(shapes.value(prop, SH.maxCount), None if contract["multivalued"] else Literal(1))
                    for key, predicate in (("class", SH["class"]), ("datatype", SH.datatype)):
                        expected = URIRef(contract[key]) if key in contract else None
                        self.assertEqual(shapes.value(prop, predicate), expected)
                    for key, predicate in (("minimum_value", SH.minInclusive), ("maximum_value", SH.maxInclusive),
                                           ("equals_string", SH.hasValue), ("pattern", SH.pattern)):
                        expected = Literal(contract[key]) if key in contract else None
                        self.assertEqual(shapes.value(prop, predicate), expected)
                    if "enum" in contract:
                        head = shapes.value(prop, SH["in"])
                        self.assertEqual({str(v) for v in Collection(shapes, head)},
                                         set(baseline["enums"][contract["enum"]]["values"]))

    def test_products_match_sources(self):
        for stem, name in (("vocabulary", "specspec.ttl"), ("shapes", "specspec.shacl.ttl"),
                           ("axioms", "specspec.owl.ttl"), ("sao-vocabulary", "specspec-sao.ttl"),
                           ("sao-shapes", "specspec-sao.shacl.ttl"), ("sao-axioms", "specspec-sao.owl.ttl")):
            with self.subTest(product=name):
                source = assemble(ROOT / "ontologies/specspec/manifests" / (stem + ".json"))
                self.assertTrue(same_graph(source, Graph().parse(ROOT / "dist" / name)))

    def test_manifest_reads_current_sources_and_rejects_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "manifests").mkdir()
            manifest = directory / "manifests/example.json"
            manifest.write_text(json.dumps({"format": "turtle", "files": ["source.ttl"]}))
            source = directory / "source.ttl"
            source.write_text("<urn:a> <urn:b> <urn:c> .")
            first = assemble(manifest)
            source.write_text("<urn:a> <urn:b> <urn:d> .")
            self.assertFalse(same_graph(first, assemble(manifest)))
            for files in (["../outside.ttl"], ["source.ttl", "source.ttl"]):
                manifest.write_text(json.dumps({"format": "turtle", "files": files}))
                with self.assertRaises(ValueError):
                    assemble(manifest)

    def test_rdfs_inheritance_without_intersection_domains(self):
        vocabulary, _, axioms = core_sources()
        self.assertEqual(set(vocabulary.objects(SPEC.authored_by, RDFS.domain)), set())
        data = Graph()
        data += vocabulary
        data += axioms
        data.add((DEMO.requirement, RDF.type, SPEC.Requirement))
        DeductiveClosure(RDFS_Semantics).expand(data)
        self.assertIn((DEMO.requirement, RDF.type, SPEC.Claim), data)
        self.assertIn((DEMO.requirement, RDF.type, SPEC.SpecElement), data)
        self.assertNotIn((DEMO.requirement, RDF.type, SPEC.Decision), data)


if __name__ == "__main__":
    unittest.main()
