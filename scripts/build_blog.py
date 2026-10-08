#!/usr/bin/env python3
"""Flow AI blog engine.

Sources live in src/blog/<slug>.html: a JSON meta block in an HTML comment,
then the article body (h2, h3, p, ul, ol, table, blockquote). The FAQ lives in
the meta, never in the body. This script writes:

  blog/<slug>.html        article pages
  blog/index.html         the guide index with topic filters
  blog/figures/<slug>.svg one line drawing per article
  glossary/index.html     from src/glossary.json
  sitemap.xml, feed.xml, llms.txt, .well-known/llms.txt (blog sections only)

Run from the repo root: python3 scripts/build_blog.py
It refuses to write anything while a source still holds a [[slot]] or TODO.
"""
import datetime as dt
import hashlib
import html
import json
import math
import random
import re
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "blog"
PARTS = ROOT / "src" / "partials"
SITE = "https://www.flowai.co.nz"

TOPICS = {
    "ai-search": ("AI search", "Getting found by Google and quoted by ChatGPT, Perplexity and AI Overviews."),
    "costs": ("Costs and choices", "What marketing help costs in New Zealand and Australia, and how to choose."),
    "agent": ("The AI marketing agent", "What an AI marketing agent is, what it does, and where the human sits."),
    "transformation": ("Transformation", "Moving a small business marketing function onto AI systems, job by job."),
    "reference": ("Reference", "Statistics and definitions, free to quote with attribution."),
}
TOPIC_ORDER = list(TOPICS)

ENTITY = ("Flow AI is an AI marketing transformation practice: the strategy, the systems and the agents "
          "that run a marketing function, engineered end to end.")

