#!/usr/bin/env python3
"""Build the agent templates: /templates/, one page per template, and /privacy.html.

Add a template by adding an entry to TEMPLATES and running:
    python3 tools/build-templates.py && python3 tools/build-llms-full.py

The header, footer, tag manager, reveal script and agent icons are lifted from
index.html on every run, so these pages never drift from the rest of the site.
Every step, input and output below is paraphrased from the skill's own SKILL.md:
never describe a capability the skill does not have, never show a sample result
that was not actually run.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = (ROOT / "index.html").read_text()
SYSTEM = (ROOT / "sprints" / "index.html").read_text()  # the agent team diagram lives here
SITE = "https://www.flowai.co.nz"
UPDATED = "2026-10-02"
V = "9"  # asset version query; bump with texture/dotfield/alive changes


def chunk(start, end, text=INDEX):
    a = text.index(start)
    b = text.index(end, a) + len(end)
    return text[a:b]


GTM_HEAD = chunk("  <!-- Google Tag Manager -->", "  <!-- End Google Tag Manager -->")
GTM_BODY = chunk("<!-- Google Tag Manager (noscript) -->", "<!-- End Google Tag Manager (noscript) -->")
HEADER = chunk('<header class="site-header">', "</header>")
FOOTER = chunk('<footer class="site-footer">', "</footer>")
REVEAL = chunk("  <script>\n    (function () {\n      var reduceMotion", "    }());\n") + "  </script>"


def icon(label):
    """The agent's line icon, exactly as it appears in the agent team diagram."""
    if label == "Marketing HQ":
        li = re.search(r'<li class="is-core">(.*?)</li>', SYSTEM, re.S).group(1)
    else:
        li = re.search(r'<li data-group="[a-z]+">(?:(?!</li>).)*?' + re.escape(label) + r'.*?</li>', SYSTEM, re.S).group(0)
    return re.search(r'<svg class="agent-ico".*?</svg>', li, re.S).group(0)


AGENTS = {
    "hq": ("Marketing HQ", "/sprints/positioning.html", "Install Marketing HQ as a one-week positioning sprint"),
    "search": ("Search agent", "/sprints/ai-search.html", "Install the search agent as a one-week AI-search sprint"),
    "content": ("Content agent", "/sprints/content-engine.html", "Install the content agent as a one-week content engine sprint"),
    "community": ("Community agent", "/contact.html", "Ask about running the community agent every month"),
}

REVIEW = ("A marketing engineer reviews it", "Amber checks the result before it reaches you. That rule holds on every Flow AI run.")

SAMPLE_CRAWLERS = [
    ("GPTBot", "OpenAI", "1", "Allowed", "Named in robots.txt"),
    ("OAI-SearchBot", "OpenAI", "1", "Allowed", "Named in robots.txt"),
    ("ChatGPT-User", "OpenAI", "1", "Allowed", "Named in robots.txt"),
    ("ClaudeBot", "Anthropic", "1", "Allowed", "Named in robots.txt"),
    ("PerplexityBot", "Perplexity", "1", "Allowed", "Named in robots.txt"),
    ("Google-Extended", "Google", "2", "Allowed", "Named in robots.txt"),
    ("GoogleOther", "Google", "2", "Allowed", "Default rule"),
    ("Applebot-Extended", "Apple", "2", "Allowed", "Default rule"),
    ("Amazonbot", "Amazon", "2", "Allowed", "Default rule"),
    ("FacebookBot", "Meta", "2", "Allowed", "Default rule"),
    ("CCBot", "Common Crawl", "3", "Allowed", "Named in robots.txt"),
    ("anthropic-ai", "Anthropic", "3", "Allowed", "Named in robots.txt"),
    ("Bytespider", "ByteDance", "3", "Allowed", "Named in robots.txt"),
    ("cohere-ai", "Cohere", "3", "Allowed", "Default rule"),
]

