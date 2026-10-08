#!/usr/bin/env python3
"""Check that a Chinese page keeps the English page's structure.

    python3 scripts/zh_parity.py about.html            # compares about.html with zh/about.html
    python3 scripts/zh_parity.py src/blog/aeo-checklist.html   # compares with src/zh/blog/...

Compares the sequence of tags and the attributes that must never change (class, id, href,
src, data-* keys, role, type, name, for). Text, alt, title, aria-label, placeholder and
meta content may differ. It also flags house-rule breaks in the Chinese text: dashes,
exclamation marks and banned words. Exit code 1 on any problem.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FREE = {"alt", "title", "aria-label", "placeholder", "content", "value", "lang", "hreflang",
        "data-share-title", "data-share-text", "data-missing", "data-title", "aria-valuetext",
        "data-label", "data-say", "data-tip", "data-q", "data-name", "data-text", "label"}
# The build owns these, so they are allowed to differ.
OWNED = ("site-header", "site-footer")
BANNED = ["——", "—", "–", "！", "!", "赋能", "打造", "一站式", "颠覆", "革命性", "无缝", "抓手",
          "闭环", "降本增效", "助力", "引领", "极致", "全方位", "深度融合", "重塑", "解锁", "世界级",
          "顶级", "硬核", "Novie", "Novamind"]


SITE = "https://www.flowai.co.nz"


def unzh(v):
    """Undo what scripts/i18n.py does to a Chinese page, so only translator changes show."""
    if v is None:
        return v
    v = v.replace("amber-lan-cv-zh.pdf", "amber-lan-cv.pdf").replace("Amber-Lan-CV-zh.pdf", "Amber-Lan-CV.pdf")
    if v == "/zh" or v.startswith("/zh/") or v.startswith("/zh?") or v.startswith("/zh#"):
        v = v[3:] or "/"
    elif v.startswith(SITE + "/zh/"):
        v = SITE + v[len(SITE) + 3:]
    return v


class Shape(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.seq, self.text, self.skip, self.owned = [], [], 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if self.owned or tag in ("header", "footer") and any(o in cls for o in OWNED):
            if tag in ("header", "footer") and not self.owned:
                self.seq.append((tag, cls))
            self.owned += tag in ("header", "footer")
            return
        if tag in ("script", "style"):
            self.skip += 1
        a = {k: unzh(v) for k, v in a.items()}
        keep = tuple(sorted((k, v if not k.startswith("data-") or k in ("data-lane", "data-topic", "data-filter", "data-view") else "") for k, v in a.items()
                            if k not in FREE and not (tag == "meta" and k == "content")))
        self.seq.append((tag, keep))

    def handle_endtag(self, tag):
        if self.owned:
            if tag in ("header", "footer"):
                self.owned -= 1
            return
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, d):
        if not self.owned and not self.skip:
            self.text.append(d)


def shape(path):
    raw = Path(path).read_text()
    raw = re.sub(r"<!--\s*i18n:start\s*-->.*?<!--\s*i18n:end\s*-->", "", raw, flags=re.S)
    raw = re.sub(r'<span class="lang-switch".*?中文</a></span>', "", raw, flags=re.S)
    raw = re.sub(r"<script>/\* Missing pages under /zh/.*?</script>", "", raw, flags=re.S)
    raw = re.sub(r'<link rel="icon" href="/?favicon.svg"', '<link rel="icon" href="favicon.svg"', raw)
    if "<!--meta" in raw[:20]:
        raw = raw.split("-->", 1)[1]
    p = Shape()
    p.feed(raw)
    return p


def pair(en):
    en = Path(en)
    rel = en.resolve().relative_to(ROOT)
    if rel.parts[:2] == ("src", "blog"):
        return ROOT / "src" / "zh" / "blog" / rel.name
    return ROOT / "zh" / rel


def check(en):
    zh = pair(en)
    if not zh.exists():
        print(f"missing {zh.relative_to(ROOT)}")
        return 1
    a, b = shape(en), shape(zh)
    bad = 0
    for i, (x, y) in enumerate(zip(a.seq, b.seq)):
        if x != y:
            print(f"{zh.relative_to(ROOT)}: structure differs at tag {i}:\n  en {x}\n  zh {y}")
            bad = 1
            break
    if not bad and len(a.seq) != len(b.seq):
        print(f"{zh.relative_to(ROOT)}: {len(a.seq)} tags in English, {len(b.seq)} in Chinese")
        bad = 1
    raw = zh.read_text()
    text = "".join(b.text)
    if "<!--meta" in raw[:20]:
        text += raw.split("-->", 1)[0].replace("<!--meta", "")
    for w in BANNED:
        if w in text:
            ctx = text[max(0, text.index(w) - 30): text.index(w) + 30].replace("\n", " ")
            print(f"{zh.relative_to(ROOT)}: house rule: '{w}' in ...{ctx}...")
            bad = 1
    if not bad:
        print(f"ok {zh.relative_to(ROOT)}")
    return bad


if __name__ == "__main__":
    sys.exit(max([check(p) for p in sys.argv[1:]] or [0]))
