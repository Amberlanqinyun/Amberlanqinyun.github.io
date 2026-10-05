"""Geometric pattern figures for the Flow AI guides.

A library of flat shapes (rings, zigzags, dot grids, stripes, arches, chevrons,
crosses, confetti) in cream on Warm Ink, with Amber as the one accent ink.
Each guide gets ONE element, centred, chosen for what the guide is about
(see ASSIGN). Everything is drawn here from geometry, so no stock art is used.
"""
import hashlib
import math
import random

INK = "#171715"
CREAM = "#5f5e5a"   # cream at ~35% over Warm Ink: present, never louder than the title
AMBER = "#6e5428"   # amber at ~40% over Warm Ink
W, H = 960, 540
SW = 7  # stroke width in canvas units (the card shows the canvas at ~0.4x)


class Canvas:
    def __init__(self):
        self.defs, self.body, self.n = [], [], 0

    def uid(self):
        self.n += 1
        return f"k{self.n}"

    def add(self, s):
        self.body.append(s)

    def clip(self, inner):
        cid = self.uid()
        self.defs.append(f'<clipPath id="{cid}">{inner}</clipPath>')
        return cid


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def stroke(color=CREAM, w=SW, extra=""):
    return f'fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{extra}'


# ------------------------------------------------------------------ shapes
# Every shape draws itself centred on (cx, cy) inside a box of side s.

def dot_triangle(c, cx, cy, s, r):
    half = s * 0.55
    tri = [(cx, cy - s / 2), (cx - half, cy + s / 2), (cx + half, cy + s / 2)]
    off = [(x + s * 0.12, y + s * 0.08) for x, y in tri]
    c.add(f'<polygon points="{pts(off)}" fill="{AMBER}"/>')
    cid = c.clip(f'<polygon points="{pts(tri)}"/>')
    step = s / 7
    dots = "".join(f'<circle cx="{cx - half + i * step:.1f}" cy="{cy - s / 2 + j * step:.1f}" r="{s * 0.028:.1f}" fill="{CREAM}"/>'
                   for i in range(9) for j in range(8))
    c.add(f'<g clip-path="url(#{cid})">{dots}</g>')


def zigzag(c, cx, cy, s, r):
    w, amp, n = s * 1.0, s * 0.11, 7
    for k in (0, 1):
        y0 = cy + (k - 0.5) * s * 0.2
        p = [(cx - w / 2 + i * w / n, y0 + (amp if i % 2 else -amp)) for i in range(n + 1)]
        c.add(f'<polyline points="{pts(p)}" {stroke()}/>')


def rings(c, cx, cy, s, r):
    n = r.randint(4, 6)
    for i in range(n):
        rad = s * 0.5 * (i + 1) / n
        col = AMBER if (i == n - 1 and r.random() < 0.4) else CREAM
        c.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" {stroke(col)}/>')


def stripes_square(c, cx, cy, s, r):
    a = s * 0.8
    cid = c.clip(f'<rect x="{cx - a / 2:.1f}" y="{cy - a / 2:.1f}" width="{a:.1f}" height="{a:.1f}"/>')
    gap = a / 7
    lines = "".join(f'<line x1="{cx - a + i * gap:.1f}" y1="{cy + a / 2:.1f}" x2="{cx + i * gap:.1f}" y2="{cy - a / 2:.1f}" stroke="{AMBER}" stroke-width="{gap * 0.42:.1f}"/>'
                    for i in range(-8, 20))
    c.add(f'<g clip-path="url(#{cid})">{lines}</g>')


def dot_grid(c, cx, cy, s, r):
    n = r.choice([6, 7, 8])
    step = s * 0.8 / (n - 1)
    x0, y0 = cx - s * 0.4, cy - s * 0.4
    c.add("".join(f'<circle cx="{x0 + i * step:.1f}" cy="{y0 + j * step:.1f}" r="{s * 0.022:.1f}" fill="{CREAM}"/>'
                  for i in range(n) for j in range(n)))


def disc_dots(c, cx, cy, s, r):
    c.add(f'<circle cx="{cx + s * 0.1:.1f}" cy="{cy - s * 0.08:.1f}" r="{s * 0.36:.1f}" fill="{AMBER}"/>')
    n, step = 7, s * 0.09
    x0, y0 = cx - s * 0.36, cy - s * 0.18
    c.add("".join(f'<circle cx="{x0 + i * step:.1f}" cy="{y0 + j * step:.1f}" r="{s * 0.024:.1f}" fill="{CREAM}"/>'
                  for i in range(n) for j in range(n)))


