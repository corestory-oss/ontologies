#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Generate an RDFS vocabulary projection of SAO, not instance data or validation shapes."""
from __future__ import annotations
import argparse
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "sao.yml")
    parser.add_argument("--output", type=Path, default=ROOT / "sao.ttl")
    parser.add_argument("--check", action="store_true", help="Check the committed export matches the current schema")
    args = parser.parse_args()
    graph = build_graph(args.schema)
    validate_projection(graph, args.schema)
    if args.check:
        existing = Graph().parse(args.output, format="turtle")
        if set(existing) != set(graph):
            parser.exit(1, "RDFS export is stale; regenerate with scripts/export_rdfs.py.\n")
    else:
        text = "# Generated from sao.yml and its imports; edit LinkML, then regenerate.\n# Copyright (c) 2026 CoreStory, Inc. — Apache-2.0\n\n" + graph.serialize(format="turtle")
        args.output.write_text(text)
        assert set(Graph().parse(args.output, format="turtle")) == set(graph)
    classes = len(set(graph.subjects(RDF.type, RDFS.Class)))
    properties = len(set(graph.subjects(RDF.type, RDF.Property)))
    print(f"RDFS export {'matches' if args.check else 'written'}: {classes} classes, {properties} properties, {len(graph)} triples.")

if __name__ == "__main__":
    main()
