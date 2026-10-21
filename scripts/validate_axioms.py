#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Validate each ontology's OWL supplement without changing its inference policy."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.validators import sao_axioms, specspec_axioms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ontology", choices=("sao", "specspec"))
    args = parser.parse_args()
    if args.ontology in (None, "sao"):
        _, _, pairs = sao_axioms.check_axioms()
        print(f"sao: {len(pairs)} inverse pairs and reasoning manifest pass.")
    if args.ontology in (None, "specspec"):
        specspec_axioms.check_axioms()
        print("specspec: core and bridge property typing pass.")


if __name__ == "__main__":
    main()
