# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Cross-ontology contracts and repository relocation regression checks."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import DCTERMS

from scripts.build_rdf import ROOT, assemble, same_graph
from scripts.catalog import catalog
from scripts.validate_rdf import example, fixture_errors, sources, validate_graph
from scripts.validators import sao, specspec


class EcosystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocabulary, cls.shapes = sources("ecosystem")

    def check(self, data):
        return validate_graph(data, "ecosystem", vocabulary=self.vocabulary, shapes=self.shapes)

    def test_catalog_versions_match_ontology_metadata(self):
        for name, entry in catalog().items():
            vocabulary = assemble(ROOT / entry["source"] / "manifests/vocabulary.json")
            self.assertEqual(set(vocabulary.objects(URIRef(entry["namespace"]), DCTERMS.hasVersion)),
                             {Literal(entry["version"])}, name)

    def test_all_products_match_authored_graphs(self):
        for name, entry in catalog().items():
            for manifest, filename in entry["products"].items():
                with self.subTest(ontology=name, product=manifest):
                    source = assemble(ROOT / entry["source"] / "manifests" / (manifest + ".json"))
                    self.assertTrue(same_graph(source, Graph().parse(ROOT / filename)))

    def test_combined_example_and_evidence(self):
        data = example("ecosystem")
        conforms, _, report = self.check(data)
        self.assertTrue(conforms, report)
        self.assertEqual(fixture_errors(data), [])

    def test_combined_validation_enforces_sao_fields(self):
        data = example("ecosystem")
        data.remove((URIRef("urn:specspec:demo:software:withdraw"), specspec.SAO.name, None))
        conforms, _, report = self.check(data)
        self.assertFalse(conforms)
        self.assertIn("MinCountConstraintComponent", report)

    def test_combined_validation_enforces_specspec_fields(self):
        data = example("ecosystem")
        data.remove((URIRef("urn:specspec:demo:no-overdraft"), specspec.SPEC.origin, None))
        conforms, _, report = self.check(data)
        self.assertFalse(conforms)
        self.assertIn("MinCountConstraintComponent", report)

    def test_bridge_range_enforced_in_combined_profile(self):
        data = example("ecosystem")
        data.set((URIRef("urn:specspec:demo:software:withdraw"), RDF.type, specspec.SAO.System))
        conforms, _, report = self.check(data)
        self.assertFalse(conforms)
        self.assertIn("ClassConstraintComponent", report)

    def test_independent_sources_do_not_require_the_bridge(self):
        for name, namespace, other in (("sao", specspec.SAO, specspec.SPEC),
                                       ("specspec", specspec.SPEC, specspec.SAO)):
            vocabulary, _ = sources(name)
            self.assertFalse(any(isinstance(term, URIRef) and str(term).startswith(str(other))
                                 for triple in vocabulary for term in triple), name)

    def test_build_works_after_checkout_directory_rename(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "renamed-ontology-checkout"
            checkout.mkdir()
            for name in ("scripts", "ontologies", "dist"):
                shutil.copytree(ROOT / name, checkout / name,
                                ignore=shutil.ignore_patterns("__pycache__"))
            result = subprocess.run([sys.executable, str(checkout / "scripts/build_rdf.py"), "--check"],
                                    cwd=directory, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
