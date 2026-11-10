#!/usr/bin/env python3
"""Generate content/lactobacillaceae.md from the curated genus CSV.

The CSV is the source of truth. When a genus is added or a fermentation type
filled in, update assets/lactobacillaceae/genus_*.csv and re-run:

    python3 scripts/build_lactobacillaceae.py

Charts are plain inline SVG sized for the 42rem content column. Colours come
from CSS custom properties defined in quartz/styles/custom.scss, so light and
dark mode are handled there, not here.
"""

import csv
import glob
import os
import re
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "content", "lactobacillaceae.md")

# Chart geometry. 672px is the 42rem content column at a 16px root.
W = 672


def esc(s):
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    out = []
    for r in rows:
        name = (r["Tax name"] or "").strip()
        if not name:
            continue
        authority = (r["Authority"] or "").strip()
        m = re.search(r"(1[6-9]\d\d|20\d\d)", authority)
        out.append(
            {
                "name": name,
                "authority": authority,
                "year": int(m.group(1)) if m else None,
                "ferm": (r["Fermentation_type"] or "").strip() or "Unassigned",
                "type_species": (r["Type_species"] or "").strip(),
                "formal": (r["Scientific name is formal"] or "").strip().upper() == "TRUE",
                "source": (r["Source"] or "").strip(),
                "note": (r["Note"] or "").strip(),
                "y_order": int(r["Y_order"]) if (r.get("Y_order") or "").strip() else None,
            }
        )
    return out


def rounded_top_rect(x, y, w, h, r):
    """Rect with rounded top corners, square at the baseline."""
    r = min(r, w / 2, h)
    if r <= 0:
        return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/>'
    return (
        f'<path d="M{x:.1f} {y + h:.1f} L{x:.1f} {y + r:.1f} '
        f"Q{x:.1f} {y:.1f} {x + r:.1f} {y:.1f} L{x + w - r:.1f} {y:.1f} "
        f'Q{x + w:.1f} {y:.1f} {x + w:.1f} {y + r:.1f} L{x + w:.1f} {y + h:.1f} Z"/>'
    )


SERIES = [
    ("Homo", "homo", "Homofermentative"),
    ("Hetero", "hetero", "Heterofermentative"),
    ("Unassigned", "unassigned", "Unassigned"),
]


def tally_years(recs):
    years = sorted({r["year"] for r in recs if r["year"]})
    per = {y: Counter(r["ferm"] for r in recs if r["year"] == y) for y in years}
    return years, per


def legend_for(per, years):
    out = ['<div class="lacto-legend">']
    for key, cls, lab in SERIES:
        if any(per[y].get(key, 0) for y in years):
            out.append(
                f'<span class="lacto-key"><span class="lacto-dot lacto-{cls}"></span>{lab}</span>'
            )
    out.append("</div>")
    return "\n".join(out)


def rounded_end_rect(x, y, w, h, r, side):
    """Rect rounded on one side only, square at the baseline."""
    r = min(r, w / 2 if side == "top" else h / 2, h if side == "top" else w)
    if r <= 0:
        return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/>'
    if side == "top":
        return (
            f'<path d="M{x:.1f} {y + h:.1f} L{x:.1f} {y + r:.1f} '
            f"Q{x:.1f} {y:.1f} {x + r:.1f} {y:.1f} L{x + w - r:.1f} {y:.1f} "
            f'Q{x + w:.1f} {y:.1f} {x + w:.1f} {y + r:.1f} L{x + w:.1f} {y + h:.1f} Z"/>'
        )
    # right
    return (
        f'<path d="M{x:.1f} {y:.1f} L{x + w - r:.1f} {y:.1f} '
        f"Q{x + w:.1f} {y:.1f} {x + w:.1f} {y + r:.1f} L{x + w:.1f} {y + h - r:.1f} "
        f'Q{x + w:.1f} {y + h:.1f} {x + w - r:.1f} {y + h:.1f} L{x:.1f} {y + h:.1f} Z"/>'
    )


# --- chart 1: the fermentation split, as one whole ------------------------


