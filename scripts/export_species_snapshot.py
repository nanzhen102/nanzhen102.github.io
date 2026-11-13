#!/usr/bin/env python3
"""Reduce the lab's species release to the public columns the website uses.

    python3 scripts/export_species_snapshot.py            # the newest release folder
    python3 scripts/export_species_snapshot.py 2026-11-11

Reads <lab>/releases/<date>/ (species_list.csv, species_ledger.csv, species_crosswalk.csv, checks/) and writes
    assets/lactobacillaceae/species/species_<date>.csv     one row per name, public columns only
    assets/lactobacillaceae/species/release_<date>.json    release date, counts, audit result, manifest hash

The release has about 60 columns; most are working notes (to_do, chk_*, flags, your_row, ...) and stay out.
Fermentation type and lifestyle live only in the ledger, so they are joined on the name here.

It needs the lab folder, which is NOT in this repo, so it only runs on the author's machine. The page generator
(build_lactobacillaceae_species.py) reads the snapshot it writes.
"""

import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter

LAB = "/Users/nanzhen/Documents/1_phd_2020/5_doctoral_program/0.1_type_strain_tree/18_202611_automate/1_genus_species_acc_update/releases"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "assets", "lactobacillaceae", "species")

# Two rows take their LPSN fields (record, status, authority, DOI) from the SUPERSEDED record of the old name, so
# they read "synonym" and cite the reclassification paper. Their final names are right (confirmed 2026-11-12), and
# these are the values on the CURRENT LPSN records, read from lpsn.dsmz.de on 2026-11-12. Remove an entry once the
# release itself carries the current record: the guard below says so.
OVERRIDES = {
    "Leuconostoc gasicomitatum": dict(
        lpsn_id="777545",  # was 791679, the synonym Leuconostoc gelidum subsp. gasicomitatum
        authority="Björkroth et al. 2001",
        publication_doi="10.1128/aem.66.9.3764-3772.2000",  # the effective publication (AEM 2000)
    ),
    "Lentilactobacillus rapi subsp. dabitei": dict(
        lpsn_id="28390",  # was 41192, the synonym Lentilactobacillus dabitei
        authority="Li et al. 2022",
        publication_doi="10.1099/ijsem.0.005359",
    ),
}

# The same two renamed rows also keep the RANK of their old names: Leuconostoc gasicomitatum says "subspecies"
# (its old name was a subspecies) and Lentilactobacillus rapi subsp. dabitei says "species". A name's rank is
# in the name, so the rank here is read from the name; this guard stops the build if any other row disagrees
# with its own name.
RANK_DISAGREES = {"Leuconostoc gasicomitatum", "Lentilactobacillus rapi subsp. dabitei"}

# What the release's genome tiers mean, in one short public phrase each. The tier names are the release's own.
GENOME_NOTE = {
    "strain_in_lpsn": "",
    "only_genome_not_type_strain": "not_type_strain",
    "not_type_strain": "not_type_strain",
    "ncbi_reference_not_type_strain": "not_type_strain",
    "equivalence": "ncbi_type_material",
    "ncbi_type_material": "ncbi_type_material",
    "": "no_genome",
}

COLUMNS = [
    "kind", "name", "genus", "genus_y_order", "parent", "status", "status_text", "authority", "publication_doi",
    "lpsn_id", "lpsn_url", "ncbi_taxid", "ncbi_url", "type_strains", "genome_acc", "genome_url", "genome_strain",
    "genome_size_bp", "genome_gc", "genome_level", "genome_note", "fermentation", "lifestyle", "change", "note",
]


def read(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))


def status_of(text):
    t = text.lower()
    if t.startswith("not validly published"):
        return "not_valid"
    if "illegitimate" in t:
        return "illegitimate"
    if "synonym of its species" in t:
        return "subspecies_abandoned"
    return "valid"


