# flowai.co.nz site architecture

Last updated: 2026-08-20

## Pages in the sitemap

| URL | Job | Notes |
|---|---|---|
| `/` | The offer: hero, problem, what gets built, process, free tools, founding terms, pricing, proof, bio teaser, FAQ, contact | Primary conversion page. FAQPage + Organization + Person + WebSite schema. |
| `/about.html` | Everything about Amber under one page: position, current role, shipped systems with source links, capabilities | Consolidated from the former `/cv.html`. ProfilePage schema. |
| `/work.html` | Portfolio organised as the go-to-market machine: Strategy, Demand engines, Built to ship | WebPage + BreadcrumbList schema. |
| `/cases.html` | Evidence library for working systems, open source tools, and product builds | CollectionPage + ItemList + BreadcrumbList schema. |
| `/work/six-month-marketing-function.html` | Flagship case study: six months of one operator running a whole marketing function on AI systems | Article + BreadcrumbList schema. |
| `/work/enterprise-gtm.html` | Case study: three demand engines, one pipeline, one launch | Article + BreadcrumbList schema. |
| `/work/content-engine.html` | Case study: the voice-gated content engine | Article + BreadcrumbList schema. |
| `/work/geo-seo-toolkit.html` | Case study: the GEO/AEO toolkit, running on this site | Article + BreadcrumbList schema. |
| `/skills/` | Installable public skill library with filtering, deep links, sharing, and direct source inspection | CollectionPage + ItemList + FAQPage schema. |
| `/blog/` | Guide index, one substantial piece a week | Cluster plan at ~/Desktop/flowai-seo-cluster/. |
| `/blog/ai-marketing-for-small-business-nz.html` | Pillar guide for the content cluster | Article + FAQPage + BreadcrumbList schema. |
| `/tools/benchmark.html` | Free AI-readiness benchmark (lead magnet, no email gate) | WebApplication schema. |
| `/tools/pricing.html` | Free interactive Lerner-rule pricing model | WebApplication schema. |

## Pages deliberately not in the sitemap

- `/cv.html` — redirect stub (meta refresh + canonical) to `/about.html`; noindex. Kept so old links keep working.
- `/flowai-brand-guidelines.html` — internal brand system document, live but not a customer page.
- `/404.html` — served automatically by GitHub Pages for missing URLs.
- `/skills/*/SKILL.md`: raw public skill source files (MIT licensed). Linked from `/skills/`, kept out of the sitemap because they are not HTML pages.

## Planned

- Remaining 12 spoke posts of the `/blog/` cluster per `~/Desktop/flowai-seo-cluster/cluster-plan.md` (pillar is live; add each spoke to sitemap and feed with its real publish date, and swap in the spoke links held as HTML comments in the pillar).

## Conventions

- Sitemap uses `lastmod` only (no `priority`/`changefreq`; Google ignores them).
- Every page: absolute `flowai.co.nz` canonical, JSON-LD, og:title/description/image, one H1.
- robots.txt allows all AI answer-engine crawlers and references the sitemap.
- `llms.txt` at root and `/.well-known/llms.txt` mirror the site structure; update both when pages change.
- `.nojekyll` must stay in the repo root or GitHub Pages stops serving `.well-known/`.

## Two languages: English at `/`, Simplified Chinese at `/zh/` (since 2026-10-08)

Every page has a Chinese twin at the same path under `/zh/` (`/about` and `/zh/about`,
`/blog/aeo-checklist` and `/zh/blog/aeo-checklist`). The header carries an `EN | 中文` switch. The
choice is global: it is remembered in the browser, so after picking 中文 any English page a visitor
opens sends them to its Chinese twin (and the reverse). Crawlers never carry a stored choice, so
each URL always serves its own language, linked with hreflang (`en`, `zh-Hans`, `x-default` = English).

| Piece | Where |
|---|---|
| Chinese static pages | `zh/<same path>.html`, translated by hand from the English page |
| Chinese guides | `src/zh/blog/<slug>.html` (same format and slug as `src/blog`), built by `scripts/build_blog.py` into `zh/blog/` |
| Chinese glossary | `src/zh/glossary.json` (each entry keeps the English term in `en`, so anchors match) |
| Switch, hreflang, Chinese header/footer, link rewriting, sitemap block | `scripts/i18n.py` |
| Switch styling and Chinese typography | `assets/i18n.css` |
| Chinese strings in shared scripts | `ZH` branches in `assets/*.js` (`document.documentElement.lang`) |
| Chinese CV | `assets/amber-lan-cv-zh.pdf`, printed from `/zh/about` like the English one |
| Voice, house rules and terminology for Chinese | `i18n/ZH-STYLE.md` |
| What was translated from which English version | `i18n/zh-sources.json` |

Workflow after any change:

1. Run the generators you touched (`python3 scripts/build_blog.py`, `python3 tools/build-templates.py`).
2. Run `python3 scripts/i18n.py`. It always runs last. It reports English pages with no Chinese twin,
   Chinese pages whose English source changed since translation (stale), and English prose left
   in Chinese pages.
3. Translate or update what it lists, following `i18n/ZH-STYLE.md`, then check structure with
   `python3 scripts/zh_parity.py <english file>` and record it with
   `python3 scripts/i18n.py --stamp <chinese file>`.
4. New English page: add its Chinese twin in the same pass, or it ships English-only and the report
   lists it as missing.