def wave(c, cx, cy, s, r):
    w, amp, n = s * 1.0, s * 0.08, 4
    p = w / n
    x0 = cx - w / 2
    d = f"M{x0:.1f},{cy:.1f} Q{x0 + p / 4:.1f},{cy - amp:.1f} {x0 + p / 2:.1f},{cy:.1f}"
    for i in range(1, 2 * n):
        d += f" T{x0 + p / 2 * (i + 1):.1f},{cy:.1f}"
    col = AMBER if r.random() < 0.3 else CREAM
    c.add(f'<path d="{d}" {stroke(col)}/>')


def chevrons(c, cx, cy, s, r):
    w, h, n = s * 0.55, s * 0.18, 4
    for i in range(n):
        y = cy - s * 0.38 + i * s * 0.22
        c.add(f'<polyline points="{pts([(cx - w / 2, y + h), (cx, y), (cx + w / 2, y + h)])}" {stroke()}/>')


def dash_ring(c, cx, cy, s, r):
    n, R = 22, s * 0.42
    for i in range(n):
        a = i * math.tau / n
        c.add(f'<line x1="{cx + R * 0.82 * math.cos(a):.1f}" y1="{cy + R * 0.82 * math.sin(a):.1f}" '
              f'x2="{cx + R * math.cos(a):.1f}" y2="{cy + R * math.sin(a):.1f}" {stroke()}/>')


def dot_ring(c, cx, cy, s, r):
    n, R = 20, s * 0.4
    c.add("".join(f'<circle cx="{cx + R * math.cos(i * math.tau / n):.1f}" cy="{cy + R * math.sin(i * math.tau / n):.1f}" r="{s * 0.028:.1f}" fill="{CREAM}"/>'
                  for i in range(n)))


def cross_wave(c, cx, cy, s, r):
    a, b = s * 0.17, s * 0.45
    poly = [(cx - a, cy - b), (cx + a, cy - b), (cx + a, cy - a), (cx + b, cy - a), (cx + b, cy + a), (cx + a, cy + a),
            (cx + a, cy + b), (cx - a, cy + b), (cx - a, cy + a), (cx - b, cy + a), (cx - b, cy - a), (cx - a, cy - a)]
    filled = r.random() < 0.5
    if filled:
        c.add(f'<polygon points="{pts(poly)}" fill="{AMBER}"/>')
    cid = c.clip(f'<polygon points="{pts(poly)}"/>')
    ws = []
    for k in range(7):
        y = cy - b + k * s * 0.15
        d = f"M{cx - b:.1f},{y:.1f}" + "".join(f" q{s * 0.06:.1f},{-s * 0.05:.1f} {s * 0.12:.1f},0 t{s * 0.12:.1f},0" for _ in range(4))
        ws.append(f'<path d="{d}" {stroke(INK if filled else CREAM, SW * 0.8)}/>')
    c.add(f'<g clip-path="url(#{cid})">{"".join(ws)}</g>')
    c.add(f'<polygon points="{pts(poly)}" {stroke()}/>')


def arch_row(c, cx, cy, s, r):
    n, rad = 4, s * 0.1
    x0 = cx - (n - 1) * rad * 1.25
    for i in range(n):
        x = x0 + i * rad * 2.5
        c.add(f'<path d="M{x - rad:.1f},{cy:.1f} A{rad:.1f},{rad:.1f} 0 0 1 {x + rad:.1f},{cy:.1f}" {stroke()}/>')


def hstripes(c, cx, cy, s, r):
    n = 5
    for i in range(n):
        y = cy - s * 0.32 + i * s * 0.16
        c.add(f'<rect x="{cx - s * 0.5:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s * 0.075:.1f}" fill="{AMBER if i % 2 == 0 else CREAM}"/>')


def rainbow(c, cx, cy, s, r):
    R, rr = s * 0.5, s * 0.26
    y = cy + s * 0.2
    c.add(f'<path d="M{cx - R:.1f},{y:.1f} A{R:.1f},{R:.1f} 0 0 1 {cx + R:.1f},{y:.1f} L{cx + rr:.1f},{y:.1f} '
          f'A{rr:.1f},{rr:.1f} 0 0 0 {cx - rr:.1f},{y:.1f} Z" fill="{AMBER}"/>')
    m = (R + rr) / 2
    c.add(f'<path d="M{cx - m:.1f},{y:.1f} A{m:.1f},{m:.1f} 0 0 1 {cx + m:.1f},{y:.1f}" {stroke(INK, SW * 1.4)}/>')
    c.add(f'<line x1="{cx - R:.1f}" y1="{y + s * 0.08:.1f}" x2="{cx + R:.1f}" y2="{y + s * 0.08:.1f}" {stroke()}/>')


