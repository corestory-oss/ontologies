#!/usr/bin/env python3
"""Check schema imports; optionally compare resolved definitions with a baseline.

Run: uv run python scripts/migration/sao/check_schema.py [--compare path/to/baseline.yml]
The comparison excludes only LinkML's source-file/import provenance fields.
Descriptions, comments, constraints, inferred attributes, and term IRIs are included.
"""
import argparse
import json
from pathlib import Path

from linkml_runtime.dumpers import json_dumper
from linkml_runtime.utils.schemaview import SchemaView

PROVENANCE = {"from_schema", "imported_from", "source_file"}
SECTIONS = ("classes", "slots", "enums", "types", "subsets")


def normalized(value):
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in value.items() if not (key in PROVENANCE and isinstance(item, str))}
    if isinstance(value, list):
        return [normalized(item) for item in value]
    return value


def definition(value):
    return normalized(json.loads(json_dumper.dumps(value)))


def check_imports(view):
    owners = {}
    schemas = view.all_schema()
    for schema in schemas:
        for section in SECTIONS:
            for name in getattr(schema, section):
                key = (section, name)
                if key in owners:
                    raise ValueError(f"Duplicate {section}.{name}: {owners[key]} and {schema.name}")
                owners[key] = schema.name
    # Exercise attribute inheritance and slot-use resolution across module boundaries.
    for name in view.all_classes():
        view.induced_class(name)
    for section in ("classes", "slots", "enums", "types"):
        for element in getattr(view, f"all_{section}")().values():
            view.get_uri(element, expand=True)
    return schemas


def compare(before, after):
    root_before = definition(before.schema)
    root_after = definition(after.schema)
    for field in (*SECTIONS, "imports"):
        root_before.pop(field, None)
        root_after.pop(field, None)
    if root_before != root_after:
        raise ValueError("Root schema metadata changed")
    for section in SECTIONS:
        old = getattr(before, f"all_{section}")()
        new = getattr(after, f"all_{section}")()
        if set(old) != set(new):
            raise ValueError(f"{section} names changed: {set(old) ^ set(new)}")
        for name in old:
            if definition(old[name]) != definition(new[name]):
                raise ValueError(f"Definition changed: {section}.{name}")
            if section != "subsets" and before.get_uri(old[name], expand=True) != after.get_uri(new[name], expand=True):
                raise ValueError(f"Term IRI changed: {section}.{name}")
    for name in before.all_classes():
        if definition(before.induced_class(name)) != definition(after.induced_class(name)):
            raise ValueError(f"Inherited attributes or constraints changed: {name}")
    print("Resolved definitions, inherited attributes, root metadata, and term IRIs are equivalent.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=Path(__file__).resolve().parents[3] / "legacy/sao/sao.yml")
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    view = SchemaView(str(args.schema.resolve()))
    schemas = check_imports(view)
    print(f"Resolved {len(schemas)} schemas; no duplicate definitions or unresolved imports.")
    if args.compare:
        before = SchemaView(str(args.compare.resolve()))
        check_imports(before)
        compare(before, view)


if __name__ == "__main__":
    main()
