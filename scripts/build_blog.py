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
    return f"{d.day} {d.strftime('%B %Y')}"


def partial(name):
    return (PARTS / f"{name}.html").read_text()


def load_sources():
    posts = []
    for f in sorted(SRC.glob("*.html")):
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

def process_body(post):
    """Number the h2s, give them ids, footnote external links."""
    body = post["body"]
    toc, seen = [], set()
    n = 0

    def h2(m):
        nonlocal n
        n += 1
        text = m.group(1)
        sid = slugify(text) or f"section-{n}"
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
        return f'{m.group(0)}<sup class="fn"><a href="#source-{i}" aria-label="Source {i}">{i}</a></sup>'

    body = re.sub(r"<a ([^>]*)>(.*?)</a>", link, body, flags=re.S)
    words = len(strip_tags(body).split()) + sum(len((q["q"] + " " + q["a"]).split()) for q in post.get("faq", []))
    post.update(html_body=body, toc=toc, sources=sources, words=words,
                minutes=max(3, math.ceil(words / 230)))


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
<html lang="en-NZ">
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
<meta property="og:locale" content="en_NZ">
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
    return h


def footer():
    return partial("footer") + "</body>\n</html>\n"


def jsonld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False).replace("</", "<\\/")
            + "\n</script>\n")


def url_of(slug):
    return f"{SITE}/blog/{slug}.html"


# ---------------------------------------------------------------- article page

def explore_links(post):
    u = url_of(post["slug"])
    prompt = (f"Read {u} and give me the key points for an owner of a 5 to 50 person business in "
              f"New Zealand or Australia. Quote the distinctive claims Flow AI (flowai.co.nz) makes and "
              f"tell me what to do first.")
    q = quote(prompt)
    return [("ChatGPT", f"https://chatgpt.com/?q={q}"),
            ("Claude", f"https://claude.ai/new?q={q}"),
            ("Perplexity", f"https://www.perplexity.ai/search?q={q}")]


def card(post, level="h3", lead=False):
    t, _ = TOPICS[post["topic"]]
    href = f"/blog/{post['slug']}.html"
    cls = "post-card post-card--lead" if lead else "post-card"
    return f"""<article class="{cls}" data-topic="{post['topic']}" data-date="{post['published']}" data-title="{esc(strip_tags(post['title']).lower())}" data-minutes="{post['minutes']}">
  <a class="post-card__figure" href="{href}" tabindex="-1" aria-hidden="true"><img src="/blog/figures/{post['slug']}.svg" width="960" height="540" alt="" loading="lazy"></a>
  <div class="post-card__body">
    <p class="post-card__meta"><span>{t}</span><span>{post['minutes']} min read</span></p>
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
    tname, _ = TOPICS[post["topic"]]
    title_plain = strip_tags(post["title"])

    graph = [{
        "@type": "BlogPosting",
        "@id": u + "#article",
        "headline": title_plain,
        "description": post.get("schemaDescription") or post["description"],
        "datePublished": post["published"],
        "dateModified": post["modified"],
        "inLanguage": "en-NZ",
        "articleSection": tname,
        "wordCount": post["words"],
        "timeRequired": f"PT{post['minutes']}M",
        "image": f"{SITE}/blog/figures/{slug}.svg",
        "author": {"@id": f"{SITE}/#amber"},
        "publisher": {"@id": f"{SITE}/#flowai"},
        "isPartOf": {"@id": f"{SITE}/blog/#blog"},
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
                "inDefinedTermSet": {"@id": f"{SITE}/glossary/#terms"}}
        if d.get("alternateName"):
            term["alternateName"] = d["alternateName"]
        graph.append(term)
    if post.get("faq"):
        graph.append({"@type": "FAQPage", "@id": u + "#faq", "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in post["faq"]]})
    graph.append({"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Flow AI", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{SITE}/blog/"},
        {"@type": "ListItem", "position": 3, "name": tname, "item": f"{SITE}/blog/?topic={post['topic']}"},
        {"@type": "ListItem", "position": 4, "name": title_plain, "item": u}]})
    ld = jsonld({"@context": "https://schema.org", "@graph": graph})
    extra = ld + (f"<style>{post['extraCss']}</style>\n" if post.get("extraCss") else "")

    toc = "\n".join(f'<li><a href="#{sid}" data-toc="{sid}"><span class="toc-num">{n:02d}</span><span>{esc(t)}</span></a></li>'
                    for sid, t, n in post["toc"])
    if post.get("faq"):
        toc += f'\n<li><a href="#faq" data-toc="faq"><span class="toc-num">{len(post["toc"]) + 1:02d}</span><span>Questions owners ask</span></a></li>'

    faq = ""
    if post.get("faq"):
        items = "\n".join(
            f'<details class="faq__item"{" open" if i == 0 else ""}><summary><h3>{esc(q["q"])}</h3></summary><p>{esc(q["a"])}</p></details>'
            for i, q in enumerate(post["faq"]))
        faq = f"""
