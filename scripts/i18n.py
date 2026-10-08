#!/usr/bin/env python3
"""Flow AI bilingual layer: English at /, Simplified Chinese at /zh/.

Run from the repo root after any page or generator change:

    python3 scripts/build_blog.py && python3 scripts/i18n.py

What it does, every run, idempotently:

  every page   adds hreflang (en, zh-Hans, x-default), /assets/i18n.css and the language
               script to <head>, and the EN | 中文 switch to the header. The script makes the
               choice global: pick 中文 once and every English page you open sends you to its
               Chinese twin (and back), remembered in localStorage.
  Chinese      sets lang="zh-Hans", the Chinese canonical and og:url, the Chinese header,
  pages        footer and skip link (built from the English page's own header and footer, so
               they never drift), points every internal link at its /zh/ twin, rewrites page
               URLs in JSON-LD, and swaps in the Chinese CV.
  sitemap      lists every Chinese page between <!-- zh:start --> and <!-- zh:end -->.

Then it reports what needs a translator:

  missing      English pages with no Chinese twin
  stale        Chinese pages whose English source changed since it was translated
               (sources and their fingerprints live in i18n/zh-sources.json)
  untranslated Chinese pages with runs of English prose left in the visible text

After translating or updating a page, record it:  python3 scripts/i18n.py --stamp zh/about.html
(no path = stamp everything). Translation rules: i18n/ZH-STYLE.md.
"""
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.flowai.co.nz"
STAMPS = ROOT / "i18n" / "zh-sources.json"
# English only: a redirect stub and an internal brand document.
EXCLUDE = {"cv.html", "flowai-brand-guidelines.html"}
NO_PAIR = {"404.html"}  # served by GitHub Pages at any missing URL, so no hreflang
SKIP_DIRS = {"src", "zh", ".git", "node_modules", "scripts", "i18n", ".well-known", "fonts", "images"}
KEEP_IDS = {f"{SITE}/#amber", f"{SITE}/#flowai", f"{SITE}/#website"}

HEADER_ZH = [
    ('aria-label="Flow AI home"', 'aria-label="Flow AI 首页"'),
    ('aria-label="Primary navigation"', 'aria-label="主导航"'),
    ('>How it works</a>', '>合作方式</a>'),
    ('>Guides</a>', '>指南</a>'),
    ('>About</a>', '>关于我</a>'),
    ('>Work with me</a>', '>与我合作</a>'),
]
FOOTER_ZH = HEADER_ZH + [
    ('>AI marketing engineer, Auckland<', '>AI 营销工程师，奥克兰<'),
    ('>I build marketing systems with the teams who run them, and review everything they send.<',
     '>我与负责运营的团队一起搭建营销系统，并审核系统发出的每一项内容。<'),
    ('aria-label="Footer"', 'aria-label="页脚"'),
    ('>Work</a>', '>作品</a>'),
    ('>Free templates</a>', '>免费模板</a>'),
    ('>Manifesto</a>', '>宣言</a>'),
    ('>Privacy</a>', '>隐私政策</a>'),
    ('&copy; 2026, Auckland, New Zealand', '&copy; 2026 · 新西兰奥克兰'),
    ('aria-label="Amber Lan on LinkedIn"', 'aria-label="Amber Lan 的 LinkedIn"'),
    ('aria-label="Amber Lan on GitHub"', 'aria-label="Amber Lan 的 GitHub"'),
    ('aria-label="Email Amber Lan"', 'aria-label="给 Amber Lan 发邮件"'),
    ('title="Email"', 'title="邮件"'),
]
SKIP_ZH = {
    "Skip to content": "跳到正文", "Skip to the guide": "跳到指南正文", "Skip to the form": "跳到表单",
    "Skip to cases": "跳到案例", "Skip to the guides": "跳到指南列表", "Skip to the glossary": "跳到术语表",
    "Skip to the skill library": "跳到技能库",
}

# The language script. Runs in <head> before first paint, so a remembered choice redirects
# without a flash. Crawlers never carry a stored choice, so they always see the page they asked for.
LANG_JS = ("(function(){try{var k='flowai-lang',d=document,c=/^zh/.test(d.documentElement.lang)?'zh':'en',"
           "p=localStorage.getItem(k);d.addEventListener('click',function(e){var a=e.target.closest&&"
           "e.target.closest('[data-lang]');if(a)localStorage.setItem(k,a.getAttribute('data-lang'))});"
           "if(p&&p!==c){var l=d.querySelector('link[rel=alternate][hreflang='+(p==='zh'?'zh-Hans':'en')+']');"
           "if(l){var u=new URL(l.href);if(u.pathname!==location.pathname)location.replace(u.pathname+location.search+location.hash)}}}catch(e){}})();")


