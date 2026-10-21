#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Validate editable shapes and a data graph without consulting LinkML."""
import argparse
from pathlib import Path
from rdflib import Graph, RDF, RDFS, Namespace
from pyshacl import validate
from scripts.build_rdf import assemble, ROOT
SH = Namespace("http://www.w3.org/ns/shacl#")


def sources():
    vocabulary = assemble(ROOT / "ontologies/sao/manifests/vocabulary.json")
    shapes = assemble(ROOT / "ontologies/sao/manifests/shapes.json")
    classes = set(vocabulary.subjects(RDF.type, RDFS.Class))
    targets = set(shapes.objects(None, SH.targetClass))
    if targets != classes:
        raise ValueError(f"Shape coverage mismatch: missing={classes-targets}, unknown={targets-classes}")
    properties = set(vocabulary.subjects(RDF.type, RDF.Property))
    for path in shapes.objects(None, SH.path):
        if path not in properties:
            raise ValueError(f"Shape refers to undeclared property: {path}")
    return vocabulary, shapes


def check_data(data, vocabulary, shapes, meta=False):
    return validate(data, shacl_graph=shapes, ont_graph=vocabulary,
                    inference="none", meta_shacl=meta, advanced=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, nargs="?", default=ROOT / "examples/sao/rdf/system.ttl")
    args = parser.parse_args()
    vocabulary, shapes = sources()
    data = Graph().parse(args.data, format="turtle")
    classes = set(vocabulary.subjects(RDF.type, RDFS.Class))
    if not any(class_name in classes for class_name in data.objects(None, RDF.type)):
        parser.error("Data has no explicitly typed SAO nodes; refusing vacuous validation")
    conforms, _, report = check_data(data, vocabulary, shapes, meta=True)
    if not conforms:
        parser.exit(1, report)
    print(f"Shapes pass SHACL meta-validation; {args.data} conforms to the initial RDF profile.")

if __name__ == "__main__":
    main()
