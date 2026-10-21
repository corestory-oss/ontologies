#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Check OWL property typing without adding new inference policy."""
from rdflib import RDF
from rdflib.namespace import OWL

from scripts.build_rdf import ROOT, assemble
from scripts.validators.specspec import core_sources


def check_axioms():
    core_sources()
    vocabulary = assemble(ROOT / "ontologies/specspec/manifests/sao-vocabulary.json")
    axioms = assemble(ROOT / "ontologies/specspec/manifests/sao-axioms.json")
    declared = set(vocabulary.subjects(RDF.type, RDF.Property))
    objects = set(axioms.subjects(RDF.type, OWL.ObjectProperty))
    datatypes = set(axioms.subjects(RDF.type, OWL.DatatypeProperty))
    if declared != objects | datatypes or objects & datatypes:
        raise ValueError("Bridge property typing coverage mismatch")
    if list(axioms.triples((None, OWL.inverseOf, None))) or list(
        axioms.subjects(RDF.type, OWL.TransitiveProperty)
    ):
        raise ValueError("Bridge introduces unreviewed inference axioms")
    return vocabulary, axioms


if __name__ == "__main__":
    check_axioms()
