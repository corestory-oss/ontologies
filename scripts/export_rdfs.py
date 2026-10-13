#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Generate an RDFS vocabulary projection of SAO, not instance data or validation shapes."""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from urllib.parse import quote
from pathlib import Path
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, SKOS
from linkml_runtime.utils.schemaview import SchemaView

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = Namespace("http://schema.org/")
EXPORT = Namespace("https://ontologies.corestory.ai/sao/export/")


def build_graph(schema_path: Path) -> Graph:
    view = SchemaView(str(schema_path.resolve()))
    graph = Graph()
    for prefix, expansion in view.schema.prefixes.items():
        graph.bind(prefix, str(expansion.prefix_reference))
    for prefix, ns in (("rdf", RDF), ("rdfs", RDFS), ("dcterms", DCTERMS),
                       ("skos", SKOS), ("schema", SCHEMA), ("export", EXPORT)):
        graph.bind(prefix, ns, replace=True)
    ontology = URIRef(view.schema.id)
    graph.add((ontology, RDF.type, SCHEMA.DefinedTermSet))
    graph.add((ontology, DCTERMS.title, Literal(view.schema.title)))
    graph.add((ontology, DCTERMS.description, Literal(view.schema.description)))
    graph.add((ontology, DCTERMS.hasVersion, Literal(view.schema.version)))
    graph.add((ontology, DCTERMS.license, URIRef("https://www.apache.org/licenses/LICENSE-2.0")))

    def uri(element):
        return URIRef(view.get_uri(element, expand=True))

    def describe(element, node):
        graph.add((node, RDFS.label, Literal(element.name)))
        graph.add((node, RDFS.isDefinedBy, ontology))
        if element.description:
            graph.add((node, RDFS.comment, Literal(element.description)))
        for comment in element.comments:
            graph.add((node, SKOS.note, Literal(comment)))

    classes, enums, types = view.all_classes(), view.all_enums(), view.all_types()
    for name, cls in classes.items():
        node = uri(cls)
        graph.add((node, RDF.type, RDFS.Class))
        describe(cls, node)
        for parent in [cls.is_a, *cls.mixins]:
            if parent:
                graph.add((node, RDFS.subClassOf, uri(classes[parent])))

    # Enums remain literal-valued datatypes. Their declared values are descriptive
    # annotations, not a closed extension enforced by RDFS.
    graph.add((EXPORT.permissibleValue, RDF.type, RDF.Property))
    graph.add((EXPORT.permissibleValue, RDFS.label, Literal("declared permissible value")))
    graph.add((EXPORT.permissibleValue, RDFS.comment, Literal("Describes a LinkML enum value; does not impose a closed RDFS enumeration.")))
    for name, enum in enums.items():
        node = uri(enum)
        graph.add((node, RDF.type, RDFS.Datatype))
        graph.add((node, RDFS.subClassOf, RDFS.Literal))
        describe(enum, node)
        for value, definition in enum.permissible_values.items():
            entry = URIRef(str(EXPORT) + "values/" + quote(str(name), safe="") + "/" + quote(str(value), safe=""))
            graph.add((node, EXPORT.permissibleValue, entry))
            graph.add((entry, RDF.value, Literal(str(value))))
            if definition.description:
                graph.add((entry, RDFS.comment, Literal(definition.description)))
            if definition.meaning:
                graph.add((entry, RDFS.seeAlso, URIRef(view.expand_curie(definition.meaning))))

    for name, datatype in types.items():
        node = uri(datatype)
        graph.add((node, RDF.type, RDFS.Datatype))
        if datatype.typeof:
            graph.add((node, RDFS.subClassOf, uri(types[datatype.typeof])))
        # Built-in type documentation is supplied by LinkML, not authored in SAO.
        if str(node).startswith(str(view.schema.id)):
            describe(datatype, node)
            if datatype.pattern:
                graph.add((node, SKOS.note, Literal("LinkML pattern (not enforced by RDFS): " + datatype.pattern)))

    def range_uri(name):
        if name in classes:
            return uri(classes[name])
        if name in enums:
            return uri(enums[name])
        if name in types:
            return uri(types[name])
        raise ValueError(f"Unresolved LinkML range: {name}")

    properties = defaultdict(lambda: {"domains": set(), "ranges": set(), "slots": []})
    for name, slot in view.all_slots().items():
        item = properties[uri(slot)]
        item["slots"].append((None, slot))
        if slot.domain:
            item["domains"].add(uri(classes[slot.domain]))
        if slot.range:
            item["ranges"].add(range_uri(slot.range))
    for name, cls in classes.items():
        # Include local declarations and overrides, not every inherited use.
        for slot_name in set(cls.slots) | set(cls.attributes) | set(cls.slot_usage):
            slot = view.induced_slot(slot_name, name)
            item = properties[uri(slot)]
            item["domains"].add(uri(cls))
            if slot.range:
                item["ranges"].add(range_uri(slot.range))
            item["slots"].append((name, slot))
    for node, item in properties.items():
        graph.add((node, RDF.type, RDF.Property))
        graph.add((node, RDFS.isDefinedBy, ontology))
        for class_name, slot in item["slots"]:
            graph.add((node, RDFS.label, Literal(slot.name)))
            if slot.description:
                context = f"[{class_name}] " if class_name else ""
                graph.add((node, RDFS.comment, Literal(context + slot.description)))
            for comment in slot.comments:
                graph.add((node, SKOS.note, Literal(comment)))
            if slot.is_a:
                graph.add((node, RDFS.subPropertyOf, uri(view.get_slot(slot.is_a))))
        for values, axiom, annotation in ((item["domains"], RDFS.domain, SCHEMA.domainIncludes),
                                         (item["ranges"], RDFS.range, SCHEMA.rangeIncludes)):
            if len(values) == 1:
                graph.add((node, axiom, next(iter(values))))
            elif values:
                # Multiple rdfs:domain/range axioms mean intersection, not union.
                for value in values:
                    graph.add((node, annotation, value))
    return graph


