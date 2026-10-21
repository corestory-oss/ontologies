#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Validate SAO, SpecSpec, and their composition from editable Turtle sources."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdflib import Graph, RDF, RDFS
from scripts.build_rdf import ROOT, assemble
from scripts.validators import sao, specspec


PROFILES = ("sao", "specspec", "ecosystem")


def sources(ontology):
    if ontology == "sao":
        return sao.sources()
    if ontology == "specspec":
        return specspec.sources()
    if ontology == "ecosystem":
        sao_vocabulary, sao_shapes = sao.sources()
        vocabulary, shapes = specspec.sources(sao_vocabulary)
        shapes += sao_shapes
        return vocabulary, shapes
    raise ValueError(f"Unknown validation profile: {ontology}")


def example(ontology):
    if ontology == "ecosystem":
        return assemble(ROOT / "examples/ecosystem/manifest.json")
    relative = "sao/rdf/system.ttl" if ontology == "sao" else "specspec/modernization/graph.ttl"
    return Graph().parse(ROOT / "examples" / relative, format="turtle")


def validate_graph(data, ontology, meta=False, vocabulary=None, shapes=None):
    if vocabulary is None or shapes is None:
        vocabulary, shapes = sources(ontology)
    known = set(vocabulary.subjects(RDF.type, RDFS.Class))
    if ontology == "specspec":
        known = {t for t in known if str(t).startswith(str(specspec.SPEC))}
    if not any(t in known for t in data.objects(None, RDF.type)):
        raise ValueError("No explicitly typed ontology nodes; refusing vacuous validation")
    return sao.check_data(data, vocabulary, shapes, meta=meta)


def fixture_errors(data):
    directory = ROOT / "examples/specspec/modernization"
    manifest = json.loads((directory / "sources.json").read_text())
    return specspec.check_evidence(data, manifest, directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, nargs="?")
    parser.add_argument("--ontology", choices=("all", *PROFILES), default="all")
    parser.add_argument("--sources", type=Path, help="Optional local evidence fixture manifest")
    parser.add_argument("--sao-vocabulary", type=Path, help="For SpecSpec endpoint-type checks only")
    parser.add_argument("--bridge-data", type=Path)
    args = parser.parse_args()
    if args.data and args.ontology == "all":
        parser.error("Choose --ontology sao, specspec, or ecosystem for a supplied data graph")
    if bool(args.sao_vocabulary) != bool(args.bridge_data):
        parser.error("--sao-vocabulary and --bridge-data must be supplied together")
    if args.bridge_data and args.ontology != "specspec":
        parser.error("Endpoint-type bridge checks require --ontology specspec; use ecosystem for full composition")
    if args.sources and args.ontology == "all":
        parser.error("Choose one ontology profile when supplying --sources")
    for profile in PROFILES if args.ontology == "all" else (args.ontology,):
        data = Graph().parse(args.data, format="turtle") if args.data else example(profile)
        vocabulary, shapes = sources(profile)
        if args.bridge_data:
            data.parse(args.bridge_data, format="turtle")
            vocabulary, shapes = specspec.sources(args.sao_vocabulary)
        conforms, _, report = validate_graph(data, profile, meta=True, vocabulary=vocabulary, shapes=shapes)
        if not conforms:
            parser.exit(1, report)
        if args.sources:
            errors = specspec.check_evidence(data, json.loads(args.sources.read_text()), args.sources.parent)
        elif args.data is None and profile in ("specspec", "ecosystem"):
            errors = fixture_errors(data)
        else:
            errors = []
        if errors:
            parser.exit(1, "\n".join(errors) + "\n")
        print(f"{profile}: SHACL meta-validation and conformance pass ({len(data)} data triples).")
        if args.bridge_data:
            print("Bridge endpoint types checked; full SAO instance shapes were not applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
