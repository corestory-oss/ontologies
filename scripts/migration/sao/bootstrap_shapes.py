#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""One-time LinkML-to-SHACL bootstrap. Output directory must be empty."""
import argparse
from collections import Counter
import json
from pathlib import Path
from urllib.parse import quote
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD
from linkml_runtime.utils.schemaview import SchemaView

ROOT = Path(__file__).resolve().parents[3]
SH = Namespace("http://www.w3.org/ns/shacl#")
SHAPES = Namespace("https://ontologies.corestory.ai/sao/shapes/")


def bootstrap(schema_path, output):
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Refusing to overwrite editable Turtle shapes: output directory must be empty")
    output.mkdir(parents=True, exist_ok=True)
    view = SchemaView(str(Path(schema_path).resolve()))
    classes, enums, types = view.all_classes(), view.all_enums(), view.all_types()
    topics = {}
    for schema in view.all_schema():
        topic = Path(schema.source_file).stem if schema.source_file else "common"
        for name in schema.classes:
            topics[name] = topic
    graphs = {}
    counts = Counter()

    def term(element):
        return URIRef(view.get_uri(element, expand=True))

    def rdf_list(graph, head, values):
        for i, value in enumerate(values):
            cell = head if i == 0 else URIRef(str(head) + "/cell/" + str(i))
            following = URIRef(str(head) + "/cell/" + str(i + 1)) if i + 1 < len(values) else RDF.nil
            graph.add((cell, RDF.first, value))
            graph.add((cell, RDF.rest, following))
        return head if values else RDF.nil

    def constraints(graph, node, slot):
        if slot.any_of:
            options = []
            for i, option in enumerate(slot.any_of):
                child = URIRef(str(node) + "/alternative/" + str(i))
                constraints(graph, child, option)
                options.append(child)
            head = URIRef(str(node) + "/alternatives")
            graph.add((node, SH["or"], rdf_list(graph, head, options)))
            counts["any_of"] += 1
            return
        range_name = slot.range or view.schema.default_range
        if range_name in classes:
            graph.add((node, SH["class"], term(classes[range_name])))
            counts["class_range"] += 1
        elif range_name in enums:
            head = URIRef(str(node) + "/values")
            graph.add((node, SH["in"], rdf_list(graph, head, [Literal(str(v)) for v in enums[range_name].permissible_values])))
            counts["enum"] += 1
        elif range_name in types:
            scalar = types[range_name]
            pattern = slot.pattern or scalar.pattern
            visited = set()
            while scalar.typeof and not scalar.uri:
                if scalar.name in visited:
                    raise ValueError("Cyclic datatype definition")
                visited.add(scalar.name)
                scalar = types[scalar.typeof]
                pattern = pattern or scalar.pattern
            if scalar.uri:
                graph.add((node, SH.datatype, URIRef(view.expand_curie(scalar.uri))))
                counts["datatype"] += 1
            if pattern:
                graph.add((node, SH.pattern, Literal(pattern)))
                counts["pattern"] += 1
        else:
            raise ValueError(f"Unknown range {range_name}")
        if slot.pattern and range_name not in types:
            graph.add((node, SH.pattern, Literal(slot.pattern)))
        for field, predicate in (("minimum_value", SH.minInclusive), ("maximum_value", SH.maxInclusive)):
            value = getattr(slot, field)
            if value is not None:
                graph.add((node, predicate, Literal(value)))
                counts[field] += 1

    for name, cls in classes.items():
        graph = graphs.setdefault(topics.get(name, "common"), Graph())
        graph.bind("sh", SH);graph.bind("saosh", SHAPES)
        graph.bind("sao", Namespace(str(view.schema.id)));graph.bind("xsd", XSD)
        shape = SHAPES[name + "Shape"]
        graph.add((shape, RDF.type, SH.NodeShape))
        graph.add((shape, SH.targetClass, term(cls)))
        graph.add((shape, SH.closed, Literal(False)))
        # Flatten induced slots, retaining class-local ranges and inherited constraints.
        for slot in view.class_induced_slots(name):
            node = URIRef(str(SHAPES) + quote(name, safe="") + "/" + quote(slot.name, safe=""))
            graph.add((shape, SH.property, node))
            graph.add((node, RDF.type, SH.PropertyShape))
            graph.add((node, SH.path, term(slot)))
            if slot.description:
                graph.add((node, SH.description, Literal(slot.description)))
            minimum = slot.minimum_cardinality
            if slot.required:
                minimum = max(minimum or 0, 1)
            if minimum is not None:
                graph.add((node, SH.minCount, Literal(minimum)))
                counts["min_count"] += 1
            maximum = slot.maximum_cardinality
            if not slot.multivalued:
                maximum = min(maximum, 1) if maximum is not None else 1
            if maximum is not None:
                graph.add((node, SH.maxCount, Literal(maximum)))
                counts["max_count"] += 1
            constraints(graph, node, slot)
            counts["property_shapes"] += 1
    for name, graph in graphs.items():
        (output / (name + ".ttl")).write_text(("# Editable SHACL source, initially bootstrapped from SAO 2.1.0.\n# Copyright (c) 2026 CoreStory, Inc. — Apache-2.0\n\n" + graph.serialize(format="turtle")).rstrip() + "\n")
    report = {"baseline_version": str(view.schema.version), "classes": len(classes), "constraints": dict(counts),
              "status": "Initial translation; semantic equivalence has not been established",
              "deferred": ["Inverse relationship entailments and inconsistent inverse declarations", "Identifier-to-RDF-subject mapping and JSON/YAML inlining", "Abstract classes and mixin serialization", "Closed-world validation policy (initial shapes are open)", "Full validation equivalence and arbitrary LinkML metamodel features"]}
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "legacy/sao/sao.yml")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = bootstrap(args.schema, args.output_dir)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
