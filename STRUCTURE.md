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
- `assets/highend.css` is the last stylesheet on every page and `assets/nav.js` the last script (both added just before `</head>`, also in the head templates of `scripts/build_blog.py` and `tools/build-templates.py`). They carry the high-end treatment from October 2026: the floating island header and its phone menu, pill buttons with the nested arrow, double-bezel panels, the amber light behind the hero and the closer, and spring-eased reveals. Remove those two tags to go back to the plain layout; nothing else depends on them. Its last block, "Taste pass (16 Oct 2026)", sets one panel style (single hairline, one container radius), plain sentence-case section labels, the Home stats band and proof list, and left-aligned hero copy on phones; it can be read or removed as one change.
- `assets/liquid.css` and `assets/liquid.js` load right after `highend.css` on every page (and in the three page builders). They carry the liquid glass look from 21 October 2026: a violet night ground with still stars, clear frosted glass panels, white pill primary buttons, the WebGL liquid orb in the home stage, and a quieter orb behind other heroes (not on guides, articles or the profile). Remove those two tags to go back to the warm-ink look; nothing else depends on them.
- `assets/glass.css` and `assets/glass.js` load last, right after `liquid.js`, on every page (and in the two page builders). They carry the glass system from 22 October 2026: the sky's lilac and indigo light returns behind every section (drifting with scroll where `animation-timeline` is supported), every panel on the site is the hero card's glass with a line of light along its top edge, text sits in three tiers (headline, one voice line, quiet meta), and sections sit closer together with more air inside. Buttons stay amber. Since 23 October the same file also opens the home stage at its foot (the frame and the liquid fade out instead of stopping on an edge), draws a line figure at the top of each of the four sprint cards, sets the manifesto teaser as a three-node flow (`.layer-flow`), and runs rails with beads through numbered steps. The conversion pass of the same day makes the offer explicit on the home page: the primary button asks for the written plan, the hero cards carry the offer (two working days, fixed price) and the proof (six months in production), the plan appears as a glass document (`.plan-sheet`), the four figures sit two to a row at display size, and the form button asks for the plan. Later the same day the home hero became the run: on wide screens the hero pins for two and a half screens of scroll while the copy lifts away, the liquid shrinks toward the centre and the workspace rises to meet it, then the run plays (glass.js writes `--p` on `.hero--run`; phones and reduced motion keep the stacked layout). The header mark and favicon are now the orb reduced to a sign (`assets/flowai-mark.svg?v=2`, `favicon.svg?v=2`; the old face marks are kept as `flowai-mark-dot.svg` and `favicon-dot.svg`), and amber buttons keep their arrow on hover. On 23 October the Services pages (all eight) and How it works gained the same handover as the home page: the hero sits inside a `.rise-track` wrapper, pins for 70vh of scroll while the copy lifts and the quiet orb shrinks, and the next section rises over it (`glass.js` writes `--p` on the track; glass.js also sets `html.glass`, which gates every choreography rule). The services hero lost its dot character; the one-paragraph answer now follows the agents grid as a quiet line. The home steps are titles only, the sprint cards carry no week line, and the plan document lists the ten agents under their outcomes. The favicon tile is the site's night violet (`favicon.svg?v=3`). The home demo is now the run sheet (`assets/demo.js?v=6`, `[data-run-sheet]`, styles in glass.css section 15): one brief typed in, three steps on a rail, the work that came back as rows, one amber Approve button, and four tabs that replay the runs; the example business is an accounting firm in Auckland (also on Contact, the manifesto and How it works). The old chat-window demo, its sidebar and the one-run overlay in dot.js are no longer mounted (dot.js looks for `[data-demo]`, which no page carries). Remove those two tags to go back to the liquid look; nothing else depends on them.

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
