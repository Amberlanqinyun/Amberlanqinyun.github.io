#!/usr/bin/env python3
"""
Flow AI editorial diagrams, generated in the flowai-mono brand system.

Two inks on the Warm Ink substrate: Cream carries structure, type and rules
through density changes; Amber carries exactly one accent event per image.
Google Sans Flex throughout, sentence case, uppercase only on tracked labels.

Output: /assets/diagram-*.svg  (16:9, self-contained, no external fonts assumed
beyond the site's own face, with a system fallback stack).
"""

import math
import pathlib

# ---- Inks (design-system/colors.json) -------------------------------------
INK = "#0E0E0D"      # substrate, Warm Ink
CREAM = "#FAF8F3"    # dominant plate
AMBER = "#E4A43C"    # accent plate, one job per image

FONT = "'Google Sans Flex','Google Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"

W, H = 1600, 900
OUT = pathlib.Path(__file__).parent


def cream(alpha):
    """Cream at a density. A density change of one plate, never a new ink."""
    return f'fill="{CREAM}" fill-opacity="{alpha}"'


def head(title, desc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">{title}</title><desc id="d">{desc}</desc>
<defs>
  <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2"/>
    <feColorMatrix type="saturate" values="0"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="{INK}"/>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.028"/>'''


def label(x, y, text, size=13, anchor="start", alpha=0.54, track=0.2, weight=500):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{track}em" text-transform="uppercase" fill="{CREAM}" fill-opacity="{alpha}" '
            f'text-anchor="{anchor}">{text.upper()}</text>')


def txt(x, y, text, size, weight=400, alpha=1.0, anchor="start", track=0, color=CREAM):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{track}em" fill="{color}" fill-opacity="{alpha}" text-anchor="{anchor}">{text}</text>')


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def arc(cx, cy, r, a0, a1, alpha, dash=None, width=1):
    x0, y0 = polar(cx, cy, r, a0)
    x1, y1 = polar(cx, cy, r, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    d = f'M {x0:.1f} {y0:.1f} A {r} {r} 0 {large} {sweep} {x1:.1f} {y1:.1f}'
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="{d}" fill="none" stroke="{CREAM}" stroke-opacity="{alpha}" '
            f'stroke-width="{width}"{dash_attr}/>')


# ===========================================================================
# 1. The system map — three outcomes, the systems that sit under them.
#    Focal event: the orbital fan, cropped hard at the right edge.
#    Release zone: the lower-left quadrant, deliberately empty.
#    Amber's one job: the centre node. Everything orbits the pipeline.
# ===========================================================================
def system_map(systems, claim_label, boxes=None):
    # The centre stays on canvas: it is the Amber accent and the thing the
    # whole fan orbits. Each arc gets its own angular span so the eleven
    # labels interleave instead of stacking on one another.
    CX, CY = 1408, 812
    # The fan orbits a centre at the bottom right, so the LARGEST radius sits
    # highest and reads first. Radii therefore run large to small, putting
    # Get found at the top and Keep customers at the bottom: the order a
    # visitor actually walks. Spans are reversed with them so each arc keeps
    # the angular span it was tuned against.
    RADII = [548, 392, 236]
    SPANS = [(214, 252), (206, 262), (198, 250)]
    s = [head("Flow AI system map",
              "Three outcomes with the marketing systems that sit underneath each one, "
              "arranged as three arcs around a single pipeline.")]

    # -- left column: the counterweight to the fan -------------------------
    s.append(label(96, 156, "The system map", size=15))
    s.append(txt(96, 262, "Three outcomes.", 72, weight=600, track=-0.03))
    s.append(txt(96, 346, f"{claim_label} systems", 72, weight=600, track=-0.03))
    s.append(txt(96, 430, "underneath.", 72, weight=600, track=-0.03, alpha=0.38))
    s.append(txt(96, 500, "Start where the gap is widest.", 26, weight=300, alpha=0.72))

    # thin rule, the poster's one ruled band
    s.append(f'<path d="M 96 556 L 600 556" stroke="{CREAM}" stroke-opacity="0.2" stroke-width="1"/>')

    # -- the fan ------------------------------------------------------------
    for i, (r, group, span) in enumerate(zip(RADII, systems, SPANS)):
        s.append(arc(CX, CY, r, span[0] - 6, span[1] + 8, [0.30, 0.21, 0.15][i], width=1))

        # outcome name, set off the arc's lower-left end
        # dropped below the arc's terminus so it never fouls a system label
        ox, oy = polar(CX, CY, r, span[0] - 6)
        s.append(f'<path d="M {ox:.1f} {oy:.1f} L {ox - 14:.1f} {oy + 22:.1f}" stroke="{CREAM}" '
                 f'stroke-opacity="0.2" stroke-width="1"/>')
        s.append(txt(ox - 22, oy + 44, group["name"], 30, weight=600, anchor="end",
                     alpha=0.95, track=-0.02))
        if boxes is not None:
            boxes.append((group["name"], 30, ox - 22, oy + 44, "end"))

        # the systems, as nodes along the arc
        n = len(group["items"])
        for j, name in enumerate(group["items"]):
            deg = span[0] + (span[1] - span[0]) * ((j + 0.5) / n)
            x, y = polar(CX, CY, r, deg)
            lx, ly = polar(CX, CY, r - 22, deg)
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{CREAM}" fill-opacity="0.9"/>')
            s.append(f'<path d="M {x:.1f} {y:.1f} L {lx:.1f} {ly:.1f}" stroke="{CREAM}" '
                     f'stroke-opacity="0.22" stroke-width="1"/>')
            s.append(txt(lx - 10, ly + 7, name, 22, weight=400, anchor="end", alpha=0.74))
            if boxes is not None:
                boxes.append((name, 22, lx - 10, ly + 7, "end"))

    # -- Amber: the one accent event, and the thing the fan orbits ---------
    s.append(f'<circle cx="{CX}" cy="{CY}" r="8" fill="{AMBER}"/>')
    s.append(f'<circle cx="{CX}" cy="{CY}" r="30" fill="none" stroke="{AMBER}" stroke-opacity="0.32" stroke-width="1"/>')
    s.append(txt(CX - 46, CY + 8, "One pipeline", 22, weight=600, anchor="end", color=AMBER))

    s.append("</svg>")
    return "\n".join(s)