def segmented_bar(counts, total):
    """One whole split into parts, as HTML rather than SVG.

    A flex row keeps the blocks proportional at any width while the labels
    stay at their CSS size, so this needs no scrolling on a phone.
    """
    order = [
        ("Homo", "homo", "Homofermentative"),
        ("Hetero", "hetero", "Heterofermentative"),
        ("Unassigned", "unassigned", "Unassigned"),
    ]
    parts = [(cls, lab, counts.get(k, 0)) for k, cls, lab in order if counts.get(k, 0)]

    out = [
        '<div class="lacto-split" role="img" aria-label="Fermentation type across '
        f"{total} genera: " + ", ".join(f"{lab} {n}" for _, lab, n in parts) + '.">'
    ]
    for cls, lab, n in parts:
        share = 100 * n / total
        # A block narrower than its label prints none; the value stays in the
        # legend's tooltip and in the table. 8% is the share that still fits a
        # padded digit at the narrowest layout (343px).
        tight = " lacto-split-value--tight" if share < 8 else ""
        out.append(
            f'<div class="lacto-split-part lacto-{cls}" style="flex: {n} 1 0"'
            f' title="{esc(lab)}: {n} genera, {share:.0f}%">'
            f'<span class="lacto-split-value{tight}">{n}</span></div>'
        )
    out.append("</div>")

    out.append('<div class="lacto-legend">')
    for cls, lab, n in parts:
        out.append(
            f'<span class="lacto-key"><span class="lacto-dot lacto-{cls}"></span>{lab}</span>'
        )
    out.append("</div>")
    return "\n".join(out)


# --- chart 2: proposals per year, stacked by fermentation type ------------


def year_chart(recs):
    """Two renderings of the same tally: columns on a wide screen, horizontal
    bars on a narrow one. A single 672px-wide column chart would either shrink
    its year labels to about 5px on a phone or open scrolled onto its empty
    left half, so the narrow screen gets a layout built for it instead."""
    years, per = tally_years(recs)
    return (
        f'<div class="lacto-wide">{_year_columns(years, per, recs)}</div>\n'
        f'<div class="lacto-narrow">{_year_bars(years, per, recs)}</div>\n'
        + legend_for(per, years)
    )


def _ticks(tallest):
    step = 5 if tallest <= 25 else 10
    ticks = list(range(0, tallest + step, step))
    return ticks, ticks[-1]


def _year_columns(years, per, recs):
    tallest = max(sum(c.values()) for c in per.values())
    pad_l, pad_r, pad_t, pad_b = 30, 6, 16, 34
    plot_w, plot_h = W - pad_l - pad_r, 236
    h = plot_h + pad_t + pad_b
    band = plot_w / len(years)
    bar_w = min(24.0, band * 0.6)
    ticks, y_max = _ticks(tallest)
    gap = 2

    def ypx(v):
        return pad_t + plot_h - plot_h * v / y_max

    svg = [
        f'<svg class="lacto-chart" viewBox="0 0 {W} {h:.0f}" width="{W}" height="{h:.0f}" '
        f'role="img" aria-label="Genera proposed per year from {years[0]} to {years[-1]}, '
        f"split by fermentation type. The 2020 reclassification accounts for "
        f'{sum(per[2020].values()) if 2020 in per else 0} of {len(recs)} genera." '
        f'preserveAspectRatio="xMidYMin meet">'
    ]
    for t in ticks:
        svg.append(
            f'<line class="lacto-grid" x1="{pad_l}" x2="{W - pad_r}" '
            f'y1="{ypx(t):.1f}" y2="{ypx(t):.1f}"/>'
        )
        svg.append(
            f'<text class="lacto-tick lacto-tick-y" x="{pad_l - 8}" y="{ypx(t) + 4:.1f}">{t}</text>'
        )

    for i, y in enumerate(years):
        cx = pad_l + band * (i + 0.5)
        x = cx - bar_w / 2
        total = sum(per[y].values())
        stack = [(cls, lab, per[y].get(k, 0)) for k, cls, lab in SERIES if per[y].get(k, 0)]
        cursor = 0.0
        for j, (cls, lab, n) in enumerate(stack):
            y0, y1 = ypx(cursor + n), ypx(cursor)
            seg_h = y1 - y0 - (gap if j > 0 else 0)
            svg.append(f'<g class="lacto-seg lacto-{cls}">')
            svg.append(f"<title>{y} &middot; {esc(lab)}: {n}</title>")
            svg.append(
                rounded_end_rect(x, y0, bar_w, max(seg_h, 1.0), 4 if j == len(stack) - 1 else 0, "top")
            )
            svg.append("</g>")
            cursor += n
        if total == tallest:
            svg.append(
                f'<text class="lacto-value" x="{cx:.1f}" y="{ypx(total) - 7:.1f}">{total}</text>'
            )
        svg.append(
            f'<text class="lacto-tick lacto-tick-x" x="{cx:.1f}" y="{pad_t + plot_h + 18}">{y}</text>'
        )
    svg.append(
        f'<line class="lacto-axis" x1="{pad_l}" x2="{W - pad_r}" '
        f'y1="{ypx(0):.1f}" y2="{ypx(0):.1f}"/>'
    )
    svg.append("</svg>")
    return "\n".join(svg)