# ---------------------------------------------------------------- paths

def en_pages():
    out = []
    for f in sorted(ROOT.rglob("*.html")):
        rel = f.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or str(rel) in EXCLUDE or rel.parts[0].startswith("."):
            continue
        if rel.parts[0] == "tools" and len(rel.parts) == 1:
            continue
        out.append(str(rel))
    return out


def url_path(rel):
    """English URL path of a page file: about.html -> /about, blog/index.html -> /blog/."""
    rel = rel[3:] if rel.startswith("zh/") else rel
    if rel == "index.html":
        p = "/"
    elif rel.endswith("/index.html"):
        p = "/" + rel[: -len("index.html")]
    else:
        p = "/" + rel[: -len(".html")]
    return p


def zh_path(p):
    return "/zh" + p if p != "/" else "/zh/"


PAGES = en_pages()
PAIRED = {r for r in PAGES if (ROOT / "zh" / r).exists()}
ZH_SET = {url_path(r) for r in PAIRED}  # English URL paths that have a Chinese twin


def to_zh(href, absolute=False):
    """Map an English internal URL to its Chinese twin, or return it unchanged."""
    base = SITE if absolute else ""
    rest = href[len(base):] if absolute else href
    if not rest.startswith("/") or rest.startswith("//") or rest.startswith("/zh/") or rest == "/zh":
        return href
    m = re.match(r"([^?#]*)(.*)$", rest)
    path, tail = m.group(1), m.group(2)
    path = path or "/"
    if path in ZH_SET:
        return base + zh_path(path) + tail
    return href


# ---------------------------------------------------------------- page edits

def visible_text(html):
    html = re.sub(r"<!--\s*i18n:start.*?i18n:end\s*-->", "", html, flags=re.S)
    html = re.sub(r"<(header|footer) class=\"site-(header|footer)\".*?</\1>", "", html, flags=re.S)
    html = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", html, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def fingerprint(path):
    t = (ROOT / path).read_text()
    if not path.endswith(".json") and not path.startswith("src/"):
        t = visible_text(t)
    return hashlib.sha1(t.encode()).hexdigest()[:12]


def source_of(zh_rel):
    """The English file a Chinese page was translated from (None when generated chrome only)."""
    if zh_rel.startswith("zh/blog/") and zh_rel != "zh/blog/index.html":
        return "src/blog/" + zh_rel.split("/")[-1], "src/zh/blog/" + zh_rel.split("/")[-1]
    if zh_rel == "zh/glossary/index.html":
        return "src/glossary.json", "src/zh/glossary.json"
    if zh_rel == "zh/blog/index.html":
        return None, None
    return zh_rel[3:], zh_rel


def switch(en_href, zh_href, current):
    label = "语言" if current == "zh" else "Language"
    en_cur = ' aria-current="true"' if current == "en" else ""
    zh_cur = ' aria-current="true"' if current == "zh" else ""
    return (f'<span class="lang-switch" role="group" aria-label="{label}">'
            f'<a href="{en_href}" lang="en" hreflang="en" data-lang="en"{en_cur}>EN</a>'
            f'<span class="lang-switch__sep" aria-hidden="true">|</span>'
            f'<a href="{zh_href}" lang="zh-Hans" hreflang="zh-Hans" data-lang="zh"{zh_cur}>中文</a></span>')


def with_switch(header, sw):
    """Put the switch on its own line just before the header CTA, replacing any earlier one."""
    header = re.sub(r'\s*<span class="lang-switch".*?中文</a></span>', "", header, flags=re.S)
    return re.sub(r'\s*\n([ \t]*)(<a class="site-header__cta")',
                  lambda m: "\n" + m.group(1) + sw + "\n" + m.group(1) + m.group(2), header, count=1)


def head_block(rel, lang):
    en_rel = rel[3:] if lang == "zh" else rel
    lines = []
    if en_rel in PAIRED and en_rel not in NO_PAIR:
        en_url = SITE + url_path(en_rel)
        zh_url = SITE + zh_path(url_path(en_rel))
        lines += [f'<link rel="alternate" hreflang="en" href="{en_url}">',
                  f'<link rel="alternate" hreflang="zh-Hans" href="{zh_url}">',
                  f'<link rel="alternate" hreflang="x-default" href="{en_url}">']
    lines += ['<link rel="stylesheet" href="/assets/i18n.css?v=1">', f"<script>{LANG_JS}</script>"]
    return "<!-- i18n:start -->\n" + "\n".join(lines) + "\n<!-- i18n:end -->"