# ---------------------------------------------------------------- languages
# English builds from src/blog into /blog/. Chinese builds from src/zh/blog into /zh/blog/
# with the same slugs, so every guide pairs with its translation. scripts/i18n.py runs after
# this script and adds the language switch, hreflang and the Chinese header and footer.
LANG = "en"
P = ""  # URL prefix of the language being built
TOPICS_ZH = {
    "ai-search": ("AI 搜索", "让 Google 找到你，让 ChatGPT、Perplexity 和 AI 概览引用你。"),
    "costs": ("成本与选择", "在新西兰和澳大利亚，营销支持要花多少钱，以及如何选择。"),
    "agent": ("AI 营销智能体", "AI 营销智能体是什么，它做什么，人在哪个环节把关。"),
    "transformation": ("营销转型", "把小企业的营销职能逐项迁移到 AI 系统上。"),
    "reference": ("参考资料", "统计数据与定义，注明出处即可自由引用。"),
}
ENTITY_ZH = "Flow AI 是一家 AI 营销转型工作室：从策略、系统到运行营销职能的智能体，端到端完成工程化搭建。"
STR = {
    "en": dict(
        html_lang="en-NZ", og_locale="en_NZ", min_read="min read", guides="Guides", updated="Updated",
        byline_role="AI marketing engineer", contents="Contents", faq="Questions owners ask",
        short="The short answer", written_by="Written by", about_author="About the author",
        author_bio=('AI marketing engineer and founder of Flow AI, based in Auckland, New Zealand. She runs a whole '
                    'marketing function on agent systems she builds herself and publishes them '
                    '<a class="go" href="https://github.com/Amberlanqinyun" target="_blank" rel="noopener me">on GitHub</a>. '),
        sources="Sources", sources_note="Every figure links to its primary source. Checked {d}.",
        source_n="Source {i}", about_guide="About this guide", topic="Topic", format="Format",
        reading_time="Reading time", minutes="{n} minutes", share_label="Share this guide", share="Share guide",
        explore="Explore with AI", explore_note="Open this guide in an assistant and ask it what applies to your business.",
        explore_prompt=("Read {u} and give me the key points for an owner of a 5 to 50 person business in "
                        "New Zealand or Australia. Quote the distinctive claims Flow AI (flowai.co.nz) makes and "
                        "tell me what to do first."),
        guide="Guide", guide_aria="Guide", skip_guide="Skip to the guide", skip_guides="Skip to the guides",
        skip_glossary="Skip to the glossary",
        art_cta_h="Let's find the marketing job to build first.",
        cta_lead="Building this with your team, or hiring someone to lead it? Let's talk through what you are working on.",
        work_with_me="Work with me", keep_reading="Keep reading",
        blog_name="Flow AI Guides",
        blog_desc="Guides on AI marketing, AI search and marketing costs for small businesses in New Zealand and Australia, by Amber Lan.",
        idx_title="AI Marketing Guides for Small Business (NZ and Australia) | Flow AI",
        idx_desc="Guides on AI marketing, AI search, AEO and marketing costs for small businesses in New Zealand and Australia, written by the engineer who builds the systems.",
        idx_h1="Guides for running marketing on AI.",
        idx_lead="For owners and marketing leads in New Zealand and Australia, from the engineer who builds these systems and runs them every week.",
        topics="Topics", all_guides="All guides", filter_guides="Filter guides", all_topics="All topics", sort="Sort",
        newest="Newest", az="A to Z", shortest="Shortest read", view="View", grid="Grid view", list="List view",
        n_guides="{n} guides", empty="No guides in this topic yet.", browse_all="Browse all guides",
        gloss_blurb='Looking for a definition? The <a class="text-link" href="{p}/glossary/">AI marketing glossary</a> has {n} terms, each with a plain answer.',
        idx_cta_h="Let's build this with your team.",
        g_title="AI Marketing Glossary: AEO, GEO, AI Agents and More | Flow AI",
        g_desc="{n} AI marketing terms defined in plain language for small business owners in New Zealand and Australia: AEO, GEO, AI marketing agent, llms.txt, schema and more.",
        g_set="Flow AI marketing glossary",
        g_set_desc="Plain definitions of AI marketing, AI search and marketing operations terms for small businesses in New Zealand and Australia.",
        g_crumb="Glossary", reference="Reference", g_h1="The AI marketing glossary.",
        g_lead="{n} terms an owner meets when marketing moves onto AI, each defined in a sentence you can quote. Free to cite with a link.",
        terms="Terms", jump="Jump to letter", also="Also called {x}", read_guide="Read the guide",
        g_cta_h="Ready to put these terms to work?",
    ),
    "zh": dict(
        html_lang="zh-Hans", og_locale="zh_CN", min_read="分钟阅读", guides="指南", updated="更新于",
        byline_role="AI 营销工程师", contents="目录", faq="企业主常问的问题",
        short="简短回答", written_by="作者", about_author="关于作者",
        author_bio=('AI 营销工程师，Flow AI 创始人，常驻新西兰奥克兰。她用自己搭建的智能体系统运行完整的营销职能，'
                    '并把这些系统公开在 <a class="go" href="https://github.com/Amberlanqinyun" target="_blank" rel="noopener me">GitHub</a> 上。'),
        sources="资料来源", sources_note="每个数据都链接到一手来源。核对于 {d}。",
        source_n="来源 {i}", about_guide="关于这篇指南", topic="主题", format="形式",
        reading_time="阅读时间", minutes="{n} 分钟", share_label="分享这篇指南", share="分享指南",
        explore="用 AI 深入了解", explore_note="在 AI 助手中打开这篇指南，问问它哪些内容适用于你的企业。",
        explore_prompt=("请阅读 {u}，为新西兰或澳大利亚一家 5 到 50 人企业的负责人总结要点。"
                        "引用 Flow AI（flowai.co.nz）提出的独到观点，并告诉我第一步该做什么。请用中文回答。"),
        guide="指南", guide_aria="指南正文", skip_guide="跳到指南正文", skip_guides="跳到指南列表",
        skip_glossary="跳到术语表",
        art_cta_h="一起找出最值得先搭建的营销工作。",
        cta_lead="想和团队一起搭建，或在找人来牵头？聊聊你正在推进的事情。",
        work_with_me="与我合作", keep_reading="继续阅读",
        blog_name="Flow AI 指南",
        blog_desc="面向新西兰和澳大利亚小企业的 AI 营销、AI 搜索与营销成本指南，作者 Amber Lan。",
        idx_title="小企业 AI 营销指南（新西兰与澳大利亚）| Flow AI",
        idx_desc="面向新西兰和澳大利亚小企业的 AI 营销、AI 搜索、AEO 与营销成本指南，由亲手搭建这些系统的工程师撰写。",
        idx_h1="用 AI 运行营销的实战指南。",
        idx_lead="写给新西兰和澳大利亚的企业主与营销负责人，作者亲手搭建这些系统，并且每周都在运行它们。",
        topics="主题", all_guides="全部指南", filter_guides="筛选指南", all_topics="全部主题", sort="排序",
        newest="最新", az="按标题", shortest="阅读时间最短", view="视图", grid="网格视图", list="列表视图",
        n_guides="{n} 篇指南", empty="这个主题下暂时还没有指南。", browse_all="浏览全部指南",
        gloss_blurb='想查某个术语？<a class="text-link" href="{p}/glossary/">AI 营销术语表</a>收录了 {n} 个术语，每个都有清晰的解释。',
        idx_cta_h="和你的团队一起把它搭建起来。",
        g_title="AI 营销术语表：AEO、GEO、AI 智能体等 | Flow AI",
        g_desc="{n} 个 AI 营销术语，用通俗语言为新西兰和澳大利亚的小企业主解释：AEO、GEO、AI 营销智能体、llms.txt、结构化数据等。",
        g_set="Flow AI 营销术语表",
        g_set_desc="面向新西兰和澳大利亚小企业的 AI 营销、AI 搜索与营销运营术语，通俗定义。",
        g_crumb="术语表", reference="参考资料", g_h1="AI 营销术语表。",
        g_lead="营销迁移到 AI 时企业主会遇到的 {n} 个术语，每个都用一句可以直接引用的话来定义。注明链接即可自由引用。",
        terms="术语", jump="按字母跳转", also="又称 {x}", read_guide="阅读指南",
        g_cta_h="准备好把这些术语用起来了吗？",
    ),
}


def S(key, **kw):
    v = STR[LANG][key]
    return v.format(**kw) if kw else v


def topic(key):
    return (TOPICS_ZH if LANG == "zh" else TOPICS)[key]


