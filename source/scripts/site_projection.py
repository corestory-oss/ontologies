# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
#!/usr/bin/env python3
"""Experimental read-only Turtle → RDF Garden 2 display projection.

No inference or ontology rewriting. JSON is a browsing view, never a schema.
"""
from collections import Counter
import hashlib
from html import escape
import json
import re
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, SKOS

from scripts.catalog import ROOT, catalog
SH = Namespace('http://www.w3.org/ns/shacl#')
SCHEMA = Namespace('http://schema.org/')
SAO = Namespace('https://ontologies.corestory.ai/sao/')
SPEC = Namespace('https://ontologies.corestory.ai/specspec/')
PREFIXES = {
    'sao': str(SAO), 'spec': str(SPEC), 'specsao': str(SPEC) + 'sao/',
    'rdf': str(RDF), 'rdfs': str(RDFS), 'owl': str(OWL), 'xsd': str(XSD),
    'sh': str(SH), 'skos': str(SKOS), 'dcterms': str(DCTERMS), 'schema': str(SCHEMA),
}


def compact(node):
    value = str(node)
    for prefix, namespace in sorted(PREFIXES.items(), key=lambda p: -len(p[1])):
        if value.startswith(namespace):
            return prefix + ':' + value[len(namespace):]
    return value


def link(node):
    return f'<a href="{escape(str(node), quote=True)}">{escape(compact(node))}</a>'


def literal_json(node):
    if isinstance(node, URIRef):
        return str(node)
    result = {'@value': str(node)}
    if node.language:
        result['@language'] = node.language
    elif node.datatype:
        result['@type'] = str(node.datatype)
    return result


