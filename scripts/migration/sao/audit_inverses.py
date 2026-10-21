#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Audit inverse declarations from the legacy baseline; bootstrap safe OWL axioms once."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from rdflib import Graph, Namespace, RDF, URIRef, Literal
from rdflib.namespace import OWL, DCTERMS, RDFS
from linkml_runtime.utils.schemaview import SchemaView
ROOT = Path(__file__).resolve().parents[3]


def audit(schema_path, vocabulary):
    view = SchemaView(str(Path(schema_path).resolve()))
    properties = set(vocabulary.subjects(RDF.type, RDF.Property))
    names = defaultdict(set)
    slots = []
    for name, slot in view.all_slots(attributes=False).items():
        names[name].add(str(view.get_uri(slot, expand=True)))
        slots.append(("global", slot))
    for name in view.all_classes():
        for slot in view.class_induced_slots(name):
            names[slot.name].add(str(view.get_uri(slot, expand=True)))
            slots.append((name, slot))
    claims = defaultdict(set)
    contexts = defaultdict(set)
    issues = defaultdict(set)
    counts = {"contextual_declarations": 0}
    classes = view.all_classes()
    for owner, slot in slots:
        if not slot.inverse:
            continue
        counts["contextual_declarations"] += 1
        source = str(view.get_uri(slot, expand=True))
        candidates = names.get(slot.inverse, set())
        if URIRef(source) not in properties:
            issues[source].add("source property not declared in Turtle vocabulary")
        if len(candidates) != 1:
            issues[source].add("inverse name is missing or resolves to multiple IRIs: " + slot.inverse)
            continue
        target = next(iter(candidates))
        if URIRef(target) not in properties:
            issues[source].add("inverse property not declared in Turtle vocabulary")
        if slot.range not in classes and not slot.any_of:
            issues[source].add("inverse declaration has a non-class range: " + str(slot.range))
        claims[source].add(target)
        contexts[(source, target)].add(owner)
        if owner != "global":
            forward_ranges = [option.range for option in slot.any_of] if slot.any_of else [slot.range]
            for range_name in forward_ranges:
                if range_name not in classes:
                    issues[source].add("inverse range alternative is not a class: " + str(range_name))
                    continue
                inverse_slots = [candidate for candidate in view.class_induced_slots(range_name)
                                 if candidate.name == slot.inverse]
                if not inverse_slots:
                    issues[source].add(f"{owner}.{slot.name}: {range_name} has no {slot.inverse} slot")
                    continue
                inverse_slot = inverse_slots[0]
                reverse_ranges = [option.range for option in inverse_slot.any_of] if inverse_slot.any_of else [inverse_slot.range]
                ancestors = set(view.class_ancestors(owner))
                if not any(candidate in ancestors for candidate in reverse_ranges):
                    issues[source].add(f"{owner}.{slot.name}: {range_name}.{slot.inverse} cannot point back to {owner}; range=" + str(reverse_ranges))
    # An axiom also affects uses that never declared an inverse locally. Check
    # those shared-property uses before accepting a global inverse statement.
    for owner, slot in slots:
        if owner == "global" or slot.inverse:
            continue
        source = str(view.get_uri(slot, expand=True))
        if len(claims[source]) != 1:
            continue
        target = next(iter(claims[source]))
        forward_ranges = [option.range for option in slot.any_of] if slot.any_of else [slot.range]
        for range_name in forward_ranges:
            if range_name not in classes:
                issues[source].add(f"Global inverse would apply to non-class-valued {owner}.{slot.name}")
                continue
            reverse = [candidate for candidate in view.class_induced_slots(range_name)
                       if str(view.get_uri(candidate, expand=True)) == target]
            if not reverse:
                issues[source].add(f"Global inverse would apply to {owner}.{slot.name}, but {range_name} has no inverse property " + target)
                contexts[(source,target)].add(owner + " (implied globally; no local inverse declaration)")
                continue
            reverse_ranges = [option.range for option in reverse[0].any_of] if reverse[0].any_of else [reverse[0].range]
            if not any(candidate in view.class_ancestors(owner) for candidate in reverse_ranges):
                issues[source].add(f"Global inverse cannot point back to {owner}.{slot.name}")
    # OWL inverseOf is global and symmetric. Exclude the entire component when
    # declarations form a fan-out, chain, unresolved endpoint, or one-way pair.
    adjacency = defaultdict(set)
    for source, targets in claims.items():
        for target in targets:
            adjacency[source].add(target);adjacency[target].add(source)
    accepted, unresolved, visited = [], [], set()
    for start in sorted(set(adjacency) | set(issues)):
        if start in visited:
            continue
        todo, members = [start], set()
        while todo:
            node = todo.pop()
            if node in members:
                continue
            members.add(node);todo.extend(adjacency[node] - members)
        visited.update(members)
        reasons = sorted({reason for node in members for reason in issues[node]})
        if len(members) != 2:
            reasons.append("multiple inverse partners would equate distinct property IRIs")
        if len(members) == 2:
            a,b = sorted(members)
            if claims[a] != {b} or claims[b] != {a}:
                reasons.append("inverse declarations are not uniquely reciprocal")
        edges = [dict(property=a, inverse=b, declared_on=sorted(contexts[(a,b)]))
                 for a in sorted(members) for b in sorted(claims[a])]
        if reasons:
            unresolved.append(dict(properties=sorted(members), reasons=reasons, declarations=edges))
        else:
            a,b = sorted(members)
            accepted.append([a,b])
    counts.update(properties_with_inverse_claims=sum(bool(targets) for targets in claims.values()), accepted_pairs=len(accepted),
                  unresolved_groups=len(unresolved), excluded_properties=sum(len(g["properties"]) for g in unresolved))
    return dict(baseline_version=str(view.schema.version), counts=counts,
                accepted_pairs=accepted, unresolved_groups=unresolved,
                note="Historical declaration audit. Accepted means uniquely reciprocal names and resource-valued endpoints, also checked class-local ranges against named class ancestry. This is a declaration-consistency check, not a proof of arbitrary instance conformance.")


