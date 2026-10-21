#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Validate SpecSpec RDF and optional SAO links using editable Turtle sources."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import OWL
from pyshacl import validate

from scripts.build_rdf import ROOT, assemble

SPEC = Namespace("https://ontologies.corestory.ai/specspec/")
BRIDGE = Namespace(str(SPEC) + "sao/")
SAO = Namespace("https://ontologies.corestory.ai/sao/")
SH = Namespace("http://www.w3.org/ns/shacl#")


@lru_cache(maxsize=1)
def core_sources():
    vocabulary = assemble(ROOT / "ontologies/specspec/manifests/vocabulary.json")
    shapes = assemble(ROOT / "ontologies/specspec/manifests/shapes.json")
    axioms = assemble(ROOT / "ontologies/specspec/manifests/axioms.json")
    check_sources(vocabulary, shapes, axioms)
    return vocabulary, shapes, axioms


def check_sources(vocabulary, shapes, axioms):
    classes = set(vocabulary.subjects(RDF.type, RDFS.Class))
    targets = set(shapes.objects(None, SH.targetClass))
    if classes != targets:
        raise ValueError(f"Class/shape coverage mismatch: {classes ^ targets}")
    properties = set(vocabulary.subjects(RDF.type, RDF.Property))
    for path in shapes.objects(None, SH.path):
        if path not in properties:
            raise ValueError(f"Shape refers to undeclared property: {path}")
    objects = set(axioms.subjects(RDF.type, OWL.ObjectProperty))
    datatypes = set(axioms.subjects(RDF.type, OWL.DatatypeProperty))
    # Enum annotation predicates need no OWL property classification.
    shape_properties = set(shapes.objects(None, SH.path))
    if objects & datatypes or not objects | datatypes <= properties:
        raise ValueError("Invalid OWL property typing")
    if not shape_properties <= objects | datatypes:
        raise ValueError("OWL property typing is incomplete")
    # The original draft had no inverse/transitivity claims. New inference
    # policy needs a deliberate modeling change, not a representation migration.
    if list(axioms.triples((None, OWL.inverseOf, None))) or list(
        axioms.subjects(RDF.type, OWL.TransitiveProperty)
    ):
        raise ValueError("New inference axioms require an explicit modeling change")


def sources(sao_vocabulary=None):
    vocabulary, shapes, _ = core_sources()
    if sao_vocabulary is None:
        return vocabulary, shapes
    bridge_vocabulary = assemble(ROOT / "ontologies/specspec/manifests/sao-vocabulary.json")
    bridge_shapes = assemble(ROOT / "ontologies/specspec/manifests/sao-shapes.json")
    combined_vocabulary = Graph()
    combined_vocabulary += vocabulary
    combined_vocabulary += bridge_vocabulary
    if isinstance(sao_vocabulary, Graph):
        combined_vocabulary += sao_vocabulary
    else:
        combined_vocabulary.parse(sao_vocabulary, format="turtle")
    combined_shapes = Graph()
    combined_shapes += shapes
    combined_shapes += bridge_shapes
    # Check bridge coverage without requiring shapes for the external vocabulary.
    bridge_classes = set(bridge_vocabulary.subjects(RDF.type, RDFS.Class))
    bridge_targets = set(bridge_shapes.objects(None, SH.targetClass))
    if bridge_classes != bridge_targets:
        raise ValueError("Bridge class/shape coverage mismatch")
    declared = set(combined_vocabulary.subjects(RDF.type, RDF.Property))
    for path in combined_shapes.objects(None, SH.path):
        if path not in declared:
            raise ValueError(f"Bridge shape uses undeclared property: {path}")
    return combined_vocabulary, combined_shapes


def check_data(data, vocabulary=None, shapes=None, meta=False):
    if vocabulary is None or shapes is None:
        vocabulary, shapes = sources()
    known = set(vocabulary.subjects(RDF.type, RDFS.Class))
    if not any(
        t in known and str(t).startswith(str(SPEC))
        for t in data.objects(None, RDF.type)
    ):
        raise ValueError("No explicitly typed SpecSpec nodes; refusing vacuous validation")
    return validate(
        data,
        shacl_graph=shapes,
        ont_graph=vocabulary,
        inference="none",
        meta_shacl=meta,
        advanced=False,
    )


def check_evidence(data, manifest, directory):
    """Verify synthetic local source fixtures after SHACL conformance passes."""
    errors = []
    contents = {}
    directory = Path(directory).resolve()
    for identifier, relative in manifest.items():
        node = URIRef(identifier)
        if (node, RDF.type, SPEC.SourceSnapshot) not in data:
            errors.append(f"Unknown snapshot in fixture manifest: {identifier}")
            continue
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory):
            errors.append(f"Fixture escapes example directory: {relative}")
            continue
        if not path.is_file():
            errors.append(f"Missing fixture: {relative}")
            continue
        blob = path.read_bytes()
        revision = "sha256:" + hashlib.sha256(blob).hexdigest()
        if str(data.value(node, SPEC.revision)) != revision:
            errors.append(f"{identifier}: source digest mismatch")
        contents[node] = blob.decode().splitlines()
    for anchor in data.subjects(RDF.type, SPEC.EvidenceAnchor):
        snapshot = data.value(anchor, SPEC.snapshot)
        if snapshot not in contents:
            continue
        if Path(manifest[str(snapshot)]).name != str(data.value(anchor, SPEC.path)):
            errors.append(f"{anchor}: source path mismatch")
        end = data.value(anchor, SPEC.line_end)
        if end is not None and int(end) > len(contents[snapshot]):
            errors.append(f"{anchor}: anchor exceeds source length")
    return errors


def main():
    example = ROOT / "examples/specspec/modernization/graph.ttl"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, nargs="?", default=example)
    parser.add_argument(
        "--sao-vocabulary", type=Path,
        help="Optional SAO vocabulary, without loading its full instance shapes",
    )
    parser.add_argument(
        "--bridge-data", type=Path,
        help="Additional bridge link and external identity/type triples",
    )
    parser.add_argument("--sources", type=Path, help="Optional local fixture manifest (JSON)")
    args = parser.parse_args()
    if bool(args.sao_vocabulary) != bool(args.bridge_data):
        parser.error("--sao-vocabulary and --bridge-data must be supplied together")
    data = Graph().parse(args.data, format="turtle")
    if args.bridge_data:
        data.parse(args.bridge_data, format="turtle")
    vocabulary, shapes = sources(args.sao_vocabulary)
    conforms, _, report = check_data(data, vocabulary, shapes, meta=True)
    if not conforms:
        parser.exit(1, report)
    manifest = args.sources
    if manifest is None and args.data.resolve() == example.resolve():
        manifest = example.parent / "sources.json"
    if manifest:
        errors = check_evidence(data, json.loads(manifest.read_text()), manifest.parent)
        if errors:
            parser.exit(1, "\n".join(errors) + "\n")
    print(f"SHACL meta-validation and RDF conformance pass: {args.data}; {len(data)} data triples.")
    if args.sao_vocabulary:
        print("Optional bridge passes against the supplied SAO vocabulary (external types, not full SAO instance conformance).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