def nested_triangles(c, cx, cy, s, r):
    for k, col in ((1.0, CREAM), (0.6, AMBER)):
        half = s * 0.5 * k
        tri = [(cx, cy - half * 0.95), (cx - half, cy + half * 0.75), (cx + half, cy + half * 0.75)]
        c.add(f'<polygon points="{pts(tri)}" {stroke(col)}/>')


def diamonds(c, cx, cy, s, r):
    n, d = 4, s * 0.12
    x0 = cx - (n - 1) * d * 1.05
    for i in range(n):
        x = x0 + i * d * 2.1
        col = AMBER if i % 2 else CREAM
        c.add(f'<polygon points="{pts([(x, cy - d), (x + d, cy), (x, cy + d), (x - d, cy)])}" fill="{col}"/>')


def confetti(c, cx, cy, s, r):
    for _ in range(16):
        x, y = cx + r.uniform(-0.38, 0.38) * s, cy + r.uniform(-0.36, 0.36) * s
        a, l = r.uniform(0, math.pi), s * 0.07
        c.add(f'<line x1="{x - l * math.cos(a):.1f}" y1="{y - l * math.sin(a):.1f}" x2="{x + l * math.cos(a):.1f}" y2="{y + l * math.sin(a):.1f}" {stroke()}/>')


def donut_dots(c, cx, cy, s, r):
    R, rr = s * 0.45, s * 0.2
    c.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" {stroke()}/>')
    c.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" {stroke()}/>')
    for ring, n in ((0.27, 14), (0.38, 20)):
        c.add("".join(f'<circle cx="{cx + s * ring * math.cos(i * math.tau / n):.1f}" cy="{cy + s * ring * math.sin(i * math.tau / n):.1f}" r="{s * 0.02:.1f}" fill="{CREAM}"/>'
                      for i in range(n)))


def striped_disc_square(c, cx, cy, s, r):
    a = s * 0.55
    c.add(f'<rect x="{cx:.1f}" y="{cy - a * 0.1:.1f}" width="{a:.1f}" height="{a:.1f}" fill="{AMBER}"/>')
    R = s * 0.38
    cid = c.clip(f'<circle cx="{cx - s * 0.05:.1f}" cy="{cy:.1f}" r="{R:.1f}"/>')
    lines = "".join(f'<rect x="{cx - R - s * 0.05:.1f}" y="{cy - R + i * R * 0.25:.1f}" width="{2 * R:.1f}" height="{R * 0.11:.1f}" fill="{CREAM}"/>'
                    for i in range(9))
    c.add(f'<circle cx="{cx - s * 0.05:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="{INK}"/>')
    c.add(f'<g clip-path="url(#{cid})">{lines}</g>')


def pluses(c, cx, cy, s, r):
    for dx, dy, k in ((-0.25, -0.2, 1.0), (0.12, 0.05, 0.75), (0.32, -0.3, 0.55)):
        x, y, a, t = cx + dx * s, cy + dy * s, s * 0.14 * k, s * 0.05 * k
        c.add(f'<path d="M{x - a:.1f},{y:.1f} H{x + a:.1f} M{x:.1f},{y - a:.1f} V{y + a:.1f}" {stroke(CREAM, t * 1.4)}/>')


def dash_column(c, cx, cy, s, r):
    dash = f' stroke-dasharray="{s * 0.08:.1f} {s * 0.06:.1f}"'
    for x in (cx - s * 0.2, cx, cx + s * 0.2):
        c.add(f'<line x1="{x:.1f}" y1="{cy - s * 0.42:.1f}" x2="{x:.1f}" y2="{cy + s * 0.42:.1f}" {stroke(extra=dash)}/>')