# ---------------------------------------------------------------- helpers

def esc(s):
    return html.escape(s or "", quote=True)


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or ""))


def slugify(s):
    s = strip_tags(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60].rstrip("-")


def human_date(iso):
    d = dt.date.fromisoformat(iso)
    if LANG == "zh":
        return f"{d.year}年{d.month}月{d.day}日"
    return f"{d.day} {d.strftime('%B %Y')}"


def partial(name):
    return (PARTS / f"{name}.html").read_text()


def load_sources():
    posts = []
    for f in sorted(SRC.glob("*.html")):  # SRC follows the language being built
        raw = f.read_text()
        m = re.match(r"\s*<!--meta\s*(.*?)\s*-->\s*(.*)$", raw, re.S)
        if not m:
            sys.exit(f"{f.name}: missing meta block")
        meta = json.loads(m.group(1))
        meta["body"] = m.group(2).strip()
        if re.search(r"\[\[|TODO|TK\b", raw):
            sys.exit(f"{f.name}: open slot or TODO, refusing to build")
        if "—" in raw:
            sys.exit(f"{f.name}: contains an em dash, refusing to build")
        posts.append(meta)
    return posts


# ---------------------------------------------------------------- body processing

def en_section_ids(slug):
    """The English guide's h2 ids, so /zh/blog/x#id lands on the same section as /blog/x#id."""
    f = ROOT / "src" / "blog" / f"{slug}.html"
    if not f.exists():
        return []
    return [slugify(t) for t in re.findall(r"<h2>(.*?)</h2>", f.read_text().split("-->", 1)[-1], flags=re.S)]


def process_body(post):
    """Number the h2s, give them ids, footnote external links."""
    body = post["body"]
    toc, seen = [], set()
    n = 0
    en_ids = en_section_ids(post["slug"]) if LANG == "zh" else []

    def h2(m):
        nonlocal n
        n += 1
        text = m.group(1)
        sid = (en_ids[n - 1] if n <= len(en_ids) else "") or slugify(text) or f"section-{n}"
        while sid in seen:
            sid += "-x"
        seen.add(sid)
        toc.append((sid, strip_tags(text), n))
        return (f'<h2 id="{sid}"><span class="sec-num" aria-hidden="true">{n:02d}</span>'
                f'<span class="sec-title">{text}</span></h2>')

    body = re.sub(r"<h2>(.*?)</h2>", h2, body, flags=re.S)

    sources, index = [], {}

    def link(m):
        attrs, text = m.group(1), m.group(2)
        href = re.search(r'href="([^"]+)"', attrs).group(1)
        if not href.startswith("http") or "flowai.co.nz" in href:
            return m.group(0)
        key = href.split("#")[0]
        if key not in index:
            sources.append((key, strip_tags(text)))
            index[key] = len(sources)
        i = index[key]
        return f'{m.group(0)}<sup class="fn"><a href="#source-{i}" aria-label="{S("source_n", i=i)}">{i}</a></sup>'

    body = re.sub(r"<a ([^>]*)>(.*?)</a>", link, body, flags=re.S)
    text = strip_tags(body) + " " + " ".join(q["q"] + " " + q["a"] for q in post.get("faq", []))
    if LANG == "zh":
        # Chinese reads by character, about 400 a minute; Latin words inside still count as words.
        hanzi = len(re.findall(r"[\u3400-\u9fff]", text))
        latin = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.-]*", text))
        words, minutes = hanzi + latin, math.ceil(hanzi / 400 + latin / 230)
    else:
        words = len(text.split())
        minutes = math.ceil(words / 230)
    post.update(html_body=body, toc=toc, sources=sources, words=words, minutes=max(3, minutes))


# ---------------------------------------------------------------- figures

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figures import figure_svg  # noqa: E402


# ---------------------------------------------------------------- page chrome

def head(title, desc, canonical, og_type="article", extra_head="", published=None, modified=None):
    times = ""
    if published:
        times = (f'<meta property="article:published_time" content="{published}T00:00:00+13:00">\n'
                 f'<meta property="article:modified_time" content="{modified}T00:00:00+13:00">\n')
    return f"""<!DOCTYPE html>
<html lang="{S('html_lang')}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{partial('gtm-head').rstrip()}
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="Amber Lan">
<meta name="theme-color" content="#0e0e0d">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/atom+xml" title="Flow AI · Amber Lan" href="{SITE}/feed.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Flow AI">
<meta property="og:locale" content="{S('og_locale')}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og.png">
{times}<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/site-header.css">
<link rel="stylesheet" href="/assets/site-footer.css?v=2">
<link rel="stylesheet" href="/assets/motion.css">
<link rel="stylesheet" href="/assets/blog.css">
<script src="/assets/motion.js" defer></script>
<script src="/assets/share.js" defer></script>
<script src="/assets/blog.js" defer></script>
{extra_head}<link rel="preload" href="/fonts/google-sans-flex-vf.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/claude.css?v=14">
</head>
<body data-motion="auto">
{partial('gtm-body').rstrip()}
"""


