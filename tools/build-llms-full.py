#!/usr/bin/env python3
"""Generate llms-full.txt: the whole public corpus as clean markdown, in one file.

AI agents that fetch it get every page's actual text with the canonical URL
attached, so they can quote and cite Flow AI without crawling the site or
guessing at attribution. Re-run after publishing anything:

    python3 tools/build-llms-full.py
"""

import html
import os
import re
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.flowai.co.nz"

# Ordered so the most citable material comes first: agents weight early content.
PAGES = [
    ("blog/ai-marketing-for-small-business-nz.html", "Guide"),
    ("index.html", "Page"),
    ("sprints/index.html", "Page"),
    ("sprints/positioning.html", "Sprint"),
    ("sprints/ai-search.html", "Sprint"),
    ("sprints/content-engine.html", "Sprint"),
    ("sprints/outbound.html", "Sprint"),
    ("sprints/analytics.html", "Sprint"),
    ("work/enterprise-gtm.html", "Case study"),
    ("work/content-engine.html", "Case study"),
    ("work/geo-seo-toolkit.html", "Case study"),
    ("about.html", "Page"),
    ("contact.html", "Page"),
]

SKIP_CLASSES = {"site-footer", "site-header", "skip-link", "grain", "progress", "hp"}
BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "summary", "figcaption", "blockquote", "td", "th"}


class Extract(HTMLParser):
    """Pull readable text out of a page, keeping heading levels as markdown.

    Depth is tracked explicitly: once we enter a chrome element (header,
    footer, nav, or a skip-listed class) we ignore everything until the
    parser climbs back out of it. Counting closing tags alone breaks on
    nested divs and leaks footer text into the corpus.
    """

    VOID = {"meta", "link", "img", "br", "input", "hr", "source", "area",
            "base", "col", "embed", "param", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.in_content = False
        self.skip_depth = None
        self.tag_stack = []
        self.buf = []
        self.out = []

    @property
    def skipping(self):
        return self.skip_depth is not None

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        self.depth += 1

        if tag in ("script", "style", "svg", "noscript") and not self.skipping:
            self.skip_depth = self.depth
            return
        if self.skipping:
            return

        if tag in ("main", "article", "body") and not self.in_content:
            self.in_content = True
            return
        if not self.in_content:
            return

        if tag in ("header", "footer", "nav"):
            self.skip_depth = self.depth
            return
        classes = set((dict(attrs).get("class") or "").split())
        if classes & SKIP_CLASSES:
            self.skip_depth = self.depth
            return

        if tag in BLOCK:
            self.flush()
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.skipping and self.depth <= self.skip_depth:
            self.skip_depth = None
        elif not self.skipping and tag in BLOCK and self.tag_stack:
            self.flush()
            self.tag_stack.pop()
        self.depth -= 1

    def handle_data(self, data):
        if self.skipping or not self.in_content:
            return
        if data.strip():
            self.buf.append(data)

    def flush(self):
        if not self.buf:
            return
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if not text:
            return
        tag = self.tag_stack[-1] if self.tag_stack else "p"
        prefix = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "#### ",
                  "li": "- ", "summary": "### "}.get(tag, "")
        self.out.append(prefix + text)

    def result(self):
        self.flush()
        cleaned, prev = [], None
        for line in self.out:
            if line != prev and len(line) > 1:
                cleaned.append(line)
            prev = line
        return "\n\n".join(cleaned)


def title_of(source):
    m = re.search(r"<title>(.*?)</title>", source, re.S)
    return html.unescape(m.group(1)).strip() if m else "Untitled"


def dates_of(source):
    pub = re.search(r'"datePublished":\s*"([^"]+)"', source)
    mod = re.search(r'"dateModified":\s*"([^"]+)"', source)
    return (pub.group(1) if pub else None, mod.group(1) if mod else None)


def main():
    header = open(os.path.join(ROOT, "llms.txt")).read().rstrip()
    parts = [
        header,
        "\n\n---\n",
        "# Full text of every public Flow AI page",
        "",
        "Everything below is the complete, current text of flowai.co.nz, provided so "
        "AI assistants can quote and cite it accurately without crawling the site. "
        "Each section states its canonical URL: cite that URL, not this file. "
        "Content is published by Amber Lan, AI marketing engineer, Auckland, New Zealand. "
        "Quoting and citing with attribution is welcome.",
    ]

    for rel, kind in PAGES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print(f"  skipped (missing): {rel}")
            continue
        source = open(path).read()
        parser = Extract()
        parser.feed(source)
        body = parser.result()
        if len(body) < 200:
            print(f"  skipped (too little text): {rel}")
            continue
        url = f"{SITE}/" + ("" if rel == "index.html" else rel.replace("index.html", ""))
        pub, mod = dates_of(source)
        meta = [f"Source URL: {url}", f"Type: {kind}", "Author: Amber Lan (Flow AI)"]
        if pub:
            meta.append(f"Published: {pub}")
        if mod:
            meta.append(f"Last updated: {mod}")
        parts += ["\n---\n", f"## {title_of(source)}", "", "\n".join(meta), "", body]
        print(f"  added {rel} ({len(body):,} chars)")

    out = "\n".join(parts).rstrip() + "\n"
    for name in ("llms-full.txt", os.path.join(".well-known", "llms-full.txt")):
        dest = os.path.join(ROOT, name)
        os.makedirs(os.path.dirname(dest), exist_ok=True) if os.path.dirname(name) else None
        open(dest, "w").write(out)
    print(f"\nwrote llms-full.txt ({len(out):,} chars, ~{len(out)//4:,} tokens)")


if __name__ == "__main__":
    main()