TEMPLATES = [
    dict(
        slug="brand-dna", agent="hq", name="Brand DNA researcher",
        lead="Give it a site address and it writes the brief every other agent works from: positioning, audience, competitors, voice, and the content gaps worth closing.",
        card="Turns a site address into an evidence-backed brand brief, with the content gaps worth closing.",
        field=("Your site", "company.co.nz", "Which site should it research?"),
        install="npx skills add Amberlanqinyun/Amberlanqinyun.github.io --skill research-brand",
        repo="https://github.com/Amberlanqinyun/Amberlanqinyun.github.io/tree/main/skills/research-brand",
        steps=[
            ("Read the website", "Homepage, about, pricing, product, blog and customer pages: what you do in your own words, the tagline, features, pricing and proof."),
            ("Search the web", "Third-party descriptions, reviews, comparisons and company records. How others describe a business is often clearer than its own copy."),
            ("Name the competitors", "Three to five direct competitors, each with where it overlaps and where it differs."),
            ("Write the brief", "One self-contained Brand DNA file. Anything not public is marked as not found, and every source is listed with the date it was read."),
        ],
        needs=["Your site address", "Optionally, one line on what the business does"],
        returns=["What the business does, in plain words", "Target customer, pricing and key features", "Three to five competitors and your differentiators", "Brand voice and social proof", "Content gaps, with why each one matters", "Every source, dated"],
    ),
    dict(
        slug="geo-audit", agent="search", name="Full GEO audit",
        lead="A complete check of how visible your site is to ChatGPT, Claude, Perplexity and Google's AI answers, scored out of 100 and turned into a ranked 30-day plan.",
        card="Scores your site's AI-search visibility out of 100 and ranks the fixes into a 30-day plan.",
        field=("Your site", "company.co.nz", "Which site should it audit?"),
        install="npx skills add Amberlanqinyun/geo-seo-claude --skill geo-audit",
        repo="https://github.com/Amberlanqinyun/geo-seo-claude",
        steps=[
            ("Map the site", "The homepage is read, the business type identified, and up to 50 pages sampled from the sitemap, within the rules of your robots.txt."),
            ("Run six checks in parallel", "AI citability, brand authority, experience and expertise in the content, technical access, structured data, and presence on the platforms AI systems cite."),
            ("Score it", "The six results combine into one GEO score out of 100, weighted toward citability and authority."),
            ("Rank the fixes", "Every issue is sorted into critical, high, medium or low, with the quick wins pulled out first."),
            ("Plan the month", "A 30-day action plan, one theme a week."),
        ],
        needs=["Your site address", "A sitemap if you have one; the audit can crawl without it"],
        returns=["A GEO score out of 100, with a score for each of the six areas", "Issues ranked critical, high, medium and low", "Quick wins for this week", "A 30-day action plan, week by week", "The list of pages analysed"],
    ),
    dict(
        slug="ai-crawler-check", agent="search", name="AI crawler access check",
        lead="Finds out which AI systems can read your site. Fourteen AI crawlers are checked against your robots.txt, page tags and server headers, with the exact fix if any are blocked.",
        card="Checks whether fourteen AI crawlers, from ChatGPT to Perplexity, can read your site.",
        field=("Your site", "company.co.nz", "Which site should it check?"),
        install="npx skills add Amberlanqinyun/geo-seo-claude --skill geo-crawlers",
        repo="https://github.com/Amberlanqinyun/geo-seo-claude",
        steps=[
            ("Read robots.txt", "Every rule is tested against fourteen AI crawlers in three tiers: the answer engines, the wider AI ecosystem, and training-only crawlers."),
            ("Check page tags", "Meta robots tags that can quietly block AI systems page by page."),
            ("Check server headers", "X-Robots-Tag headers, which override everything else."),
            ("Look for AI files", "Whether llms.txt and a sitemap are in place to point AI systems at your best pages."),
            ("Check rendering", "Whether your content needs JavaScript to appear, which many AI crawlers do not run."),
        ],
        needs=["Your site address"],
        returns=["An access table for all fourteen crawlers", "An AI visibility score out of 100", "Any critical blocks, named", "A ready-to-paste robots.txt recommendation"],
        sample=dict(
            title="flowai.co.nz, checked 2 October 2026",
            note="All fourteen crawlers can read the site. Nine are named in robots.txt and five are allowed by the default rule. No page tags or headers block them, and llms.txt and the sitemap are both in place.",
            rows=SAMPLE_CRAWLERS,
        ),
    ),
    dict(
        slug="ai-citability", agent="search", name="AI citability scorer", cta="Score my page",
        lead="Scores one page on how likely AI assistants are to quote it, block by block, and rewrites the weakest passages so they can be cited.",
        card="Scores one page, block by block, on how likely AI assistants are to quote it.",
        field=("Page to score", "company.co.nz/services", "Which page should it score?"),
        install="npx skills add Amberlanqinyun/geo-seo-claude --skill geo-citability",
        repo="https://github.com/Amberlanqinyun/geo-seo-claude",
        steps=[
            ("Read the page", "The page is fetched and its main content separated from navigation and footers."),
            ("Split it into blocks", "Each heading and the passage under it becomes one block, the unit an AI system quotes."),
            ("Score every block", "Answer quality 30%, self-containment 25%, readable structure 20%, evidence density 15%, original data 10%."),
            ("Score the page", "The block scores combine into one citability score out of 100."),
            ("Rewrite the weakest", "Specific rewrites for the lowest-scoring blocks, written answer-first."),
        ],
        needs=["One public page address"],
        returns=["A citability score out of 100", "The strongest blocks, and why they work", "The weakest blocks, each with a rewrite", "Quick reformatting wins", "A score for every section"],
    ),
    dict(
        slug="content-evidence-audit", agent="content", name="Content evidence auditor", cta="Check my page",
        lead="Checks every link, statistic, source and company claim in a draft or a published page before it goes out, and names the exact fix for each problem.",
        card="Checks every link, statistic and claim in a draft or page before it goes live.",
        field=("Page or draft link", "company.co.nz/blog/post", "Which page or draft should it check?"),
        install="npx skills add Amberlanqinyun/Amberlanqinyun.github.io --skill audit-content",
        repo="https://github.com/Amberlanqinyun/Amberlanqinyun.github.io/tree/main/skills/audit-content",
        steps=[
            ("Load the context", "The draft, plus your Brand DNA if one exists, which becomes the source of truth for claims about your business."),
            ("Pull out every claim", "Links, statistics, named sources, research citations and claims about your own product."),
            ("Open every link", "Each one is fetched and read to confirm it supports the exact claim attached to it. Every link, with no sampling."),
            ("Trace every number", "Statistics are traced to their original source, and the patterns of invented figures are flagged."),
            ("Check your own claims", "Metrics and features are checked against your Brand DNA, and dates and numbers against each other."),
        ],
        needs=["A public page link, or a shared draft link", "Your Brand DNA, if you have one"],
        returns=["A result for every claim: passed, broken, mismatched or unverifiable", "Critical issues to fix before publishing", "Warnings worth fixing", "A specific fix for each issue", "What passed, so you know it is safe"],
    ),
    dict(
        slug="reddit-opportunities", agent="community", name="Reddit opportunity researcher",
        lead="Finds the Reddit threads where your business can genuinely help, the communities worth joining, and the exact words buyers use, ranked by what to act on first.",
        card="Finds the Reddit threads where your business can genuinely help, ranked by what to act on first.",
        field=("Your site", "company.co.nz", "Which business should it research?"),
        install="npx skills add Amberlanqinyun/Amberlanqinyun.github.io --skill reddit-opportunity-research",
        repo="https://github.com/Amberlanqinyun/Amberlanqinyun.github.io/tree/main/skills/reddit-opportunity-research",
        install_note="Run the Brand DNA researcher first: this template reads its brand_dna.md.",
        steps=[
            ("Start from your Brand DNA", "The Brand DNA researcher runs first, so the search starts from your real audience, pains and competitors."),
            ("Search in buyers' words", "Twenty to forty Reddit searches across problems, solutions and competitors, in the language users actually use."),
            ("Read the threads", "Each promising thread is captured: the pain, the phrasing, the competitors mentioned, and whether you could add value."),
            ("Score each one", "Pain intensity, fit for a helpful reply, content fit, community activity, and how often it comes back."),
            ("Turn it into demand", "The searches and AI prompts buyers are likely making, and the content worth creating for them."),
        ],
        needs=["Your site address", "The Brand DNA is built first, as part of the run"],
        returns=["The pain points users discuss, in their words", "The communities worth joining", "A ranked list: act now, build content first, monitor, or skip", "Likely Google, Reddit and AI searches", "Content ideas and next actions"],
        footnote="Research only. Nothing is ever posted for you.",
    ),
]