def put_head(html, block):
    if "<!-- i18n:start -->" in html:
        return re.sub(r"<!-- i18n:start -->.*?<!-- i18n:end -->", lambda m: block, html, count=1, flags=re.S)
    m = re.search(r'<link rel="canonical"[^>]*>\n?', html) or re.search(r"<meta charset[^>]*>\n?", html, re.I)
    i = m.end() if m else html.index("</head>")
    return html[:i] + block + "\n" + html[i:]


def rewrite_links(html):
    def a_tag(m):
        tag = m.group(0)
        if "data-lang=" in tag:  # the language switch already points where it should
            return tag
        tag = re.sub(r'(\shref=")([^"]+)(")', lambda x: x.group(1) + to_zh(to_zh(x.group(2)), absolute=True) + x.group(3), tag)
        tag = re.sub(r'(\sdata-share-url=")([^"]+)(")', lambda x: x.group(1) + to_zh(x.group(2)) + x.group(3), tag)
        return tag
    return re.sub(r"<(a|button)\b[^>]*>", a_tag, html)


def absolute_urls(html, rel):
    """A Chinese page sits one folder deeper, so relative asset URLs become root-relative."""
    base = Path("/" + rel).parent

    def fix(m):
        v = m.group(2)
        if re.match(r"^(#|/|[a-z][a-z0-9+.-]*:)", v, re.I) or "'" in v or not v:
            return m.group(0)
        return m.group(1) + str((base / v)).replace("//", "/") + m.group(3)
    return re.sub(r'(<(?:link|script|img|source|a)\b[^>]*?\s(?:href|src)=")([^"]*)(")', fix, html)


def rewrite_jsonld(html):
    def fix(o, inside=False):
        if isinstance(o, dict):
            ent = inside or (o.get("@id") in KEEP_IDS and len(o) > 1)
            for k, v in list(o.items()):
                if k == "inLanguage" and isinstance(v, str) and v.startswith("en"):
                    o[k] = "zh-Hans"
                elif isinstance(v, str) and k in ("@id", "url", "item", "mainEntityOfPage") and not ent and v not in KEEP_IDS:
                    o[k] = to_zh(v, absolute=True)
                elif isinstance(v, (dict, list)):
                    fix(v, ent)
        elif isinstance(o, list):
            for x in o:
                fix(x, inside)

    def block(m):
        try:
            data = json.loads(m.group(2))
        except ValueError:
            print("  warn: JSON-LD did not parse, left as is")
            return m.group(0)
        fix(data)
        out = json.dumps(data, indent=2, ensure_ascii=False).replace("</", "<\\/")
        return m.group(1) + "\n" + out + "\n" + m.group(3)

    return re.sub(r'(<script type="application/ld\+json">)\s*(.*?)\s*(</script>)', block, html, flags=re.S)


def process_en(rel):
    f = ROOT / rel
    html = f.read_text()
    new = put_head(html, head_block(rel, "en"))
    if rel in PAIRED and rel not in NO_PAIR:
        zh_href = zh_path(url_path(rel))
    else:
        zh_href = "/zh/"
    sw = switch(url_path(rel) if rel not in NO_PAIR else "/", zh_href, "en")
    new = re.sub(r'<header class="site-header">.*?</header>', lambda m: with_switch(m.group(0), sw), new, count=1, flags=re.S)
    if new != html:
        f.write_text(new)
        return True
    return False


def process_zh(rel):
    """rel is the English page; the Chinese twin lives at zh/<rel>."""
    zrel = "zh/" + rel
    f = ROOT / zrel
    en = (ROOT / rel).read_text()
    html = f.read_text()
    new = re.sub(r"<html\b[^>]*>", '<html lang="zh-Hans">', html, count=1)
    p = url_path(rel)
    zurl = SITE + zh_path(p)
    if rel not in NO_PAIR:
        new = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{zurl}">', new, count=1)
        new = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{zurl}">', new, count=1)
    new = re.sub(r'<meta property="og:locale" content="[^"]*">', '<meta property="og:locale" content="zh_CN">', new, count=1)
    new = put_head(new, head_block(zrel, "zh"))

    # header and footer: the English page's own, translated, so nav state never drifts
    eh = re.search(r'<header class="site-header">.*?</header>', en, re.S)
    ef = re.search(r'<footer class="site-footer">.*?</footer>', en, re.S)
    if eh:
        h = re.sub(r'<span class="lang-switch".*?中文</a></span>\s*', "", eh.group(0), flags=re.S)
        for a, b in HEADER_ZH:
            h = h.replace(a, b)
        h = rewrite_links(h)
        h = with_switch(h, switch(p if rel not in NO_PAIR else "/", zh_path(p), "zh"))
        new = re.sub(r'<header class="site-header">.*?</header>', lambda m: h, new, count=1, flags=re.S)
    if ef:
        ft = ef.group(0)
        for a, b in FOOTER_ZH:
            ft = ft.replace(a, b)
        ft = rewrite_links(ft)
        new = re.sub(r'<footer class="site-footer">.*?</footer>', lambda m: ft, new, count=1, flags=re.S)
    new = re.sub(r'(<a class="skip-link"[^>]*>)([^<]*)(</a>)',
                 lambda m: m.group(1) + SKIP_ZH.get(m.group(2).strip(), m.group(2)) + m.group(3), new)

    new = rewrite_links(new)
    new = absolute_urls(new, rel)
    new = rewrite_jsonld(new)
    if (ROOT / "assets" / "amber-lan-cv-zh.pdf").exists():
        new = new.replace('href="/assets/amber-lan-cv.pdf" download="Amber-Lan-CV.pdf"',
                          'href="/assets/amber-lan-cv-zh.pdf" download="Amber-Lan-CV-zh.pdf"')
    if new != html:
        f.write_text(new)
        return True
    return False


