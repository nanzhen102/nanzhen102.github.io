"""One-off: collapse the 442-tip core-genome tree to a genus-level tree (rooted on the Carnobacterium outgroup)
and write assets/lactobacillaceae/genus_tree.json, which scripts/make_life_tree.py reads.

It needs the lab folder (treefile + species database) that is NOT in this repo, so it only runs on the author's machine.
Re-run it only when the tree itself changes, not when the genus CSV does."""
import csv, json, os, sys
from Bio import Phylo
BASE = "/Users/nanzhen/Documents/1_phd_2020/5_doctoral_program/0.1_type_strain_tree"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = sorted(__import__("glob").glob(os.path.join(REPO, "assets", "lactobacillaceae", "genus_*.csv")))[-1]

def build():
    tree = Phylo.read(f"{BASE}/12_tree_202412/5_tree/TypeStrainDB_core_alignment_442.fasta.treefile", "newick")
    db = {}
    for r in csv.DictReader(open(f"{BASE}/18_202611_automate/0_baseline_202611/full_name_type_strain_DB_202506.csv", encoding="utf-8-sig")):
        db.setdefault(r["ACC"].strip(), r["Genus"].strip())
    for t in list(tree.get_terminals()):
        if t.name not in db: tree.prune(t)                          # 3 unmatched tips dropped
    tips = {t.name: db[t.name] for t in tree.get_terminals()}
    out = [t for t in tree.get_terminals() if tips[t.name] == "Carnobacterium"]
    tree.root_with_outgroup(*out)
    ingroup = [c for c in tree.root.clades if not all(tips[t.name] == "Carnobacterium" for t in c.get_terminals())][0]
    depth = tree.depths()
    base = depth[ingroup]
    # collapse each genus to one leaf at its crown
    genera = sorted({g for g in tips.values() if g != "Carnobacterium"})
    problems = {}
    leaf_of = {}
    for g in genera:
        ts = [t for t in ingroup.get_terminals() if tips[t.name] == g]
        node = ts[0] if len(ts) == 1 else ingroup.common_ancestor(ts)
        extra = {tips[t.name] for t in node.get_terminals()} - {g}
        if extra: problems[g] = sorted(extra)
        leaf_of[g] = node
    def conv(n):
        gs = [g for g, node in leaf_of.items() if node is n]
        if gs: return {"genus": gs[0], "d": depth[n] - base, "n": len(n.get_terminals())}
        kids = [conv(c) for c in n.clades]
        kids = [k for k in kids if k]
        if len(kids) == 1: return kids[0]
        return {"kids": kids, "d": depth[n] - base}
    return conv(ingroup), problems, genera

def leaves(n): return [n["genus"]] if "genus" in n else [g for k in n["kids"] for g in leaves(k)]

if __name__ == "__main__":
    root, problems, genera = build()
    print("genera:", len(genera), "| genera whose clade contains other genera (not monophyletic):", problems or "none")
    order = {r["Tax name"]: int(r["Y_order"]) for r in csv.DictReader(open(CSV, encoding="utf-8-sig")) if r["Y_order"].strip()}
    print("genera in tree not in the CSV order:", sorted(set(genera) - set(order)), "| CSV order not in tree:", sorted(set(order) - set(genera)))
    # can the children of every node be arranged so the page's tree order is contiguous?
    bad = []
    def check(n):
        if "genus" in n: return
        ys = sorted(order[g] for g in leaves(n))
        if ys[-1] - ys[0] + 1 != len(ys): bad.append((len(ys), ys[0], ys[-1]))
        for k in n["kids"]: check(k)
    check(root)
    print("clades whose members are NOT contiguous in the page's tree order:", len(bad), bad[:6])
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "assets", "lactobacillaceae", "genus_tree.json")
    json.dump(root, open(out, "w"), indent=1); print("wrote", out)