def esc(s):
    return html.escape(s, quote=True)


def head(title, description, path, schema, og_type="website"):
    url = SITE + path
    return f"""<!doctype html>
<html lang="en-NZ">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{GTM_HEAD}
  <script>document.documentElement.className += ' js';</script>
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#0e0e0d">
<link rel="alternate" type="application/atom+xml" title="Flow AI · Amber Lan" href="{SITE}/feed.xml">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Flow AI">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{json.dumps(schema, indent=2, ensure_ascii=False)}
</script>
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/site-header.css">
<link rel="stylesheet" href="/assets/site-footer.css?v=2">
<link rel="stylesheet" href="/assets/motion.css">
<link rel="stylesheet" href="/assets/texture.css?v={V}">
<link rel="stylesheet" href="/assets/templates.css?v={V}">
<script src="/assets/motion.js" defer></script>
<script src="/assets/alive.js?v={V}" defer></script>
<script src="/assets/template-form.js?v={V}" defer></script>
<link rel="preload" href="/fonts/google-sans-flex-vf.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/claude.css?v=6">
</head>
<body>
{GTM_BODY}

<a class="skip-link" href="#main">Skip to content</a>
<div class="grain" aria-hidden="true"></div>

{HEADER}
"""


def foot():
    return f"""
{REVEAL}
{FOOTER}
</body>
</html>
"""


