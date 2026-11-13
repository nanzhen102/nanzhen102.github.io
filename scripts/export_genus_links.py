#!/usr/bin/env python3
"""Copy the genus authorities and publication DOIs from the lab's release to the website.

    python3 scripts/export_genus_links.py            # the newest release folder that has a genus_list.csv
    python3 scripts/export_genus_links.py 2026-11-10

Reads <lab>/releases/<date>/genus_list.csv and writes assets/lactobacillaceae/links_genus_<date>.csv, one row per
genus: genus, authority, doi, doi_kind. The genus page links each "Proposed" entry to that DOI.

doi_kind says what the DOI is:
  publication     the paper that proposed the genus (LPSN's publication DOI)
  approved_lists  Approved Lists of Bacterial Names, 1980: the genera that have no separate publication DOI
  species_paper   the paper that described the genus's only species, for a genus with no LPSN record
                  (Candidatus Gallilactobacillus: Gilroy et al. 2021 proposed it together with its species)

Like export_species_snapshot.py it needs the lab folder, which is not in this repo, so it only runs on the author's
machine. The page generator (build_lactobacillaceae.py) reads the file it writes and stops if a genus has no link.
"""

import csv
import glob
import os
import sys

LAB = "/Users/nanzhen/Documents/1_phd_2020/5_doctoral_program/0.1_type_strain_tree/18_202611_automate/1_genus_species_acc_update/releases"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO, "assets", "lactobacillaceae")


def main():
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        folders = sorted(d for d in os.listdir(LAB) if os.path.exists(os.path.join(LAB, d, "genus_list.csv")))
        if not folders:
            sys.exit(f"no release with a genus_list.csv in {LAB}")
        date = folders[-1]
    src = os.path.join(LAB, date, "genus_list.csv")
    if not os.path.exists(src):
        sys.exit(f"{src} does not exist")
    release = {r["genus"].strip(): r for r in csv.DictReader(open(src, encoding="utf-8-sig")) if r["genus"].strip()}

    # The page's own genus CSV is the list of genera shown; the release must cover exactly those.
    genus_csv = sorted(glob.glob(os.path.join(ASSETS, "genus_*.csv")))[-1]
    site = {r["Tax name"].strip(): r for r in csv.DictReader(open(genus_csv, encoding="utf-8-sig")) if r["Tax name"].strip()}
    assert set(release) == set(site), (
        f"the release and {os.path.basename(genus_csv)} list different genera: "
        f"only in the release {sorted(set(release) - set(site))}, only in the CSV {sorted(set(site) - set(release))}"
    )

    # Candidatus Gallilactobacillus has no LPSN record: its paper is the one that described its species.
    species_csv = sorted(glob.glob(os.path.join(ASSETS, "species", "species_*.csv")))[-1]
    species_doi = {}
    for r in csv.DictReader(open(species_csv, encoding="utf-8-sig")):
        if r["kind"] in ("species", "subspecies") and r["publication_doi"].strip():
            species_doi.setdefault(r["genus"], set()).add(r["publication_doi"].strip())

    rows = []
    for genus in sorted(release, key=lambda g: int(site[g]["Y_order"]) if site[g]["Y_order"].strip() else 10**6):
        r = release[genus]
        authority = r["lpsn_authority"].strip()
        pub, listed = r["lpsn_publication_doi"].strip(), r["lpsn_ijsem_list_doi"].strip()
        if pub:
            doi, kind = pub, "publication"
        elif "Approved Lists" in authority and listed:
            doi, kind = listed, "approved_lists"
        else:
            authority = authority or site[genus]["Authority"].strip()
            dois = species_doi.get(genus, set())
            assert len(dois) == 1 and authority, (
                f"{genus}: no publication DOI in the release and no single species paper to fall back on ({sorted(dois)}). "
                "Decide where its link should point."
            )
            doi, kind = next(iter(dois)), "species_paper"
        rows.append({"genus": genus, "authority": authority, "doi": doi, "doi_kind": kind})

    out = os.path.join(ASSETS, f"links_genus_{date}.csv")
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["genus", "authority", "doi", "doi_kind"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for old in glob.glob(os.path.join(ASSETS, "links_genus_*.csv")):
        if old != out:
            os.remove(old)  # one file: the page reads the newest, and an old one would only confuse
    kinds = {k: sum(1 for r in rows if r["doi_kind"] == k) for k in ("publication", "approved_lists", "species_paper")}
    print(f"wrote {os.path.relpath(out, REPO)}: {len(rows)} genera, {kinds}")


if __name__ == "__main__":
    main()