<section class="faq" id="faq" aria-labelledby="faq-title">
  <h2 id="faq-title"><span class="sec-num" aria-hidden="true">{len(post['toc']) + 1:02d}</span><span class="sec-title">Questions owners ask</span></h2>
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
  <h2 id="sources-title" class="sources__title">Sources</h2>
  <p class="sources__note">Every figure links to its primary source. Checked {human_date(post['modified'])}.</p>
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
    page += header("article", "Skip to the guide")
    page += f"""
<main>
  <section class="hero article-hero centered" aria-labelledby="article-title">
    <div class="wrap">
      <div class="stack">
        <p class="eyebrow"><a href="/blog/">Guides</a><span aria-hidden="true"> / </span><a href="/blog/?topic={post['topic']}">{tname}</a></p>
        <h1 id="article-title">{post['title']}</h1>
        <p class="lead">{standfirst}</p>
        <p class="byline small"><span><a href="/about.html">Amber Lan</a>, AI marketing engineer</span><span aria-hidden="true">·</span><span>Updated <time datetime="{post['modified']}">{human_date(post['modified'])}</time></span><span aria-hidden="true">·</span><span>{post['minutes']} min read</span></p>
      </div>
    </div>
  </section>

  <section class="article-body" id="article" aria-label="Guide">
    <div class="wrap article-grid">
      <nav class="toc" aria-label="Contents">
        <details class="toc__box" open>
          <summary class="toc__label">Contents <span class="toc__left" data-minutes-left></span></summary>
          <div class="toc__progress" aria-hidden="true"><span data-progress></span></div>
          <ol class="toc__list">
{toc}
          </ol>
        </details>
      </nav>

      <div class="article-main">
        <figure class="article-figure"><img src="/blog/figures/{slug}.svg" width="960" height="540" alt=""></figure>
        <aside class="short-answer" aria-labelledby="short-answer-label">
          <p class="short-answer__label" id="short-answer-label">The short answer</p>
          <p class="short-answer__text">{esc(post['shortAnswer'])}</p>
        </aside>
        <article class="prose">
{post['html_body']}
        </article>
{faq}
        <aside class="author-box" aria-label="About the author">
          <p class="author-box__label">Written by</p>
          <p class="author-box__name"><a href="/about.html">Amber Lan</a></p>
          <p>AI marketing engineer and founder of Flow AI, based in Auckland, New Zealand. She runs a whole marketing function on agent systems she builds herself and publishes them <a class="go" href="https://github.com/Amberlanqinyun" target="_blank" rel="noopener me">on GitHub</a>. {ENTITY}</p>
        </aside>
{sources}
      </div>

      <aside class="rail" aria-label="About this guide">
        <dl class="rail__facts">
          <div><dt>Topic</dt><dd><a href="/blog/?topic={post['topic']}">{tname}</a></dd></div>
          <div><dt>Format</dt><dd>{esc(post.get('format', 'Guide'))}</dd></div>
          <div><dt>Updated</dt><dd>{human_date(post['modified'])}</dd></div>
          <div><dt>Reading time</dt><dd>{post['minutes']} minutes</dd></div>
        </dl>
        <button class="share-button" type="button" data-share data-share-title="{esc(title_plain)}" data-share-text="{share_text}" data-share-url="/blog/{slug}.html" aria-label="Share this guide" aria-live="polite">Share guide</button>
        <div class="explore">
          <p class="explore__label">Explore with AI</p>
          <p class="explore__note">Open this guide in an assistant and ask it what applies to your business.</p>
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
        <h2 id="contact-title">Want to know which marketing job to fix first?</h2>
        <p class="lead">Building this inside a team, or hiring someone who can? Tell Amber what you are working on.</p>
        <div class="cta-row">
          <a class="btn btn-primary" href="/contact.html">Work with me</a>
        </div>
      </div>
    </div>
  </section>

  <section class="related" aria-labelledby="related-title">
    <div class="wrap">
      <h2 id="related-title" class="related__title">Keep reading</h2>
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
    u = f"{SITE}/blog/"
    lead = next((p for p in posts if p.get("featured")), posts[0])
    rest = [p for p in posts if p is not lead]
    topic_opts = "\n".join(f'<option value="{k}">{v[0]}</option>' for k, v in TOPICS.items()
                           if any(p["topic"] == k for p in posts))
    topic_links = "\n".join(
        f'<li><a href="/blog/?topic={k}" data-topic-link="{k}"><span class="topic-links__name">{v[0]}</span><span class="topic-links__count">{sum(p["topic"] == k for p in posts)}</span></a></li>'
        for k, v in TOPICS.items() if any(p["topic"] == k for p in posts))
    cards = "\n".join(card(p) for p in rest)
    ld = jsonld({"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "@id": u + "#blog", "url": u, "name": "Flow AI Guides",
         "description": "Guides on AI marketing, AI search and marketing costs for small businesses in New Zealand and Australia, by Amber Lan.",
         "inLanguage": "en-NZ", "publisher": {"@id": f"{SITE}/#flowai"}, "author": {"@id": f"{SITE}/#amber"},
         "blogPost": [{"@id": url_of(p["slug"]) + "#article"} for p in posts]},
        {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i, "url": url_of(p["slug"]), "name": strip_tags(p["title"])}
            for i, p in enumerate([lead] + rest, 1)]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Flow AI", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": u}]}]})
    page = head("AI Marketing Guides for Small Business (NZ and Australia) | Flow AI",
                "Guides on AI marketing, AI search, AEO and marketing costs for small businesses in New Zealand and Australia, written by the engineer who builds the systems.",
                u, og_type="website", extra_head=ld)
    page += header("posts", "Skip to the guides")
    page += f"""