def agent_label(key, extra=""):
    name = AGENTS[key][0]
    cls = " is-hq" if key == "hq" else ""
    return f'<span class="tpl-agent{cls}">{icon(name)}{esc(name)}{extra}</span>'


def card(t, anchor=None):
    ident = anchor or t["slug"]
    meta = f'Needs: {t["field"][0].lower()}'
    return f"""          <a class="tpl-card" id="{ident}" href="/templates/{t['slug']}.html">
            <p class="eyebrow">{agent_label(t['agent'])}</p>
            <h3>{esc(t['name'])}</h3>
            <p>{esc(t['card'])}</p>
            <p class="eyebrow tpl-meta">{esc(meta)}</p>
            <span class="text-link arrow-link">Open the template</span>
          </a>"""


def gallery():
    seen, cards = set(), []
    for t in TEMPLATES:
        anchor = None if t["agent"] in seen else t["agent"]
        seen.add(t["agent"])
        cards.append(card(t, anchor))
    schema = {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "@id": f"{SITE}/templates/", "name": "Flow AI agent templates",
        "description": "Free agent templates from Flow AI. Run one on your site, reviewed by a marketing engineer, or install it in Claude Code.",
        "dateModified": UPDATED,
        "mainEntity": {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/templates/{t['slug']}.html", "name": t["name"]}
            for i, t in enumerate(TEMPLATES)]},
    }
    body = f"""<main id="main">
  <section class="hero centered" aria-labelledby="templates-title">
    <div class="wrap">
      <div class="stack">
        <p class="eyebrow">Agent templates · free</p>
        <h1 id="templates-title" data-words>Put an agent to work on your site.</h1>
        <p class="lead">Pick a template and Flow AI runs it on your site. Amber reviews the result before it reaches you, within two working days. Every template is open source too, so you can install it yourself.</p>
      </div>
      <div class="tpl-grid reveal">
{chr(10).join(cards)}
      </div>
    </div>
  </section>

  <section id="how" class="centered" aria-labelledby="how-title">
    <div class="wrap">
      <div class="stack reveal">
        <p class="eyebrow">How a run works</p>
        <h2 id="how-title">Your email, one agent, a reviewed result.</h2>
        <p class="lead">Each template is one agent from the Flow AI team with one fixed job. Tell it where to look, and the result comes back checked by a person.</p>
      </div>
      <div class="grid grid-3 reveal" style="text-align:left">
        <div class="step">
          <span class="small">01</span>
          <h3>Pick a template</h3>
          <p>Each one names what it needs and exactly what comes back, so you know what you are asking for.</p>
        </div>
        <div class="step">
          <span class="small">02</span>
          <h3>Add your email and site</h3>
          <p>That is all a run needs. The agent does the research and the drafting.</p>
        </div>
        <div class="step">
          <span class="small">03</span>
          <h3>Get the result, reviewed</h3>
          <p>Amber checks every run before it is sent, and it reaches your inbox within two working days.</p>
        </div>
      </div>
      <p class="small reveal" style="margin-top:2.25rem">Prefer to run them yourself? Each template page carries its install command for Claude Code, and the <a class="text-link" href="/skills/">skill library</a> holds 125 more.</p>
    </div>
  </section>

  <section id="contact" class="contact centered" aria-labelledby="end-title">
    <div class="wrap">
      <div class="stack reveal">
        <h2 id="end-title">Want the whole team working?</h2>
        <p class="lead">A free audit names the first agent to install on your business and what it would change.</p>
        <div class="cta-row">
          <a class="btn btn-primary" href="/contact.html">Get a free audit</a>
          <a class="text-link arrow-link" href="/sprints/">See how it works</a>
        </div>
      </div>
    </div>
  </section>
</main>
"""
    page = head("Free agent templates | Flow AI", "Free agent templates from Flow AI. Pick one and it runs on your site, reviewed by a marketing engineer, within two working days. Or install it yourself in Claude Code.", "/templates/", schema) + body + foot()
    (ROOT / "templates").mkdir(exist_ok=True)
    (ROOT / "templates/index.html").write_text(page)


