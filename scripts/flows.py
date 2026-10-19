"""Flowcharts inside Amber Lan's guides.

A guide marks where a diagram goes with an empty placeholder in its body:

    <figure class="flow" data-flow="report-flow"></figure>

and describes the diagram in src/flows/<slug>.json, shared by English and Chinese:

    {
      "report-flow": {
        "caption": {"en": "...", "zh": "..."},
        "cols": 4,
        "nodes": [
          {"id": "crm", "col": 0, "row": 0, "kind": "source",
           "label": {"en": "CRM and scheduler", "zh": "..."}, "note": {"en": "queried live", "zh": "..."}},
          {"id": "page", "col": 2, "row": 0, "span": 2, "label": {...}}
        ],
        "edges": [["crm", "page"], ["page", "review", {"en": "draft", "zh": "..."}]]
      }
    }

Kinds: step (default), source (dashed), out (filled, the result) and human (amber, the
step where a person decides). Rules (house rules, October 2026): at most 7 nodes, at most
4 columns, one idea per diagram, every box taken from what the article already says.

The figure is drawn twice: a wide grid for desktop and a single stacked column for phones
(CSS shows one). Labels stay real SVG text. A visually hidden paragraph reads the diagram
as a list for screen readers and for llms-full.txt, which drops the SVG itself.
"""
import json
import re
from html import escape
from pathlib import Path

WIDE_W, NARROW_W = 640, 340
GAP_X, GAP_Y, PAD = 30, 44, 14
FS_LABEL, FS_NOTE, FS_EDGE = 14.5, 12, 11.5
LH_LABEL, LH_NOTE = 18, 15
MAX_NODES, MAX_COLS = 7, 4

LEGEND = {"en": "The amber box is the step where a person decides.", "zh": "琥珀色方框是由人做决定的一步。"}
READ_AS_LIST = {"en": "Diagram, read as a list:", "zh": "图示内容（文字版）："}
GOES_TO = {"en": "leads to", "zh": "接着是"}


def _cjk(s):
    return bool(re.search(r"[㐀-鿿]", s))


def _width(s, fs):
    w = 0.0
    for ch in s:
        if re.match(r"[㐀-鿿　-〿＀-￯]", ch):
            w += fs
        elif ch in "il.,:;'|!() ":
            w += fs * 0.3
        elif ch.isupper() or ch in "mwMW":
            w += fs * 0.68
        else:
            w += fs * 0.53
    return w


def wrap(text, fs, max_w):
    """Break a label into lines that fit max_w. Chinese breaks between characters."""
    lines, line = [], ""
    tokens = list(text) if _cjk(text) and " " not in text.strip() else re.findall(r"\S+\s*", text)
    if _cjk(text):  # mixed text: keep Latin words whole, split Chinese per character
        tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9.'’+-]*\s*|\s+|.", text)
    for t in tokens:
        if line and _width((line + t).rstrip(), fs) > max_w:
            lines.append(line.rstrip())
            line = t.lstrip()
        else:
            line += t
    if line.strip():
        lines.append(line.rstrip())
    return lines


def load(slug, root):
    f = Path(root) / "src" / "flows" / f"{slug}.json"
    if not f.exists():
        return {}
    raw = f.read_text()
    if "—" in raw or "–" in raw:
        raise SystemExit(f"{f.name}: contains a dash, refusing to build")
    specs = json.loads(raw)
    for fid, spec in specs.items():
        nodes = spec["nodes"]
        if len(nodes) > MAX_NODES:
            raise SystemExit(f"{f.name} {fid}: {len(nodes)} nodes, the limit is {MAX_NODES}")
        if spec.get("cols", 1) > MAX_COLS:
            raise SystemExit(f"{f.name} {fid}: more than {MAX_COLS} columns")
        ids = {n["id"] for n in nodes}
        for e in spec["edges"]:
            if e[0] not in ids or e[1] not in ids:
                raise SystemExit(f"{f.name} {fid}: edge {e[0]} -> {e[1]} names a missing node")
    return specs


def _t(v, lang):
    return (v or {}).get(lang) or (v or {}).get("en") or ""


def _box_lines(n, lang, inner_w):
    label = wrap(_t(n["label"], lang), FS_LABEL, inner_w)
    note = wrap(_t(n.get("note"), lang), FS_NOTE, inner_w) if n.get("note") else []
    h = PAD * 2 + len(label) * LH_LABEL + (len(note) * LH_NOTE + 4 if note else 0)
    return label, note, h