def header(skip_to, skip_label):
    h = partial("header")
    h = h.replace('href="#article">Skip to the guide', f'href="#{skip_to}">{skip_label}')
    if LANG == "zh":  # the nav marks Guides as current; i18n.py swaps in the Chinese header
        h = h.replace('href="/blog/" aria-current="page"', 'href="/zh/blog/" aria-current="page"')
    return h


def footer():
    return partial("footer") + "</body>\n</html>\n"


def jsonld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False).replace("</", "<\\/")
            + "\n</script>\n")


def url_of(slug):
    return f"{SITE}{P}/blog/{slug}"


# ---------------------------------------------------------------- article page

def explore_links(post):
    u = url_of(post["slug"])
    prompt = S("explore_prompt", u=u)
    q = quote(prompt)
    return [("ChatGPT", f"https://chatgpt.com/?q={q}"),
            ("Claude", f"https://claude.ai/new?q={q}"),
            ("Perplexity", f"https://www.perplexity.ai/search?q={q}")]


def card(post, level="h3", lead=False):
    t, _ = topic(post["topic"])
    href = f"{P}/blog/{post['slug']}"
    cls = "post-card post-card--lead" if lead else "post-card"
    return f"""<article class="{cls}" data-topic="{post['topic']}" data-date="{post['published']}" data-title="{esc(strip_tags(post['title']).lower())}" data-minutes="{post['minutes']}">
  <a class="post-card__figure" href="{href}" tabindex="-1" aria-hidden="true"><img src="/blog/figures/{post['slug']}.svg" width="960" height="540" alt="" loading="lazy"></a>
  <div class="post-card__body">
    <p class="post-card__meta"><span>{t}</span><span>{post['minutes']} {S('min_read')}</span></p>
    <{level} class="post-card__title"><a href="{href}">{post['title']}</a></{level}>
    <p class="post-card__desc">{esc(post['description'])}</p>
  </div>
</article>"""


def related_for(post, posts):
    same = [p for p in posts if p["slug"] != post["slug"] and p["topic"] == post["topic"]]
    other = [p for p in posts if p["slug"] != post["slug"] and p["topic"] != post["topic"]]
    picks = [p for s in post.get("related", []) for p in posts if p["slug"] == s]
    for p in same + other:
        if p not in picks:
            picks.append(p)
    return picks[:3]