# ===========================================================================
# 2. Pillar cards — one per outcome. A repeated object system: the same
#    arc geometry, one band lit, the other two held back.
# ===========================================================================
def pillar(systems, index):
    CX, CY = 1408, 812
    # Large to small, matching the system map: Get found reads first.
    RADII = [542, 396, 250]
    SPAN = (196, 264)
    g = systems[index]
    s = [head(f"Flow AI — {g['name']}", g["line"])]

    s.append(label(96, 156, g["name"], size=15))
    s.append(txt(96, 268, g["head"][0], 66, weight=600, track=-0.03))
    s.append(txt(96, 348, g["head"][1], 66, weight=600, track=-0.03, alpha=0.38))
    s.append(txt(96, 420, g["line"], 26, weight=300, alpha=0.72))

    for i, r in enumerate(RADII):
        lit = (i == index)
        s.append(arc(CX, CY, r, SPAN[0] - 4, SPAN[1] + 4, 0.34 if lit else 0.08, width=1))
        if not lit:
            continue
        n = len(g["items"])
        for j, name in enumerate(g["items"]):
            deg = SPAN[0] + (SPAN[1] - SPAN[0]) * ((j + 0.72) / n)
            x, y = polar(CX, CY, r, deg)
            lx, ly = polar(CX, CY, r - 22, deg)
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{CREAM}" fill-opacity="0.95"/>')
            s.append(f'<path d="M {x:.1f} {y:.1f} L {lx:.1f} {ly:.1f}" stroke="{CREAM}" stroke-opacity="0.25"/>')
            s.append(txt(lx - 10, ly + 8, name, 24, weight=400, anchor="end", alpha=0.88))

    s.append(f'<circle cx="{CX}" cy="{CY}" r="8" fill="{AMBER}"/>')
    s.append("</svg>")
    return "\n".join(s)