def validate_projection(graph: Graph, schema_path: Path):
    view = SchemaView(str(schema_path.resolve()))
    for cls in view.all_classes().values():
        node = URIRef(view.get_uri(cls, expand=True))
        assert (node, RDF.type, RDFS.Class) in graph, f"Missing class: {cls.name}"
        for parent in [cls.is_a, *cls.mixins]:
            if parent:
                parent_uri = URIRef(view.get_uri(view.get_class(parent), expand=True))
                assert (node, RDFS.subClassOf, parent_uri) in graph
    for node in graph.subjects(RDF.type, RDF.Property):
        assert len(set(graph.objects(node, RDFS.domain))) <= 1
        assert len(set(graph.objects(node, RDFS.range))) <= 1
    owl_prefix = "http://www.w3.org/2002/07/owl#"
    assert not any(isinstance(term, URIRef) and str(term).startswith(owl_prefix)
                   for triple in graph for term in triple), "Unexpected OWL terms"


def partition_graph(graph: Graph, schema_path: Path) -> dict[str, Graph]:
    """Partition the completed projection, so shared declarations keep global semantics."""
    view = SchemaView(str(schema_path.resolve()))
    owners = defaultdict(set)
    module_directory = schema_path.resolve().parent / "schema"
    topics = {"ontology", "common"}
    for schema in view.all_schema():
        source = Path(schema.source_file) if schema.source_file else None
        if source is not None:
            if not source.is_absolute():
                source = schema_path.resolve().parent / source
            source = source.resolve()
        if source and source.parent == module_directory:
            topic = source.stem
            topics.add(topic)
        elif source == schema_path.resolve():
            topic = "ontology"
        else:
            topic = "common"  # Built-in LinkML datatypes.
        for definitions in (schema.classes, schema.enums, schema.types, schema.slots):
            for element in definitions.values():
                node = URIRef(view.get_uri(element, expand=True))
                owners[node].add(topic)
        for cls in schema.classes.values():
            for name in set(cls.slots) | set(cls.attributes) | set(cls.slot_usage):
                slot = view.induced_slot(name, cls.name)
                owners[URIRef(view.get_uri(slot, expand=True))].add(topic)
    for enum in view.all_enums().values():
        node = URIRef(view.get_uri(enum, expand=True))
        for entry in graph.objects(node, EXPORT.permissibleValue):
            owners[entry].update(owners[node])
    owners[URIRef(view.schema.id)] = {"ontology"}
    owners[EXPORT.permissibleValue] = {"common"}
    pieces = {name + ".ttl": Graph() for name in sorted(topics)}
    for piece in pieces.values():
        for prefix, expansion in graph.namespaces():
            piece.bind(prefix, expansion, replace=True)
    for triple in graph:
        candidates = owners[triple[0]]
        # A shared property is defined once in common, after considering every
        # module's declarations. Per-module inference would narrow it incorrectly.
        topic = next(iter(candidates)) if len(candidates) == 1 else "common"
        pieces[topic + ".ttl"].add(triple)
    return pieces


