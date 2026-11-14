#!/usr/bin/env python3
"""Generate content/lactobacillaceae-species.md from the species snapshot.

    python3 scripts/build_lactobacillaceae_species.py

The page lists every current name in Lactobacillaceae: family, then genus in the tree order of the genus page,
then species, with subspecies nested under their species. For each name: authority, LPSN status, type strains,
genome, DOI, and the fermentation type and lifestyle curated by the author and Michael Gänzle.

The page is "unlisted" (front matter): its ~100 KB of table text would otherwise be added to the site-wide search
index, which every page of the site downloads. It is still served, and linked from the genus page.

Reads assets/lactobacillaceae/species/species_<release>.csv (written by export_species_snapshot.py from the lab's
release) and the newest genus_*.csv, which gives the genus order and fermentation type. Like the genus page, every
number is derived, and the build stops if the pieces disagree.
"""

import csv
import datetime
import glob
import importlib.util
import json
import os
import re
import sys
from collections import Counter

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ASSETS = os.path.join(REPO, "assets", "lactobacillaceae")
OUT = os.path.join(REPO, "content", "lactobacillaceae-species.md")

spec = importlib.util.spec_from_file_location("genus_page", os.path.join(HERE, "build_lactobacillaceae.py"))
genus_page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(genus_page)
esc, _authority = genus_page.esc, genus_page._authority

LIFESTYLE_DOI = "10.1093/femsre/fux030"  # Duar et al. 2017, the lifestyle categories
LINKEDIN = "https://www.linkedin.com/in/nanzhen/"  # Nanzhen Qiao
GANZLE_SCHOLAR = "https://scholar.google.com/citations?user=Zc29kvEAAAAJ&hl=en"  # Michael Gänzle, University of Alberta
NOT_ASSESSED = '<span class="lacto-na">not yet assessed</span>'
GENOME_NOTE = {
    "not_type_strain": "genome strain {s} is not a type strain",
    "ncbi_type_material": "genome strain {s} is NCBI type material; LPSN lists other deposits",
    "no_genome": "no genome available",
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def read(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))


def name_html(name):
    if " subsp. " in name:
        left, epithet = name.split(" subsp. ")
        return f"<em>{esc(left)}</em> subsp. <em>{esc(epithet)}</em>"
    return f"<em>{esc(name)}</em>"


def link(href, text):
    return f'<a href="{esc(href)}">{text}</a>'


def chips(r):
    out = []
    if r["change"] == "new":
        out.append('<span class="lacto-chip">new</span>')
    if r["status"] == "not_valid":
        out.append('<span class="lacto-chip lacto-chip-warn">not validly published</span>')
    elif r["status"] == "illegitimate":
        out.append('<span class="lacto-chip lacto-chip-warn">illegitimate name, replacement needed</span>')
    elif r["status"] == "subspecies_abandoned":
        out.append('<span class="lacto-chip lacto-chip-warn">subspecies division abandoned</span>')
    return " ".join(out)


def traits(r):
    f = r["fermentation"]
    ferm = (f'<span class="lacto-dot lacto-{f.lower()}"></span>{esc(f)}' if f in ("Homo", "Hetero") else NOT_ASSESSED)
    life = esc(r["lifestyle"]) if r["lifestyle"] else NOT_ASSESSED
    return f'<span class="lacto-ferm">{ferm}</span><span class="lacto-auth-note">{life}</span>'


def genome(r):
    if not r["genome_acc"]:
        return f'<span class="lacto-note">{GENOME_NOTE["no_genome"]}</span>'
    facts = [f"{int(r['genome_size_bp']) / 1e6:.1f} Mb", f"GC {float(r['genome_gc']):.1f}%", r["genome_level"]]
    note = GENOME_NOTE.get(r["genome_note"], "").format(s=esc(r["genome_strain"]))
    return (link(r["genome_url"], esc(r["genome_acc"])) + f'<span class="lacto-auth-note">{esc(" · ".join(facts))}</span>'
            + (f'<span class="lacto-note">{note}</span>' if note else ""))


def links(r):
    parts = [link(f"https://doi.org/{r['publication_doi']}", "DOI"), link(r["lpsn_url"], "LPSN")]
    if r["ncbi_url"]:
        parts.append(link(r["ncbi_url"], "NCBI"))
    return "&nbsp;·&nbsp;".join(parts)  # non-breaking: the three links stay on one line