def _year_bars(years, per, recs):
    """Narrow-screen variant: years down the side, bars running right."""
    NW = 335
    pad_l, pad_r, pad_t = 34, 24, 8
    row = 22
    bar_h = 12
    plot_w = NW - pad_l - pad_r
    plot_h = row * len(years)
    h = pad_t + plot_h + 26
    longest = max(sum(c.values()) for c in per.values())
    ticks, x_max = _ticks(longest)
    gap = 2

    def xpx(v):
        return pad_l + plot_w * v / x_max

    svg = [
        f'<svg class="lacto-chart lacto-chart-narrow" viewBox="0 0 {NW} {h:.0f}" '
        f'width="{NW}" height="{h:.0f}" role="img" aria-label="Genera proposed per year '
        f'from {years[0]} to {years[-1]}, split by fermentation type." '
        f'preserveAspectRatio="xMinYMin meet">'
    ]
    for t in ticks:
        svg.append(
            f'<line class="lacto-grid" y1="{pad_t}" y2="{pad_t + plot_h}" '
            f'x1="{xpx(t):.1f}" x2="{xpx(t):.1f}"/>'
        )
        svg.append(
            f'<text class="lacto-tick lacto-tick-x" x="{xpx(t):.1f}" '
            f'y="{pad_t + plot_h + 16}">{t}</text>'
        )

    for i, y in enumerate(years):
        cy = pad_t + row * i + row / 2
        yb = cy - bar_h / 2
        total = sum(per[y].values())
        stack = [(cls, lab, per[y].get(k, 0)) for k, cls, lab in SERIES if per[y].get(k, 0)]
        cursor = 0.0
        for j, (cls, lab, n) in enumerate(stack):
            x0, x1 = xpx(cursor), xpx(cursor + n)
            seg_w = x1 - x0 - (gap if j > 0 else 0)
            svg.append(f'<g class="lacto-seg lacto-{cls}">')
            svg.append(f"<title>{y} &middot; {esc(lab)}: {n}</title>")
            svg.append(
                rounded_end_rect(
                    x0 + (gap if j > 0 else 0), yb, max(seg_w, 1.0), bar_h,
                    4 if j == len(stack) - 1 else 0, "right",
                )
            )
            svg.append("</g>")
            cursor += n
        if total == longest:
            svg.append(
                f'<text class="lacto-value lacto-value-end" x="{xpx(total) + 6:.1f}" '
                f'y="{cy + 4:.1f}">{total}</text>'
            )
        svg.append(
            f'<text class="lacto-tick lacto-tick-y" x="{pad_l - 8}" y="{cy + 4:.1f}">{y}</text>'
        )
    svg.append(
        f'<line class="lacto-axis" y1="{pad_t}" y2="{pad_t + plot_h}" '
        f'x1="{pad_l}" x2="{pad_l}"/>'
    )
    svg.append("</svg>")
    return "\n".join(svg)


# --- the table ------------------------------------------------------------


def _authority(authority):
    """A trailing nomenclatural note (Approved Lists 1980) goes on its own
    smaller line, so one long row does not set the column's width."""
    if " (" in authority and authority.endswith(")"):
        head, note = authority.split(" (", 1)
        return f'{esc(head)}<span class="lacto-auth-note">({esc(note)}</span>'
    return esc(authority)


def table(recs):
    cls = {"Homo": "homo", "Hetero": "hetero", "Unassigned": "unassigned"}
    short = {"Homo": "Homo", "Hetero": "Hetero", "Unassigned": "—"}
    out = [
        '<div class="lacto-table-wrap">',
        '<table class="lacto-table">',
        "<thead><tr>",
        "<th>Genus</th><th>Type species</th><th>Fermentation</th><th>Proposed</th>",
        "</tr></thead>",
        "<tbody>",
    ]
    # Phylogenetic order (Y_order), which is the order the genera sit in on the
    # tree. The few with no Y_order yet fall to the end.
    for r in sorted(recs, key=lambda r: (r["y_order"] is None, r["y_order"] or 0, r["name"])):
        # Abbreviate the genus in the type species: it is already in column 1.
        # "Candidatus Gallilactobacillus intestinavium" takes the standard
        # nomenclatural short form, "Ca. G. intestinavium".
        parts = r["type_species"].split(" ")
        if parts[0] == "Candidatus" and len(parts) >= 3:
            ts = f"Ca. {parts[1][0]}. {' '.join(parts[2:])}"
        elif len(parts) >= 2:
            ts = f"{parts[0][0]}. {' '.join(parts[1:])}"
        else:
            ts = r["type_species"]
        out.append(
            "<tr>"
            f'<td class="lacto-genus"><em>{esc(r["name"])}</em></td>'
            f'<td><em>{esc(ts)}</em></td>'
            f'<td class="lacto-ferm"><span class="lacto-dot lacto-{cls[r["ferm"]]}"></span>'
            f'{short[r["ferm"]]}</td>'
            f'<td class="lacto-auth">{_authority(r["authority"])}</td>'
            "</tr>"
        )
    out += ["</tbody>", "</table>", "</div>"]
    return "\n".join(out)