def load_manifest(manifest_path: Path) -> Graph:
    """Load each Turtle document separately into one RDF graph."""
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("format") != "turtle" or not manifest.get("files"):
        raise ValueError("Invalid Turtle manifest")
    files = manifest["files"]
    if len(files) != len(set(files)):
        raise ValueError("Duplicate Turtle manifest entry")
    graph = Graph()
    for filename in files:
        path = (manifest_path.parent / filename).resolve()
        if not path.is_relative_to(manifest_path.parent.resolve()) or path.suffix != ".ttl":
            raise ValueError(f"Invalid Turtle manifest path: {filename}")
        graph.parse(path, format="turtle")
    return graph


def write_or_check(graph: Graph, pieces: dict[str, Graph], output: Path,
                   modules_dir: Path, check: bool):
    manifest = {"format": "turtle", "files": sorted(pieces)}
    manifest_path = modules_dir / "manifest.json"
    expected = set(graph)
    if check:
        if set(Graph().parse(output, format="turtle")) != expected:
            raise ValueError("Complete RDFS export is stale")
        if json.loads(manifest_path.read_text()) != manifest:
            raise ValueError("Turtle manifest is stale")
        if {p.name for p in modules_dir.glob("*.ttl")} != set(pieces):
            raise ValueError("Unexpected or missing Turtle module")
        for filename, piece in pieces.items():
            if set(Graph().parse(modules_dir / filename, format="turtle")) != set(piece):
                raise ValueError(f"Turtle module is stale: {filename}")
    else:
        modules_dir.mkdir(parents=True, exist_ok=True)
        header = "# Generated from sao.yml and its imports; edit LinkML, then regenerate.\n# Copyright (c) 2026 CoreStory, Inc. — Apache-2.0\n\n"
        output.write_text(header + graph.serialize(format="turtle"))
        for filename, piece in pieces.items():
            (modules_dir / filename).write_text(header + piece.serialize(format="turtle"))
        # This directory is generator-owned; remove exports for deleted modules.
        for path in modules_dir.glob("*.ttl"):
            if path.name not in pieces:
                path.unlink()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    if set(load_manifest(manifest_path)) != expected:
        raise ValueError("Assembled Turtle modules differ from the complete vocabulary")
    if set(Graph().parse(output, format="turtle")) != expected:
        raise ValueError("Complete Turtle round trip differs from the vocabulary")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "sao.yml")
    parser.add_argument("--output", type=Path, default=ROOT / "sao.ttl")
    parser.add_argument("--modules-dir", type=Path, default=ROOT / "rdf")
    parser.add_argument("--check", action="store_true", help="Check the committed complete and modular exports")
    args = parser.parse_args()
    graph = build_graph(args.schema)
    validate_projection(graph, args.schema)
    pieces = partition_graph(graph, args.schema)
    try:
        write_or_check(graph, pieces, args.output, args.modules_dir, args.check)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}; regenerate with scripts/export_rdfs.py.\n")
    classes = len(set(graph.subjects(RDF.type, RDFS.Class)))
    properties = len(set(graph.subjects(RDF.type, RDF.Property)))
    print(f"RDFS export {'matches' if args.check else 'written'}: {classes} classes, {properties} properties, {len(graph)} triples; {len(pieces)} Turtle pieces assemble identically.")

if __name__ == "__main__":
    main()