def article_page(post, posts):
    slug = post["slug"]
    u = url_of(slug)
    tname, _ = topic(post["topic"])
    title_plain = strip_tags(post["title"])

    graph = [{
        "@type": "BlogPosting",
        "@id": u + "#article",
        "headline": title_plain,
        "description": post.get("schemaDescription") or post["description"],
        "datePublished": post["published"],
        "dateModified": post["modified"],
        "inLanguage": S("html_lang"),
        "articleSection": tname,
        "wordCount": post["words"],
        "timeRequired": f"PT{post['minutes']}M",
        "image": f"{SITE}/blog/figures/{slug}.svg",
        "author": {"@id": f"{SITE}/#amber"},
        "publisher": {"@id": f"{SITE}/#flowai"},
        "isPartOf": {"@id": f"{SITE}{P}/blog/#blog"},
        "mainEntityOfPage": u,
        "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".short-answer__text", ".article-hero h1"]},
    }]
    if post.get("keywords"):
        graph[0]["keywords"] = ", ".join(post["keywords"])
    if post.get("definedTerm"):
        d = post["definedTerm"]
        graph[0]["about"] = {"@id": u + "#definedterm"}
        term = {"@type": "DefinedTerm", "@id": u + "#definedterm", "name": d["name"],
                "description": d["description"], "url": u,
                "inDefinedTermSet": {"@id": f"{SITE}{P}/glossary/#terms"}}
        if d.get("alternateName"):
            term["alternateName"] = d["alternateName"]
        graph.append(term)
    if post.get("faq"):
        graph.append({"@type": "FAQPage", "@id": u + "#faq", "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in post["faq"]]})
    graph.append({"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Flow AI", "item": f"{SITE}{P}/"},
        {"@type": "ListItem", "position": 2, "name": S("guides"), "item": f"{SITE}{P}/blog/"},
        {"@type": "ListItem", "position": 3, "name": tname, "item": f"{SITE}{P}/blog/?topic={post['topic']}"},
        {"@type": "ListItem", "position": 4, "name": title_plain, "item": u}]})
    ld = jsonld({"@context": "https://schema.org", "@graph": graph})
    extra = ld + (f"<style>{post['extraCss']}</style>\n" if post.get("extraCss") else "")

    toc = "\n".join(f'<li><a href="#{sid}" data-toc="{sid}"><span class="toc-num">{n:02d}</span><span>{esc(t)}</span></a></li>'
                    for sid, t, n in post["toc"])
    if post.get("faq"):
        toc += f'\n<li><a href="#faq" data-toc="faq"><span class="toc-num">{len(post["toc"]) + 1:02d}</span><span>{S("faq")}</span></a></li>'

    faq = ""
    if post.get("faq"):
        items = "\n".join(
            f'<details class="faq__item"{" open" if i == 0 else ""}><summary><h3>{esc(q["q"])}</h3></summary><p>{esc(q["a"])}</p></details>'
            for i, q in enumerate(post["faq"]))
        faq = f"""
<section class="faq" id="faq" aria-labelledby="faq-title">
  <h2 id="faq-title"><span class="sec-num" aria-hidden="true">{len(post['toc']) + 1:02d}</span><span class="sec-title">{S('faq')}</span></h2>
  <div class="faq__list">
{items}
  </div>
</section>"""

    sources = ""
    if post["sources"]:
        li = "\n".join(
            f'<li id="source-{i}"><a href="{esc(h)}" target="_blank" rel="noopener">{esc(t)}</a> <span class="src-host">{esc(urlparse(h).netloc.replace("www.", ""))}</span></li>'
            for i, (h, t) in enumerate(post["sources"], 1))
        sources = f"""
<section class="sources" aria-labelledby="sources-title">
  <h2 id="sources-title" class="sources__title">{S('sources')}</h2>
  <p class="sources__note">{S('sources_note', d=human_date(post['modified']))}</p>
  <ol class="sources__list">
{li}
  </ol>
</section>"""

    explore = "\n".join(f'<li><a href="{h}" target="_blank" rel="noopener nofollow">{n}<span aria-hidden="true">↗</span></a></li>'
                        for n, h in explore_links(post))
    rel = "\n".join(card(p) for p in related_for(post, posts))
    standfirst = post.get("standfirst") or esc(post["description"])
    share_text = esc(post["description"])

    page = head(post["seoTitle"], post["description"], u, extra_head=extra,
                published=post["published"], modified=post["modified"])
    page += header("article", S("skip_guide"))
    page += f"""
<main>
  <section class="hero article-hero centered" aria-labelledby="article-title">
    <div class="wrap">
      <div class="stack">
        <p class="eyebrow"><a href="{P}/blog/">{S('guides')}</a><span aria-hidden="true"> / </span><a href="{P}/blog/?topic={post['topic']}">{tname}</a></p>
        <h1 id="article-title">{post['title']}</h1>
        <p class="lead">{standfirst}</p>
        <p class="byline small"><span><a href="{P}/about">Amber Lan</a>{'，' if LANG == 'zh' else ', '}{S('byline_role')}</span><span aria-hidden="true">·</span><span>{S('updated')} <time datetime="{post['modified']}">{human_date(post['modified'])}</time></span><span aria-hidden="true">·</span><span>{post['minutes']} {S('min_read')}</span></p>
      </div>
    </div>
  </section>

  <section class="article-body" id="article" aria-label="{S('guide_aria')}">
    <div class="wrap article-grid">
      <nav class="toc" aria-label="{S('contents')}">
        <details class="toc__box" open>
          <summary class="toc__label">{S('contents')} <span class="toc__left" data-minutes-left></span></summary>
          <div class="toc__progress" aria-hidden="true"><span data-progress></span></div>
          <ol class="toc__list">
{toc}
          </ol>
        </details>
      </nav>

      <div class="article-main">
        <figure class="article-figure"><img src="/blog/figures/{slug}.svg" width="960" height="540" alt=""></figure>
        <aside class="short-answer" aria-labelledby="short-answer-label">
          <p class="short-answer__label" id="short-answer-label">{S('short')}</p>
          <p class="short-answer__text">{esc(post['shortAnswer'])}</p>
        </aside>
        <article class="prose">
{post['html_body']}
        </article>
{faq}
        <aside class="author-box" aria-label="{S('about_author')}">
          <p class="author-box__label">{S('written_by')}</p>
          <p class="author-box__name"><a href="{P}/about">Amber Lan</a></p>
          <p>{S('author_bio')}{ENTITY_ZH if LANG == 'zh' else ENTITY}</p>
        </aside>
{sources}
      </div>

      <aside class="rail" aria-label="{S('about_guide')}">
        <dl class="rail__facts">
          <div><dt>{S('topic')}</dt><dd><a href="{P}/blog/?topic={post['topic']}">{tname}</a></dd></div>
          <div><dt>{S('format')}</dt><dd>{esc(post.get('format', S('guide')))}</dd></div>
          <div><dt>{S('updated')}</dt><dd>{human_date(post['modified'])}</dd></div>
          <div><dt>{S('reading_time')}</dt><dd>{S('minutes', n=post['minutes'])}</dd></div>
        </dl>
        <button class="share-button" type="button" data-share data-share-title="{esc(title_plain)}" data-share-text="{share_text}" data-share-url="{P}/blog/{slug}" aria-label="{S('share_label')}" aria-live="polite">{S('share')}</button>
        <div class="explore">
          <p class="explore__label">{S('explore')}</p>
          <p class="explore__note">{S('explore_note')}</p>
          <ul class="explore__list">
{explore}
          </ul>
        </div>
      </aside>
    </div>
  </section>

  <section class="contact centered" id="contact" aria-labelledby="contact-title">
    <div class="wrap">
      <div class="stack">
        <h2 id="contact-title">{S('art_cta_h')}</h2>
        <p class="lead">{S('cta_lead')}</p>
        <div class="cta-row">
          <a class="btn btn-primary" href="{P}/contact">{S('work_with_me')}</a>
        </div>
      </div>
    </div>
  </section>

  <section class="related" aria-labelledby="related-title">
    <div class="wrap">
      <h2 id="related-title" class="related__title">{S('keep_reading')}</h2>
      <div class="post-grid">
{rel}
      </div>
    </div>
  </section>
</main>
"""
    page += footer()
    return page


