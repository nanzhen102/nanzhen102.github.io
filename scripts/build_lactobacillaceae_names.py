#!/usr/bin/env python3
"""Generate content/lactobacillaceae-names.md: type an old species name, get the name it has now.

    python3 scripts/build_lactobacillaceae_names.py

The page is a lookup tool, like LactoTax (https://www.lactobacillus.ualberta.ca/): one search box, and under it a
single folded list of every old name with its current name. The details of a name (type strain, genome, DOI,
fermentation type) are on the Species page, which each result links to.

Reads the name map that export_name_map.py copied into assets/lactobacillaceae/names/ (name_map_species_<date>.csv,
name_lookup_<date>.csv) and the species snapshot, which says which names have a row on the Species page. The search
is a small script over the lookup table embedded in the page; there is no server. The overview page shows the same
numbers in its third box: it calls summary() here, so the two cannot disagree.
"""

import csv
import glob
import importlib.util
import json
import os
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ASSETS = os.path.join(REPO, "assets", "lactobacillaceae")
OUT = os.path.join(REPO, "content", "lactobacillaceae-names.md")
LACTOTAX = "https://www.lactobacillus.ualberta.ca/"
ZHENG = "https://doi.org/10.1099/ijsem.0.004107"  # Zheng et al. 2020
# Old names shown as examples (the search hints here, the box on the overview). Each must be in the lookup.
EXAMPLES = ["Lactobacillus casei", "Lactobacillus reuteri", "Lactobacillus brevis"]
# One old name for each kind of change (see summary()), shown beside its count.
CHANGE_EXAMPLE = {"genus": "Lactobacillus casei", "species": "Lactobacillus cellobiosus", "same": "Lactobacillus bulgaricus",
                  "family": "Lactobacillus xylosus", "none": "Lactobacillus rogosae"}


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


genus_page = _load("genus_page", "build_lactobacillaceae.py")
species_page = _load("species_page", "build_lactobacillaceae_species.py")
esc, name_html, MONTHS = genus_page.esc, species_page.name_html, species_page.MONTHS


def read(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))


def newest(pattern):
    files = sorted(glob.glob(os.path.join(ASSETS, pattern)))
    if not files:
        sys.exit(f"no {pattern} in assets/lactobacillaceae/: run scripts/export_name_map.py")
    return files[-1]


def kind_short(k):
    """The lookup's name_kind, in one or two words for the search result."""
    if "lookup-only" in k:
        return "not in the species list"
    if "misspelling" in k:
        return "misspelling"
    if "LactoTax's spelling" in k:
        return "LactoTax spelling"
    if k.startswith("synonym"):
        return "synonym"
    if k == "current name":
        return "current name"
    return "old name"


def is_name(s):
    """False for a fragment that is not a name, like 'subsp. plantarum' (a LactoTax cell split in two)."""
    return bool(s) and s[0].isupper()


