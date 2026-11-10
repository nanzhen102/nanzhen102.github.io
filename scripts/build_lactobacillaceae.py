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
import datetime
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


WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
}


def _num(n):
    return WORDS.get(n, str(n))


def _join(items):
    """a, b, and c"""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _early_cluster(recs):
    """The oldest genera, cut at the longest quiet stretch in the record.

    Derived rather than named, so the opening sentence stays true when the
    CSV gains or loses an early genus.
    """
    years = sorted({r["year"] for r in recs if r["year"]})
    if len(years) < 3:
        return None
    gap, i = max((years[i + 1] - years[i], i) for i in range(len(years) - 1))
    cutoff = years[i]
    early = sorted(
        (r for r in recs if r["year"] and r["year"] <= cutoff), key=lambda r: r["year"]
    )
    return early, cutoff, gap


def _hit(x, y, w, h, tip):
    """A transparent hover target over one segment, carrying its own readout.

    These are emitted after every bar, so they sit on top for both hit-testing
    and painting, and one CSS rule drives them all: no per-segment ids.
    """
    pad = 3  # a thin segment is still easy to hit
    return (
        '<g class="lacto-hit">'
        f'<rect class="lacto-hitarea" x="{x:.1f}" y="{y - pad:.1f}" '
        f'width="{w:.1f}" height="{h + pad * 2:.1f}"/>'
        f'<rect class="lacto-hitring" x="{x:.1f}" y="{y:.1f}" '
        f'width="{w:.1f}" height="{h:.1f}" rx="3"/>'
        f"{tip}</g>"
    )


def _svg_tip(cx, top, lines, bounds, below=False):
    """A hover readout drawn inside the SVG.

    Emitted after every bar and referenced by id, so it always paints on top
    and is never clipped by a later column. Width is estimated from the text,
    then clamped to the plot so the tip cannot overflow the chart.
    """
    pad = 7
    lh = 13
    w = max(len(t) for t in lines) * 6.0 + pad * 2
    h = lh * len(lines) + pad * 2 - 3
    x = cx - w / 2
    x = max(bounds[0], min(x, bounds[1] - w))
    y = top + 8 if below else top - h - 8
    rows = "".join(
        f'<text class="lacto-tiptext{" lacto-tiptext-head" if i == 0 else ""}" '
        f'x="{x + pad:.1f}" y="{y + pad + lh * i + 9:.1f}">{t}</text>'
        for i, t in enumerate(lines)
    )
    return (
        '<g class="lacto-svgtip">'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5"/>'
        f"{rows}</g>"
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
        '<div class="lacto-split" role="list" aria-label="Fermentation type across '
        f"{total} genera: " + ", ".join(f"{lab} {n}" for _, lab, n in parts) + '.">'
    ]
    for cls, lab, n in parts:
        share = 100 * n / total
        # A block narrower than its own label prints none; the value stays in
        # the hover readout and in the table. Measured against the narrowest
        # layout (343px) and the digits this particular number needs.
        needed = 14 + 7.5 * len(str(n))
        tight = " lacto-split-value--tight" if 343 * n / total < needed else ""
        out.append(
            f'<div class="lacto-split-part lacto-{cls}" style="flex: {n} 1 0"'
            f' tabindex="0" role="listitem"'
            f' aria-label="{esc(lab)}: {n} genera, {share:.0f} percent">'
            f'<span class="lacto-split-value{tight}">{n}</span>'
            f'<span class="lacto-tip"><strong>{esc(lab)}</strong>'
            f"<span>{n} genera &middot; {share:.0f}%</span></span></div>"
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

    tips = []
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
            svg.append(
                rounded_end_rect(x, y0, bar_w, max(seg_h, 1.0), 4 if j == len(stack) - 1 else 0, "top")
            )
            svg.append("</g>")
            tips.append(
                _hit(
                    x, y0, bar_w, max(seg_h, 1.0),
                    _svg_tip(
                        cx, y0,
                        [f"{y} \u00b7 {lab}", f"{n} " + ("genus" if n == 1 else "genera")],
                        (2, W - 2),
                        below=y0 < 46,
                    ),
                )
            )
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
    # Tips last so they paint over every bar.
    svg.append('<g class="lacto-tips">' + "".join(tips) + "</g>")
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

    tips = []
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
            svg.append(
                rounded_end_rect(
                    x0 + (gap if j > 0 else 0), yb, max(seg_w, 1.0), bar_h,
                    4 if j == len(stack) - 1 else 0, "right",
                )
            )
            svg.append("</g>")
            tips.append(
                _hit(
                    x0 + (gap if j > 0 else 0), yb, max(seg_w, 1.0), bar_h,
                    _svg_tip(
                        (x0 + x1) / 2, yb,
                        [f"{y} \u00b7 {lab}", f"{n} " + ("genus" if n == 1 else "genera")],
                        (2, NW - 2),
                        below=yb < 40,
                    ),
                )
            )
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
    svg.append('<g class="lacto-tips">' + "".join(tips) + "</g>")
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


def _rows(recs, key):
    cls = {"Homo": "homo", "Hetero": "hetero", "Unassigned": "unassigned"}
    short = {"Homo": "Homo", "Hetero": "Hetero", "Unassigned": "\u2014"}
    out = []
    for r in sorted(recs, key=key):
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
            f"<td><em>{esc(ts)}</em></td>"
            f'<td class="lacto-ferm"><span class="lacto-dot lacto-{cls[r["ferm"]]}"></span>'
            f'{short[r["ferm"]]}</td>'
            f'<td class="lacto-auth">{_authority(r["authority"])}</td>'
            "</tr>"
        )
    return out


