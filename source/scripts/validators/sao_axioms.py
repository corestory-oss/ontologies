#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Check the authored inverse supplement without loading the legacy LinkML baseline."""
from collections import defaultdict
from rdflib import RDF, URIRef, Namespace, RDFS
from rdflib.namespace import OWL
from scripts.build_rdf import assemble, ROOT


def check_shape_ranges(vocabulary, shapes, pairs):
    """Check every authored use, including uses with no legacy inverse annotation."""
    sh = Namespace("http://www.w3.org/ns/shacl#")
    partners = {a:b for a,b in pairs} | {b:a for a,b in pairs}
    def ranges(node):
        if shapes.value(node, sh.datatype) is not None or shapes.value(node, sh["in"]) is not None:
            return set()
        result = set(shapes.objects(node, sh["class"]))
        for head in shapes.objects(node, sh["or"]):
            for option in shapes.items(head):
                result |= ranges(option)
        return result
    cases = {}
    for shape, owner in shapes.subject_objects(sh.targetClass):
        cases[owner] = {shapes.value(node, sh.path):ranges(node)
                        for node in shapes.objects(shape, sh.property)}
    for owner, slots in cases.items():
        ancestors, todo = {owner}, [owner]
        while todo:
            current = todo.pop()
            for parent in vocabulary.objects(current, RDFS.subClassOf):
                if parent not in ancestors:
                    ancestors.add(parent);todo.append(parent)
        for property, allowed in slots.items():
            if property not in partners:
                continue
            if not allowed:
                raise ValueError(f"Inverse property is not class-valued on {owner}: {property}")
            for target in allowed:
                reverse = cases.get(target, {}).get(partners[property], set())
                if not ancestors & reverse:
                    raise ValueError(f"Inverse range mismatch: {owner} / {property} / {target}")


def check_axioms():
    vocabulary = assemble(ROOT / "ontologies/sao/manifests/vocabulary.json")
    axioms = assemble(ROOT / "ontologies/sao/manifests/axioms.json")
    declared = set(vocabulary.subjects(RDF.type,RDF.Property))
    partners = defaultdict(set)
    pairs = set()
    for a,b in axioms.subject_objects(OWL.inverseOf):
        if a == b or not isinstance(a,URIRef) or not isinstance(b,URIRef):
            raise ValueError("Expected distinct named inverse properties")
        if a not in declared or b not in declared:
            raise ValueError(f"Undeclared inverse endpoint: {a}, {b}")
        for property in (a,b):
            if (property,RDF.type,OWL.ObjectProperty) not in axioms:
                raise ValueError(f"Inverse endpoint lacks object-property declaration: {property}")
        partners[a].add(b);partners[b].add(a)
        pair = tuple(sorted((a,b)))
        if pair in pairs:
            raise ValueError("Duplicate symmetric inverse declaration")
        pairs.add(pair)
    if any(len(values)!=1 for values in partners.values()):
        raise ValueError("Multiple inverse partners require explicit modeling review")
    shapes = assemble(ROOT / "ontologies/sao/manifests/shapes.json")
    check_shape_ranges(vocabulary, shapes, pairs)
    reasoning = assemble(ROOT / "ontologies/sao/manifests/reasoning.json")
    if set(reasoning) != set(vocabulary) | set(axioms):
        raise ValueError("Reasoning manifest does not assemble vocabulary plus axioms")
    if not pairs:
        raise ValueError("Inverse supplement is empty")
    return vocabulary, axioms, pairs

if __name__ == "__main__":
    _,_,pairs = check_axioms()
    print(f"Validated {len(pairs)} uniquely paired inverse axioms and the reasoning manifest.")
