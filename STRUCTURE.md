# flowai.co.nz site architecture

Last updated: 2026-08-20

## Pages in the sitemap

| URL | Job | Notes |
|---|---|---|
| `/` | The offer: hero, problem, what gets built, process, free tools, founding terms, pricing, proof, bio teaser, FAQ, contact | Primary conversion page. FAQPage + Organization + Person + WebSite schema. |
| `/about.html` | Everything about Amber under one page: position, current role, shipped systems with source links, capabilities | Consolidated from the former `/cv.html`. ProfilePage schema. |
| `/work.html` | Portfolio organised as the go-to-market machine: Strategy, Demand engines, Built to ship | WebPage + BreadcrumbList schema. |
| `/cases.html` | Evidence library for working systems, open source tools, and product builds | CollectionPage + ItemList + BreadcrumbList schema. |
| `/work/enterprise-gtm.html` | Case study: three demand engines, one pipeline, one launch | Article + BreadcrumbList schema. |
| `/work/content-engine.html` | Case study: the voice-gated content engine | Article + BreadcrumbList schema. |
| `/work/geo-seo-toolkit.html` | Case study: the GEO/AEO toolkit, running on this site | Article + BreadcrumbList schema. |
| `/skills/` | Installable public skill library with filtering, deep links, sharing, and direct source inspection | CollectionPage + ItemList + FAQPage schema. |
| `/skills/research-brand/SKILL.md` | Public skill: evidence-backed brand research | Source file, MIT licensed. |
| `/skills/reddit-opportunity-research/SKILL.md` | Public skill: ethical Reddit opportunity research | Source file, MIT licensed. |
| `/skills/audit-content/SKILL.md` | Public skill: pre-publication claim and link audit | Source file, MIT licensed. |
| `/blog/` | Guide index, one substantial piece a week | Cluster plan at ~/Desktop/flowai-seo-cluster/. |
| `/blog/ai-marketing-for-small-business-nz.html` | Pillar guide for the content cluster | Article + FAQPage + BreadcrumbList schema. |
| `/tools/benchmark.html` | Free AI-readiness benchmark (lead magnet, no email gate) | WebApplication schema. |
| `/tools/pricing.html` | Free interactive Lerner-rule pricing model | WebApplication schema. |

## Pages deliberately not in the sitemap

- `/cv.html` — redirect stub (meta refresh + canonical) to `/about.html`; noindex. Kept so old links keep working.
- `/flowai-brand-guidelines.html` — internal brand system document, live but not a customer page.
- `/404.html` — served automatically by GitHub Pages for missing URLs.

## Planned

- Remaining 12 spoke posts of the `/blog/` cluster per `~/Desktop/flowai-seo-cluster/cluster-plan.md` (pillar is live; add each spoke to sitemap and feed with its real publish date, and swap in the spoke links held as HTML comments in the pillar).

## Conventions

- Sitemap uses `lastmod` only (no `priority`/`changefreq`; Google ignores them).
- Every page: absolute `flowai.co.nz` canonical, JSON-LD, og:title/description/image, one H1.
- robots.txt allows all AI answer-engine crawlers and references the sitemap.
- `llms.txt` at root and `/.well-known/llms.txt` mirror the site structure; update both when pages change.
- `.nojekyll` must stay in the repo root or GitHub Pages stops serving `.well-known/`.
