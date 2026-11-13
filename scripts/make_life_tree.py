#!/usr/bin/env python3
"""Render the animation at the top of /lactobacillaceae: added by year, placed by relationship.

A round genus-level tree (assets/lactobacillaceae/genus_tree.json, the lab's core-genome tree collapsed to
genera) fills in as genera were described. Every genus lights up at its phylogenetic slot and grows a branch to
it, and the tree re-organises as relatives arrive. Years, fermentation type and tree order come from the same
genus_*.csv the page is built from, so a new CSV gives a new animation.

    python3 scripts/make_life_tree.py

writes content/lactobacillaceae-banner-<datestamp>.gif and a still .png (shown to visitors who ask for reduced
motion). The loop opens on the finished tree so a visitor never lands on a blank tile, lets it dissolve to the
empty slots, rebuilds it year by year, and ends on the same finished tree, so it closes without a fade or a rest. build_lactobacillaceae.py refuses to build the page if that GIF is missing for the newest CSV.

Needs matplotlib, numpy, Pillow and (for the small file) ffmpeg. The colours are the site's night-mode tokens.
"""

import glob
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True  # importing the page builder must not leave a __pycache__ behind

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ASSETS = os.path.join(REPO, "assets", "lactobacillaceae")

SIZE, SS, FPS = 440, 2, 8  # the tree's square, supersampling for smooth lines, frames per second
BW = 960  # banner width: the tree square on the left, a gradient and the title on the right
END = (37, 65, 89)  # the far end of the gradient: the tree's blue, darkened and greyed so it stays quiet
TITLE, TITLE_FONT, TITLE_MAX = "Lactobacillaceae", 3, 66  # Bold Italic, as the page sets the family name
# Two lines under the title, in falling emphasis: what each name carries, who keeps it
# current. No date, so the GIF never goes stale. (text, size px, share of white)
LINES = [
    ("Type strains \u00b7 Fermentation type \u00b7 Lifestyle", 24, 0.86),
    ("Updated by Nanzhen Qiao and Michael G\u00e4nzle", 20, 0.58),
]
LINE_PITCH, TITLE_Y, SUB_TOP = 44, 112, 36  # distance between lines, title top, gap under the title (all px)
TEXT_X, MARGIN = SIZE + 36, 44  # the text starts clear of the tree and keeps a margin on the right
WHITE = (246, 244, 238)
BEAT, GROW, STAG, SETTLE = 0.7, 2.0, 0.12, 1.8  # one year / a branch growing / ripple step / bloom settle (s)
OPEN, DISSOLVE, HOLD = 0.8, 0.7, 2.4  # finished tree at the start / dissolve to empty / settle at the end (s)
BG, SLOT, LINE, TEXT = (16, 15, 15), (52, 51, 49), (135, 133, 128), (183, 181, 172)  # #100f0f page
COL = {"Homo": (213, 81, 129), "Hetero": (67, 133, 190), "Unassigned": (135, 133, 128)}  # #d55181 / #4385be
S = SIZE * SS
C = S / 2
RING = 0.405 * S
RROOT, RMAX = 0.30, 0.84
TH0, TH1 = np.deg2rad(18), np.deg2rad(342)  # tips fill the circle except a gap at the top
GAP = np.deg2rad(6)  # the two unplaced genera sit in that gap