def template_page(t):
    agent_name, sprint_href, sprint_text = AGENTS[t["agent"]]
    label, placeholder, missing = t["field"]
    steps = t["steps"] + [REVIEW]
    review_cls = ' class="is-review"'
    steps_html = "\n".join(
        f'        <li{review_cls if (title, text) == REVIEW else ""}><span class="eyebrow">{i + 1:02d}</span><div><b>{esc(title)}</b><span>{esc(text)}</span></div></li>'
        for i, (title, text) in enumerate(steps))
    needs = "\n".join(f"            <li>{esc(x)}</li>" for x in t["needs"])
    returns = "\n".join(f"            <li>{esc(x)}</li>" for x in t["returns"])
    footnote = f'\n      <p class="small reveal" style="margin-top:var(--s-6)">{esc(t["footnote"])}</p>' if t.get("footnote") else ""
    install_note = f' {esc(t["install_note"])}' if t.get("install_note") else ""

    sample = ""
    if t.get("sample"):
        s = t["sample"]
        rows = "\n".join(f"              <tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td><td>{esc(d)}</td><td>{esc(e)}</td></tr>" for a, b, c, d, e in s["rows"])
        sample = f"""
  <section id="sample" class="centered" aria-labelledby="sample-title">
    <div class="wrap">
      <div class="stack reveal">
        <p class="eyebrow">A real run</p>
        <h2 id="sample-title">{esc(s['title'])}</h2>
        <p class="lead">{esc(s['note'])}</p>
      </div>
      <div class="tablewrap tpl-sample reveal">
        <table>
          <thead><tr><th>Crawler</th><th>Operator</th><th>Tier</th><th>Status</th><th>How</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
    </div>
  </section>
"""

    others = [o for o in TEMPLATES if o["slug"] != t["slug"]]
    others.sort(key=lambda o: (o["agent"] != t["agent"]))
    related = "\n".join(
        f'            <li><b>{esc(AGENTS[o["agent"]][0])}</b><span><a class="text-link" href="/templates/{o["slug"]}.html">{esc(o["name"])}</a>. {esc(o["card"])}</span></li>'
        for o in others[:3])

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "SoftwareSourceCode", "@id": f"{SITE}/templates/{t['slug']}.html",
             "name": t["name"], "description": t["lead"], "codeRepository": t["repo"],
             "license": "https://opensource.org/licenses/MIT", "isAccessibleForFree": True,
             "author": {"@type": "Person", "@id": f"{SITE}/#amber", "name": "Amber Lan"},
             "publisher": {"@type": "Organization", "@id": f"{SITE}/#flowai", "name": "Flow AI"},
             "dateModified": UPDATED},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Agent templates", "item": f"{SITE}/templates/"},
                {"@type": "ListItem", "position": 2, "name": t["name"], "item": f"{SITE}/templates/{t['slug']}.html"}]},
        ],
    }

    body = f"""<main id="main" data-template-id="{t['slug']}">
  <section class="hero centered" aria-labelledby="tpl-title">
    <div class="wrap">
      <div class="stack">
        <p class="eyebrow tpl-crumb"><a href="/templates/">Agent templates</a> · {agent_label(t['agent'])}</p>
        <h1 id="tpl-title" data-words>{esc(t['name'])}</h1>
        <p class="lead">{esc(t['lead'])}</p>
      </div>

      <div class="run">
        <div class="run__path">
          <p class="eyebrow">Free · reviewed by a person</p>
          <h2>Run it for me</h2>
          <p>Flow AI runs this agent for you. Amber reviews the result, and it reaches your inbox within two working days.</p>
          <form data-template-form data-template-id="{t['slug']}" data-template-name="{esc(t['name'])}" novalidate>
            <div class="field">
              <label for="tpl-email">Your email</label>
              <input id="tpl-email" name="email" type="email" autocomplete="email" inputmode="email" enterkeyhint="next" required placeholder="you@company.co.nz">
            </div>
            <div class="field">
              <label for="tpl-site">{esc(label)}</label>
              <input id="tpl-site" name="site" type="text" autocomplete="url" inputmode="url" enterkeyhint="send" required placeholder="{esc(placeholder)}" data-missing="{esc(missing)}">
            </div>
            <div class="hp" aria-hidden="true">
              <label for="tpl-role">Leave this field empty</label>
              <input id="tpl-role" name="company-role" type="text" tabindex="-1" autocomplete="off">
            </div>
            <div><button class="btn btn-primary" type="submit">{esc(t.get("cta", "Run it on my site"))}</button></div>
            <p class="form-note">Your email is used to send this result and reply about it, nothing else. <a href="/privacy.html">Privacy</a>.</p>
            <div class="form-status" role="status" aria-live="polite"></div>
          </form>
        </div>
        <div class="run__path">
          <p class="eyebrow">Open source · MIT</p>
          <h2>Install it yourself</h2>
          <p>Runs in Claude Code on your own machine.{install_note}</p>
          <div class="install">
            <code>{esc(t['install'])}</code>
            <button class="copy-button" type="button" data-copy="{esc(t['install'])}" aria-label="Copy the install command">Copy</button>
            <p class="small"><a class="text-link" href="{esc(t['repo'])}" target="_blank" rel="noopener">Read the source on GitHub</a></p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section id="steps" class="centered" aria-labelledby="steps-title">
    <div class="wrap">
      <div class="stack reveal">
        <p class="eyebrow">How it runs</p>
        <h2 id="steps-title">Step by step, then a person checks it.</h2>
      </div>
      <ol class="tpl-steps reveal">
{steps_html}
      </ol>
    </div>
  </section>

  <section id="io" class="centered" aria-labelledby="io-title">
    <div class="wrap">
      <div class="stack reveal">
        <p class="eyebrow">In and out</p>
        <h2 id="io-title">What it needs, and what you get back.</h2>
      </div>
      <div class="tpl-io reveal">
        <div>
          <h3>What it needs</h3>
          <ul>
{needs}
          </ul>
        </div>
        <div>
          <h3>What comes back</h3>
          <ul>
{returns}
          </ul>
        </div>
      </div>{footnote}
    </div>
  </section>
{sample}
  <section id="related" class="centered" aria-labelledby="related-title">
    <div class="wrap">
      <div class="stack reveal">
        <p class="eyebrow">More templates</p>
        <h2 id="related-title">Keep going.</h2>
      </div>
      <div class="narrow reveal tpl-related" style="text-align:left; margin-left:0">
        <ul class="systems">
{related}
            <li><b>All</b><span><a class="text-link" href="/templates/">Every agent template</a>, and the <a class="text-link" href="/skills/">skill library</a> behind them.</span></li>
        </ul>
      </div>
    </div>
  </section>

  <section id="contact" class="contact centered" aria-labelledby="end-title">
    <div class="wrap">
      <div class="stack reveal">
        <h2 id="end-title">Want the {esc(agent_name.lower() if t['agent'] != 'hq' else 'Marketing HQ')} running every month?</h2>
        <p class="lead">A template is one run. A sprint installs the agent on your business in a week, documented and handed over, and the engine runs it every month after that.</p>
        <div class="cta-row">
          <a class="btn btn-primary" href="/contact.html">Get a free audit</a>
          <a class="text-link arrow-link" href="{sprint_href}">{esc(sprint_text)}</a>
        </div>
      </div>
    </div>
  </section>
</main>
"""
    title = f"{t['name']} | Free Flow AI agent template"
    desc = f"{t['card']} Run it on your site free, reviewed by a marketing engineer, or install it in Claude Code."
    page = head(title, desc, f"/templates/{t['slug']}.html", schema, og_type="article") + body + foot()
    (ROOT / f"templates/{t['slug']}.html").write_text(page)


