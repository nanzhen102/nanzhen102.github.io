#!/usr/bin/env python3
"""Generate content/lactobacillaceae.md, the overview at /lactobacillaceae.

    python3 scripts/build_lactobacillaceae_hub.py

The overview is the front door to the two detail pages. It holds the animation, then the two headline numbers:
the genera (from the genus CSV) and the species and subspecies (from the species snapshot), each in a card with its own
date, a fermentation split, and a link to its page. Everything else lives on /lactobacillaceae-genera and
/lactobacillaceae-species.

It also writes one short note per release to content/lactobacillaceae-release-<date>.md (flat files: a folder would get an auto-generated index page, dated at every build, that the feed would announce each time). The site's RSS feed carries
each note as its own item, so a release reaches subscribers (the overview page itself keeps one address and would not
be announced again). From the second release on, the note lists the genera and names added or removed since the
previous genus CSV and species snapshot.

Run it after build_lactobacillaceae.py and build_lactobacillaceae_species.py (build_lactobacillaceae_all.py does
all three in order): it reads their output to check that the numbers it shows are the numbers on those pages.
"""

import csv
import glob
import importlib.util
import os
import re
import sys
from collections import Counter

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ASSETS = os.path.join(REPO, "assets", "lactobacillaceae")
CONTENT = os.path.join(REPO, "content")
OUT = os.path.join(CONTENT, "lactobacillaceae.md")

spec = importlib.util.spec_from_file_location("genus_page", os.path.join(HERE, "build_lactobacillaceae.py"))
genus_page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(genus_page)
esc, segmented_bar = genus_page.esc, genus_page.segmented_bar

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def hero_of(path):
    """The headline number a generated page shows."""
    if not os.path.exists(path):
        sys.exit(f"{os.path.relpath(path, REPO)} does not exist: run build_lactobacillaceae_all.py")
    m = re.search(r'<p class="lacto-hero">(\d+)</p>', open(path, encoding="utf-8").read())
    assert m, f"no headline number in {os.path.relpath(path, REPO)}"
    return int(m.group(1))


def _list(names, cap=40):
    """'_A b_, _C d_ and 7 more' (italic, sorted, capped so a big release stays readable)."""
    names = sorted(names)
    shown = ", ".join(f"_{esc(n)}_" for n in names[:cap])
    return shown + (f" and {len(names) - cap} more" if len(names) > cap else "")


