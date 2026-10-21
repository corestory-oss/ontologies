# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
import sys
import tomllib
from pathlib import Path
import unittest
from rdflib import Graph, Namespace, RDF, Literal, XSD
from rdflib.namespace import OWL, DCTERMS
from owlrl import DeductiveClosure, OWLRL_Semantics
ROOT=Path(__file__).resolve().parents[2]
from scripts.validators.sao import sources, check_data
from scripts.validators.sao_axioms import check_axioms
S=Namespace('https://ontologies.corestory.ai/sao/')
EX=Namespace('https://example.org/saov3/')
SH=Namespace('http://www.w3.org/ns/shacl#')

class RelationshipThreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocabulary,cls.shapes=sources()
        _,cls.axioms,_=check_axioms()

    def node(self,g,class_name,key):
        node=EX[key];g.add((node,RDF.type,S[class_name]))
        for shape in self.shapes.subjects(SH.targetClass,S[class_name]):
            for property in self.shapes.objects(shape,SH.property):
                if not self.shapes.value(property,SH.minCount):continue
                path=self.shapes.value(property,SH.path)
                allowed=self.shapes.value(property,SH['in'])
                datatype=self.shapes.value(property,SH.datatype)
                examples={XSD.dateTime:'2026-10-14T00:00:00Z', XSD.date:'2026-10-14', XSD.integer:'1', XSD.boolean:'true', XSD.decimal:'1.0', XSD.double:'1.0', XSD.anyURI:'https://example.org/value'}
                value=next(self.shapes.items(allowed)) if allowed else Literal(examples.get(datatype,key),datatype=datatype)
                g.add((node,path,value))
        return node

    def conforms(self,g):
        return check_data(g,self.vocabulary,self.shapes)[0]

    def reason(self,g):
        data=Graph();data+=g;data+=self.vocabulary;data+=self.axioms
        DeductiveClosure(OWLRL_Semantics).expand(data)
        return data

    def test_version_metadata_consistent_and_legacy_pinned(self):
        version=__import__('json').loads((ROOT/'ontologies/catalog.json').read_text())['ontologies']['sao']['version']
        self.assertEqual(version,'3.0.0')
        self.assertEqual(set(self.vocabulary.objects(S[''],DCTERMS.hasVersion)),{Literal(version)})
        self.assertEqual(set(self.axioms.objects(S['axioms/'],DCTERMS.hasVersion)),{Literal(version)})
        # The legacy schema has not been relabeled as the new RDF contract.
        self.assertIn('version: 2.1.0',(ROOT/'legacy/sao/sao.yml').read_text())

    def test_versions_keep_class_pairing(self):
        g=Graph();contract=self.node(g,'Contract','contract');schema=self.node(g,'Schema','schema')
        cv=self.node(g,'ContractVersion','cv');sv=self.node(g,'SchemaVersion','sv')
        g.add((contract,S.has_versions,cv));g.add((schema,S.has_versions,sv))
        self.assertTrue(self.conforms(g))
        expanded=self.reason(g)
        self.assertIn((cv,S.version_of,contract),expanded)
        self.assertIn((sv,S.version_of,schema),expanded)
        self.assertTrue(self.conforms(expanded))
        g.set((contract,S.has_versions,sv));self.assertFalse(self.conforms(g))

    def test_log_entry_pairs(self):
        g=Graph();log=self.node(g,'Log','log');audit=self.node(g,'AuditLog','audit')
        entry=self.node(g,'LogEntry','entry');record=self.node(g,'AuditEntry','record')
        g.add((log,S.contains_entries,entry));g.add((audit,S.contains_entries,record))
        self.assertTrue(self.conforms(g))
        expanded=self.reason(g)
        self.assertIn((entry,S.entry_in,log),expanded);self.assertIn((record,S.entry_in,audit),expanded)
        g.set((log,S.contains_entries,record));self.assertFalse(self.conforms(g))

    def test_callable_uses_heterogeneous_resources(self):
        g=Graph();call=self.node(g,'CallableUnit','call');file=self.node(g,'FileDefinition','file')
        primitive=self.node(g,'ConcurrencyPrimitive','primitive')
        g.add((call,S.uses,file));g.add((call,S.uses,primitive))
        self.assertTrue(self.conforms(g))
        expanded=self.reason(g)
        self.assertIn((file,S.used_by_callables,call),expanded);self.assertIn((primitive,S.used_by_callables,call),expanded)
        wrong=self.node(g,'Contract','wrong');g.add((call,S.uses,wrong));self.assertFalse(self.conforms(g))

    def test_constraints_keep_class_pairing(self):
        g=Graph();collection=self.node(g,'Collection','collection');permission=self.node(g,'Permission','permission')
        database=self.node(g,'DatabaseConstraint','database');authorization=self.node(g,'Constraint','authorization')
        g.add((collection,S.has_constraints,database));g.add((permission,S.has_constraints,authorization))
        self.assertTrue(self.conforms(g))
        expanded=self.reason(g)
        self.assertIn((database,S.constrains,collection),expanded);self.assertIn((authorization,S.constrains,permission),expanded)
        g.set((collection,S.has_constraints,authorization));self.assertFalse(self.conforms(g))

    def test_subscription_roles_do_not_cross(self):
        g=Graph();actor=self.node(g,'Actor','actor');interface=self.node(g,'EventInterface','interface')
        subscription=self.node(g,'Subscription','subscription')
        g.add((actor,S.owns_subscriptions,subscription));g.add((interface,S.subscriptions_to_interface,subscription))
        self.assertTrue(self.conforms(g))
        expanded=self.reason(g)
        self.assertIn((subscription,S.subscribed_by_actor,actor),expanded)
        self.assertIn((subscription,S.subscribes_to_interface,interface),expanded)
        self.assertNotIn((subscription,S.subscribes_to_interface,actor),expanded)
        self.assertNotIn((subscription,S.subscribed_by_actor,interface),expanded)
        self.assertTrue(self.conforms(expanded))

    def test_file_operation_roles_do_not_cross(self):
        g=Graph();file=self.node(g,'FileDefinition','file');call=self.node(g,'CallableUnit','call')
        operation=self.node(g,'FileOperation','operation')
        g.add((file,S.operations_on_file,operation));g.add((call,S.operations_in_callable,operation))
        self.assertTrue(self.conforms(g))
        expanded=self.reason(g)
        self.assertIn((operation,S.operates_on_file,file),expanded)
        self.assertIn((operation,S.performed_in_callable,call),expanded)
        self.assertNotIn((operation,S.operates_on_file,call),expanded)
        self.assertNotIn((operation,S.performed_in_callable,file),expanded)
        self.assertTrue(self.conforms(expanded))

    def test_membership_includes_data_and_keeps_structures_distinct(self):
        g=Graph();unit=self.node(g,'EncapsulationUnit','unit');call=self.node(g,'CallableUnit','call')
        structure=self.node(g,'DataStructure','structure');element=self.node(g,'DataElement','element')
        field=self.node(g,'DataElement','field')
        g.add((unit,S.contains_callable_units,call));g.add((unit,S.contains_data_structures,structure))
        g.add((unit,S.unit_contains_data_elements,element));g.add((structure,S.contains_data_elements,field))
        self.assertTrue(self.conforms(g))
        expanded=self.reason(g)
        for member in (call,structure,element):
            self.assertIn((member,S.contained_in_unit,unit),expanded)
            self.assertIn((unit,S.contains_unit_members,member),expanded)
        self.assertNotIn((unit,S.contains_callable_units,element),expanded)
        self.assertNotIn((structure,S.contains_unit_members,field),expanded)
        self.assertNotIn((field,S.contained_in_unit,structure),expanded)
        self.assertTrue(self.conforms(expanded))

    def test_every_retired_predicate_is_rejected(self):
        retired=set(self.vocabulary.subjects(OWL.deprecated,Literal(True)))
        self.assertEqual(len(retired),9)
        for predicate in retired:
            with self.subTest(predicate=predicate):
                g=Graph();owner=self.node(g,'System','owner')
                g.add((owner,predicate,EX.target));self.assertFalse(self.conforms(g))

if __name__=='__main__':unittest.main()
