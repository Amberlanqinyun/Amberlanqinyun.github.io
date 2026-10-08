# Flow AI · Simplified Chinese (简体中文) style guide

The Chinese site lives under `/zh/`. It is the same site, written natively in Simplified Chinese for
mainland, Singapore, Malaysia, Taiwan-reading and New Zealand/Australia Chinese-speaking founders,
marketing leads and hiring managers. It should read as if a senior bilingual marketing leader wrote it
in Chinese first. Never word-for-word translation.

## Voice

- Register: professional, warm, collaborative, aspirational. Senior (CMO-level thinking, team-level
  execution). Peer to peer, never teacher, never salesy.
- Natural business Chinese: 书面但不僵硬. Short clear sentences. Translate meaning and intent, then
  check it still says exactly what the English says. Never add facts, numbers, clients or claims.
- Keep the page's grammatical person: About is first person (我). Elsewhere keep what the English uses
  (Flow AI / 我 / 你). Address the reader as 你 (not 您) for a warm peer tone; 您 only inside a formal
  email template or form confirmation if the English is formal.
- No 小红书 style: no emoji, no 宝子/家人们, no 干货, no exclamation marks (！ or !).

## House rules (a line that breaks one fails)

- No dashes as punctuation: never "——", "—", "–". Use ，：；。or （）.
- No 不是……而是…… / 与其……不如…… / "X，而非 Y" contrast constructions used as a rhetorical beat.
- No rhetorical lists of exactly three parallel phrases (排比三连) used as a beat. No stacked adjectives.
- Banned words: 赋能, 打造, 一站式, 颠覆, 革命性, 无缝, 抓手, 闭环, 降本增效, 助力, 引领, 极致,
  全方位, 深度融合, 生态, 矩阵 (as buzzword), 重塑, 解锁, 释放潜能, 世界级, 顶级, 硬核.
- Headlines never open on 不 / 没有 / 从不 / 绝不 / 别.
- No public prices beyond what the English page already states; no free audit.
- Never mention Novie or Novamind Labs. Never add a Chinese name for Amber: she is "Amber Lan" in
  every language.

## Typography

- Full-width Chinese punctuation in Chinese sentences: ，。：；？（）“ ”. Use “ ” for quotes.
- Put one half-width space between Chinese characters and Latin letters or Arabic numerals:
  "用 Claude Code 搭建", "12 篇稿件", "AEO 检查清单". No space next to full-width punctuation.
- Numbers stay Arabic. Currency stays as written (NZ$4,500). Percentages: 42%.
- Dates: 2026年10月8日. Months: 10月. Weekdays: 周一.
- Keep product UI labels short; Chinese button text 2 to 6 characters where possible.

## Terminology (use exactly, consistently)

| English | 简体中文 |
|---|---|
| Flow AI, Flow Intelligence, the Flow Engine | keep in English: Flow AI, Flow Intelligence, Flow Engine |
| Amber Lan | Amber Lan |
| AI marketing engineer | AI 营销工程师 |
| marketing engineer | 营销工程师 |
| GTM engineer | GTM 工程师 |
| go-to-market (GTM) | 市场进入（GTM）on first use, then GTM |
| AI agent / agent | AI 智能体 / 智能体 |
| Search agent, Content agent, Outbound agent, Reporting agent, Community agent | 搜索智能体, 内容智能体, 外联智能体, 报告智能体, 社群智能体 |
| agent system | 智能体系统 |
| AI search | AI 搜索 |
| AEO (answer engine optimisation) | AEO（答案引擎优化） |
| GEO (generative engine optimisation) | GEO（生成式引擎优化） |
| SEO | SEO（搜索引擎优化）on first use, then SEO |
| AI Overviews | Google AI 概览（AI Overviews） |
| answer engine | 答案引擎 |
| citation / cited by ChatGPT | 引用 / 被 ChatGPT 引用 |
| llms.txt, robots.txt, schema | keep: llms.txt, robots.txt, 结构化数据（schema） |
| sprint / one-week sprint | 冲刺 / 一周冲刺 |
| handover | 交接 |
| scope / written scope | 范围 / 书面范围说明 |
| positioning | 定位 |
| content engine | 内容引擎 |
| voice / brand voice / voice gate | 品牌语调 / 语调关卡 |
| outbound | 主动外联 |
| pipeline | 销售管线 |
| demand engine | 需求引擎 |
| lead / enquiry | 潜在客户 / 咨询 |
| case study | 案例研究 |
| marketing function | 营销职能 |
| marketing lead | 营销负责人 |
| owner (business owner) | 企业主 |
| small business | 小企业（5 到 50 人的企业 when the English says so） |
| agency / freelancer / in-house | 代理机构 / 自由职业者 / 内部团队 |
| fractional CMO | 兼职 CMO（fractional CMO） |
| AI CMO | AI CMO |
| retainer | 月度服务费（retainer） |
| human in the loop | 人工把关（human in the loop） |
| review / reviewed by a person | 审核 / 由人审核 |
| template | 模板 |
| skill (Claude skill) | 技能（skill） |
| guide | 指南 |
| glossary | 术语表 |
| manifesto | 宣言 |
| New Zealand, Auckland, Australia | 新西兰, 奥克兰, 澳大利亚 |
| Claude Code, ChatGPT, Claude, Perplexity, Gemini, HubSpot, GitHub, LinkedIn, Google | keep in English |

## Fixed UI labels

| English | 简体中文 |
|---|---|
| How it works | 合作方式 |
| Guides | 指南 |
| About | 关于我 |
| Work | 作品 |
| Free templates | 免费模板 |
| Manifesto | 宣言 |
| Privacy | 隐私政策 |
| Work with me | 与我合作 |
| Get my CV | 下载简历 |
| Let's talk | 聊聊吧 |
| Read the case study | 阅读案例 |
| Read the guide | 阅读指南 |
| Read more / Show less | 展开 / 收起 |
| Questions owners ask | 企业主常问的问题 |
| The short answer | 简短回答 |
| Contents | 目录 |
| Sources | 资料来源 |
| min read | 分钟阅读 |
| Share guide | 分享指南 |
| Link copied / Copy failed / Copied | 链接已复制 / 复制失败 / 已复制 |

## What to translate in HTML

Translate: every visible text node; `alt`, `title`, `aria-label`, `placeholder`, `value` of buttons;
`<title>`; meta description, og:title, og:description, twitter:title, twitter:description;
string values in JSON-LD that are human text (name, headline, description, text, jobTitle,
FAQ question and answer; FAQ text must match the visible FAQ text exactly); user-facing strings
inside inline `<script>` blocks (messages, labels, button states). `data-*` attributes that hold
display text (data-share-title, data-share-text, data-missing and the like).

Keep exactly: every tag, class, id, href, src, data-* key, inline style, SVG geometry, code, install
commands, file paths, URLs, email addresses, numbers, brand and product names, and JavaScript logic.
Leave links pointing at their English paths (`/about`, `/blog/...`): the build rewrites internal links
to `/zh/` automatically. Leave the site header and site footer in English: the build replaces them.
Keep `<html lang="en-NZ">` as is: the build sets `zh-Hans`.
