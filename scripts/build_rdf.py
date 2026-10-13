#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Assemble editable Turtle sources. No LinkML dependency or regeneration."""
import argparse
import json
from pathlib import Path
from rdflib import Graph, BNode
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parents[1]

def assemble(manifest_path):
    manifest_path = Path(manifest_path)
    root = manifest_path.parent.parent.resolve()
    manifest = json.loads(manifest_path.read_text())
    files = manifest.get("files", [])
    if manifest.get("format") != "turtle" or not files or len(files) != len(set(files)):
        raise ValueError("Invalid or duplicate Turtle manifest entries")
    graph = Graph()
    for filename in files:
        path = (root / filename).resolve()
        if not path.is_relative_to(root) or path.suffix != ".ttl":
            raise ValueError(f"Unsafe manifest entry: {filename}")
        graph.parse(path, format="turtle")
    return graph


def same_graph(left, right):
    # Named source nodes make the ordinary path fast; support standard Turtle
    # anonymous property shapes and RDF lists as well.
    if not any(isinstance(term, BNode) for graph in (left, right) for triple in graph for term in triple):
        return set(left) == set(right)
    return isomorphic(left, right)


def build(check=False):
    products = {"vocabulary": ROOT / "sao.ttl", "shapes": ROOT / "sao.shacl.ttl"}
    for name, output in products.items():
        manifest = ROOT / "rdf/manifests" / (name + ".json")
        listed = set(json.loads(manifest.read_text())["files"])
        directory = ROOT / "rdf" / name
        actual = {str(path.relative_to(ROOT / "rdf")) for path in directory.rglob("*.ttl")}
        if listed != actual:
            raise ValueError(f"{name}: manifest and source files disagree")
        graph = assemble(manifest)
        if check:
            if not same_graph(Graph().parse(output, format="turtle"), graph):
                raise ValueError(f"{output.name} is stale; run scripts/build_rdf.py")
        else:
            header = "# Generated distribution; edit rdf/ source files, then run scripts/build_rdf.py.\n# Copyright (c) 2026 CoreStory, Inc. — Apache-2.0\n\n"
            output.write_text(header + graph.serialize(format="turtle"))
            if not same_graph(Graph().parse(output, format="turtle"), graph):
                raise ValueError(f"{output.name} did not round-trip")
        print(f"{name}: {len(graph)} triples {'match' if check else 'assembled'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    build(args.check)