def left_out_item(r):
    """One name the release leaves out, for the note in a genus that has no listed name."""
    status = "not validly published" if r["status"] == "not_valid" else esc(r["status_text"])
    doi = link("https://doi.org/" + r["publication_doi"], "DOI")
    return f"{name_html(r['name'])} ({esc(r['authority'])}), {status} ({doi}&nbsp;·&nbsp;{link(r['lpsn_url'], 'LPSN')})"


def row(r):
    name_cell = f'<td class="lacto-name">{name_html(r["name"])} {chips(r)}<span class="lacto-auth-note">{_authority(r["authority"])}</span></td>'
    if r["kind"] == "parent":
        cls = "lacto-parent"
        middle = '<td colspan="3" class="lacto-na">subspecies below</td>'
    else:
        cls = "lacto-subrow" if r["kind"] == "subspecies" else "lacto-sp"
        middle = (f'<td class="lacto-traits">{traits(r)}</td><td class="lacto-ts">{esc(r["type_strains"])}</td>'
                  f'<td class="lacto-genome">{genome(r)}</td>')
    return f'<tr class="{cls}">{name_cell}{middle}<td class="lacto-links">{links(r)}</td></tr>'


def main():
    snaps = sorted(glob.glob(os.path.join(ASSETS, "species", "species_*.csv")))
    if not snaps:
        sys.exit("no assets/lactobacillaceae/species/species_<date>.csv: run scripts/export_species_snapshot.py")
    snap = snaps[-1]
    release = re.search(r"species_(\d{4}-\d{2}-\d{2})\.csv", snap).group(1)
    info = json.load(open(os.path.join(ASSETS, "species", f"release_{release}.json"), encoding="utf-8"))
    rows = read(snap)

    genus_csv = sorted(glob.glob(os.path.join(ASSETS, "genus_*.csv")))[-1]
    genera = {g["name"]: g for g in genus_page.load(genus_csv)}

    # ---- agreement between the two pages ------------------------------------------------------------------------
    unknown = sorted({r["genus"] for r in rows} - set(genera))
    assert not unknown, f"genera in the species release that the genus page does not know: {unknown}"
    for g in {r["genus"] for r in rows}:
        yo = {r["genus_y_order"] for r in rows if r["genus"] == g}
        assert len(yo) == 1, f"{g} has more than one tree position in the snapshot: {yo}"
        want = str(genera[g]["y_order"] or "")
        assert yo == {want}, f"{g}: the genus page puts it at tree position {want!r}, the species release at {yo}"
    real = [r for r in rows if r["kind"] in ("species", "subspecies")]
    left_out = {}
    for r in rows:
        if r["kind"] == "left_out":
            left_out.setdefault(r["genus"], []).append(r)
    assert all(r["type_strains"] and r["publication_doi"] and r["authority"] for r in real), "a name lacks type strains, a DOI or an authority"
    assert all(r["publication_doi"] and r["authority"] for r in rows), "a heading lacks a DOI or an authority"
    names = [r["name"] for r in rows]
    assert len(set(names)) == len(names), "duplicate names in the snapshot"

    by_genus = {}
    for r in rows:
        if r["kind"] != "left_out":
            by_genus.setdefault(r["genus"], []).append(r)
    # Every genus of the genus page gets a section. One with no listed name must say why, so that a genus never
    # disappears from the page without a reason.
    nameless = sorted(set(genera) - set(by_genus))
    unexplained = [g for g in nameless if g not in left_out]
    assert not unexplained, f"genera with no listed name and no explanation in the snapshot: {unexplained}"
    order = sorted(genera, key=lambda g: (genera[g]["y_order"] is None, genera[g]["y_order"] or 0, g))
    placed_total = sum(1 for g in genera.values() if g["y_order"])

    n_species = sum(1 for r in real if r["kind"] == "species")
    n_sub = sum(1 for r in real if r["kind"] == "subspecies")
    total = n_species + n_sub
    y, m, d = (int(x) for x in release.split("-"))
    asof = f"{MONTHS[m - 1]} {d}, {y}"
    iso = datetime.date(y, m, d).isoformat()

    # The genus list in three lines: the placed genera in two halves of the tree order, then the genera that are
    # not placed on the tree yet.
    def index_item(g):
        n = sum(1 for r in by_genus.get(g, []) if r["kind"] != "parent")
        return f'<a href="#{genus_page._slug(g)}"><em>{esc(g)}</em></a>&nbsp;({n})'

    placed_genera = [g for g in order if genera[g]["y_order"]]
    unplaced_genera = [g for g in order if not genera[g]["y_order"]]
    half = (len(placed_genera) + 1) // 2
    index = '<ul class="lacto-gindex">\n' + "\n".join(
        f'<li>{"; ".join(index_item(g) for g in group)}</li>'
        for group in (placed_genera[:half], placed_genera[half:], unplaced_genera)
        if group
    ) + "\n</ul>"

    sections = []
    for g in order:
        rs = by_genus.get(g, [])
        n = sum(1 for r in rs if r["kind"] != "parent")
        ferm = genera[g]["ferm"]
        pos = (f"phylogenetic position based on genus ({genera[g]['y_order']} of {placed_total})" if genera[g]["y_order"]
               else "phylogenetic position based on genus: not yet placed on the tree")
        dot = f'<span class="lacto-dot lacto-{ferm.lower()}"></span>' if ferm in ("Homo", "Hetero") else ""
        ferm_txt = {"Homo": "homofermentative", "Hetero": "heterofermentative"}.get(ferm, "fermentation type not assigned")
        what = "species and subspecies" if any(r["kind"] == "subspecies" for r in rs) else "species"
        cap = f'<p class="lacto-gcap">{n} {what} · {dot}{ferm_txt} · {pos}</p>'
        if not rs:
            items = "; ".join(left_out_item(r) for r in left_out[g])
            reasons = "; ".join(dict.fromkeys(esc(r["note"]) for r in left_out[g]))
            sections.append(f'## _{g}_\n\n{cap}\n\n<p class="lacto-gnote">No species are listed. Left out: {items}. {reasons}.</p>\n')
            continue
        head = "<thead><tr>" + "".join(f'<th scope="col">{h}</th>' for h in ("Name", "Fermentation, lifestyle", "Type strains", "Genome", "Links")) + "</tr></thead>"
        body = "\n".join(row(r) for r in rs)
        sections.append(f"## _{g}_\n\n{cap}\n\n<table class=\"lacto-table lacto-species\">{head}<tbody>\n{body}\n</tbody></table>\n")

    md = f"""---
title: Lactobacillaceae species
date: {iso}
unlisted: true
---

{genus_page.tabs("species")}

<p class="lacto-hero">{total}</p>
<p class="lacto-hero-label">species and subspecies currently placed in <em>Lactobacillaceae</em> family ({n_species} species, {n_sub} subspecies), updated on {asof}.</p>

For detailed lifestyle updates, check [Duar et al. 2017](https://doi.org/{LIFESTYLE_DOI}), and stay tuned to the most recent posts and publications of [Nanzhen Qiao]({LINKEDIN}) and [Michael Gänzle]({GANZLE_SCHOLAR}).

<p class="lacto-keyline"><span class="lacto-dot lacto-homo"></span>homofermentative <span class="lacto-dot lacto-hetero"></span>heterofermentative <span class="lacto-chip">new</span> not in the June 2025 list</p>

<p class="lacto-gindex-label"><span aria-hidden="true">\U0001F447</span> Jump to a genus (number of species and subspecies):</p>
{index}

{chr(10).join(sections)}
"""
    # ---- the page must say what the data says ---------------------------------------------------------------------
    assert md.count('<tr class="lacto-sp">') + md.count('<tr class="lacto-subrow">') == total, "table rows and the headline count disagree"
    assert md.count('<tr class="lacto-parent">') == sum(1 for r in rows if r["kind"] == "parent")
    for status, text in (("not_valid", "not validly published"), ("illegitimate", "illegitimate name"), ("subspecies_abandoned", "subspecies division abandoned")):
        want = sum(1 for r in rows if r["status"] == status and r["kind"] != "left_out")
        assert md.count(f">{text}") == want, f"{want} rows are {text}, but the page labels {md.count('>' + text)}"
    assert md.count('<span class="lacto-chip">new</span>') == sum(1 for r in real if r["change"] == "new") + 1  # + the legend
    assert Counter(r["kind"] for r in real) == {"species": n_species, "subspecies": n_sub}
    # The genus page prints a count for each genus and links it here; the two pages must count the same names.
    assert Counter(r["genus"] for r in real) == genus_page._species_counts(), "the genus page and this page count different names per genus"
    assert info["counts"]["species"] + info["counts"]["subspecies"] == total, "the release summary and the snapshot disagree"
    headings = re.findall(r"^## _(.+)_$", md, re.M)
    assert len(headings) == len(set(headings)) == len(order), "genus headings are missing or repeated"

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(md.rstrip("\n") + "\n\n[🐝](#top)\n")  # back-to-top link, as on the home page
    print(f"wrote {OUT}")
    print(f"  {total} names ({n_species} species, {n_sub} subspecies) in {len(order)} genera, release {release}")
    print(f"  page text {len(md) // 1024} KB")


if __name__ == "__main__":
    main()