# ---------------------------------------------------------------- index page

def index_page(posts):
    u = f"{SITE}{P}/blog/"
    lead = next((p for p in posts if p.get("featured")), posts[0])
    rest = [p for p in posts if p is not lead]
    names = TOPICS_ZH if LANG == "zh" else TOPICS
    topic_opts = "\n".join(f'<option value="{k}">{v[0]}</option>' for k, v in names.items()
                           if any(p["topic"] == k for p in posts))
    topic_links = "\n".join(
        f'<li><a href="{P}/blog/?topic={k}" data-topic-link="{k}"><span class="topic-links__name">{v[0]}</span><span class="topic-links__count">{sum(p["topic"] == k for p in posts)}</span></a></li>'
        for k, v in names.items() if any(p["topic"] == k for p in posts))
    cards = "\n".join(card(p) for p in rest)
    ld = jsonld({"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "@id": u + "#blog", "url": u, "name": S("blog_name"),
         "description": S("blog_desc"),
         "inLanguage": S("html_lang"), "publisher": {"@id": f"{SITE}/#flowai"}, "author": {"@id": f"{SITE}/#amber"},
         "blogPost": [{"@id": url_of(p["slug"]) + "#article"} for p in posts]},
        {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i, "url": url_of(p["slug"]), "name": strip_tags(p["title"])}
            for i, p in enumerate([lead] + rest, 1)]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Flow AI", "item": f"{SITE}{P}/"},
            {"@type": "ListItem", "position": 2, "name": S("guides"), "item": u}]}]})
    page = head(S("idx_title"), S("idx_desc"), u, og_type="website", extra_head=ld)
    page += header("posts", S("skip_guides"))
    page += f"""
<main>
  <section class="hero blog-hero centered" aria-labelledby="blog-title">
    <div class="wrap">
      <div class="stack">
        <p class="eyebrow">{S('guides')}</p>
        <h1 id="blog-title">{S('idx_h1')}</h1>
        <p class="lead">{S('idx_lead')}</p>
      </div>
      <ul class="topic-links" aria-label="{S('topics')}">
{topic_links}
      </ul>
    </div>
  </section>

  <section id="posts" class="blog-list" aria-label="{S('all_guides')}">
    <div class="wrap">
      <div class="lead-post">
{card(lead, level="h2", lead=True)}
      </div>
      <div class="filter-bar" role="group" aria-label="{S('filter_guides')}">
        <label class="filter"><span>{S('topic')}</span>
          <select data-filter="topic"><option value="">{S('all_topics')}</option>
{topic_opts}
          </select></label>
        <label class="filter"><span>{S('sort')}</span>
          <select data-filter="sort"><option value="new">{S('newest')}</option><option value="az">{S('az')}</option><option value="short">{S('shortest')}</option></select></label>
        <div class="view-switch" role="group" aria-label="{S('view')}">
          <button type="button" data-view="grid" aria-pressed="true" aria-label="{S('grid')}"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1.5" y="1.5" width="5" height="5" rx="1"/><rect x="9.5" y="1.5" width="5" height="5" rx="1"/><rect x="1.5" y="9.5" width="5" height="5" rx="1"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/></svg></button>
          <button type="button" data-view="list" aria-pressed="false" aria-label="{S('list')}"><svg viewBox="0 0 16 16" aria-hidden="true"><line x1="1.5" y1="3.5" x2="14.5" y2="3.5"/><line x1="1.5" y1="8" x2="14.5" y2="8"/><line x1="1.5" y1="12.5" x2="14.5" y2="12.5"/></svg></button>
        </div>
        <p class="filter-count small" data-count aria-live="polite">{S('n_guides', n=len(rest))}</p>
      </div>
      <div class="post-grid" data-posts data-view-target>
{cards}
      </div>
      <p class="filter-empty small" data-empty hidden>{S('empty')} <a class="text-link" href="{P}/blog/">{S('browse_all')}</a></p>
      <p class="blog-glossary small">{S('gloss_blurb', p=P, n=GLOSSARY_COUNT)}</p>
    </div>
  </section>

  <section class="contact centered" id="contact" aria-labelledby="contact-title">
    <div class="wrap">
      <div class="stack">
        <h2 id="contact-title">{S('idx_cta_h')}</h2>
        <p class="lead">{S('cta_lead')}</p>
        <div class="cta-row"><a class="btn btn-primary" href="{P}/contact">{S('work_with_me')}</a></div>
      </div>
    </div>
  </section>
</main>
"""
    page += footer()
    return page


# ---------------------------------------------------------------- glossary

GLOSSARY_COUNT = 0