def bootstrap_axioms(report):
    graph = Graph()
    graph.bind("sao", Namespace("https://ontologies.corestory.ai/sao/"))
    graph.bind("owl", OWL);graph.bind("dcterms", DCTERMS);graph.bind("rdfs", RDFS)
    ontology = URIRef("https://ontologies.corestory.ai/sao/axioms/")
    graph.add((ontology, RDF.type, OWL.Ontology))
    graph.add((ontology, DCTERMS.title, Literal("SAO inverse relationship supplement")))
    graph.add((ontology, RDFS.seeAlso, URIRef("https://ontologies.corestory.ai/sao/")))
    for a,b in report["accepted_pairs"]:
        graph.add((URIRef(a), RDF.type, OWL.ObjectProperty))
        graph.add((URIRef(b), RDF.type, OWL.ObjectProperty))
        graph.add((URIRef(a), OWL.inverseOf, URIRef(b)))
    return graph

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "legacy/sao/sao.yml")
    parser.add_argument("--vocabulary", type=Path, default=ROOT / "dist/sao.ttl")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--axioms", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists() or args.axioms.exists():
        parser.error("Output files must not exist; refusing to overwrite editable sources")
    report = audit(args.schema, Graph().parse(args.vocabulary, format="turtle"))
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.axioms.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    args.axioms.write_text(("# Editable OWL supplement; audit decisions are documented in docs/sao/inverse-relationships.md.\n# Copyright (c) 2026 CoreStory, Inc. — Apache-2.0\n\n"+bootstrap_axioms(report).serialize(format="turtle")).rstrip()+"\n")
    print(json.dumps(report["counts"]))