def privacy():
    schema = {"@context": "https://schema.org", "@type": "WebPage", "@id": f"{SITE}/privacy.html",
              "name": "Privacy at Flow AI", "dateModified": UPDATED,
              "publisher": {"@type": "Organization", "@id": f"{SITE}/#flowai", "name": "Flow AI"}}
    rows = [
        ("Who", "Flow AI is run by Amber Lan in Auckland, New Zealand. Questions about your information go to <a class=\"text-link\" href=\"mailto:amber.lan.growth.digital@gmail.com\">amber.lan.growth.digital@gmail.com</a>."),
        ("What is collected", "Only what you type into a form on this site: your email, and the name, website, page address or message you choose to add."),
        ("Why", "To reply to you, run the template you asked for, and send you the result. Your email is never added to a mailing list unless you ask to join one."),
        ("How it travels", "Forms are delivered to Amber's inbox by <a class=\"text-link\" href=\"https://formsubmit.co\" target=\"_blank\" rel=\"noopener\">FormSubmit</a>, and stored in Gmail. If a form cannot send, your own email app sends it instead."),
        ("Measurement", "The site loads Google Tag Manager to understand which pages are used. It can set cookies for that purpose. The site's own code never passes what you type into a form to it."),
        ("Sharing", "Your information is never sold or shared with anyone for their marketing."),
        ("Keeping it", "Kept only as long as needed to help you and to keep a record of the work. Ask, and it is deleted."),
        ("Your rights", "Under the New Zealand Privacy Act 2020 you can ask to see or correct the information held about you, by email at any time. If you are unhappy with the answer, you can contact the <a class=\"text-link\" href=\"https://www.privacy.org.nz\" target=\"_blank\" rel=\"noopener\">Office of the Privacy Commissioner</a>."),
    ]
    items = "\n".join(f"          <li><b>{a}</b><span>{b}</span></li>" for a, b in rows)
    body = f"""<main id="main">
  <section class="hero centered" aria-labelledby="privacy-title">
    <div class="wrap">
      <div class="stack">
        <p class="eyebrow">Privacy · updated 2 October 2026</p>
        <h1 id="privacy-title" data-words>Your information, in plain words.</h1>
        <p class="lead">What this site collects, why, where it goes, and how to see or remove it.</p>
      </div>
    </div>
  </section>

  <section id="detail" class="centered" aria-labelledby="detail-title">
    <div class="wrap">
      <div class="stack reveal">
        <h2 id="detail-title" class="visually-hidden">The detail</h2>
      </div>
      <div class="narrow reveal" style="text-align:left; margin-left:0">
        <ul class="systems">
{items}
        </ul>
      </div>
    </div>
  </section>
</main>
"""
    page = head("Privacy | Flow AI", "What flowai.co.nz collects, why, where it goes, and how to see, correct or remove it under the New Zealand Privacy Act 2020.", "/privacy.html", schema) + body + foot()
    (ROOT / "privacy.html").write_text(page.replace('<h2 id="detail-title" class="visually-hidden">The detail</h2>', '<h2 id="detail-title">The detail.</h2>'))


if __name__ == "__main__":
    gallery()
    for t in TEMPLATES:
        template_page(t)
    privacy()
    print(f"built /templates/ with {len(TEMPLATES)} templates, and /privacy.html")
