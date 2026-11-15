#!/usr/bin/env python3
"""Copy the lab's name map (old names -> current names) into the website repo.

    python3 scripts/export_name_map.py                 # the newest name_map_<date> folder
    python3 scripts/export_name_map.py 2026-11-14

Reads <lab>/1_LactoTax_transfer_Nanzhen/name_map_<date>/ (name_map_species.csv, name_lookup.csv, name_map_genera.csv)
and writes assets/lactobacillaceae/names/<file>_<date>.csv, plus names_<date>.json with the counts. The Names page
(build_lactobacillaceae_names.py) reads these. The map is built from the species release, the LPSN crosswalk and
LactoTax; its own README says how. The newest copy is the only one kept.

Like the other export scripts it needs the lab folder, which is not in this repo, so it only runs on the author's machine.
"""

import csv
import glob
import json
import os
import re
import shutil
import sys
from collections import Counter

LAB = "/Users/nanzhen/Documents/1_phd_2020/5_doctoral_program/0.1_type_strain_tree/18_202611_automate/1_genus_species_acc_update/1_LactoTax_transfer_Nanzhen"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "assets", "lactobacillaceae", "names")
FILES = ("name_map_species", "name_lookup", "name_map_genera")


def read(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))


def main():
    folders = sorted(d for d in os.listdir(LAB) if re.fullmatch(r"name_map_\d{4}-\d{2}-\d{2}", d))
    if not folders:
        sys.exit(f"no name_map_<date> folder in {LAB}")
    date = sys.argv[1] if len(sys.argv) > 1 else folders[-1].removeprefix("name_map_")
    base = os.path.join(LAB, f"name_map_{date}")
    for f in FILES:
        if not os.path.exists(os.path.join(base, f + ".csv")):
            sys.exit(f"{os.path.join(base, f + '.csv')} does not exist")

    species = read(os.path.join(base, "name_map_species.csv"))
    lookup = read(os.path.join(base, "name_lookup.csv"))
    genera = read(os.path.join(base, "name_map_genera.csv"))

    # What the Names page relies on; the lab build checks more, these are the ones a wrong copy would break.
    names = [r["name"] for r in lookup]
    cur = {r["current_name"] for r in species}
    assert len(set(names)) == len(names), "name_lookup.csv has a name twice"
    assert all(r["current_name"] in cur for r in lookup), "a lookup name leads to a current name that is not in the species map"
    assert len({r["current_name"] for r in species}) == len(species), "name_map_species.csv has a current name twice"
    assert not [n for n in names if len(n.split()) > 6], "a lookup name reads like a sentence"
    in_scope = [r for r in species if r["rank"] in ("species", "subspecies")]
    assert sum(int(g["n_names_now"]) for g in genera) == len(in_scope), "the genus counts do not add up to the species rows"
    assert all(int(g["n_from_lactobacillus"]) + int(g["n_described_2020_or_later"]) + int(g["n_moved_from_other_genus"]) == int(g["n_names_now"]) for g in genera)

    os.makedirs(OUT, exist_ok=True)
    for f in FILES:
        shutil.copyfile(os.path.join(base, f + ".csv"), os.path.join(OUT, f"{f}_{date}.csv"))
    info = {
        "release": date,
        "names_in_map": len(in_scope),
        "lookup_only": len(species) - len(in_scope),
        "searchable_names": len(lookup),
        "genera": len(genera),
        "what_happened": dict(Counter(r["what_happened"].split(" | ")[0].split(" (")[0] for r in in_scope)),
    }
    json.dump(info, open(os.path.join(OUT, f"names_{date}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for old in glob.glob(os.path.join(OUT, "*_20*.*")):
        if date not in os.path.basename(old):
            os.remove(old)
    print(f"wrote assets/lactobacillaceae/names/*_{date}.csv: {len(in_scope)} names, {len(species) - len(in_scope)} lookup-only, "
          f"{len(lookup)} searchable names, {len(genera)} genera")


if __name__ == "__main__":
    main()