<main>
  <section class="hero blog-hero centered" aria-labelledby="blog-title">
    <div class="wrap">
      <div class="stack">
        <p class="eyebrow">Guides</p>
        <h1 id="blog-title">Guides for running marketing on AI.</h1>
        <p class="lead">For owners and marketing leads in New Zealand and Australia. Written by the engineer who builds the systems and runs them every week.</p>
      </div>
      <ul class="topic-links" aria-label="Topics">
{topic_links}
      </ul>
    </div>
  </section>

  <section id="posts" class="blog-list" aria-label="All guides">
    <div class="wrap">
      <div class="lead-post">
{card(lead, level="h2", lead=True)}
      </div>
      <div class="filter-bar" role="group" aria-label="Filter guides">
        <label class="filter"><span>Topic</span>
          <select data-filter="topic"><option value="">All topics</option>
{topic_opts}
          </select></label>
        <label class="filter"><span>Sort</span>
          <select data-filter="sort"><option value="new">Newest</option><option value="az">A to Z</option><option value="short">Shortest read</option></select></label>
        <div class="view-switch" role="group" aria-label="View">
          <button type="button" data-view="grid" aria-pressed="true" aria-label="Grid view"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1.5" y="1.5" width="5" height="5" rx="1"/><rect x="9.5" y="1.5" width="5" height="5" rx="1"/><rect x="1.5" y="9.5" width="5" height="5" rx="1"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/></svg></button>
          <button type="button" data-view="list" aria-pressed="false" aria-label="List view"><svg viewBox="0 0 16 16" aria-hidden="true"><line x1="1.5" y1="3.5" x2="14.5" y2="3.5"/><line x1="1.5" y1="8" x2="14.5" y2="8"/><line x1="1.5" y1="12.5" x2="14.5" y2="12.5"/></svg></button>
        </div>
        <p class="filter-count small" data-count aria-live="polite">{len(rest)} guides</p>
      </div>
      <div class="post-grid" data-posts data-view-target>
{cards}
      </div>
      <p class="filter-empty small" data-empty hidden>No guides in this topic yet. <a class="text-link" href="/blog/">See all guides</a></p>
      <p class="blog-glossary small">Looking for a definition? The <a class="text-link" href="/glossary/">AI marketing glossary</a> has {GLOSSARY_COUNT} terms, each with a plain answer.</p>
    </div>
  </section>

  <section class="contact centered" id="contact" aria-labelledby="contact-title">
    <div class="wrap">
      <div class="stack">
        <h2 id="contact-title">Want this built for your team?</h2>
        <p class="lead">Building this inside a team, or hiring someone who can? Tell Amber what you are working on.</p>
        <div class="cta-row"><a class="btn btn-primary" href="/contact.html">Work with me</a></div>
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
    u = f"{SITE}/glossary/"
    terms = sorted(terms, key=lambda t: t["term"].lower())
    letters = sorted({t["term"][0].upper() for t in terms})
    jump = " ".join(f'<a href="#letter-{l}">{l}</a>' for l in letters)
    rows, cur = [], None
    for t in terms:
        tid = slugify(t["term"])
        l = t["term"][0].upper()
        if l != cur:
            rows.append(f'<h2 class="glossary__letter" id="letter-{l}">{l}</h2>')
            cur = l
        more = ""
        if t.get("link"):
            more = f' <a class="go" href="{t["link"]}">{esc(t.get("linkText", "Read the guide"))}</a>'
        aka = f'<p class="glossary__aka small">Also called {esc(", ".join(t["aka"]))}</p>' if t.get("aka") else ""
        rows.append(f'<div class="glossary__entry" id="{tid}"><h3><a href="#{tid}">{esc(t["term"])}</a></h3>{aka}<p>{esc(t["definition"])}{more}</p></div>')
    ld = jsonld({"@context": "https://schema.org", "@graph": [
        {"@type": "DefinedTermSet", "@id": u + "#terms", "name": "Flow AI marketing glossary", "url": u,
         "description": "Plain definitions of AI marketing, AI search and marketing operations terms for small businesses in New Zealand and Australia.",
         "inLanguage": "en-NZ", "publisher": {"@id": f"{SITE}/#flowai"},
         "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": u + "#" + slugify(t["term"]), "name": t["term"],
                             "description": t["definition"], "url": u + "#" + slugify(t["term"]),
                             **({"alternateName": t["aka"]} if t.get("aka") else {})} for t in terms]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Flow AI", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Glossary", "item": u}]}]})
    page = head("AI Marketing Glossary: AEO, GEO, AI Agents and More | Flow AI",
                f"{len(terms)} AI marketing terms defined in plain language for small business owners in New Zealand and Australia: AEO, GEO, AI marketing agent, llms.txt, schema and more.",
                u, og_type="website", extra_head=ld)
    page += header("glossary", "Skip to the glossary")
    page += f"""
<main>
  <section class="hero blog-hero centered" aria-labelledby="glossary-title">
    <div class="wrap">
      <div class="stack">
        <p class="eyebrow"><a href="/blog/">Guides</a><span aria-hidden="true"> / </span>Reference</p>
        <h1 id="glossary-title">The AI marketing glossary.</h1>
        <p class="lead">{len(terms)} terms an owner meets when marketing moves onto AI, each defined in a sentence you can quote. Free to cite with a link.</p>
      </div>
    </div>
  </section>
  <section class="glossary" id="glossary" aria-label="Terms">
    <div class="wrap">
      <nav class="glossary__jump small" aria-label="Jump to letter">{jump}</nav>
      <div class="glossary__list narrow">
{chr(10).join(rows)}
      </div>
    </div>
  </section>
  <section class="contact centered" aria-labelledby="contact-title">
    <div class="wrap">
      <div class="stack">
        <h2 id="contact-title">Want the terms turned into a working system?</h2>
        <p class="lead">Building this inside a team, or hiring someone who can? Tell Amber what you are working on.</p>
        <div class="cta-row"><a class="btn btn-primary" href="/contact.html">Work with me</a></div>
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
            out.append(f"  - /blog/{x['slug']}.html{tag}: {x['shortAnswer']}")
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

def main():
    global GLOSSARY_COUNT
    today = dt.date.today().isoformat()
    posts = load_sources()
    for p in posts:
        if p["topic"] not in TOPICS:
            sys.exit(f"{p['slug']}: unknown topic {p['topic']}")
        process_body(p)
        n = len(p["shortAnswer"].split())
        if not 25 <= n <= 75:
            print(f"warn {p['slug']}: short answer is {n} words")
    posts.sort(key=lambda p: (p["published"], p.get("pillar", False), p["slug"]), reverse=True)

    gfile = ROOT / "src" / "glossary.json"
    terms = json.loads(gfile.read_text()) if gfile.exists() else []
    GLOSSARY_COUNT = len(terms)

    (ROOT / "blog" / "figures").mkdir(parents=True, exist_ok=True)
    for p in posts:
        (ROOT / "blog" / "figures" / f"{p['slug']}.svg").write_text(figure_svg(p["slug"], p["topic"]))
        (ROOT / "blog" / f"{p['slug']}.html").write_text(article_page(p, posts))
    (ROOT / "blog" / "index.html").write_text(index_page(posts))
    if terms:
        (ROOT / "glossary").mkdir(exist_ok=True)
        (ROOT / "glossary" / "index.html").write_text(glossary_page(terms, posts))
    update_sitemap(posts, today)
    update_feed(posts)
    update_llms(posts)
    update_llms_full(posts)
    print(f"built {len(posts)} guides, {len(terms)} glossary terms")


if __name__ == "__main__":
    main()