def _table(rows):
    return (
        '<table class="lacto-table">'
        "<thead><tr>"
        "<th>Genus</th><th>Type species</th><th>Fermentation</th><th>Proposed</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def table(recs):
    """Two orderings, switched with a radio pair and :checked.

    Pure CSS rather than a script: Quartz navigates as a single-page app, and a
    script written into the markdown would not re-run after an in-site
    navigation. Both orderings are rendered and one is hidden.
    """
    # Phylogenetic order (Y_order), the order the genera sit in on the tree.
    # The few with no Y_order yet fall to the end.
    tree = _rows(recs, lambda r: (r["y_order"] is None, r["y_order"] or 0, r["name"]))
    alpha = _rows(recs, lambda r: r["name"].replace("Candidatus ", "").lower())

    n_unplaced = sum(1 for r in recs if r["y_order"] is None)
    unplaced_note = (
        f" The {_num(n_unplaced)} "
        + ("genus" if n_unplaced == 1 else "genera")
        + " not yet placed on it "
        + ("is" if n_unplaced == 1 else "are")
        + " listed last."
        if n_unplaced
        else ""
    )

    return "\n".join(
        [
            '<div class="lacto-order">',
            '<div class="lacto-order-controls" role="group" aria-label="Table order">',
            "<span>Order</span>",
            # Each radio sits beside its own label: focusing one never scrolls
            # the page away from the control.
            '<input class="lacto-order-radio" type="radio" name="lacto-order"'
            ' id="lacto-order-tree" checked />',
            '<label for="lacto-order-tree">Phylogenetic</label>',
            '<input class="lacto-order-radio" type="radio" name="lacto-order"'
            ' id="lacto-order-az" />',
            '<label for="lacto-order-az">A\u2013Z</label>',
            "</div>",
            '<p class="lacto-caption lacto-view-tree">The order they sit in on the'
            f" tree.{unplaced_note}</p>",
            '<p class="lacto-caption lacto-view-az">Alphabetical by genus name.</p>',
            f'<div class="lacto-table-wrap lacto-view-tree">{_table(tree)}</div>',
            f'<div class="lacto-table-wrap lacto-view-az">{_table(alpha)}</div>',
            "</div>",
        ]
    )


def _check(md, recs, ferm):
    """Fail loudly if the page could contradict its own source.

    Everything on the page comes from the CSV, so the headline figure, the
    chart totals and both orderings of the table have to agree. These are the
    numbers a reader would compare.
    """
    total = len(recs)

    # Headline figure.
    hero = re.search(r'<p class="lacto-hero">(\d+)</p>', md)
    assert hero and int(hero.group(1)) == total, "hero figure does not match the CSV"

    # Both tables carry every genus, exactly once.
    for cls, label in (("lacto-view-tree", "phylogenetic"), ("lacto-view-az", "alphabetical")):
        block = md.split(f'lacto-table-wrap {cls}"')[1].split("</table>")[0]
        rows = re.findall(r'<td class="lacto-genus"><em>([^<]+)</em>', block)
        assert len(rows) == total, f"{label} table has {len(rows)} rows, expected {total}"
        assert sorted(rows) == sorted(
            r["name"] for r in recs
        ), f"{label} table does not hold the same genera as the CSV"

    # Section heading and fermentation split.
    assert f"## All {total} genera" in md, "section heading does not match the CSV"
    assert sum(ferm.values()) == total, "fermentation counts do not sum to the total"

    # Every genus appears in exactly one segment of the split bar.
    segments = re.findall(r'class="lacto-split-part [^"]*" style="flex: (\d+) ', md)
    assert segments, "no split bar segments found"
    assert sum(int(n) for n in segments) == total, (
        "split bar segments do not sum to the total"
    )

    print(f"  checked: hero, both tables, heading and split bar all agree on {total}")


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
    stamp = re.search(r"genus_(\d{4})(\d{2})(\d{2})", os.path.basename(path))
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    if stamp:
        y, m, d = stamp.group(1), int(stamp.group(2)), int(stamp.group(3))
        asof = f"{months[m - 1]} {d}, {y}"
        iso_date = f"{y}-{m:02d}-{d:02d}"
    else:
        # No datestamp in the filename: fall back to the file's mtime so the
        # page never carries a date that contradicts its source.
        t = datetime.date.fromtimestamp(os.path.getmtime(path))
        asof = f"{months[t.month - 1]} {t.day}, {t.year}"
        iso_date = t.isoformat()

    unassigned = [r for r in recs if r["ferm"] == "Unassigned"]

    # The opening history sentence, derived so it stays true as the CSV
    # changes. Both halves are dropped if the data no longer supports them.
    history = []
    early = _early_cluster(recs)
    if early:
        cluster, cutoff, gap = early
        named = _join([f"_{r['name']}_ ({r['year']})" for r in cluster])
        history.append(
            f"For the {gap} years after {cutoff}, the family held just "
            f"{_num(len(cluster))} "
            + ("genus" if len(cluster) == 1 else "genera")
            + f": {named}."
        )
    if n2020:
        history.append(
            "Then [Zheng et al. 2020](https://doi.org/10.1099/ijsem.0.004107) "
            "split the old, sprawling _Lactobacillus_ into "
            f"{n2020} genera on whole-genome evidence, {100 * n2020 / total:.0f}% "
            "of the family as it stands today."
        )
    history = " ".join(history)

    md = f"""---
title: Lactobacillaceae
date: {iso_date}
---

Updated {asof}.

<p class="lacto-hero">{total}</p>
<p class="lacto-hero-label">genera currently placed in <em>Lactobacillaceae</em></p>

For detailed homofermentative and heterofermentative fermentation in
_Lactobacillaceae_, check
[Gänzle 2015](https://doi.org/10.1016/j.cofs.2015.03.001) and
[Qiao & Gänzle 2026](https://doi.org/10.1016/j.fm.2025.104945).

{segmented_bar(ferm, total)}

## When they were named

{year_chart(recs)}

<p class="lacto-caption">Only years in which at least one current genus was named
appear on the axis, so the spacing between them is not to scale.</p>

{history}

## All {total} genera

{table(recs)}

<p class="lacto-source">Source file: <code>{os.path.basename(path)}</code>, request from
<a href="mailto:nanzhen.qiao@gmail.com"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7" /><rect x="2" y="4" width="20" height="16" rx="2" /></svg>nanzhen.qiao@gmail.com</a>.
The tree itself is built with
<a href="https://github.com/nanzhen102/core-genome-phylogeny">core-genome-phylogeny</a>.</p>
"""
    _check(md, recs, ferm)

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {OUT}")
    print(f"  {total} genera from {os.path.basename(path)}")
    print(f"  {dict(ferm)}")
    print(f"  years {years[0]}–{years[-1]}, {len(years)} distinct")


if __name__ == "__main__":
    main()