def _arrow(x1, y1, x2, y2, pts=None):
    """A path through the points, ending in a small arrowhead at (x2, y2)."""
    pts = [(x1, y1)] + (pts or []) + [(x2, y2)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    px, py = pts[-2]
    dx, dy = x2 - px, y2 - py
    ln = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / ln, dy / ln
    s = 6
    head = (f"M{x2 - ux * s - uy * s * 0.75:.1f},{y2 - uy * s + ux * s * 0.75:.1f} L{x2:.1f},{y2:.1f} "
            f"L{x2 - ux * s + uy * s * 0.75:.1f},{y2 - uy * s - ux * s * 0.75:.1f}")
    return f'<path class="fl-edge" d="{d}"/><path class="fl-head" d="{head}"/>'


def _node_svg(n, x, y, w, h, label, note):
    kind = n.get("kind", "step")
    out = [f'<rect class="fl-box {kind}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="10"/>']
    block = len(label) * LH_LABEL + (len(note) * LH_NOTE + 4 if note else 0)
    ty = y + (h - block) / 2 + LH_LABEL * 0.78
    for ln in label:
        out.append(f'<text class="fl-label" x="{x + w / 2:.1f}" y="{ty:.1f}" text-anchor="middle">{escape(ln)}</text>')
        ty += LH_LABEL
    if note:
        ty += 4
        for ln in note:
            out.append(f'<text class="fl-note" x="{x + w / 2:.1f}" y="{ty - 3:.1f}" text-anchor="middle">{escape(ln)}</text>')
            ty += LH_NOTE
    return out


def _wide(spec, lang):
    cols = spec.get("cols", 1)
    cw = (WIDE_W - GAP_X * (cols - 1)) / cols
    nodes = spec["nodes"]
    nrows = max(n["row"] + n.get("span", 1) for n in nodes)
    sizes = {n["id"]: _box_lines(n, lang, cw - PAD * 2) for n in nodes}
    rh = [0.0] * nrows
    for n in nodes:
        if n.get("span", 1) == 1:
            rh[n["row"]] = max(rh[n["row"]], sizes[n["id"]][2])
    rh = [h or 56 for h in rh]
    ry = [0.0]
    for h in rh[:-1]:
        ry.append(ry[-1] + h + GAP_Y)
    geo = {}
    for n in nodes:
        r, sp = n["row"], n.get("span", 1)
        x = n["col"] * (cw + GAP_X)
        y = ry[r]
        h = ry[r + sp - 1] + rh[r + sp - 1] - y
        if sp == 1:
            h = rh[r]
        elif sp >= 3:  # a box across three or more rows keeps its own height, centred; arrows branch to it
            own = max(sizes[n["id"]][2], 56)
            if h > own + 40:
                y, h = y + (h - own) / 2, own
        geo[n["id"]] = (x, y, cw, h)
    H = ry[-1] + rh[-1]
    parts = []
    for e in spec["edges"]:
        ax, ay, aw, ah = geo[e[0]]
        bx, by, bw, bh = geo[e[1]]
        lo, hi = max(ay, by), min(ay + ah, by + bh)
        # A straight line only when one box's centre lies within the other's height; otherwise an elbow.
        if lo < hi and not (ay <= by + bh / 2 <= ay + ah or by <= ay + ah / 2 <= by + bh):
            lo = hi
        if bx > ax + aw - 1 and lo < hi:  # side by side with overlapping heights: straight line
            y = by + bh / 2 if ay <= by + bh / 2 <= ay + ah else ay + ah / 2
            parts.append(_arrow(ax + aw, y, bx - 2, y))
            mx, my = (ax + aw + bx) / 2, y - 6
        elif bx + bw < ax + 1 and lo < hi:
            y = (lo + hi) / 2
            parts.append(_arrow(ax, y, bx + bw + 2, y))
            mx, my = (ax + bx + bw) / 2, y - 6
        elif abs(ax - bx) < 1:  # same column
            if by > ay:
                parts.append(_arrow(ax + aw / 2, ay + ah, bx + bw / 2, by - 2))
                mx, my = ax + aw / 2 + 8, (ay + ah + by) / 2
            else:
                parts.append(_arrow(ax + aw / 2, ay, bx + bw / 2, by + bh + 2))
                mx, my = ax + aw / 2 + 8, (by + bh + ay) / 2
        else:  # elbow: across the gap, then along the column gap, then in
            if bx > ax:
                gx = bx - GAP_X / 2
                y1, y2 = ay + ah / 2, by + bh / 2
                parts.append(_arrow(ax + aw, y1, bx - 2, y2, [(gx, y1), (gx, y2)]))
            else:
                gx = bx + bw + GAP_X / 2
                y1, y2 = ay + ah / 2, by + bh / 2
                parts.append(_arrow(ax, y1, bx + bw + 2, y2, [(gx, y1), (gx, y2)]))
            mx, my = gx + 6, (ay + ah / 2 + by + bh / 2) / 2
        if len(e) > 2 and e[2]:
            anchor = "middle" if abs(ax - bx) > 1 and (lo < hi) else "start"
            parts.append(f'<text class="fl-elabel" x="{mx:.1f}" y="{my:.1f}" text-anchor="{anchor}">{escape(_t(e[2], lang))}</text>')
    for n in nodes:
        x, y, w, h = geo[n["id"]]
        label, note, _ = sizes[n["id"]]
        parts += _node_svg(n, x, y, w, h, label, note)
    return WIDE_W, H, parts


def _narrow(spec, lang):
    """One column in the order the nodes are listed, arrows where an edge joins neighbours."""
    nodes = spec["nodes"]
    joined = {(e[0], e[1]) for e in spec["edges"]} | {(e[1], e[0]) for e in spec["edges"]}
    w = NARROW_W
    y, parts, prev = 0.0, [], None
    for n in nodes:
        label, note, h = _box_lines(n, lang, w - PAD * 2)
        if prev is not None:
            if (prev[0], n["id"]) in joined:
                parts.append(_arrow(w / 2, prev[1], w / 2, y + 28 - 2))
            y += 28
        parts += _node_svg(n, 0, y, w, h, label, note)
        prev = (n["id"], y + h)
        y += h
    return w, y, parts


def as_text(spec, lang):
    """The diagram as sentences, for screen readers and llms-full.txt."""
    names = {n["id"]: _t(n["label"], lang) + (f" ({_t(n.get('note'), lang)})" if n.get("note") else "") for n in spec["nodes"]}
    out = []
    for n in spec["nodes"]:
        nxt = [names[e[1]].split(" (")[0] for e in spec["edges"] if e[0] == n["id"]]
        s = names[n["id"]]
        if nxt:
            s += (" " if lang == "en" else "，") + GOES_TO[lang] + " " + ("、" if lang == "zh" else ", ").join(nxt)
        out.append(s + ("." if lang == "en" else "。"))
    return " ".join(out) if lang == "en" else "".join(out)


def render(spec, lang, fid):
    ww, wh, wp = _wide(spec, lang)
    nw, nh, np_ = _narrow(spec, lang)
    cap = _t(spec["caption"], lang)
    legend = any(n.get("kind") == "human" for n in spec["nodes"])
    svg = lambda cls, w, h, p: (f'<svg class="{cls}" viewBox="-2 -2 {w + 4:.0f} {h + 4:.0f}" width="{w + 4:.0f}" height="{h + 4:.0f}" '
                                f'aria-hidden="true" focusable="false">{"".join(p)}</svg>')
    return (f'<figure class="flow" id="flow-{fid}">'
            f'{svg("flow__wide", ww, wh, wp)}{svg("flow__narrow", nw, nh, np_)}'
            f'<p class="visually-hidden">{escape(READ_AS_LIST[lang])} {escape(as_text(spec, lang))}</p>'
            f'<figcaption>{escape(cap)}' + (f' <span class="flow__legend">{escape(LEGEND[lang])}</span>' if legend else "") +
            '</figcaption></figure>')


def expand(body, slug, lang, root):
    """Swap each placeholder in a guide body for its drawn figure."""
    specs = None

    def sub(m):
        nonlocal specs
        if specs is None:
            specs = load(slug, root)
        fid = m.group(1)
        if fid not in specs:
            raise SystemExit(f"{slug}: no flow '{fid}' in src/flows/{slug}.json")
        return render(specs[fid], lang, fid)

    return re.sub(r'<figure class="flow" data-flow="([a-z0-9-]+)"></figure>', sub, body)