def summary():
    """Everything the page and the overview's box say, read from the name map."""
    species = read(newest("names/name_map_species_*.csv"))
    lookup = [r for r in read(newest("names/name_lookup_*.csv")) if is_name(r["name"])]
    date = re.search(r"_(\d{4}-\d{2}-\d{2})\.csv", newest("names/name_map_species_*.csv")).group(1)
    y, m, d = (int(x) for x in date.split("-"))
    snap_names = {r["name"] for r in read(newest("species/species_*.csv")) if r["kind"] in ("species", "subspecies")}

    in_scope = [r for r in species if r["rank"] in ("species", "subspecies")]
    missing = [r["current_name"] for r in in_scope if r["current_name"] not in snap_names]
    assert not missing, f"names in the name map that are not on the Species page: {missing[:5]}"
    cur_index = {r["current_name"]: i for i, r in enumerate(species)}
    assert all(r["current_name"] in cur_index for r in lookup), "a lookup name leads to a name that is not in the map"

    # The old names: every name that is not the current one and is a real former name or synonym (a misspelling or
    # LactoTax's own spelling can be searched, but is not listed as an "old name"), plus a name with no standing at all.
    def listed(r):
        if "no standing" in r["name_kind"]:
            return True
        return r["name"] != r["current_name"] and kind_short(r["name_kind"]) in ("old name", "synonym")
    old = sorted((r for r in lookup if listed(r)), key=lambda r: r["name"].lower())

    # What happened to each old name. "Renamed" can mean four things, so the pages say which:
    #   genus    a new genus, the species (or subspecies) name kept       Lactobacillus casei -> Lacticaseibacillus casei
    #   species  a new genus and a different species or subspecies name   Lactobacillus cellobiosus -> Limosilactobacillus fermentum
    #            (merged into another species, or a species became a subspecies or the reverse)
    #   same     the same genus, under another name                       Lactobacillus bulgaricus -> L. delbrueckii subsp. bulgaricus
    #   family   no longer in Lactobacillaceae                            Lactobacillus xylosus -> Lactococcus lactis
    #   none     no valid species name today                              Lactobacillus rogosae
    by_cur = {r["current_name"]: r for r in species}

    def parts(name):
        w = name.split()
        if w[0] == "Candidatus":
            w = w[1:]
        return w[0], w[-1], any(t in w for t in ("subsp.", "ssp.", "spp."))

    def stem(epithet):  # casei / casei, confusus / confusa: the ending follows the gender of the genus
        for suf in ("ensis", "ense", "us", "um", "is", "ae", "ii", "a", "e", "i"):
            if epithet.endswith(suf) and len(epithet) > len(suf) + 2:
                return epithet[:-len(suf)]
        return epithet

    def change(r):
        cur = by_cur[r["current_name"]]
        if "no standing" in r["name_kind"] or " sp. (" in r["current_name"]:
            return "none"
        if cur["rank"] not in ("species", "subspecies"):
            return "family"
        (g1, e1, sub1), (g2, e2, sub2) = parts(r["name"]), parts(r["current_name"])
        if g1 == g2:
            return "same"
        return "genus" if stem(e1) == stem(e2) and sub1 == sub2 else "species"

    kinds = {r["name"]: change(r) for r in old}
    counts = {k: sum(1 for v in kinds.values() if v == k) for k in ("genus", "species", "same", "family", "none")}
    assert sum(counts.values()) == len(old)
    by_name = {r["name"]: r["current_name"] for r in lookup}
    for e in EXAMPLES:
        assert kinds.get(e) == "genus", f"the example {e} is not an old name that only changed genus"
    for k, e in CHANGE_EXAMPLE.items():
        assert kinds.get(e) == k, f"the example for '{k}', {e}, is now '{kinds.get(e)}'"
    return dict(species=species, lookup=lookup, in_scope=in_scope, snap_names=snap_names, cur_index=cur_index, old=old,
                date=date, asof=f"{MONTHS[m - 1]} {d}, {y}", n_old=len(old), kinds=kinds, counts=counts,
                n_lactobacillus=sum(1 for r in old if r["name"].startswith("Lactobacillus ")),
                n_stayed=sum(1 for r in in_scope if r["what_happened"].split(" | ")[0] == "stayed in Lactobacillus"),
                examples=[(e, by_name[e]) for e in EXAMPLES],
                change_examples={k: (e, by_name[e] if k != "none" else "") for k, e in CHANGE_EXAMPLE.items()})


# What each kind of change is called on the pages, in the order they are listed.
CHANGE_LABEL = [
    ("genus", "got a new genus name; the species name stayed"),
    ("species", "got a new genus name and a different species or subspecies name"),
    ("same", "stayed in the same genus under another name"),
    ("family", "are no longer in <em>Lactobacillaceae</em>"),
    ("none", "have no valid name today"),
]