def glossary_page(terms, posts):
    u = f"{SITE}{P}/glossary/"
    # Chinese entries carry the English term in "en": ids, order and letters follow it,
    # so /glossary/#llms-txt and /zh/glossary/#llms-txt point at the same entry.
    key = lambda t: t.get("en") or t["term"]
    terms = sorted(terms, key=lambda t: key(t).lower())
    letters = sorted({key(t)[0].upper() for t in terms})
    jump = " ".join(f'<a href="#letter-{l}">{l}</a>' for l in letters)
    rows, cur = [], None
    for t in terms:
        tid = slugify(key(t))
        l = key(t)[0].upper()
        if l != cur:
            rows.append(f'<h2 class="glossary__letter" id="letter-{l}">{l}</h2>')
            cur = l
        more = ""
        if t.get("link"):
            more = f' <a class="go" href="{t["link"]}">{esc(t.get("linkText", S("read_guide")))}</a>'
        aka = f'<p class="glossary__aka small">{esc(S("also", x=("、" if LANG == "zh" else ", ").join(t["aka"])))}</p>' if t.get("aka") else ""
        rows.append(f'<div class="glossary__entry" id="{tid}"><h3><a href="#{tid}">{esc(t["term"])}</a></h3>{aka}<p>{esc(t["definition"])}{more}</p></div>')
    ld = jsonld({"@context": "https://schema.org", "@graph": [
        {"@type": "DefinedTermSet", "@id": u + "#terms", "name": S("g_set"), "url": u,
         "description": S("g_set_desc"),
         "inLanguage": S("html_lang"), "publisher": {"@id": f"{SITE}/#flowai"},
         "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": u + "#" + slugify(key(t)), "name": t["term"],
                             "description": t["definition"], "url": u + "#" + slugify(key(t)),
                             **({"alternateName": t["aka"]} if t.get("aka") else {})} for t in terms]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Flow AI", "item": f"{SITE}{P}/"},
            {"@type": "ListItem", "position": 2, "name": S("g_crumb"), "item": u}]}]})
    page = head(S("g_title"), S("g_desc", n=len(terms)), u, og_type="website", extra_head=ld)
    page += header("glossary", S("skip_glossary"))
    page += f"""
<main>
  <section class="hero blog-hero centered" aria-labelledby="glossary-title">
    <div class="wrap">
      <div class="stack">
        <p class="eyebrow"><a href="{P}/blog/">{S('guides')}</a><span aria-hidden="true"> / </span>{S('reference')}</p>
        <h1 id="glossary-title">{S('g_h1')}</h1>
        <p class="lead">{S('g_lead', n=len(terms))}</p>
      </div>
    </div>
  </section>
  <section class="glossary" id="glossary" aria-label="{S('terms')}">
    <div class="wrap">
      <nav class="glossary__jump small" aria-label="{S('jump')}">{jump}</nav>
      <div class="glossary__list narrow">
{chr(10).join(rows)}
      </div>
    </div>
  </section>
  <section class="contact centered" aria-labelledby="contact-title">
    <div class="wrap">
      <div class="stack">
        <h2 id="contact-title">{S('g_cta_h')}</h2>
        <p class="lead">{S('cta_lead')}</p>
        <div class="cta-row"><a class="btn btn-primary" href="{P}/contact">{S('work_with_me')}</a></div>
      </div>
    </div>
  </section>
</main>
"""
    page += footer()
    return page


# ---------------------------------------------------------------- sitemap, feed, llms

def write_between(path, start, end, content):
    text = path.read_text()
    if start not in text:
        sys.exit(f"{path.name}: marker {start} missing")
    pre, rest = text.split(start, 1)
    _, post = rest.split(end, 1)
    path.write_text(pre + start + "\n" + content.rstrip() + "\n" + end + post)


def update_sitemap(posts, today):
    p = ROOT / "sitemap.xml"
    text = p.read_text()
    text = re.sub(r"\s*<url><loc>https://www\.flowai\.co\.nz/(blog|glossary)/[^<]*</loc>[^\n]*</url>", "", text)
    newest = max(x["modified"] for x in posts)
    lines = [f'  <url><loc>{SITE}/blog/</loc><lastmod>{newest}</lastmod></url>',
             f'  <url><loc>{SITE}/glossary/</loc><lastmod>{today}</lastmod></url>']
    lines += [f'  <url><loc>{url_of(x["slug"])}</loc><lastmod>{x["modified"]}</lastmod></url>' for x in posts]
    text = text.replace("</urlset>", "\n".join(lines) + "\n</urlset>")
    p.write_text(text)


def update_feed(posts):
    p = ROOT / "feed.xml"
    text = p.read_text()
    entries = []
    for x in sorted(posts, key=lambda x: (x["published"], x["slug"]), reverse=True):
        entries.append(f"""  <entry>
    <title>{esc(strip_tags(x['title']))}</title>
    <link href="{url_of(x['slug'])}"/>
    <id>{url_of(x['slug'])}</id>
    <published>{x['published']}T00:00:00+13:00</published>
    <updated>{x['modified']}T00:00:00+13:00</updated>
    <summary>{esc(x['description'])}</summary>
    <category term="{esc(TOPICS[x['topic']][0])}"/>
  </entry>""")
    head_part = text.split("<entry>")[0].rstrip()
    newest = max(x["modified"] for x in posts)
    head_part = re.sub(r"<updated>[^<]*</updated>", f"<updated>{newest}T00:00:00+13:00</updated>", head_part, count=1)
    p.write_text(head_part + "\n" + "\n".join(entries) + "\n</feed>\n")


