"""Repository paths and independently versioned ontology catalog."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def catalog():
    entries = json.loads((ROOT / "ontologies/catalog.json").read_text())["ontologies"]
    outputs = set()
    for name, entry in entries.items():
        source = (ROOT / entry["source"]).resolve()
        if not source.is_relative_to(ROOT / "ontologies"):
            raise ValueError(f"Source outside ontologies/: {name}")
        for manifest, filename in entry["products"].items():
            output = (ROOT / filename).resolve()
            if not output.is_relative_to(ROOT / "dist") or output.suffix != ".ttl":
                raise ValueError(f"Output outside dist/: {filename}")
            if output in outputs:
                raise ValueError(f"Duplicate output: {filename}")
            outputs.add(output)
    return entries