def main():
    s = summary()
    species, lookup = s["species"], s["lookup"]

    def anchor(current):
        """The row of a current name on the Species page, or '' if it has none (a name outside the family)."""
        return species_page.anchor(current) if current in s["snap_names"] else ""

    def now_cell(current):
        a = anchor(current)
        return f'<a href="lactobacillaceae-species#{a}">{name_html(current)}</a>' if a else name_html(current)

    def now(r):
        if r["name"] == r["current_name"]:  # no standing: there is no name to point to
            return '<span class="lacto-na">no valid name</span>'
        return now_cell(r["current_name"])

    rows = "\n".join(f'<tr><td>{name_html(r["name"])}</td><td>{now(r)}</td></tr>' for r in s["old"])
    c = s["counts"]

    # ---- the search data: every searchable name -> its current name ---------------------------------------------------
    cur = [[r["current_name"], r["what_happened"].split(" | ")[0], anchor(r["current_name"])] for r in species]
    data = {"cur": cur, "names": [[r["name"], s["cur_index"][r["current_name"]], kind_short(r["name_kind"])] for r in lookup]}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    # A blank line ends an HTML block in markdown, so the script goes in without blank lines (it has no multi-line strings).
    script = "\n".join(l for l in open(os.path.join(HERE, "names_search.js"), encoding="utf-8").read().splitlines() if l.strip())
    assert "</script" not in script, "the script would end its own tag"

    tries = " ".join(f'<button type="button" data-name-q="{esc(old)}">{esc(old)}</button>' for old, _ in s["examples"])
    md = f"""---
title: "Lactobacillaceae: old and new names"
date: {s['date']}
unlisted: true
---

{genus_page.tabs("names")}

<p class="lacto-hero lacto-hero-text">Old name <span aria-hidden="true">→</span><span class="lacto-sr"> to </span> new name</p>
<p class="lacto-hero-label">Find the name a <em>Lactobacillus</em> species has now, updated on {s['asof']}.</p>

<div class="lacto-find">
<label for="name-search" class="lacto-find-label">Enter a species name</label>
<input id="name-search" class="lacto-find-input" type="search" placeholder="e.g. Lactobacillus casei" autocomplete="off" autocapitalize="off" spellcheck="false" />
<div id="name-results" class="lacto-find-results" aria-live="polite"><p class="lacto-find-hint">Try {tries}</p></div>
</div>
<p class="lacto-find-hint">Want the paper, the type-strain genome or why a name was excluded? <a href="lactobacillaceae#ask" data-router-ignore data-lr-open>Ask LactoRador</a></p>
<script type="application/json" id="name-data">{blob}</script>
<script>{script}</script>

In 2020 the genus _Lactobacillus_ was split ([Zheng et al. 2020]({ZHENG})). Of the {s['n_old']} old names here, {c['genus']} got a new genus name and kept the species name, {c['species']} also got a different species or subspecies name, {c['same']} stayed in the same genus under another name, {c['family']} are no longer in _Lactobacillaceae_, and {c['none']} have no valid name today. Old names come from [LPSN](https://lpsn.dsmz.de/) and [LactoTax]({LACTOTAX}).

<details class="lacto-all">
<summary>All {s['n_old']} old names, A to Z</summary>
<table class="lacto-table lacto-oldnew"><thead><tr><th scope="col">Old name</th><th scope="col">Name now</th></tr></thead><tbody>
{rows}
</tbody></table>
</details>

[🐝](#top)
"""
    # ---- the page must say what the data says ------------------------------------------------------------------
    assert md.count("<tr><td>") == s["n_old"], "the list and its count disagree"
    assert len({x[0].lower() for x in data["names"]}) == len(lookup), "search names are not unique ignoring case"
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {OUT}")
    print(f"  {s['n_old']} old names listed ({s['counts']}), {len(lookup)} names searchable; name map {s['date']}; "
          f"page text {len(md) // 1024} KB")


if __name__ == "__main__":
    main()