smooth = lambda x: (lambda t: t * t * (3 - 2 * t))(np.clip(x, 0, 1))
mix = lambda a, b, t: tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def load_builder():
    spec = importlib.util.spec_from_file_location("build_lactobacillaceae", os.path.join(HERE, "build_lactobacillaceae.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def banner_base():
    """The static part of every frame: black that turns teal to the right, and the title. The tree square is pasted
    over x < SIZE, and the gradient stays exactly the page black up to there, so the square has no edge."""
    x = np.arange(BW)
    t = np.clip((x - SIZE) / (BW - SIZE), 0, 1)
    t = t * t * (3 - 2 * t)  # eases in, so there is no visible start to the gradient
    row = np.array([[BG[k] + (END[k] - BG[k]) * ti for k in range(3)] for ti in t])
    img = Image.fromarray(np.tile(row, (SIZE, 1, 1)).round().astype(np.uint8))
    # Text at 2x, then reduced: smoother edges than drawing at 1x.
    big = img.resize((BW * 2, SIZE * 2), Image.BICUBIC)
    d = ImageDraw.Draw(big)
    ttf = "/System/Library/Fonts/HelveticaNeue.ttc"
    avail = (BW - MARGIN - TEXT_X) * 2
    px = TITLE_MAX * 2
    while ImageFont.truetype(ttf, px, index=TITLE_FONT).getlength(TITLE) > avail:
        px -= 2
    title = ImageFont.truetype(ttf, px, index=TITLE_FONT)
    y0 = TITLE_Y * 2  # the title keeps its place
    d.text((TEXT_X * 2, y0), TITLE, font=title, fill=WHITE, anchor="la")
    for i, (text, size, share) in enumerate(LINES):
        f = ImageFont.truetype(ttf, size * 2, index=7)
        assert f.getlength(text) <= avail, f"'{text}' does not fit beside the tree: shorten it or lower its size"
        fill = tuple(int(WHITE[k] * share + END[k] * (1 - share)) for k in range(3))
        d.text((TEXT_X * 2, y0 + px + SUB_TOP * 2 + i * LINE_PITCH * 2), text, font=f, fill=fill, anchor="la")
    return big.resize((BW, SIZE), Image.LANCZOS)


def iter_leaves(n):
    if "genus" in n:
        yield n
    else:
        for k in n["kids"]:
            yield from iter_leaves(k)


def main():
    csvs = sorted(glob.glob(os.path.join(ASSETS, "genus_*.csv")))
    if not csvs:
        sys.exit("no genus_*.csv in assets/lactobacillaceae/")
    csv_path = csvs[-1]
    stamp = re.search(r"genus_(\d{8})", os.path.basename(csv_path))
    if not stamp:
        sys.exit(f"{os.path.basename(csv_path)} has no datestamp (genus_YYYYMMDD.csv); the animation is named after it")
    out_gif = os.path.join(REPO, "content", f"lactobacillaceae-banner-{stamp.group(1)}.gif")
    out_png = out_gif[:-4] + ".png"

    recs = load_builder().load(csv_path)
    by_name = {r["name"]: r for r in recs}
    placed = {r["name"]: r["y_order"] for r in recs if r["y_order"]}
    unplaced = sorted((r for r in recs if not r["y_order"]), key=lambda r: (r["year"] or 0, r["name"]))

    root = json.load(open(os.path.join(ASSETS, "genus_tree.json")))
    in_tree = {n["genus"] for n in iter_leaves(root)}
    # The tree is a snapshot of the lab's tree. A genus the CSV places but the tree lacks would silently vanish
    # from the animation, so refuse to draw it.
    assert in_tree == set(placed), (
        "genus_tree.json and the CSV disagree about which genera are placed on the tree: "
        f"only in the CSV {sorted(set(placed) - in_tree)}, only in the tree {sorted(in_tree - set(placed))}. "
        "Add the genus to the tree (scripts/genus_tree.py) or fix Y_order in the CSV."
    )

    ymax = max(placed.values())

    def prep(n):
        if "genus" in n:
            n["y"] = placed[n["genus"]]
            n["R"] = 1.0
            n["theta"] = TH0 + (n["y"] - 1) / (ymax - 1) * (TH1 - TH0)
            n["ymin"] = n["y"]
            return
        for k in n["kids"]:
            prep(k)
        n["ymin"] = min(k["ymin"] for k in n["kids"])
        n["kids"].sort(key=lambda k: k["ymin"])  # the page's tree order

    prep(root)
    internal = []

    def collect(n):
        if "kids" in n:
            internal.append(n)
            for k in n["kids"]:
                collect(k)

    collect(root)
    # Nodes are spread evenly by depth rank so the inner tree stays legible. The layout is not time-scaled.
    for i, n in enumerate(sorted(internal, key=lambda n: n["d"])):
        n["R"] = RROOT + (RMAX - RROOT) * (i / (len(internal) - 1)) ** 0.85

    # Timeline: genera arrive in the order they were described.
    years = sorted({r["year"] for r in recs if r["year"]})
    t_of, events, T = {}, [], 0.0
    for y in years:
        gs = sorted((r for r in recs if r["year"] == y), key=lambda r: (r["y_order"] is None, r["y_order"] or 0))
        events.append((T, y))
        if len(gs) > 5:  # a burst (the 2020 reclassification) ripples round the ring
            for i, r in enumerate(gs):
                t_of[r["name"]] = T + i * STAG
            T += (len(gs) - 1) * STAG + SETTLE
        else:
            for r in gs:
                t_of[r["name"]] = T
            T += BEAT
    t_build = T + HOLD  # the build ends on the finished tree, which is also where the loop opens
    t_final = T + 6.0  # a fully settled finished tree
    t_end = OPEN + DISSOLVE + t_build
    nf = int(round(t_end * FPS))
    unpl_th = {r["name"]: (-GAP if i % 2 == 0 else GAP) for i, r in enumerate(unplaced)}
    leaf_theta = {n["genus"]: n["theta"] for n in iter_leaves(root)}

    fig = plt.figure(figsize=(S / 100, S / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    pt = lambda px: px * 72 / 100
    try:
        font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", int(0.056 * S), index=7)  # Light
    except OSError:
        font = ImageFont.load_default()
    xy = lambda r, th: (C + RING * r * np.sin(th), C - RING * r * np.cos(th))
    dim = lambda c: [v / 255 for v in c]

    def frame(tau, vis=1.0):
        p = {nm: float(smooth((tau - t) / GROW)) for nm, t in t_of.items()}

        def weigh(n):
            if "genus" in n:
                n["W"], n["th"] = p[n["genus"]], n["theta"]
                return
            for k in n["kids"]:
                weigh(k)
            n["W"] = sum(k["W"] for k in n["kids"])
            ws = [(float(smooth(min(1, k["W"]))), k["th"]) for k in n["kids"] if k["W"] > 1e-4]
            n["th"] = sum(w * t for w, t in ws) / sum(w for w, _ in ws) if ws else None

        weigh(root)
        segs, cols = [], []

        def draw(n):
            if "genus" in n:
                return
            for k in n["kids"]:
                if k["W"] <= 1e-4:
                    continue
                g = float(smooth(min(1, k["W"] / 0.35)))  # a new path fades in; only the tip's own stem grows
                leaf = "genus" in k
                col = LINE
                if leaf:  # a new branch starts in its fermentation colour and cools to grey
                    mat = float(smooth((tau - t_of[k["genus"]] - GROW) / 1.6))
                    col = mix(COL[by_name[k["genus"]]["ferm"]], LINE, mat)
                if abs(k["th"] - n["th"]) > 1e-6:
                    ths = np.linspace(n["th"], k["th"], max(2, int(abs(k["th"] - n["th"]) / np.deg2rad(2)) + 2))
                    segs.append(np.column_stack(xy(n["R"], ths)))
                    cols.append((*dim(LINE), g * vis))
                r_end = n["R"] + (k["R"] - n["R"]) * (p[k["genus"]] if leaf else 1.0)
                segs.append(np.array([xy(n["R"], k["th"]), xy(r_end, k["th"])]))
                cols.append((*dim(col), vis * (float(smooth(p[k["genus"]] / 0.12)) if leaf else g)))  # no zero-length dots
                draw(k)

        draw(root)
        ax.cla()
        ax.set_xlim(0, S)
        ax.set_ylim(S, 0)
        ax.axis("off")
        fig.patch.set_facecolor(dim(BG))
        sx, sy = zip(*[xy(1.0, th) for th in leaf_theta.values()])
        ax.scatter(sx, sy, s=pt(2 * 2.6 * SS) ** 2, c=[dim(SLOT)], linewidths=0, zorder=1)  # the empty slots
        if segs:
            ax.add_collection(LineCollection(segs, colors=cols, linewidths=pt(1.5 * SS), capstyle="round", zorder=2))
        lit, halo = [], []
        for nm, t in t_of.items():
            if p[nm] <= 0:
                continue
            x, y = xy(1.0, leaf_theta[nm] if nm in leaf_theta else unpl_th[nm])
            c = dim(COL[by_name[nm]["ferm"]])
            lit.append((x, y, (*c, p[nm] * vis)))
            q = float(np.clip((tau - t - 0.3 * GROW) / 1.8, 0, 1))
            if 0 < q < 1:
                halo.append((x, y, 4.6 + 13 * q, (*c, 0.5 * (1 - q) ** 1.2 * vis)))
        if lit:
            ax.scatter([a for a, _, _ in lit], [b for _, b, _ in lit], s=pt(2 * 4.6 * SS) ** 2,
                       c=[c for _, _, c in lit], linewidths=0, zorder=4)
        for x, y, rad, c in halo:
            ax.scatter([x], [y], s=pt(2 * rad * SS) ** 2, facecolors="none", edgecolors=[c], linewidths=pt(1.1 * SS), zorder=3)
        ax.scatter([C], [C], s=pt(2 * 0.235 * RING) ** 2, c=[dim(BG)], linewidths=0, zorder=6)  # clear hub for the year
        fig.canvas.draw()
        big = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
        ev = [(t, y) for t, y in events if t <= tau]
        if ev:
            # The year at the hub, drawn at 2x so glyphs can move by fractions of a pixel. Only the digits that
            # change move: the old one rises away just before the new one rises into place, so the label never
            # goes dark and the two barely overlap.
            t0, y0 = ev[-1]
            prev = ev[-2][1] if len(ev) > 1 else None
            e = float(smooth((tau - t0) / 0.6))
            leave = float(smooth(e * 1.7))  # the old digit is gone by e = 0.59 ...
            arrive = float(smooth((e - 0.35) / 0.65))  # ... the new one starts at e = 0.35
            d = ImageDraw.Draw(big)
            cell = max(font.getlength(str(k)) for k in range(10))  # fixed-width cells, so nothing shifts sideways
            x0 = S / 2 - 2 * cell
            rise = 0.30 * font.size

            def put(ch, i, dy, al):
                if al * vis > 0.01:
                    fill = tuple(int(BG[k] + (TEXT[k] - BG[k]) * al * vis) for k in range(3))
                    d.text((x0 + (i + 0.5) * cell, S / 2 + dy), ch, font=font, fill=fill, anchor="mm")

            for i, ch in enumerate(str(y0)):
                old = str(prev)[i] if prev else None
                if old == ch:
                    put(ch, i, 0, 1.0)
                else:
                    if old:
                        put(old, i, -rise * leave, 1 - leave)
                    put(ch, i, rise * (1 - arrive), arrive)
        return big.resize((SIZE, SIZE), Image.LANCZOS)

    cum = 0
    for t, y in events:
        cum += sum(1 for r in recs if r["year"] == y)
        print(f"  {t:5.1f}s  {y}  -> {cum} genera")
    assert cum == len(recs), "the timeline does not account for every genus in the CSV"

    def render(g):
        if g < OPEN:
            return frame(t_final)  # open on the finished tree
        if g < OPEN + DISSOLVE:
            return frame(t_final, 1 - float(smooth((g - OPEN) / DISSOLVE)))  # dissolve it to the empty slots
        return frame(g - OPEN - DISSOLVE)  # rebuild it year by year, ending on the same finished tree

    base = banner_base()

    def compose(tree):
        img = base.copy()
        img.paste(tree, (0, 0))
        return img

    frames = [compose(render(i / FPS)) for i in range(nf)]
    seam = np.abs(np.asarray(frames[0], int) - np.asarray(frames[-1], int)).max()
    assert seam == 0, "the loop does not close: first and last frames differ"

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is needed to write the small GIF")
    # One 256-colour palette for the whole animation, built in two parts. ffmpeg's own palettegen would look only at
    # the pixels that change (the tree) or be swamped by the static gradient, so the gradient and title get their own
    # colours (quantised from the banner base) and the tree its own (48, tuned across the tree frames as before).
    with tempfile.TemporaryDirectory() as tmp:
        for i, f in enumerate(frames):
            f.save(os.path.join(tmp, f"f{i:04d}.png"))
        tree_pal = os.path.join(tmp, "tree_palette.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%04d.png"),
                        "-vf", f"crop={SIZE}:{SIZE}:0:0,palettegen=max_colors=48:stats_mode=diff", tree_pal], check=True)
        tree_cols = np.asarray(Image.open(tree_pal).convert("RGB")).reshape(-1, 3)
        tree_cols = np.unique(tree_cols, axis=0)
        grad_cols = np.unique(np.asarray(base)[0], axis=0)  # the gradient's exact colours: no banding beyond 8-bit
        room = 256 - len(tree_cols) - len(grad_cols)
        assert room >= 24, f"the gradient alone takes {len(grad_cols)} colours"
        arr = np.asarray(base)
        ink_mask = (arr != arr[0:1]).any(axis=2)  # the pixels the text touched; the palette is spent on them
        q = Image.fromarray(arr[ink_mask].reshape(1, -1, 3).astype(np.uint8)).quantize(colors=room, method=Image.MEDIANCUT, dither=Image.NONE)
        text_cols = np.asarray(q.getpalette(), np.uint8).reshape(-1, 3)[: len(set(q.getdata()))]
        base_cols = np.concatenate([grad_cols, text_cols])
        cols = np.concatenate([base_cols, tree_cols])
        assert len(cols) <= 256, f"palette has {len(cols)} colours"
        pal_img = Image.new("RGB", (16, 16), tuple(int(v) for v in cols[0]))
        pal_img.putdata([tuple(int(v) for v in c) for c in cols] + [tuple(int(v) for v in cols[0])] * (256 - len(cols)))
        pal_path = os.path.join(tmp, "palette.png")
        pal_img.save(pal_path)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%04d.png"),
                        "-i", pal_path, "-lavfi", "paletteuse=dither=none:diff_mode=rectangle", "-loop", "0", out_gif], check=True)
    pal_p = Image.new("P", (1, 1))
    pal_p.putpalette([int(v) for c in cols for v in c] + [0] * (768 - 3 * len(cols)))
    frames[0].quantize(palette=pal_p, dither=Image.NONE).save(out_png, optimize=True)
    print(f"wrote {os.path.relpath(out_gif, REPO)} ({os.path.getsize(out_gif) / 1024:.0f} KB, {nf} frames, {t_end:.1f}s loop)")
    print(f"wrote {os.path.relpath(out_png, REPO)} ({os.path.getsize(out_png) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