def main():
    csvs = sorted(glob.glob(os.path.join(REPO, "assets", "lactobacillaceae", "genus_*.csv")))
    if not csvs:
        sys.exit("no genus_*.csv in assets/lactobacillaceae/")
    path = csvs[-1]
    recs = load(path)
    total = len(recs)
    ferm = Counter(r["ferm"] for r in recs)
    years = sorted({r["year"] for r in recs if r["year"]})
    n2020 = sum(1 for r in recs if r["year"] == 2020)
    before = sum(1 for r in recs if r["year"] and r["year"] < 2020)
    stamp = re.search(r"genus_(\d{4})(\d{2})(\d{2})", os.path.basename(path))
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    asof = (
        f"{months[int(stamp.group(2)) - 1]} {int(stamp.group(3))}, {stamp.group(1)}"
        if stamp
        else "the current snapshot"
    )

    unassigned = [r for r in recs if r["ferm"] == "Unassigned"]

    md = f"""---
title: Lactobacillaceae
date: 2026-11-09
---

Below are updated on {asof}.

## The family today

<p class="lacto-hero">{total}</p>
<p class="lacto-hero-label">genera currently placed in <em>Lactobacillaceae</em></p>

For detailed homofermentative and heterofermentative fermentation in
_Lactobacillaceae_, check
[10.1016/j.cofs.2015.03.001](https://doi.org/10.1016/j.cofs.2015.03.001) and
[10.1016/j.fm.2025.104945](https://doi.org/10.1016/j.fm.2025.104945).

{segmented_bar(ferm, total)}

## When they were named

{year_chart(recs)}

<p class="lacto-caption">Only years in which at least one current genus was named
appear on the axis, so the spacing between them is not to scale.</p>

Three genera carried the family for most of a century: _Leuconostoc_
(1878), _Lactobacillus_ (1901), and _Pediococcus_ (1903). Then
[Zheng et al. 2020](https://doi.org/10.1099/ijsem.0.004107) split the old,
sprawling _Lactobacillus_ into {n2020} genera on whole-genome evidence, and the
family went from {before} genera to {before + n2020} in a single paper.

## All {total} genera

In phylogenetic order, the order they sit in on the tree. The two genera not
yet placed on it are listed last.

{table(recs)}

## Method and caveats

The table is curated from NCBI Taxonomy, reconciled against the 2020
reclassification, with four deliberate departures:

- **Paralactobacillus is kept.** NCBI sank it into _Lactobacillus_
  (_L. selangorensis_, taxid 81857). Zheng et al. 2020 retain the genus, so this
  census does too. It is the one row with no NCBI taxid.
- **Candidatus Gallilactobacillus is included** even though the name is not
  formally validated, because the genome is in the tree.
- **{len(unassigned)} genera have no fermentation type yet**:
  {", ".join("_" + r["name"] + "_" for r in unassigned)}. Both are recent and I
  have not confirmed the phenotype against a primary description, so they are
  counted but not classified rather than guessed at.
- **Fermentation type is the genus-level generalisation**, taken from the type
  species. Individual species inside a genus can deviate, and a handful are
  facultatively heterofermentative, which this binary flattens.

Source file:
[`genus_{stamp.group(1) + stamp.group(2) + stamp.group(3) if stamp else ""}.csv`](https://github.com/nanzhen102/nanzhen102.github.io/blob/v5/assets/lactobacillaceae/{os.path.basename(path)}).
The tree itself is built with
[core-genome-phylogeny](https://github.com/nanzhen102/core-genome-phylogeny).
"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {OUT}")
    print(f"  {total} genera from {os.path.basename(path)}")
    print(f"  {dict(ferm)}")
    print(f"  years {years[0]}–{years[-1]}, {len(years)} distinct")


if __name__ == "__main__":
    main()