# ===========================================================================
# 3. Read. Install. Run. — a ruled information poster. Three steps on one
#    baseline; Amber marks only the step the visitor is at first.
# ===========================================================================
def process():
    """The three steps drawn to length, not to a grid.

    The page already renders these steps as three equal cards. Three evenly
    spaced dots on a line says exactly what three equal cards say, so an
    earlier version of this plate was pure duplication — it even repeated the
    cards' body copy word for word.

    What the card grid cannot show is that the steps are not equal. Read and
    Install happen once, in week one. Run repeats every month and does not
    end. The grid renders all three as siblings, which is a lie about the
    shape of the engagement and hides the part that actually compounds. So
    the geometry carries the asymmetry: a finite cream segment for the
    one-off work, then an amber segment that runs off the right edge because
    it never stops. The words stay in the cards; the plate keeps the shape.
    """
    s = [head("Week one to every month",
              "The three steps drawn to length on one baseline. Read and Install sit inside a short "
              "finite segment marked once, in week one. Run sits on an amber segment marked every month "
              "from then on, which runs off the right edge because the work does not end.")]

    s.append(label(96, 156, "How it works", size=15))
    s.append(txt(96, 274, "Week one to", 76, weight=600, track=-0.03))
    s.append(txt(96, 358, "every month.", 76, weight=600, track=-0.03, alpha=0.38))
    s.append(txt(96, 428, "Two steps happen once. The third never stops.", 26, weight=300, alpha=0.72))

    BASE = 640
    SPLIT = 720          # where the one-off work ends and the monthly run begins

    # Phase one: solid, finite, and it visibly ends.
    s.append(f'<path d="M 96 {BASE} L {SPLIT} {BASE}" stroke="{CREAM}" stroke-opacity="0.2"/>')
    # Phase two: the accent event. Dotted because it repeats, and it leaves the
    # canvas rather than terminating, because the run has no last month.
    s.append(f'<path d="M {SPLIT} {BASE} L 1504 {BASE}" stroke="{AMBER}" stroke-opacity="0.5" '
             f'stroke-width="3" stroke-dasharray="2 12" stroke-linecap="round"/>')

    s.append(label(96, BASE - 104, "Once, in week one", size=13, alpha=0.38))
    s.append(label(SPLIT, BASE - 104, "Every month, from then on", size=13, alpha=0.38))
    s.append(f'<path d="M 96 {BASE - 86} L 96 {BASE - 58}" stroke="{CREAM}" stroke-opacity="0.14"/>')
    s.append(f'<path d="M {SPLIT} {BASE - 86} L {SPLIT} {BASE - 58}" stroke="{CREAM}" stroke-opacity="0.14"/>')

    # x positions are the real thing being said: Read and Install crowd into the
    # short phase, Run sits alone out on the long one.
    steps = [("01", "Read", 240, False), ("02", "Install", 480, False), ("03", "Run", 860, True)]

    for num, name, x, ongoing in steps:
        col = AMBER if ongoing else CREAM
        op = 1.0 if ongoing else 0.34
        s.append(f'<circle cx="{x}" cy="{BASE}" r="7" fill="{col}" fill-opacity="{op}"/>')
        s.append(f'<path d="M {x} {BASE - 46} L {x} {BASE - 14}" stroke="{col}" stroke-opacity="{op * 0.5}"/>')
        s.append(txt(x, BASE - 62, num, 18, weight=500, alpha=0.54, track=0.16))
        s.append(txt(x, BASE + 78, name, 42, weight=600, track=-0.02))

    s.append("</svg>")
    return "\n".join(s)


SYSTEMS = [
    {"name": "Get found", "line": "Be the answer when someone searches.",
     "head": ("Be the answer.", "On Google and in ChatGPT."),
     "items": ["Positioning", "Search and AI search", "Content", "Social"]},
    {"name": "Get leads", "line": "Turn attention into enquiries.",
     "head": ("Turn attention", "into enquiries."),
     "items": ["Outbound", "Growth and conversion", "Launch", "Paid"]},
    {"name": "Keep customers", "line": "Stay in front of the people who know you.",
     "head": ("Stay in front", "of the people who know you."),
     "items": ["Community", "Measurement", "Reporting"]},
]

def collisions(boxes):
    """Approximate label boxes and report overlaps, so the fan is tuned
    against measurements rather than by eye. Width per glyph ~0.52em."""
    rects = []
    for text, size, x, y, anchor in boxes:
        w = len(text) * size * 0.52
        x0 = x - w if anchor == "end" else x
        rects.append((text, x0, x0 + w, y - size * 0.78, y + size * 0.24))
    hits = []
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
            if a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]:
                hits.append(f"{a[0]!r} x {b[0]!r}")
    return hits


if __name__ == "__main__":
    total = sum(len(g["items"]) for g in SYSTEMS)
    words = {10: "Ten", 11: "Eleven", 12: "Twelve"}
    boxes = []
    (OUT / "diagram-system-map.svg").write_text(system_map(SYSTEMS, words.get(total, str(total)), boxes))
    hits = collisions(boxes)
    print("label overlaps:", "none" if not hits else "")
    for h in hits:
        print("   !", h)
    for i, g in enumerate(SYSTEMS):
        slug = g["name"].lower().replace(" ", "-")
        (OUT / f"diagram-{slug}.svg").write_text(pillar(SYSTEMS, i))
    (OUT / "diagram-process.svg").write_text(process())
    print(f"systems listed: {total} -> label reads '{words.get(total)}'")
    for p in sorted(OUT.glob("diagram-*.svg")):
        print(f"  {p.name}  {p.stat().st_size / 1024:.1f} KB")
