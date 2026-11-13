#!/usr/bin/env python3
"""Build the three Lactobacillaceae pages in the order their checks need.

    python3 scripts/build_lactobacillaceae_all.py

  1. build_lactobacillaceae.py          -> content/lactobacillaceae-genera.md   (from the genus CSV)
  2. build_lactobacillaceae_species.py  -> content/lactobacillaceae-species.md  (from the species snapshot)
  3. build_lactobacillaceae_hub.py      -> content/lactobacillaceae.md          (the overview; it checks 1 and 2)

New species release: python3 scripts/export_species_snapshot.py first.
New genus CSV: python3 scripts/make_life_tree.py first (the overview's animation is named after the CSV).
"""

import importlib.util
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))

for name in ("build_lactobacillaceae", "build_lactobacillaceae_species", "build_lactobacillaceae_hub"):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(f"== {name}")
    module.main()
