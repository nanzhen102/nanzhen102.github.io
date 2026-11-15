#!/usr/bin/env python3
"""Write the website's genus CSV from the lab's genus release.

    python3 scripts/export_genus_csv.py            # the newest release folder that has a genus_list.csv
    python3 scripts/export_genus_csv.py 2026-11-10

Reads <lab>/releases/<date>/genus_list.csv and writes assets/lactobacillaceae/genus_<YYYYMMDD>.csv in the layout
the page generators read (Tax name, Authority, Fermentation_type, Type_species, Y_order, ...). The datestamp in the
file name is the release date: it is the "updated on" date of the Overview and Genera pages and names the banner
animation. Older genus_*.csv files are removed, because the generators read the newest one.

Column mapping:   Taxid <- ncbi_taxid          Tax name <- genus             Authority <- authority
                  Fermentation_type <- fermentation_type                     Type_species <- type_species
                  Y_order <- y_order           Source <- change              Note <- note
                  Rank is GENUS; "Scientific name is formal" is FALSE for a Candidatus name, TRUE otherwise.

Like the other export scripts it needs the lab folder, which is not in this repo, so it only runs on the author's machine.
"""

import csv
import glob
import os
import re
import sys

LAB = "/Users/nanzhen/Documents/1_phd_2020/5_doctoral_program/0.1_type_strain_tree/18_202611_automate/1_genus_species_acc_update/releases"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO, "assets", "lactobacillaceae")

COLUMNS = [
    "Taxid", "Tax name", "Authority", "Rank", "Scientific name is formal", "Fermentation_type", "Type_species",
    "In_tree", "Y_order", "Source", "Note",
]


def main():
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        folders = sorted(d for d in os.listdir(LAB) if os.path.exists(os.path.join(LAB, d, "genus_list.csv")))
        if not folders:
            sys.exit(f"no release with a genus_list.csv in {LAB}")
        date = folders[-1]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", date), f"{date!r} is not a release date (YYYY-MM-DD)"
    src = os.path.join(LAB, date, "genus_list.csv")
    if not os.path.exists(src):
        sys.exit(f"{src} does not exist")

    summary = open(os.path.join(LAB, date, "checks", "genus_audit_summary.txt"), encoding="utf-8").read().strip()
    assert "release checks failing: none" in summary and "per-row checks failing: 0" in summary, (
        f"the genus release's own audit is not clean, so nothing is exported:\n{summary}"
    )

    release = [r for r in csv.DictReader(open(src, encoding="utf-8-sig")) if r["genus"].strip()]
    names = [r["genus"].strip() for r in release]
    assert len(set(names)) == len(names), "duplicate genera in genus_list.csv"

    rows = []
    for r in release:
        g = r["genus"].strip()
        authority = r["authority"].strip()
        type_species = r["type_species"].strip()
        assert authority, f"{g} has no authority in the release"
        assert type_species, f"{g} has no type species in the release"
        rows.append({
            "Taxid": r["ncbi_taxid"].strip(), "Tax name": g, "Authority": authority, "Rank": "GENUS",
            "Scientific name is formal": "FALSE" if g.startswith("Candidatus ") else "TRUE",
            "Fermentation_type": r["fermentation_type"].strip(), "Type_species": type_species, "In_tree": "yes",
            "Y_order": r["y_order"].strip(), "Source": r["change"].strip(), "Note": r["note"].strip(),
        })
    rows.sort(key=lambda r: int(r["Y_order"]) if r["Y_order"] else 10**6)

    out = os.path.join(ASSETS, f"genus_{date.replace('-', '')}.csv")
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for old in glob.glob(os.path.join(ASSETS, "genus_*.csv")):
        if old != out:
            os.remove(old)
    placed = sum(1 for r in rows if r["Y_order"])
    unset = sum(1 for r in rows if not r["Fermentation_type"])
    print(f"wrote {os.path.relpath(out, REPO)}: {len(rows)} genera, {placed} placed on the tree, "
          f"{unset} without a fermentation type")


if __name__ == "__main__":
    main()