def write_release_note(iso, genus_asof, species_asof, n_genera, n_species, n_sub, genus_names, species_names, prev):
    """One note per release, dated like the overview page. `prev` is (previous genus names, previous species names)
    or None for the first release published on the site."""
    n_names = n_species + n_sub
    if prev is None:
        change = "Later releases list the genera, species and subspecies added or removed."
        short = "First release on this site."
    else:
        pg, ps = prev
        parts, bits = [], []
        for label, now, before in (("genera", genus_names, pg), ("species and subspecies", species_names, ps)):
            add, gone = now - before, before - now
            if add:
                parts.append(f"- Added {label} ({len(add)}): {_list(add)}")
            if gone:
                parts.append(f"- Removed {label} ({len(gone)}): {_list(gone)}")
            if add or gone:
                unit = label if label != "genera" else ("genus" if len(add) == 1 and len(gone) <= 1 else "genera")
                bits.append(f"{len(add)} {unit} added, {len(gone)} removed")
        if parts:
            change = "Since the previous release (a renamed species shows once as removed and once as added):\n\n" + "\n".join(parts)
            short = "; ".join(bits).capitalize() + "."
        else:
            change = "No genera, species or subspecies were added or removed since the previous release."
            short = "No names added or removed."
    note = f"""---
title: Lactobacillaceae release {iso}
date: {iso}
---

{n_genera} genera and {n_names} species and subspecies are currently placed in the family _Lactobacillaceae_. {short}

Genus list of {genus_asof}; species release of {species_asof} ({n_species} species, {n_sub} subspecies).

{change}

See the [overview](lactobacillaceae), the [genera](lactobacillaceae-genera) and the [species](lactobacillaceae-species).
"""
    path = os.path.join(CONTENT, f"lactobacillaceae-release-{iso}.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(note)
    return path


def main():
    # ---- genera ------------------------------------------------------------------------------------------------
    genus_csv = sorted(glob.glob(os.path.join(ASSETS, "genus_*.csv")))[-1]
    stamp = re.search(r"genus_(\d{4})(\d{2})(\d{2})", os.path.basename(genus_csv))
    assert stamp, "the animation is named after the CSV's datestamp: rename the CSV to genus_YYYYMMDD.csv"
    gy, gm, gd = (int(x) for x in stamp.groups())
    genus_asof = f"{MONTHS[gm - 1]} {gd}, {gy}"
    recs = genus_page.load(genus_csv)
    n_genera = len(recs)
    genus_ferm = Counter(r["ferm"] for r in recs)

    # The animation is rendered by scripts/make_life_tree.py and named after the CSV, so a new CSV cannot ship with
    # the previous release's animation: the build stops until it has been re-rendered.
    tree_name = f"lactobacillaceae-banner-{stamp.group(1)}{stamp.group(2)}{stamp.group(3)}"
    for ext in ("gif", "png"):
        assert os.path.exists(os.path.join(CONTENT, f"{tree_name}.{ext}")), (
            f"content/{tree_name}.{ext} is missing: run scripts/make_life_tree.py to render the animation for this CSV"
        )
    tree_alt = (
        f"Animation: the {n_genera} genera of Lactobacillaceae appear in the order they were described, "
        "each at its place on the family's phylogenetic tree. Beside it: Lactobacillaceae: type strains, fermentation type and lifestyle, "
        "updated by Nanzhen Qiao and Michael Gänzle."
    )

    # ---- species and subspecies --------------------------------------------------------------------------------
    snaps = sorted(glob.glob(os.path.join(ASSETS, "species", "species_*.csv")))
    if not snaps:
        sys.exit("no assets/lactobacillaceae/species/species_<date>.csv: run scripts/export_species_snapshot.py")
    release = re.search(r"species_(\d{4}-\d{2}-\d{2})\.csv", snaps[-1]).group(1)
    sy, sm, sd = (int(x) for x in release.split("-"))
    species_asof = f"{MONTHS[sm - 1]} {sd}, {sy}"
    listed = [r for r in csv.DictReader(open(snaps[-1], encoding="utf-8-sig")) if r["kind"] in ("species", "subspecies")]
    n_species = sum(1 for r in listed if r["kind"] == "species")
    n_sub = sum(1 for r in listed if r["kind"] == "subspecies")
    n_names = n_species + n_sub
    # A name with no fermentation type is not "unassigned": it has not been looked at yet.
    species_ferm = Counter({"Homo": 0, "Hetero": 0, "Unassigned": 0})
    for r in listed:
        species_ferm[r["fermentation"] if r["fermentation"] in ("Homo", "Hetero") else "Unassigned"] += 1

    # ---- the release note (the feed item) ------------------------------------------------------------------------
    genus_csvs = sorted(glob.glob(os.path.join(ASSETS, "genus_*.csv")))
    prev = None
    if len(genus_csvs) > 1 and len(snaps) > 1:
        prev_species = {r["name"] for r in csv.DictReader(open(snaps[-2], encoding="utf-8-sig")) if r["kind"] in ("species", "subspecies")}
        prev = ({r["name"] for r in genus_page.load(genus_csvs[-2])}, prev_species)

    # ---- the overview must say what the pages it points to say --------------------------------------------------
    assert hero_of(os.path.join(CONTENT, "lactobacillaceae-genera.md")) == n_genera, "the genera page and the overview disagree on the number of genera"
    assert hero_of(os.path.join(CONTENT, "lactobacillaceae-species.md")) == n_names, "the species page and the overview disagree on the number of names"
    assert sum(species_ferm.values()) == n_names and sum(genus_ferm.values()) == n_genera, "a fermentation split does not add up"

    iso = max(f"{gy}-{gm:02d}-{gd:02d}", release)  # the page is as new as its newest part
    md = f"""---
title: Lactobacillaceae
date: {iso}
---

<div class="lacto-tree"><picture><source media="(prefers-reduced-motion: reduce)" srcset="{tree_name}.png"><img src="{tree_name}.gif" width="960" height="440" alt="{esc(tree_alt)}" decoding="async"></picture></div>

<div class="lacto-card">
<p class="lacto-hero">{n_genera}</p>
<p class="lacto-hero-label">genera currently placed in <em>Lactobacillaceae</em> family, updated on {genus_asof}.</p>
{segmented_bar(genus_ferm, n_genera)}
<div class="lacto-card-foot">
<p class="lacto-more"><a href="lactobacillaceae-genera">All {n_genera} genera</a> with type species, fermentation type, the year each was proposed, and their order on the tree.</p>
<span class="lacto-card-go" aria-hidden="true">👉</span>
</div>
</div>

<div class="lacto-card">
<p class="lacto-hero">{n_names}</p>
<p class="lacto-hero-label">species and subspecies currently placed in <em>Lactobacillaceae</em> family ({n_species} species, {n_sub} subspecies), updated on {species_asof}.</p>
{segmented_bar(species_ferm, n_names, noun="species and subspecies", unassigned="Not yet assessed")}
<div class="lacto-card-foot">
<p class="lacto-more"><a href="lactobacillaceae-species">All {n_names} species and subspecies</a> with type strains, genomes, publication DOIs, fermentation type and lifestyle.</p>
<span class="lacto-card-go" aria-hidden="true">👉</span>
</div>
</div>

For detailed homofermentative and heterofermentative fermentation, check [Gänzle 2015](https://doi.org/10.1016/j.cofs.2015.03.001) and [Qiao & Gänzle 2026](https://doi.org/10.1016/j.fm.2025.104945). For detailed lifestyle updates, check [Duar et al. 2017](https://doi.org/10.1093/femsre/fux030), [Nanzhen Qiao](https://www.linkedin.com/in/nanzhen/) and [Michael Gänzle](https://scholar.google.com/citations?user=Zc29kvEAAAAJ&hl=en). To check how a former species name maps to its current one, use [LactoTax](https://www.lactobacillus.ualberta.ca/) and [Zheng et al. 2020](https://doi.org/10.1099/ijsem.0.004107).
"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(md.rstrip("\n") + "\n")
    note_path = write_release_note(iso, genus_asof, species_asof, n_genera, n_species, n_sub, {r["name"] for r in recs},
                                   {r["name"] for r in listed}, prev)
    print(f"wrote {OUT}")
    print(f"wrote {note_path}")
    print(f"  {n_genera} genera (CSV {gy}-{gm:02d}-{gd:02d}) and {n_names} species and subspecies (release {release})")


if __name__ == "__main__":
    main()