# ---------------------------------------------------------------- sitemap

def update_sitemap():
    sm = ROOT / "sitemap.xml"
    text = sm.read_text()
    text = re.sub(r"\s*<!-- zh:start -->.*?<!-- zh:end -->", "", text, flags=re.S)
    lastmod = dict(re.findall(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", text))
    today = dt.date.today().isoformat()
    lines = []
    for rel in sorted(PAIRED - NO_PAIR):
        en_url = SITE + url_path(rel)
        if en_url not in lastmod:  # only list pages the English sitemap lists
            continue
        lines.append(f"  <url><loc>{SITE}{zh_path(url_path(rel))}</loc><lastmod>{lastmod.get(en_url, today)}</lastmod></url>")
    block = "  <!-- zh:start -->\n" + "\n".join(lines) + "\n  <!-- zh:end -->\n"
    text = text.replace("</urlset>", block + "</urlset>")
    sm.write_text(text)
    return len(lines)


# ---------------------------------------------------------------- reports

ALLOW = re.compile(r"Flow AI|Flow Intelligence|Flow Engine|Amber Lan|Claude Code|GitHub|LinkedIn|ChatGPT")


def untranslated(zrel):
    html = (ROOT / zrel).read_text()
    html = re.sub(r"<(code|pre|kbd|samp)\b.*?</\1>", " ", html, flags=re.S)
    html = re.sub(r'<[^>]+translate="no".*?>.*?</[^>]+>', " ", html, flags=re.S)
    text = visible_text(html)
    text = ALLOW.sub(" ", text)
    return re.findall(r"(?:\b[A-Za-z][A-Za-z'’]*[,.:;]?\s+){5,}[A-Za-z][A-Za-z'’]*", text)


def load_stamps():
    return json.loads(STAMPS.read_text()) if STAMPS.exists() else {}


def stamp(paths):
    s = load_stamps()
    targets = paths or ["zh/" + r for r in PAIRED]
    for z in targets:
        src, key = source_of(z)
        if src:
            s[key] = {"source": src, "sha": fingerprint(src)}
    STAMPS.parent.mkdir(exist_ok=True)
    STAMPS.write_text(json.dumps(dict(sorted(s.items())), indent=2, ensure_ascii=False) + "\n")
    print(f"stamped {len(targets)} Chinese pages")


def report():
    missing = [r for r in PAGES if r not in PAIRED and r not in NO_PAIR]
    s = load_stamps()
    stale = []
    for r in sorted(PAIRED):
        src, key = source_of("zh/" + r)
        if src and key in s and s[key]["sha"] != fingerprint(src):
            stale.append(f"{key} (English source {src} changed)")
        elif src and key not in s:
            stale.append(f"{key} (never stamped)")
    print(f"pages: {len(PAGES)} English, {len(PAIRED)} with a Chinese twin")
    for m in missing:
        print(f"  missing  zh/{m}")
    for x in stale:
        print(f"  stale    {x}")
    for r in sorted(PAIRED):
        u = untranslated("zh/" + r)
        if u:
            print(f"  english  zh/{r}: {len(u)} run(s), e.g. \"{u[0].strip()[:70]}\"")


def main():
    args = sys.argv[1:]
    if args and args[0] == "--stamp":
        stamp(args[1:])
        return
    changed = 0
    for rel in PAGES:
        changed += process_en(rel)
    for rel in sorted(PAIRED):
        changed += process_zh(rel)
    n = update_sitemap()
    print(f"updated {changed} files, {n} Chinese URLs in the sitemap")
    report()


if __name__ == "__main__":
    main()