def main():
    releases = sorted(d for d in os.listdir(LAB) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d))
    date = sys.argv[1] if len(sys.argv) > 1 else releases[-1]
    base = os.path.join(LAB, date)
    species = read(os.path.join(base, "species_list.csv"))
    ledger_all = read(os.path.join(base, "species_ledger.csv"))
    crosswalk = read(os.path.join(base, "species_crosswalk.csv"))
    manifest_path = os.path.join(base, "checks", "species_manifest.json")
    manifest = json.load(open(manifest_path, encoding="utf-8"))

    # The audit must be clean before anything is published.
    summary = open(os.path.join(base, "checks", "audit_summary.txt"), encoding="utf-8").read().strip()
    assert "per-row checks failing: none" in summary and "release checks failing: none" in summary, (
        f"the release's own audit is not clean, so nothing is exported:\n{summary}"
    )

    ledger = {}
    for r in ledger_all:
        if r["include"] == "yes":
            assert r["final_name"] not in ledger, f"two included ledger rows for {r['final_name']}"
            ledger[r["final_name"]] = r
    names = [r["final_name"] for r in species]
    assert len(set(names)) == len(names), "duplicate final names in species_list.csv"
    missing = [n for n in names if n not in ledger]
    assert not missing, f"names in species_list.csv but not in the ledger: {missing[:5]}"

    # Guard: a row's LPSN record must be the record of its own name.
    ids_of = {}
    for c in crosswalk:
        ids_of.setdefault(c["name"], set()).add(c["lpsn_id"])
    wrong = [r["final_name"] for r in species if r["lpsn_id"] not in ids_of.get(r["final_name"], {r["lpsn_id"]})]
    stale = sorted(set(OVERRIDES) - set(wrong))
    assert not stale, f"the release is fixed for {stale}: remove them from OVERRIDES in this script"
    unexpected = sorted(set(wrong) - set(OVERRIDES))
    assert not unexpected, (
        f"these rows take their LPSN fields from a record that is not their own name's: {unexpected}. "
        "Fix the release, or add the verified current-record values to OVERRIDES."
    )

    def kind_of(name):
        return "subspecies" if " subsp. " in name else "species"

    disagree = {r["final_name"] for r in species if r["rank"] != kind_of(r["final_name"])}
    assert disagree == RANK_DISAGREES, (
        f"rows whose rank column disagrees with their own name: {sorted(disagree)}; expected {sorted(RANK_DISAGREES)}. "
        "Fix the release, or update RANK_DISAGREES after checking each one."
    )

    rows = []
    for r in species:
        L = ledger[r["final_name"]]
        o = OVERRIDES.get(r["final_name"], {})
        lpsn_id = o.get("lpsn_id", r["lpsn_id"])
        status_text = "validly published under the ICNP; correct name" if o else r["lpsn_status_web"]
        kind = kind_of(r["final_name"])
        parent = r["final_name"].split(" subsp. ")[0] if kind == "subspecies" else ""
        cls = r["class"]
        rows.append({
            "kind": kind, "name": r["final_name"], "genus": r["genus"],
            "genus_y_order": int(float(r["genus_y_order"])) if r["genus_y_order"] else "", "parent": parent,  # blank = genus not placed on the tree
            "status": status_of(status_text), "status_text": status_text,
            "authority": o.get("authority", r["lpsn_authority"]),
            "publication_doi": o.get("publication_doi", r["lpsn_publication_doi"]),
            "lpsn_id": lpsn_id, "lpsn_url": f"https://doi.org/10.83108/rn.{lpsn_id}",
            "ncbi_taxid": r["ncbi_taxid"], "ncbi_url": r["ncbi_taxonomy_url"],
            "type_strains": r["type_strains_all"], "genome_acc": r["acc"], "genome_url": r["ncbi_genome_url"],
            "genome_strain": r["acc_strain"], "genome_size_bp": r["acc_size_bp"], "genome_gc": r["acc_gc"],
            "genome_level": r["acc_level"], "genome_note": GENOME_NOTE[r["acc_tier"] if r["acc"] else ""],
            "fermentation": L["fermentation_type"], "lifestyle": L["lifestyle"],
            "change": {"NEW": "new", "NOT_VALID_NEW": "new", "RENAMED": "renamed"}.get(cls, "carried"), "note": "",
        })

    # A species that has subspecies is a heading for them. Nine of those species are not rows of the list (only
    # their subspecies are), so their heading comes from the ledger, which has their authority and DOI.
    have = {r["name"] for r in rows}
    for p in sorted({r["parent"] for r in rows if r["parent"]} - have):
        cand = [x for x in ledger_all if x["final_name"] == p and x["lpsn_authority"] and x["lpsn_publication_doi"]]
        assert cand, f"no ledger record with an authority and DOI for the parent species {p}"
        L = cand[0]
        rows.append({
            "kind": "parent", "name": p, "genus": L["genus"], "genus_y_order": next(r["genus_y_order"] for r in rows if r["genus"] == L["genus"]),
            "parent": "", "status": status_of(L["lpsn_status_web"]), "status_text": L["lpsn_status_web"],
            "authority": L["lpsn_authority"], "publication_doi": L["lpsn_publication_doi"], "lpsn_id": L["lpsn_id"],
            "lpsn_url": f"https://doi.org/10.83108/rn.{L['lpsn_id']}", "ncbi_taxid": L["ncbi_taxid"],
            "ncbi_url": L["ncbi_taxonomy_url"], "type_strains": "", "genome_acc": "", "genome_url": "", "genome_strain": "",
            "genome_size_bp": "", "genome_gc": "", "genome_level": "", "genome_note": "", "fermentation": "",
            "lifestyle": "", "change": "carried", "note": "",
        })

    # A genus of the release with no listed name still gets a place on the page, with the reason. The reason is the
    # release's own rule text: the names it left out and why.
    genus_list = read(os.path.join(os.path.dirname(LAB), manifest["sources"]["genus_release"], "genus_list.csv"))
    yo = {g["genus"].strip(): g["y_order"].strip() for g in genus_list}
    for g in sorted(set(yo) - {r["genus"] for r in rows}):
        left = [x for x in ledger_all if x["genus"] == g and x["rank"] in ("species", "subspecies")]
        assert left, f"{g} has no listed name and nothing in the ledger says why: add the reason to the release"
        for L in left:
            m = re.match(r"R\d+: left out - .+? \((.+)\); your decision [\d-]+: (.+)$", L["rule_decision"])
            note = (f"{m.group(2)}: their {m.group(1).replace('type = ', 'type is ')}" if m
                    else re.sub(r"^R\d+: left out - ", "", L["rule_decision"]))
            assert note, f"{L['final_name']} is left out but the ledger gives no rule text"
            rows.append({
                "kind": "left_out", "name": L["final_name"], "genus": g, "genus_y_order": int(yo[g]) if yo[g] else "",
                "parent": "", "status": status_of(L["lpsn_status_web"]), "status_text": L["lpsn_status_web"],
                "authority": L["lpsn_authority"], "publication_doi": L["lpsn_publication_doi"], "lpsn_id": L["lpsn_id"],
                "lpsn_url": f"https://doi.org/10.83108/rn.{L['lpsn_id']}", "ncbi_taxid": L["ncbi_taxid"],
                "ncbi_url": L["ncbi_taxonomy_url"], "type_strains": "", "genome_acc": "", "genome_url": "", "genome_strain": "",
                "genome_size_bp": "", "genome_gc": "", "genome_level": "", "genome_note": "", "fermentation": "",
                "lifestyle": "", "change": "carried", "note": note,
            })

    rows.sort(key=lambda r: (r["genus_y_order"] if r["genus_y_order"] != "" else 10**6, r["genus"], r["name"].split(" subsp. ")[0], r["kind"] == "subspecies", r["name"]))
    os.makedirs(OUT, exist_ok=True)
    csv_path = os.path.join(OUT, f"species_{date}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    kinds = Counter(r["kind"] for r in rows)
    info = {
        "release": date,
        "built": manifest["built"],
        "audit": summary,
        "manifest_sha256_16": hashlib.sha256(open(manifest_path, "rb").read()).hexdigest()[:16],
        "sources": manifest["sources"],
        "counts": {"rows": len(rows), **dict(kinds), "genera": len({r["genus"] for r in rows})},
        "status": dict(Counter(r["status"] for r in rows)),
    }
    json.dump(info, open(os.path.join(OUT, f"release_{date}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"release {date}: {len(rows)} rows {dict(kinds)} in {info['counts']['genera']} genera")
    print(f"  status: {info['status']}")
    print(f"  overrides applied: {sorted(OVERRIDES)}")
    print(f"wrote {os.path.relpath(csv_path, REPO)} ({os.path.getsize(csv_path) // 1024} KB)")


if __name__ == "__main__":
    main()
