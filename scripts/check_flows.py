#!/usr/bin/env python3
"""Check guide flowcharts before a build.

    python3 scripts/check_flows.py                 # every guide with a src/flows/<slug>.json
    python3 scripts/check_flows.py slug [slug...]  # just these

For each guide: the English and Chinese bodies hold the same placeholders, in the same order,
each one right after a paragraph; every placeholder has a spec and every spec is placed; the
spec draws in both languages within the limits (7 nodes, 4 columns); every node has an English
and a Chinese label; labels stay short enough to sit in a box (3 lines of label, 3 of note);
captions have both languages and no dashes. Exit code 1 on any problem.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import flows  # noqa: E402

PH = re.compile(r'<figure class="flow" data-flow="([a-z0-9-]+)"></figure>')


def body(path):
    return path.read_text().split("-->", 1)[1]


def check(slug):
    errs = []
    en_f, zh_f = ROOT / "src/blog" / f"{slug}.html", ROOT / "src/zh/blog" / f"{slug}.html"
    spec_f = ROOT / "src/flows" / f"{slug}.json"
    if not spec_f.exists():
        return [f"{slug}: no src/flows/{slug}.json"]
    try:
        specs = flows.load(slug, ROOT)
    except SystemExit as e:
        return [str(e)]
    en_ids = PH.findall(body(en_f))
    zh_ids = PH.findall(body(zh_f)) if zh_f.exists() else None
    if not en_ids:
        errs.append(f"{slug}: no placeholder in the English body")
    if zh_ids is not None and zh_ids != en_ids:
        errs.append(f"{slug}: placeholders differ, en {en_ids} zh {zh_ids}")
    for fid in set(en_ids) - set(specs):
        errs.append(f"{slug}: placeholder '{fid}' has no spec")
    for fid in set(specs) - set(en_ids):
        errs.append(f"{slug}: spec '{fid}' is never placed")
    for path in [en_f] + ([zh_f] if zh_ids is not None else []):
        for m in PH.finditer(body(path)):
            before = body(path)[: m.start()].rstrip()
            if not before.endswith("</p>"):
                errs.append(f"{path.name}: '{m.group(1)}' should sit right after a paragraph")
    for fid, spec in specs.items():
        for lang in ("en", "zh"):
            if not (spec.get("caption") or {}).get(lang):
                errs.append(f"{slug} {fid}: caption missing {lang}")
        for n in spec["nodes"]:
            for lang in ("en", "zh"):
                if not (n.get("label") or {}).get(lang):
                    errs.append(f"{slug} {fid} {n['id']}: label missing {lang}")
                if n.get("note") and not n["note"].get(lang):
                    errs.append(f"{slug} {fid} {n['id']}: note missing {lang}")
            if "col" not in n or "row" not in n:
                errs.append(f"{slug} {fid} {n['id']}: needs col and row")
            elif n["col"] >= spec.get("cols", 1):
                errs.append(f"{slug} {fid} {n['id']}: col {n['col']} is outside cols {spec.get('cols', 1)}")
        cells = {}
        for n in spec["nodes"]:
            for r in range(n.get("row", 0), n.get("row", 0) + n.get("span", 1)):
                k = (n.get("col"), r)
                if k in cells:
                    errs.append(f"{slug} {fid}: {n['id']} and {cells[k]} overlap at col {k[0]} row {k[1]}")
                cells[k] = n["id"]
        cols = spec.get("cols", 1)
        inner = (flows.WIDE_W - flows.GAP_X * (cols - 1)) / cols - flows.PAD * 2
        for lang in ("en", "zh"):
            for n in spec["nodes"]:
                label, note, _ = flows._box_lines(n, lang, inner)
                if len(label) > 3:
                    errs.append(f"{slug} {fid} {n['id']} ({lang}): label wraps to {len(label)} lines, shorten it")
                if len(note) > 3:
                    errs.append(f"{slug} {fid} {n['id']} ({lang}): note wraps to {len(note)} lines, shorten it")
            try:
                flows.render(spec, lang, fid)
            except Exception as e:  # noqa: BLE001
                errs.append(f"{slug} {fid} ({lang}): does not draw: {e}")
    return errs


def main():
    slugs = sys.argv[1:] or sorted(p.stem for p in (ROOT / "src/flows").glob("*.json"))
    bad = 0
    for s in slugs:
        errs = check(s)
        if errs:
            bad += 1
            print("\n".join("  " + e for e in errs))
        else:
            print(f"ok {s}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