def project():
    inputs = []
    totals = Counter()
    vocabulary, shapes, axioms = Graph(), Graph(), Graph()
    for name, entry in catalog().items():
        source = ROOT / entry['source']
        for manifest_name in entry['products']:
            layer = 'vocabulary' if manifest_name.endswith('vocabulary') else 'shapes' if manifest_name.endswith('shapes') else 'axioms'
            graph = {'vocabulary': vocabulary, 'shapes': shapes, 'axioms': axioms}[layer]
            manifest_path = source / 'manifests' / (manifest_name + '.json')
            manifest = json.loads(manifest_path.read_text())
            for filename in manifest['files']:
                path = source / filename
                blob = path.read_bytes()
                graph.parse(data=blob.decode(), format='turtle')
                inputs.append({'ontology': name, 'path': str(path.relative_to(ROOT)),
                               'sha256': hashlib.sha256(blob).hexdigest()})
    combined = Graph()
    for graph in (vocabulary, shapes, axioms):
        combined += graph
    classes = set(vocabulary.subjects(RDF.type, RDFS.Class)) | set(vocabulary.subjects(RDF.type, OWL.Class))
    datatypes = {n for n in vocabulary.subjects(RDF.type, RDFS.Datatype)
                 if str(n).startswith((str(SAO), str(SPEC)))}
    properties = set(vocabulary.subjects(RDF.type, RDF.Property))
    properties |= set(axioms.subjects(RDF.type, OWL.ObjectProperty))
    properties |= set(axioms.subjects(RDF.type, OWL.DatatypeProperty))
    extra_types = set(shapes.objects(None, SH.datatype))
    extra_types |= {RDFS.Literal, RDFS.Resource}
    for prefix, namespace in PREFIXES.items():
        combined.bind(prefix, namespace, replace=True)

    def notes(node):
        return [escape(str(v)) for v in sorted(vocabulary.objects(node, SKOS.note), key=str)]

    def describe(node, kind):
        item = {'id': str(node), 'type': kind}
        labels = sorted(set(vocabulary.objects(node, RDFS.label)), key=str)
        if labels:
            item['label'] = {'en': str(labels[0])}
        descriptions = sorted(set(vocabulary.objects(node, RDFS.comment)), key=str)
        if descriptions:
            # The RDF retains per-class comments. Collapse identical inherited
            # wording in this display view so shared properties remain readable.
            grouped = {}
            for value in descriptions:
                match = re.match(r'^\[([^\]]+)\] (.*)$', str(value), re.S)
                context, text = match.groups() if match else (None, str(value))
                grouped.setdefault(text, []).append(context)
            if len(grouped) == 1:
                rendered = next(iter(grouped))
            else:
                rendered = '\n\n'.join(
                    ('[' + ', '.join(c for c in contexts if c) + '] ' if any(contexts) else '') + text
                    for text, contexts in grouped.items()
                )
            item['definition'] = {'en': rendered}
        owner = vocabulary.value(node, RDFS.isDefinedBy)
        if owner:
            item['definedBy'] = str(owner)
        if any(bool(v.toPython()) for v in vocabulary.objects(node, OWL.deprecated)):
            item['deprecated'] = True
        return item

    def range_expression(prop):
        # Garden's shape form is disjunction-of-conjunctions. sh:in is an
        # exact-value disjunction, not a list of class restrictions.
        exact = shapes.value(prop, SH.hasValue)
        maximum = shapes.value(prop, SH.maxCount)
        if exact is not None and maximum is not None and int(maximum) == 1:
            return [literal_json(exact)]
        allowed = shapes.value(prop, SH['in'])
        if allowed is not None:
            return [literal_json(v) for v in Collection(shapes, allowed)]
        terms = list(shapes.objects(prop, SH['class'])) + list(shapes.objects(prop, SH.datatype))
        if terms:
            return [[str(t) for t in terms]]
        alternatives = shapes.value(prop, SH['or'])
        if alternatives is not None:
            return [branch for child in Collection(shapes, alternatives)
                    for branch in (range_expression(child) or [[]])]
        return None

    def property_constraint(prop):
        path = shapes.value(prop, SH.path)
        if not isinstance(path, URIRef):
            raise ValueError(f'Preview requires a named property path: {prop}')
        result = {'property': str(path)}
        for key, predicate in [('min', SH.minCount), ('max', SH.maxCount)]:
            value = shapes.value(prop, predicate)
            if value is not None:
                result[key] = int(value)
        expression = range_expression(prop)
        if expression is not None:
            result['shape'] = expression
        return result

    class_items = []
    for cls in sorted(classes | datatypes | extra_types, key=str):
        item = describe(cls, 'Class')
        parents = sorted(set(vocabulary.objects(cls, RDFS.subClassOf)), key=str)
        if parents:
            item['broader'] = [str(p) for p in parents if isinstance(p, URIRef)]
        remarks = notes(cls)
        constraints = []
        supplementary = []
        rules = []
        for target in sorted(shapes.subjects(SH.targetClass, cls), key=str):
            closed = shapes.value(target, SH.closed)
            if closed is not None:
                supplementary.append('Shape ' + escape(compact(target)) + ': '
                                     + ('closed' if bool(closed.toPython()) else 'open') + '.')
            for prop in sorted(shapes.objects(target, SH.property), key=lambda p: str(shapes.value(p, SH.path))):
                constraints.append(property_constraint(prop))
                path = shapes.value(prop, SH.path)
                for predicate, label in [(SH.hasValue, 'must include'), (SH.pattern, 'pattern'),
                                         (SH.minInclusive, 'minimum'), (SH.maxInclusive, 'maximum'),
                                         (SH.nodeKind, 'node kind')]:
                    for value in shapes.objects(prop, predicate):
                        supplementary.append(link(path) + ': ' + label + ' <code>' + escape(str(value)) + '</code>')
                totals['class_property_uses'] += 1
            for constraint in shapes.objects(target, SH.sparql):
                rules += [escape(str(message)) for message in shapes.objects(constraint, SH.message)]
        # SHACL targetClass rules apply to subclasses as well. Surface those
        # inherited messages even though Garden only inherits shape expressions.
        ancestors = set()
        pending = list(vocabulary.objects(cls, RDFS.subClassOf))
        while pending:
            ancestor = pending.pop()
            if ancestor in ancestors:
                continue
            ancestors.add(ancestor)
            pending.extend(vocabulary.objects(ancestor, RDFS.subClassOf))
        for ancestor in ancestors:
            for target in shapes.subjects(SH.targetClass, ancestor):
                for constraint in shapes.objects(target, SH.sparql):
                    rules += [escape(str(message)) + ' (via ' + escape(compact(ancestor)) + ')'
                              for message in shapes.objects(constraint, SH.message)]
        if constraints:
            item['shape'] = [constraints]
        if cls in datatypes:
            remarks.insert(0, 'RDFS datatype / enum, shown in the class browser for discoverability.')
            values = []
            # RDFLib yields a predicate once per triple; visit each predicate
            # once so an N-value enum does not render its N values N times.
            for predicate in sorted(set(vocabulary.predicates(cls)), key=str):
                if str(predicate).endswith('/permissibleValue'):
                    for entry in vocabulary.objects(cls, predicate):
                        value = vocabulary.value(entry, RDF.value)
                        text = vocabulary.value(entry, RDFS.comment)
                        values.append('<li><code>' + escape(str(value)) + '</code>'
                                      + (': ' + escape(str(text)) if text else '') + '</li>')
            if values:
                remarks.append('<h3>Allowed values</h3><ul>' + ''.join(sorted(values)) + '</ul>')
        if supplementary:
            remarks.append('<h3>Additional SHACL constraints</h3><ul>'
                           + ''.join('<li>' + s + '</li>' for s in supplementary) + '</ul>')
        if rules:
            remarks.append('<h3>SHACL graph rules</h3><ul>'
                           + ''.join('<li>' + s + '</li>' for s in sorted(set(rules))) + '</ul>')
        if remarks:
            item['remarks'] = {'en': '<div>' + ''.join('<p>' + r + '</p>' if not r.startswith('<h3>') else r for r in remarks) + '</div>'}
        class_items.append(item)

    property_items = []
    for prop in sorted(properties, key=str):
        item = describe(prop, 'Property')
        parents = [str(p) for p in vocabulary.objects(prop, RDFS.subPropertyOf) if isinstance(p, URIRef)]
        if parents:
            item['broader'] = sorted(parents)
        remarks = notes(prop)
        for graph, predicate, label in [
            (vocabulary, RDFS.domain, 'RDFS domain'), (vocabulary, RDFS.range, 'RDFS range'),
            (vocabulary, SCHEMA.domainIncludes, 'Suggested domains (annotation)'),
            (vocabulary, SCHEMA.rangeIncludes, 'Suggested ranges (annotation)'),
        ]:
            values = sorted(set(graph.objects(prop, predicate)), key=str)
            if values:
                remarks.append(escape(label) + ': ' + ', '.join(link(v) for v in values))
        inverses = set(axioms.objects(prop, OWL.inverseOf)) | set(axioms.subjects(OWL.inverseOf, prop))
        if inverses:
            remarks.append('OWL inverse: ' + ', '.join(link(v) for v in sorted(inverses, key=str)))
        users = sorted({cls for shape in shapes.subjects(SH.path, prop)
                        for node in shapes.subjects(SH.property, shape)
                        for cls in shapes.objects(node, SH.targetClass)}, key=str)
        if users:
            remarks.append('Used by: ' + ', '.join(link(v) for v in users))
        # Surface retired-predicate prohibition rules too, not only class shapes.
        for target in shapes.subjects(SH.targetSubjectsOf, prop):
            for node in [target, *shapes.objects(target, SH.property)]:
                remarks += [escape(str(m)) for m in shapes.objects(node, SH.message)]
        if remarks:
            item['remarks'] = {'en': '<div>' + ''.join('<p>' + r + '</p>' for r in remarks) + '</div>'}
        property_items.append(item)

    ontology_items = []
    for node in [SAO[''], SPEC[''], URIRef(str(SPEC) + 'sao/')]:
        item = {'id': str(node)}
        for field, predicate in [('version', DCTERMS.hasVersion), ('license', DCTERMS.license)]:
            value = vocabulary.value(node, predicate)
            if value is not None:
                item[field] = str(value)
        title = vocabulary.value(node, DCTERMS.title)
        if title:
            item['label'] = {'en': str(title)}
        ontology_items.append(item)
    payload = [
        {'@context': PREFIXES, 'type': 'Classes', 'concepts': class_items},
        {'@context': PREFIXES, 'type': 'Properties', 'concepts': property_items},
        {'@context': PREFIXES, 'type': 'Ontologies', 'concepts': ontology_items},
    ]
    metadata = {
        'garden_version': json.loads((ROOT / 'web/garden-assets.json').read_text())['version'],
        'ontologies': {name: {'namespace': item['namespace'], 'version': item['version']}
                       for name, item in catalog().items()},
        'classes': len(classes), 'local_datatypes': len(datatypes),
        'properties': len(properties), **totals,
        'inputs': sorted(inputs, key=lambda item: item['path']),
        'limitations': [
            'Display projection only; the browser does not run validation or inference.',
            'SHACL ranges, cardinalities and enums use Garden definitions.',
            'Additional constraints and graph-rule descriptions appear in remarks.',
            'RDFS datatypes appear in the class browser with their actual kind noted.',
            'Garden JSON is not a lossless RDF serialization; original Turtle is supplied.',
        ],
    }
    return payload, metadata