def half_disc(c, cx, cy, s, r):
    R = s * 0.45
    y = cy + s * 0.15
    d = f"M{cx - R:.1f},{y:.1f} A{R:.1f},{R:.1f} 0 0 1 {cx + R:.1f},{y:.1f} Z"
    c.add(f'<path d="{d}" fill="{AMBER}"/>')
    cid = c.clip(f'<path d="{d}"/>')
    lines = "".join(f'<line x1="{cx - R + i * R * 0.22:.1f}" y1="{y - R:.1f}" x2="{cx - R + i * R * 0.22:.1f}" y2="{y:.1f}" {stroke(INK, SW)}/>'
                    for i in range(1, 9))
    c.add(f'<g clip-path="url(#{cid})">{lines}</g>')


def squiggle(c, cx, cy, s, r):
    amp, n = s * 0.14, 5
    p = s * 0.8 / n
    y0 = cy - s * 0.4
    d = f"M{cx:.1f},{y0:.1f} Q{cx + amp:.1f},{y0 + p / 4:.1f} {cx:.1f},{y0 + p / 2:.1f}"
    for i in range(1, 2 * n):
        d += f" T{cx:.1f},{y0 + p / 2 * (i + 1):.1f}"
    c.add(f'<path d="{d}" {stroke()}/>')


# One element per guide, chosen for what the guide is about. No two guides share one.
ASSIGN = {
    # AI search
    "what-is-answer-engine-optimisation": rings,             # a signal finding its answer
    "how-to-get-mentioned-by-chatgpt": dash_ring,            # being in the spotlight
    "aeo-vs-seo-vs-geo": disc_dots,                          # overlapping disciplines
    "aeo-checklist": dash_column,                            # items in rows
    "seo-for-small-business-nz": donut_dots,                 # a local radius
    # costs and choices
    "ai-marketing-cost-australia-new-zealand": striped_disc_square,
    "marketing-agency-cost-nz": hstripes,                    # price bands
    "marketing-agency-alternatives-nz": diamonds,            # options side by side
    "agency-vs-freelancer-vs-in-house": pluses,              # three ways to buy
    "fractional-marketing-manager-nz": half_disc,            # part of a role
    "fractional-cmo-vs-ai-cmo": stripes_square,
    "do-you-need-an-ai-marketing-agency-nz": cross_wave,
    # the AI marketing agent
    "what-is-an-ai-marketing-agent": rainbow,                # the loop over the work
    "what-is-an-ai-cmo": nested_triangles,                   # a plan inside a plan
    "ai-marketing-automation-small-business": wave,          # steady repetition
    # transformation
    "ai-marketing-transformation-small-business": chevrons,  # moving up
    "ai-marketing-for-small-business-nz": dot_triangle,
    "ai-marketing-examples": confetti,                       # many small uses
    "ai-marketing-strategy-small-business": zigzag,
    "content-marketing-small-business-nz": arch_row,         # a steady run of pieces
    "outbound-sales-automation": squiggle,                   # the follow-up thread
    # reference
    "ai-marketing-statistics-australia-new-zealand": dot_grid,
    # keyword guides, October 2026
    "ai-for-marketers": half_disc,                           # half handed over, half kept
    "ai-agents-for-marketing": dot_ring,                     # a team around one brief
    "ai-agency-vs-ai-consultant-nz": pluses,                 # ways to buy the work
}
ALL = [rings, dash_ring, disc_dots, dash_column, donut_dots, striped_disc_square, hstripes, diamonds, pluses,
       half_disc, stripes_square, cross_wave, rainbow, nested_triangles, wave, chevrons, dot_triangle, confetti,
       zigzag, arch_row, squiggle, dot_grid, dot_ring]
# shapes drawn as a row or a line read better a little larger
WIDE = {zigzag, wave, arch_row, diamonds, hstripes, confetti, squiggle, dash_column, pluses}


def figure_svg(slug, topic):
    r = random.Random(int(hashlib.sha1(slug.encode()).hexdigest()[:8], 16))
    shape = ASSIGN.get(slug) or ALL[int(hashlib.sha1(slug.encode()).hexdigest(), 16) % len(ALL)]
    c = Canvas()
    s = 0.8 * {zigzag: 520, wave: 560, arch_row: 560, squiggle: 380, confetti: 420, dash_column: 380}.get(shape, 400 if shape in WIDE else 340)
    shape(c, W / 2, H / 2, s, r)
    defs = f"<defs>{''.join(c.defs)}</defs>" if c.defs else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-hidden="true">'
            f'{defs}<rect width="{W}" height="{H}" fill="{INK}"/>{"".join(c.body)}</svg>\n')