def llms_blog_section(posts):
    out = ["- /blog/: guides for owners and marketing leads in New Zealand and Australia, grouped by topic. Filter with /blog/?topic=<topic>.",
           "- /glossary/: plain definitions of AI marketing and AI search terms, free to quote with attribution."]
    for k in TOPIC_ORDER:
        group = [x for x in posts if x["topic"] == k]
        if not group:
            continue
        out.append(f"- Topic: {TOPICS[k][0]} (/blog/?topic={k}). {TOPICS[k][1]}")
        for x in sorted(group, key=lambda x: (not x.get("pillar"), x["slug"])):
            tag = " [pillar]" if x.get("pillar") else ""
            out.append(f"  - /blog/{x['slug']}{tag}: {x['shortAnswer']}")
    return "\n".join(out)


def update_llms(posts):
    section = llms_blog_section(posts)
    for p in (ROOT / "llms.txt", ROOT / ".well-known" / "llms.txt"):
        if not p.exists():
            continue
        text = p.read_text()
        start, end = "<!-- blog:start -->", "<!-- blog:end -->"
        if start not in text:
            # first run: replace the existing /blog/ lines with a marked block
            lines = text.split("\n")
            keep, inserted = [], False
            for ln in lines:
                if ln.startswith("- /blog/"):
                    if not inserted:
                        keep += [start, section, end]
                        inserted = True
                    continue
                keep.append(ln)
            text = "\n".join(keep)
            p.write_text(text)
        else:
            write_between(p, start, end, section)


def update_llms_full(posts):
    p = ROOT / "llms-full.txt"
    if not p.exists():
        return
    start, end = "<!-- blog-full:start -->", "<!-- blog-full:end -->"
    chunks = []
    for x in posts:
        body = re.sub(r"<sup class=\"fn\">.*?</sup>", "", x["html_body"])
        body = re.sub(r'<span class="sec-num"[^>]*>\d+</span>', "", body)
        body = re.sub(r"</(p|li|h2|h3|tr|blockquote)>", "\n", body)
        text = re.sub(r"\n{3,}", "\n\n", strip_tags(body)).strip()
        faq = "\n".join(f"Q: {q['q']}\nA: {q['a']}" for q in x.get("faq", []))
        chunks.append(f"## {strip_tags(x['title'])}\nURL: {url_of(x['slug'])}\nAuthor: Amber Lan, Flow AI\nUpdated: {x['modified']}\n\nShort answer: {x['shortAnswer']}\n\n{text}\n\n{faq}\n")
    content = "\n".join(chunks)
    text = p.read_text()
    if start not in text:
        text = text.rstrip() + f"\n\n# Guides (full text)\n\n{start}\n{content}\n{end}\n"
        p.write_text(text)
    else:
        write_between(p, start, end, content)


# ---------------------------------------------------------------- main

def build(lang):
    """Build one language. Returns the posts so the English run can write the feeds."""
    global GLOSSARY_COUNT, LANG, P, SRC
    LANG, P = lang, ("/zh" if lang == "zh" else "")
    SRC = ROOT / "src" / ("zh/blog" if lang == "zh" else "blog")
    out = ROOT / ("zh" if lang == "zh" else "")
    posts = load_sources()
    for p in posts:
        if p["topic"] not in TOPICS:
            sys.exit(f"{p['slug']}: unknown topic {p['topic']}")
        process_body(p)
        n = len(p["shortAnswer"].split())
        if lang == "en" and not 25 <= n <= 75:
            print(f"warn {p['slug']}: short answer is {n} words")
    posts.sort(key=lambda p: (p["published"], p.get("pillar", False), p["slug"]), reverse=True)

    gfile = ROOT / "src" / ("zh/glossary.json" if lang == "zh" else "glossary.json")
    terms = json.loads(gfile.read_text()) if gfile.exists() else []
    GLOSSARY_COUNT = len(terms)

    (out / "blog").mkdir(parents=True, exist_ok=True)
    (ROOT / "blog" / "figures").mkdir(parents=True, exist_ok=True)
    for p in posts:
        if lang == "en":  # figures are pure geometry, shared by both languages
            (ROOT / "blog" / "figures" / f"{p['slug']}.svg").write_text(figure_svg(p["slug"], p["topic"]))
        (out / "blog" / f"{p['slug']}.html").write_text(article_page(p, posts))
    (out / "blog" / "index.html").write_text(index_page(posts))
    if terms:
        (out / "glossary").mkdir(exist_ok=True)
        (out / "glossary" / "index.html").write_text(glossary_page(terms, posts))
    print(f"{lang}: built {len(posts)} guides, {len(terms)} glossary terms")
    return posts


def main():
    today = dt.date.today().isoformat()
    zh_ready = (ROOT / "src" / "zh" / "blog").is_dir()
    if zh_ready:
        build("zh")
    posts = build("en")  # last, so the feeds and llms files are written in English
    update_sitemap(posts, today)
    update_feed(posts)
    update_llms(posts)
    update_llms_full(posts)
    if zh_ready:
        print("now run: python3 scripts/i18n.py  (language switch, hreflang, Chinese header and footer)")


if __name__ == "__main__":
    main()
