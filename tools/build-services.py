#!/usr/bin/env python3
"""Build the AI marketing services pages, in English and Chinese.

    /ai-marketing-services                 the hub: AI marketing services for NZ and Australian businesses
    /ai-marketing-services/new-zealand
    /ai-marketing-services/australia
    /ai-marketing-services/auckland
    (and the same four under /zh/)

Edit the PAGES data below, then run:
    python3 tools/build-services.py && python3 tools/build-llms-full.py && python3 scripts/i18n.py

The head assets, tag manager, header and footer are lifted from sprints/positioning.html on every
run, so these pages never drift from the rest of the site. scripts/i18n.py then adds the language
switch, hreflang and the Chinese header and footer.

House rules: no Flow AI prices, no free audit, no invented clients, results or reviews.
Every service named here links to the page that describes it.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = (ROOT / "sprints" / "positioning.html").read_text()
SITE = "https://www.flowai.co.nz"
UPDATED = "2026-10-13"
DEFINITION = ("Flow AI provides AI marketing services for businesses in New Zealand and Australia. "
              "Amber Lan, an AI marketing engineer in Auckland, builds the AI agents that run search, "
              "content, outbound and reporting with your team, then hands them over.")


def chunk(start, end, text=SRC):
    a = text.index(start)
    return text[a:text.index(end, a) + len(end)]


GTM_HEAD = chunk("  <!-- Google Tag Manager -->", "  <!-- End Google Tag Manager -->")
PRE = SRC[SRC.index("<!-- Google Tag Manager (noscript) -->"):SRC.index("<main")]
PRE = re.sub(r'\s*<span class="lang-switch".*?</span></span>', "", PRE, flags=re.S)
PRE = PRE.replace(' aria-current="page"', "")
TAIL = SRC[SRC.index("</main>") + len("</main>"):]


def esc(s):
    return html.escape(s, quote=True)


CHECK = ('<svg viewBox="0 0 14 14" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
         'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 7.4 5.6 10.2 11.5 3.8"/></svg>')

# The agent team, as services a buyer recognises. (name, what it delivers, link)
SERVICES = {
    "en": [
        ("Positioning", "One page every agent works from: who you serve, what you claim, the proof.", "/sprints/positioning"),
        ("AI search and SEO", "Technical SEO through to answer engine optimisation, so Google ranks you and ChatGPT, Perplexity and AI Overviews cite you.", "/sprints/ai-search"),
        ("Content engine", "A month of drafts in your voice, approved by your team before anything ships.", "/sprints/content-engine"),
        ("Social", "Posts and threads in your voice, on a calendar that holds.", "/sprints/#system"),
        ("Outbound", "The right hundred buyers, researched and reached personally.", "/sprints/outbound"),
        ("Conversion", "Offers, landing pages and enquiry paths, tested and tuned monthly.", "/sprints/#system"),
        ("Launches", "Product and campaign launches sequenced across every channel.", "/sprints/#system"),
        ("Paid media checks", "Ad creative and audiences reviewed with the numbers behind them.", "/sprints/#system"),
        ("Community", "Helpful answers in the threads and forums where buyers ask.", "/sprints/#system"),
        ("Measurement", "Tracking wired properly, so every enquiry traces to a source.", "/sprints/analytics"),
        ("Reporting", "One short monthly read on what shipped and what comes next.", "/sprints/#system"),
    ],
    "zh": [
        ("定位", "所有智能体共用的一页纸：服务谁、主张什么、证据在哪里。", "/sprints/positioning"),
        ("AI 搜索与 SEO", "从技术 SEO 到 AEO（答案引擎优化），让 Google 给你排名，也让 ChatGPT、Perplexity 和 Google AI 概览引用你。", "/sprints/ai-search"),
        ("内容引擎", "一个月的稿件，用你的品牌语调写成，团队审核通过后才发布。", "/sprints/content-engine"),
        ("社交媒体", "用你的语调写帖子和讨论串，按日历稳定发布。", "/sprints/#system"),
        ("主动外联", "找准一百位买家，逐一研究，亲自联系。", "/sprints/outbound"),
        ("转化", "优惠、落地页和咨询路径，每月测试和优化。", "/sprints/#system"),
        ("发布", "产品和活动发布，在每个渠道按顺序推进。", "/sprints/#system"),
        ("付费广告检查", "广告创意和受众，用数据复盘。", "/sprints/#system"),
        ("社群", "在买家提问的讨论串和论坛里，给出真正有用的回答。", "/sprints/#system"),
        ("效果衡量", "把追踪接好，每一条咨询都能追溯到来源。", "/sprints/analytics"),
        ("报告", "每月一份简短报告：做了什么，下一步做什么。", "/sprints/#system"),
    ],
}

STEPS = {
    "en": [
        ("Scope", "We agree in writing what gets built, which data the agents may read, where a person reviews, and how we measure it. The scope sets the price."),
        ("Build", "I build the agents with your team, one at a time, on your accounts. Your people approve everything before it reaches a customer."),
        ("Hand over", "Documented handover: your team runs the system and owns every agent, prompt and file. Ongoing help is there if you want it."),
    ],
    "zh": [
        ("书面范围", "先用文字说清楚：搭建什么、智能体能读取哪些数据、由谁在哪个环节审核、如何衡量。价格依据这份范围确定。"),
        ("一起搭建", "我和你的团队一起，在你自己的账号里逐个搭建智能体。任何内容在触达客户之前，都由你的团队审核。"),
        ("交接", "完整的交接文档：系统由你的团队运行，每个智能体、提示词和文件都归你所有。需要持续支持时，我也在。"),
    ],
}

PROOF = {
    "en": [
        ("Case study", '<a class="text-link" href="/work/six-month-marketing-function">Six months of one operator running a whole marketing function on AI agents</a>, phase by phase.'),
        ("Open source", '<a class="text-link" href="/skills/">126 inspectable skills</a>, sixteen built by Flow AI, every one linked to its source.'),
        ("Try one", '<a class="text-link" href="/templates/">Free agent templates</a> you can run on your own site today.'),
        ("Method", '<a class="text-link" href="/sprints/">How the agent team works</a>, with a public checklist for every sprint.'),
    ],
    "zh": [
        ("案例研究", '<a class="text-link" href="/work/six-month-marketing-function">一个人用 AI 智能体运行完整营销职能的六个月</a>，逐阶段拆解。'),
        ("开源", '<a class="text-link" href="/skills/">126 个可检查的技能</a>，其中 16 个由 Flow AI 搭建，每一个都链接到源码。'),
        ("马上试用", '<a class="text-link" href="/templates/">免费智能体模板</a>，今天就能在你自己的网站上运行。'),
        ("方法", '<a class="text-link" href="/sprints/">智能体团队如何工作</a>，每个冲刺都有公开的交付清单。'),
    ],
}

UI = {
    "en": dict(
        lang="en-NZ", services_eyebrow="What the agents run", services_h2="Every part of marketing, one agent each.",
        services_lead="Start with the agent that closes your biggest gap. Add the next when the first is running well.",
        how_eyebrow="How a build runs", how_h2="Written scope, a build with your team, then it's yours.",
        proof_eyebrow="See it running", proof_h2="Every system is public.",
        proof_lead="Client results appear here only with real names and real numbers. Until then, judge the work itself.",
        fit_h2="When an agency is the better call.",
        fit_p="Large paid media budgets and brand campaigns with heavy production suit a full-service agency. Flow AI fits when you want marketing that runs every week on systems your team owns.",
        cost_h2="What it costs.",
        cost_p='Each build is priced per project once the written scope is agreed, so you pay for what your business needs. For market context, <a class="text-link" href="/blog/ai-marketing-cost-australia-new-zealand">the cost guide</a> sets out sourced ranges for tools, freelancers, agencies and hires in New Zealand and Australia.',
        guides_h2="Read before you choose.", faq_h2="Questions.", cta="Work with me", step="Step",
        crumb_home="Flow AI", crumb_hub="AI marketing services",
        end_note="A short form. I read every message myself and reply within two working days.",
    ),
    "zh": dict(
        lang="zh-Hans", services_eyebrow="智能体负责什么", services_h2="营销的每个环节，各由一个智能体负责。",
        services_lead="先从最大的缺口开始，搭建第一个智能体。它运行稳定后，再加下一个。",
        how_eyebrow="搭建流程", how_h2="书面范围，一起搭建，然后交给你。",
        proof_eyebrow="看它运行", proof_h2="每个系统都是公开的。",
        proof_lead="客户成果只有在可以公开真实名字和真实数字时才会出现在这里。在那之前，请直接评判作品本身。",
        fit_h2="什么时候代理机构更合适。",
        fit_p="大额付费广告预算、制作量很大的品牌活动，更适合全案代理机构。如果你希望营销每周都在运转，而且系统归自己团队所有，Flow AI 更合适。",
        cost_h2="费用。",
        cost_p='每个项目在书面范围确定后单独报价，你只为业务真正需要的部分付费。想了解市场行情，可以看<a class="text-link" href="/blog/ai-marketing-cost-australia-new-zealand">费用指南</a>，里面列出了新西兰和澳大利亚的工具、自由职业者、代理机构和内部招聘的有出处的价格区间。',
        guides_h2="做决定之前，先读这些。", faq_h2="常见问题。", cta="与我合作", step="步骤",
        crumb_home="Flow AI", crumb_hub="AI 营销服务",
        end_note="一份简短的表单。每条留言我都亲自阅读，两个工作日内回复。",
    ),
}

NZ, AU = {"@type": "Country", "name": "New Zealand"}, {"@type": "Country", "name": "Australia"}
AKL = {"@type": "City", "name": "Auckland", "containedInPlace": NZ}

PAGES = [
    dict(
        slug="", area=[NZ, AU],
        en=dict(
            title="AI Marketing Services for NZ and Australian Businesses | Flow AI",
            description="AI marketing services for New Zealand and Australian businesses: AI agents for search, content, outbound and reporting, built with your team and handed over.",
            eyebrow="AI marketing services · New Zealand and Australia",
            h1="AI marketing services for New Zealand and Australian businesses.",
            answer=DEFINITION + " Each build starts with a written scope, and your team keeps every agent.",
            lead="Let's build the marketing team your business deserves, one agent at a time, and keep it running in your hands.",
            local=None,
            places=[("New Zealand", "/ai-marketing-services/new-zealand", "Privacy Act 2020, spam law and what Kiwi buyers search."),
                    ("Australia", "/ai-marketing-services/australia", "Spam Act and privacy rules, AUD, and working across the Tasman."),
                    ("Auckland", "/ai-marketing-services/auckland", "In-person workshops, Google Maps and local AI search.")],
            guides=["what-do-ai-marketing-services-include", "how-to-choose-an-ai-marketing-provider", "ai-marketing-services-vs-tools", "ai-marketing-scope-of-work", "first-month-of-an-ai-marketing-build", "what-is-an-ai-marketing-agent"],
            faq=[
                ("What are AI marketing services?", "AI marketing services are marketing work delivered through AI systems, such as agents for search, content, outbound and reporting, with people setting direction and approving what reaches customers. Some providers run the systems for you on a retainer. Flow AI builds them with your team and hands them over, so you own them."),
                ("Is Flow AI an AI marketing agency?", "Flow AI does the work people look for when they search for an AI marketing agency: AI search, content, social, outbound and reporting. The difference is the model. One marketing engineer builds the agents with your team, documents them and hands them over, so the system stays yours instead of sitting inside a retainer."),
                ("Do you work with businesses in Australia?", "Yes. Flow AI is based in Auckland and works with businesses across New Zealand and Australia. Builds run remotely on your own accounts, with calls scheduled across the two time zones, and Australian work follows the Spam Act 2003 and the Australian Privacy Principles."),
                ("How much do AI marketing services cost?", "Flow AI prices each build per project once a written scope is agreed. Market ranges for AI tools, freelancers, agencies and in-house hires in New Zealand and Australia are set out, with sources, in the Flow AI cost guide."),
                ("Who owns the agents after the build?", "You do. Every agent, prompt, workflow and document is built on your accounts and handed over with written instructions, so your team can run, change or extend the system without Flow AI."),
                ("Where does a person review the work?", "Before anything reaches a customer. Each agent drafts, a named person on your team approves, and the scope records who reviews what. Positioning, pricing, claims and spend always stay with people."),
            ],
        ),
        zh=dict(
            title="新西兰和澳大利亚企业的 AI 营销服务 | Flow AI",
            description="面向新西兰和澳大利亚企业的 AI 营销服务：搜索、内容、主动外联和报告的 AI 智能体，与你的团队一起搭建，然后交接给你。",
            eyebrow="AI 营销服务 · 新西兰和澳大利亚",
            h1="面向新西兰和澳大利亚企业的 AI 营销服务。",
            answer="Flow AI 为新西兰和澳大利亚的企业提供 AI 营销服务。Amber Lan 是奥克兰的 AI 营销工程师，她和你的团队一起搭建负责搜索、内容、主动外联和报告的 AI 智能体，然后交接给你。每个项目都从书面范围说明开始，所有智能体都归你的团队所有。",
            lead="一起搭建你的业务值得拥有的营销团队，一次一个智能体，并且一直掌握在你自己手里。",
            local=None,
            places=[("新西兰", "/ai-marketing-services/new-zealand", "《2020 年隐私法》、垃圾邮件法，以及新西兰买家怎么搜索。"),
                    ("澳大利亚", "/ai-marketing-services/australia", "《垃圾邮件法》和隐私规则、澳元，以及跨塔斯曼海合作。"),
                    ("奥克兰", "/ai-marketing-services/auckland", "线下工作坊、Google 地图和本地 AI 搜索。")],
            guides=None,
            faq=[
                ("什么是 AI 营销服务？", "AI 营销服务是通过 AI 系统完成的营销工作，例如负责搜索、内容、主动外联和报告的智能体，由人来定方向，并审核所有触达客户的内容。有的服务商按月费替你运行这些系统。Flow AI 和你的团队一起搭建，然后交接给你，系统归你所有。"),
                ("Flow AI 是 AI 营销代理机构吗？", "人们搜索 AI 营销代理机构时想要的工作，Flow AI 都做：AI 搜索、内容、社交媒体、主动外联和报告。区别在于合作模式。一位营销工程师和你的团队一起搭建智能体，写好文档后交接给你，系统留在你手里，而不是锁在月费合同里。"),
                ("你们和澳大利亚的企业合作吗？", "合作。Flow AI 位于奥克兰，服务新西兰和澳大利亚两地的企业。项目远程进行，在你自己的账号上搭建，通话时间兼顾两地时区。澳大利亚的项目遵守《2003 年垃圾邮件法》和澳大利亚隐私原则。"),
                ("AI 营销服务要花多少钱？", "Flow AI 在书面范围确定后，按项目单独报价。新西兰和澳大利亚的 AI 工具、自由职业者、代理机构和内部招聘的市场价格区间，都附出处整理在 Flow AI 的费用指南里。"),
                ("搭建完成后，智能体归谁？", "归你。每个智能体、提示词、工作流和文档都建在你的账号上，并附书面说明交接，你的团队可以自己运行、修改或扩展，不需要依赖 Flow AI。"),
                ("人在哪个环节审核？", "在任何内容触达客户之前。智能体负责起草，你团队里一位指定的人负责批准，范围说明里写清楚谁审核什么。定位、定价、对外主张和预算，始终由人来决定。"),
            ],
        ),
    ),
    dict(
        slug="new-zealand", area=[NZ],
        en=dict(
            title="AI Marketing Services in New Zealand | Flow AI, Auckland",
            description="AI marketing services for New Zealand businesses: AI search, content, outbound and reporting agents, built with your team under NZ privacy and spam law.",
            eyebrow="AI marketing services · New Zealand",
            h1="AI marketing services in New Zealand.",
            answer="Flow AI provides AI marketing services for businesses across New Zealand, from Auckland. Amber Lan, an AI marketing engineer, builds the AI agents that run search, content, outbound and reporting with your team, under the Privacy Act 2020 and the Unsolicited Electronic Messages Act, then hands them over.",
            lead="Let's give your New Zealand business marketing that runs every week, on systems your team owns.",
            local=("Built for how New Zealand buys.", "Every build starts from the rules and habits of the New Zealand market.", [
                ("Search", 'Google handles about nine in ten New Zealand searches, so the search agent starts with your Google Business Profile, service pages and Search Console. <a class="text-link" href="/blog/seo-for-small-business-nz">SEO for NZ small business</a>.'),
                ("AI answers", 'Buyers now ask ChatGPT and Perplexity who to hire. The search agent makes your business easy for them to find and confirm. <a class="text-link" href="/blog/how-to-get-mentioned-by-chatgpt">How AI assistants choose who to mention</a>.'),
                ("Privacy", 'Agents read only the data the scope allows, and customer data stays inside the tools you already use, in line with the Privacy Act 2020. <a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI marketing and privacy law</a>.'),
                ("Email", "Outbound follows the Unsolicited Electronic Messages Act 2007: consent, clear identification and a working unsubscribe on every message."),
                ("Local data", 'Plans start from sourced New Zealand figures on AI adoption, search and marketing costs. <a class="text-link" href="/blog/ai-marketing-statistics-australia-new-zealand">62 statistics for Australia and New Zealand</a>.'),
                ("Pricing", "Quoted in NZD, plus GST, once the written scope is agreed."),
            ]),
            places=[("Auckland", "/ai-marketing-services/auckland", "Meet in person and run the build workshop on site."),
                    ("Australia", "/ai-marketing-services/australia", "Selling across the Tasman as well.")],
            guides=["ai-marketing-providers-new-zealand", "do-you-need-an-ai-marketing-agency-nz", "ai-agency-vs-ai-consultant-nz", "ai-marketing-for-small-business-nz", "marketing-agency-cost-nz", "ai-marketing-privacy-law-nz-australia"],
            faq=[
                ("Who offers AI marketing services in New Zealand?", "Providers range from established digital agencies that added AI services to AI-native agencies, automation consultants, AI search specialists and build-and-handover practices such as Flow AI. The Flow AI guide to New Zealand providers lists them by type, using each provider's own public pages, with Flow AI disclosed as the publisher."),
                ("Do you work with businesses outside Auckland?", "Yes. Flow AI works with businesses anywhere in New Zealand. Builds run remotely on your own accounts, and Auckland businesses can also meet in person for the scoping workshop."),
                ("Is my customer data safe with AI marketing agents?", "The written scope names exactly what each agent may read, and customer data stays inside the tools you already use. Agents draft from what they are allowed to see, and a person on your team approves anything that reaches a customer, in line with the Privacy Act 2020."),
                ("What do AI marketing services cost in New Zealand?", "Flow AI prices each build per project, in NZD plus GST, once the written scope is agreed. For market context, the Flow AI cost guide sets out sourced New Zealand ranges: agency retainers, freelancer rates, in-house salaries and AI tools."),
                ("How is this different from a New Zealand marketing agency?", "An agency usually runs marketing for you on a monthly retainer. Flow AI builds the AI agents that run it with your team and hands them over, so the system, the prompts and the know-how stay inside your business."),
                ("How do I start?", "Send a short note through the contact form about your business and the marketing gap that costs you most. Amber replies personally, and the first step is a written scope."),
            ],
        ),
        zh=dict(
            title="新西兰 AI 营销服务 | Flow AI，奥克兰",
            description="面向新西兰企业的 AI 营销服务：AI 搜索、内容、主动外联和报告智能体，与你的团队一起搭建，遵守新西兰隐私法和垃圾邮件法。",
            eyebrow="AI 营销服务 · 新西兰",
            h1="新西兰的 AI 营销服务。",
            answer="Flow AI 在奥克兰为新西兰各地的企业提供 AI 营销服务。AI 营销工程师 Amber Lan 和你的团队一起搭建负责搜索、内容、主动外联和报告的 AI 智能体，遵守《2020 年隐私法》和《未经请求电子信息法》，然后交接给你。",
            lead="让你在新西兰的业务拥有每周都在运转的营销，系统归你的团队所有。",
            local=("按新西兰买家的习惯来搭建。", "每个项目都从新西兰市场的规则和习惯出发。", [
                ("搜索", '新西兰大约九成的搜索发生在 Google 上，所以搜索智能体先从 Google 商家资料、服务页面和 Search Console 做起。<a class="text-link" href="/blog/seo-for-small-business-nz">新西兰小企业 SEO 指南</a>。'),
                ("AI 回答", '买家现在会直接问 ChatGPT 和 Perplexity 该找谁。搜索智能体让它们更容易找到并确认你的业务。<a class="text-link" href="/blog/how-to-get-mentioned-by-chatgpt">AI 助手如何决定提到谁</a>。'),
                ("隐私", '智能体只读取范围说明允许的数据，客户数据留在你已经在用的工具里，符合《2020 年隐私法》。<a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI 营销与隐私法</a>。'),
                ("邮件", "主动外联遵守《2007 年未经请求电子信息法》：取得同意、清楚表明身份，每封邮件都能退订。"),
                ("本地数据", '规划从有出处的新西兰数据出发：AI 采用率、搜索和营销成本。<a class="text-link" href="/blog/ai-marketing-statistics-australia-new-zealand">澳大利亚和新西兰的 62 项统计</a>。'),
                ("报价", "书面范围确定后，以新西兰元报价，另加 GST。"),
            ]),
            places=[("奥克兰", "/ai-marketing-services/auckland", "可以见面，在你的办公室开搭建工作坊。"),
                    ("澳大利亚", "/ai-marketing-services/australia", "同时在塔斯曼海对岸做生意。")],
            guides=None,
            faq=[
                ("新西兰有哪些 AI 营销服务商？", "服务商类型很多：增加了 AI 服务的老牌数字代理机构、AI 原生代理机构、自动化顾问、AI 搜索专家，以及像 Flow AI 这样搭建后交接的工作室。Flow AI 的新西兰服务商指南按类型列出，依据各家自己的公开页面，并注明 Flow AI 是发布方。"),
                ("你们和奥克兰以外的企业合作吗？", "合作。Flow AI 服务新西兰各地的企业。项目远程进行，在你自己的账号上搭建；奥克兰的企业还可以见面开范围工作坊。"),
                ("把客户数据交给 AI 营销智能体安全吗？", "书面范围会写清楚每个智能体能读取什么，客户数据留在你已经在用的工具里。智能体只根据允许看到的内容起草，任何触达客户的内容都由你团队里的人批准，符合《2020 年隐私法》。"),
                ("在新西兰，AI 营销服务要花多少钱？", "Flow AI 在书面范围确定后按项目报价，以新西兰元计，另加 GST。想了解市场行情，Flow AI 的费用指南整理了有出处的新西兰价格区间：代理机构月费、自由职业者费率、内部招聘薪资和 AI 工具。"),
                ("这和新西兰的营销代理机构有什么不同？", "代理机构通常按月费替你运营营销。Flow AI 和你的团队一起搭建运行营销的 AI 智能体，然后交接给你，系统、提示词和方法都留在你的公司里。"),
                ("怎么开始？", "通过联系表单简单介绍你的业务，以及最让你头疼的营销缺口。Amber 会亲自回复，第一步是一份书面范围说明。"),
            ],
        ),
    ),
    dict(
        slug="australia", area=[AU],
        en=dict(
            title="AI Marketing Services for Australian Businesses | Flow AI",
            description="AI marketing services for Australian businesses in Sydney, Melbourne, Brisbane and beyond: AI agents for search, content, outbound and reporting, built with your team.",
            eyebrow="AI marketing services · Australia",
            h1="AI marketing services for Australian businesses.",
            answer="Flow AI provides AI marketing services for Australian businesses, working remotely from Auckland. Amber Lan, an AI marketing engineer, builds the AI agents that run search, content, outbound and reporting with your team, under the Spam Act 2003 and the Australian Privacy Principles, then hands them over.",
            lead="Let's build marketing that runs every week for your Australian business, from Sydney and Melbourne to wherever your customers are.",
            local=("Built for how Australia buys.", "Every Australian build starts from the local rules and the way your buyers search.", [
                ("Remote by design", "The build runs on your own accounts, with short calls placed across the two time zones. Auckland is two to three hours ahead of the east coast."),
                ("Search", 'The search agent covers Google, Bing and the AI answers buyers read before they call, from Sydney and Melbourne to regional Australia. <a class="text-link" href="/blog/what-is-answer-engine-optimisation">What answer engine optimisation is</a>.'),
                ("Email", 'Outbound follows the Spam Act 2003: consent, clear identification and a working unsubscribe on every commercial message. <a class="text-link" href="/blog/outbound-sales-automation">Outbound done properly</a>.'),
                ("Privacy", 'Agents read only the data the scope allows, in line with the Australian Privacy Principles. <a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI marketing and privacy law</a>.'),
                ("Costs", 'For Australian market ranges, read <a class="text-link" href="/blog/marketing-agency-cost-australia">what a marketing agency costs in Australia</a>.'),
                ("Pricing", "Quoted per project once the written scope is agreed."),
            ]),
            places=[("New Zealand", "/ai-marketing-services/new-zealand", "Selling into New Zealand too."),
                    ("All services", "/ai-marketing-services/", "The full agent team, in one place.")],
            guides=["ai-marketing-providers-australia", "marketing-agency-cost-australia", "how-to-choose-an-ai-marketing-provider", "ai-marketing-statistics-australia-new-zealand", "fractional-cmo-vs-ai-cmo", "ai-marketing-privacy-law-nz-australia"],
            faq=[
                ("Can a New Zealand provider deliver AI marketing services in Australia?", "Yes. The agents are built on your own accounts and tools, so the work does not depend on location. Flow AI works with Australian businesses remotely, schedules calls across the two time zones and follows Australian rules on spam and privacy."),
                ("Who offers AI marketing services in Australia?", "Australian businesses can choose from AI-native agencies, established agencies adding AI, automation consultancies, AI search specialists and build-and-handover practices. The Flow AI guide to Australian providers lists them by type from their own public pages, with Flow AI disclosed as the publisher."),
                ("Do you work with businesses in Sydney and Melbourne?", "Yes, and anywhere else in Australia. Every build runs remotely, so a business in Brisbane, Perth or regional Australia gets the same process as one in Sydney or Melbourne."),
                ("Does outbound follow Australian spam law?", "Yes. Every commercial message the outbound agent drafts must meet the Spam Act 2003: consent, clear identification of the sender and a working unsubscribe. A person on your team approves the first message to every new contact."),
                ("Do you charge in Australian dollars?", "The written scope sets the price for each build, and the currency is agreed in that scope. Flow AI does not publish prices; market ranges for Australia sit in the Flow AI cost guides."),
                ("How do I start?", "Send a short note through the contact form about your business and your biggest marketing gap. Amber replies personally, and the first step is a written scope."),
            ],
        ),
        zh=dict(
            title="面向澳大利亚企业的 AI 营销服务 | Flow AI",
            description="面向悉尼、墨尔本、布里斯班等地澳大利亚企业的 AI 营销服务：搜索、内容、主动外联和报告的 AI 智能体，与你的团队一起搭建。",
            eyebrow="AI 营销服务 · 澳大利亚",
            h1="面向澳大利亚企业的 AI 营销服务。",
            answer="Flow AI 从奥克兰远程为澳大利亚企业提供 AI 营销服务。AI 营销工程师 Amber Lan 和你的团队一起搭建负责搜索、内容、主动外联和报告的 AI 智能体，遵守《2003 年垃圾邮件法》和澳大利亚隐私原则，然后交接给你。",
            lead="为你在澳大利亚的业务搭建每周都在运转的营销，从悉尼、墨尔本到你的客户所在的任何地方。",
            local=("按澳大利亚买家的习惯来搭建。", "每个澳大利亚项目都从当地规则和买家的搜索习惯出发。", [
                ("远程合作", "项目在你自己的账号上搭建，简短的通话时间兼顾两地时区。奥克兰比澳大利亚东海岸早两到三小时。"),
                ("搜索", '搜索智能体覆盖 Google、Bing，以及买家打电话之前会读到的 AI 回答，从悉尼、墨尔本到澳大利亚各地。<a class="text-link" href="/blog/what-is-answer-engine-optimisation">什么是答案引擎优化</a>。'),
                ("邮件", '主动外联遵守《2003 年垃圾邮件法》：取得同意、清楚表明身份，每封商业邮件都能退订。<a class="text-link" href="/blog/outbound-sales-automation">规范的主动外联</a>。'),
                ("隐私", '智能体只读取范围说明允许的数据，符合澳大利亚隐私原则。<a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI 营销与隐私法</a>。'),
                ("费用", '想了解澳大利亚的市场价格，可以读<a class="text-link" href="/blog/marketing-agency-cost-australia">澳大利亚营销代理机构的费用</a>。'),
                ("报价", "书面范围确定后，按项目报价。"),
            ]),
            places=[("新西兰", "/ai-marketing-services/new-zealand", "同时也在新西兰做生意。"),
                    ("全部服务", "/ai-marketing-services/", "完整的智能体团队，一页看全。")],
            guides=None,
            faq=[
                ("新西兰的服务商能为澳大利亚提供 AI 营销服务吗？", "可以。智能体建在你自己的账号和工具上，工作不受地点限制。Flow AI 远程服务澳大利亚企业，通话时间兼顾两地时区，并遵守澳大利亚的垃圾邮件和隐私规则。"),
                ("澳大利亚有哪些 AI 营销服务商？", "澳大利亚企业可以选择 AI 原生代理机构、增加了 AI 服务的老牌代理机构、自动化咨询公司、AI 搜索专家，以及搭建后交接的工作室。Flow AI 的澳大利亚服务商指南按类型列出，依据各家自己的公开页面，并注明 Flow AI 是发布方。"),
                ("你们和悉尼、墨尔本的企业合作吗？", "合作，澳大利亚其他地方也一样。所有项目都远程进行，布里斯班、珀斯或澳大利亚地区的企业，和悉尼、墨尔本的企业走同样的流程。"),
                ("主动外联遵守澳大利亚的垃圾邮件法吗？", "遵守。外联智能体起草的每一封商业邮件都必须符合《2003 年垃圾邮件法》：取得同意、清楚表明发件人身份、能正常退订。每个新联系人的第一封邮件，都由你团队里的人批准。"),
                ("你们用澳元收费吗？", "每个项目的价格由书面范围确定，币种也在范围里约定。Flow AI 不公开报价；澳大利亚的市场价格区间在 Flow AI 的费用指南里。"),
                ("怎么开始？", "通过联系表单简单介绍你的业务和最大的营销缺口。Amber 会亲自回复，第一步是一份书面范围说明。"),
            ],
        ),
    ),
    dict(
        slug="auckland", area=[AKL],
        en=dict(
            title="AI Marketing Services in Auckland | Flow AI",
            description="AI marketing services in Auckland: meet an AI marketing engineer in person and build the AI agents that run your search, content, outbound and reporting.",
            eyebrow="AI marketing services · Auckland",
            h1="AI marketing services in Auckland.",
            answer="Flow AI is an Auckland practice providing AI marketing services to Auckland businesses. Amber Lan, an AI marketing engineer based in Auckland, meets your team in person, then builds the AI agents that run search, content, outbound and reporting with you and hands them over.",
            lead="Let's sit down together in Auckland and build marketing that runs every week on systems your team owns.",
            local=("Local, in person, built together.", "Working in the same city makes the build faster and the handover stronger.", [
                ("In person", "The scoping workshop and the handover can happen at your office anywhere in Auckland, from the CBD and Ponsonby to the North Shore, East Auckland and South Auckland."),
                ("Google Maps", 'The search agent starts with your Google Business Profile: categories, service areas, photos and a steady flow of genuine reviews. <a class="text-link" href="/blog/get-recommended-by-chatgpt-auckland">How Auckland businesses get recommended</a>.'),
                ("Local AI search", "When someone asks ChatGPT for the best provider in Auckland, it draws on the open web, maps data and reviews. The agent makes sure your business shows up accurately in all three."),
                ("Same time zone", "Your team and the person building the agents work the same hours, so review loops close the same day."),
                ("Community", 'Amber builds in public and shows up at Auckland builder events. <a class="text-link" href="/about">More about Amber</a>.'),
                ("Pricing", "Quoted in NZD, plus GST, once the written scope is agreed."),
            ]),
            places=[("New Zealand", "/ai-marketing-services/new-zealand", "The same service for the rest of New Zealand."),
                    ("Australia", "/ai-marketing-services/australia", "Selling across the Tasman as well.")],
            guides=["get-recommended-by-chatgpt-auckland", "seo-for-small-business-nz", "ai-marketing-providers-new-zealand", "how-to-get-mentioned-by-chatgpt", "first-month-of-an-ai-marketing-build", "content-marketing-small-business-nz"],
            faq=[
                ("Can we meet in person in Auckland?", "Yes. Flow AI is based in Auckland, so the scoping workshop and the handover can happen at your office. The build itself runs on your own accounts between sessions, with your team reviewing as it goes."),
                ("Who offers AI marketing services in Auckland?", "Auckland has established digital agencies that added AI services, AI automation studios, AI search specialists and build-and-handover practices such as Flow AI. The Flow AI guide to New Zealand providers lists them by type from their own public pages, with Flow AI disclosed as the publisher."),
                ("Can you help my Auckland business show up on Google Maps?", "Yes. The search agent sets up and maintains your Google Business Profile, keeps your business details consistent across the web and builds a steady process for asking customers for genuine reviews. Google ranks local results on relevance, distance and prominence."),
                ("How do I get my Auckland business recommended by ChatGPT?", "Make your business easy to find and confirm: clear service pages, consistent details on your site and directories, recent genuine reviews, and mentions on sites the assistants already trust. The Flow AI guide for Auckland businesses walks through it step by step."),
                ("Do you only work with Auckland businesses?", "No. Auckland businesses can meet in person, and the same service runs remotely for businesses across New Zealand and Australia."),
                ("How do I start?", "Send a short note through the contact form. Amber replies personally, usually suggests a first meeting in Auckland, and the first step is a written scope."),
            ],
        ),
        zh=dict(
            title="奥克兰 AI 营销服务 | Flow AI",
            description="奥克兰的 AI 营销服务：和 AI 营销工程师当面沟通，一起搭建负责搜索、内容、主动外联和报告的 AI 智能体。",
            eyebrow="AI 营销服务 · 奥克兰",
            h1="奥克兰的 AI 营销服务。",
            answer="Flow AI 是一家奥克兰的工作室，为奥克兰企业提供 AI 营销服务。常驻奥克兰的 AI 营销工程师 Amber Lan 会和你的团队当面沟通，然后一起搭建负责搜索、内容、主动外联和报告的 AI 智能体，并交接给你。",
            lead="在奥克兰坐下来一起聊，搭建每周都在运转的营销，系统归你的团队所有。",
            local=("本地，见面，一起搭建。", "同在一个城市，搭建更快，交接也更扎实。", [
                ("当面合作", "范围工作坊和交接可以在你的办公室进行，奥克兰市中心、Ponsonby、北岸、东区、南区都可以。"),
                ("Google 地图", '搜索智能体从 Google 商家资料做起：类别、服务区域、照片，以及持续收集的真实评价。<a class="text-link" href="/blog/get-recommended-by-chatgpt-auckland">奥克兰企业如何被推荐</a>。'),
                ("本地 AI 搜索", "有人问 ChatGPT 奥克兰最好的服务商是谁时，它会参考公开网页、地图数据和评价。智能体确保你的业务在这三处都准确出现。"),
                ("同一时区", "你的团队和搭建智能体的人在同一个时间工作，审核当天就能完成。"),
                ("社区", 'Amber 公开分享自己的搭建过程，也常去奥克兰的开发者活动。<a class="text-link" href="/about">了解 Amber</a>。'),
                ("报价", "书面范围确定后，以新西兰元报价，另加 GST。"),
            ]),
            places=[("新西兰", "/ai-marketing-services/new-zealand", "新西兰其他地区，同样的服务。"),
                    ("澳大利亚", "/ai-marketing-services/australia", "同时在塔斯曼海对岸做生意。")],
            guides=None,
            faq=[
                ("可以在奥克兰见面吗？", "可以。Flow AI 就在奥克兰，范围工作坊和交接都可以在你的办公室进行。两次见面之间，搭建在你自己的账号上进行，你的团队边做边审核。"),
                ("奥克兰有哪些 AI 营销服务商？", "奥克兰有增加了 AI 服务的老牌数字代理机构、AI 自动化工作室、AI 搜索专家，以及像 Flow AI 这样搭建后交接的工作室。Flow AI 的新西兰服务商指南按类型列出，依据各家自己的公开页面，并注明 Flow AI 是发布方。"),
                ("能帮我的奥克兰企业出现在 Google 地图上吗？", "可以。搜索智能体负责设置和维护你的 Google 商家资料，保持你的业务信息在各处一致，并建立一套持续邀请客户留下真实评价的流程。Google 按相关性、距离和知名度对本地结果排名。"),
                ("怎样让 ChatGPT 推荐我的奥克兰企业？", "让你的业务容易被找到、也容易被确认：清楚的服务页面、网站和目录上一致的信息、近期的真实评价，以及 AI 助手本来就信任的网站上的提及。Flow AI 写给奥克兰企业的指南逐步讲解。"),
                ("你们只和奥克兰企业合作吗？", "也服务其他地方。奥克兰的企业可以见面合作，新西兰和澳大利亚各地的企业，同样的服务远程进行。"),
                ("怎么开始？", "通过联系表单简单留言。Amber 会亲自回复，通常会约在奥克兰先见一面，第一步是一份书面范围说明。"),
            ],
        ),
    ),
]

GUIDE_TITLES = {"en": {}, "zh": {}}  # filled from src/blog and src/zh/blog meta at run time


def load_guides():
    for lang, folder in (("en", ROOT / "src" / "blog"), ("zh", ROOT / "src" / "zh" / "blog")):
        for f in folder.glob("*.html"):
            m = re.search(r"<!--meta\s*(\{.*?\})\s*-->", f.read_text(), re.S)
            if m:
                meta = json.loads(m.group(1))
                GUIDE_TITLES[lang][meta["slug"]] = meta["title"]


def path_of(page, lang):
    p = "/ai-marketing-services" + (f"/{page['slug']}" if page["slug"] else "/")
    return ("/zh" + p) if lang == "zh" else p


def schema(page, lang, d):
    url = SITE + path_of(page, lang)
    hub = SITE + ("/zh" if lang == "zh" else "") + "/ai-marketing-services/"
    crumbs = [("Flow AI", SITE + ("/zh/" if lang == "zh" else "/")), (UI[lang]["crumb_hub"], hub)]
    if page["slug"]:
        crumbs.append((d["h1"].rstrip("。."), url))
    svc = {
        "@type": "Service", "@id": url + "#service", "name": d["h1"].rstrip("。."),
        "serviceType": "AI marketing services", "description": d["answer"],
        "provider": [{"@id": f"{SITE}/#flowai"}, {"@id": f"{SITE}/#amber"}],
        "areaServed": page["area"], "url": url,
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": UI[lang]["crumb_hub"], "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "description": t}}
            for n, t, _ in SERVICES[lang]]},
        "offers": {"@type": "Offer", "description": "书面范围确定后按项目报价。附交接文档，所有智能体归客户所有。" if lang == "zh" else "Priced per project after a written scope. Documented handover; the client owns every agent."},
    }
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": url, "url": url, "name": d["title"], "description": d["description"],
         "inLanguage": UI[lang]["lang"], "dateModified": UPDATED, "about": {"@id": url + "#service"},
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".svc-answer"]}},
        svc,
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]},
    ]}


STYLE = """<style>
    @media (prefers-reduced-motion: no-preference) { @view-transition { navigation: auto; } }
    .hero { padding-bottom: var(--section); }
    main .lead { max-width: 46ch; }
    .svc-answer { max-width: 60ch; margin: 2rem auto 0; font-size: 1.02rem; line-height: 1.65; opacity: .82; }
    .svc-places { display: flex; flex-wrap: wrap; justify-content: center; gap: .5rem 1.5rem; margin-top: 1.75rem; }
    .svc-steps { display: grid; gap: 1.5rem; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); margin-top: clamp(2.5rem, 5vw, 3.5rem); text-align: left; }
    .svc-note { max-width: 60ch; margin: 1.25rem 0 0; }
    .narrow { text-align: left; margin-top: clamp(2.5rem, 5vw, 3.5rem); }
</style>"""


def render(page, lang):
    d, ui = page[lang], UI[lang]
    path = path_of(page, lang)
    url = SITE + path
    zh = lang == "zh"
    pre = lambda p: p  # scripts/i18n.py rewrites links on Chinese pages to their twins
    head = f"""<!doctype html>
<html lang="{ui['lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{GTM_HEAD}
  <title>{esc(d['title'])}</title>
  <meta name="description" content="{esc(d['description'])}">
  <meta name="theme-color" content="#0e0e0d">
  <link rel="canonical" href="{url}">
  <link rel="alternate" type="application/atom+xml" title="Flow AI" href="{SITE}/feed.xml">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <meta property="og:title" content="{esc(d['title'])}">
  <meta property="og:description" content="{esc(d['description'])}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Flow AI">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/og.png">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
{json.dumps(schema(page, lang, d), indent=2, ensure_ascii=False)}
  </script>
<link rel="stylesheet" href="/assets/site.css">
{STYLE}
<link rel="stylesheet" href="/assets/site-header.css">
<link rel="stylesheet" href="/assets/site-footer.css?v=2">
<link rel="stylesheet" href="/assets/motion.css">
<link rel="stylesheet" href="/assets/visual.css?v=1">
<script src="/assets/motion.js" defer></script>
<script src="/assets/visual.js?v=1" defer></script>
<link rel="preload" href="/fonts/google-sans-flex-vf.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/claude.css?v=14">
<link rel="stylesheet" href="/assets/highend.css?v=6">
<script>document.documentElement.className += ' has-nav';</script>
<script src="/assets/dot.js?v=6" defer></script>
<script src="/assets/nav.js?v=1" defer onerror="document.documentElement.classList.remove('has-nav')"></script>
</head>
<body data-motion="auto">
"""
    chrome = PRE.replace('<a href="/ai-marketing-services/">', '<a href="/ai-marketing-services/" aria-current="page">', 1)
    places = " &middot; ".join(f'<a class="text-link arrow-link" href="{pre(u)}">{esc(n)}</a>' for n, u, _ in d["places"])
    services = "".join(
        f'<li><span class="vlabel">{i + 1:02d}{CHECK}</span><b><a class="text-link" href="{pre(u)}">{esc(n)}</a></b><p>{esc(t)}</p></li>'
        for i, (n, t, u) in enumerate(SERVICES[lang]))
    steps = "\n".join(
        f'          <div class="step"><span class="small">0{i + 1}</span><h3>{esc(n)}</h3><p>{esc(t)}</p></div>'
        for i, (n, t) in enumerate(STEPS[lang]))
    proof = "\n".join(f'            <li><b>{esc(k)}</b><span>{v}</span></li>' for k, v in PROOF[lang])
    local = ""
    if d["local"]:
        h2, lead, rows = d["local"]
        items = "\n".join(f'            <li><b>{esc(k)}</b><span>{v}</span></li>' for k, v in rows)
        local = f"""
    <section id="local" class="centered" aria-labelledby="local-title">
      <div class="wrap">
        <div class="stack reveal">
          <h2 id="local-title">{esc(h2)}</h2>
          <p class="lead">{esc(lead)}</p>
        </div>
        <div class="narrow reveal">
          <ul class="systems">
{items}
          </ul>
        </div>
      </div>
    </section>
"""
    guides_slugs = d["guides"] if d["guides"] is not None else page["en"]["guides"]
    g_items = []
    for s in guides_slugs:
        t = GUIDE_TITLES[lang].get(s) or GUIDE_TITLES["en"].get(s)
        if t:
            g_items.append(f'            <li><b>{"指南" if zh else "Guide"}</b><span><a class="text-link" href="{pre("/blog/" + s)}">{esc(t)}</a></span></li>')
    for n, u, t in d["places"]:
        g_items.append(f'            <li><b>{"地区" if zh else "Place"}</b><span><a class="text-link" href="{pre(u)}">{esc(n)}</a>: {esc(t)}</span></li>')
    faq = "\n".join(f"""          <details>
            <summary>{esc(q)}</summary>
            <p>{esc(a)}</p>
          </details>""" for q, a in d["faq"])
    main = f"""  <main id="main">
    <section class="hero centered" data-fdot-host aria-labelledby="hero-title">
      <div class="wrap">
        <div class="stack">
          <svg class="fdot fdot--hero" data-fdot="flow" viewBox="0 0 100 100" aria-hidden="true" focusable="false"></svg>
          <p class="eyebrow">{esc(d['eyebrow'])}</p>
          <h1 id="hero-title">{esc(d['h1'])}</h1>
          <p class="lead">{esc(d['lead'])}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="{pre('/contact')}">{esc(ui['cta'])}</a>
            <a class="text-link" href="#services">{"看看智能体负责什么" if zh else "Explore what the agents run"}</a>
          </div>
          <p class="svc-answer">{esc(d['answer'])}</p>
          <p class="svc-places small">{places}</p>
        </div>
      </div>
    </section>

    <section id="services" class="centered" aria-labelledby="services-title">
      <div class="wrap">
        <div class="stack">
          <p class="eyebrow">{esc(ui['services_eyebrow'])}</p>
          <h2 id="services-title">{esc(ui['services_h2'])}</h2>
          <p class="lead">{esc(ui['services_lead'])}</p>
        </div>
        <ul class="dgrid reveal" aria-label="{esc(ui['services_h2'])}">{services}</ul>
      </div>
    </section>

    <section id="how" class="centered" aria-labelledby="how-title">
      <div class="wrap">
        <div class="stack reveal">
          <p class="eyebrow">{esc(ui['how_eyebrow'])}</p>
          <h2 id="how-title">{esc(ui['how_h2'])}</h2>
        </div>
        <div class="svc-steps reveal">
{steps}
        </div>
      </div>
    </section>
{local}
    <section id="proof" class="centered" aria-labelledby="proof-title">
      <div class="wrap">
        <div class="stack reveal">
          <p class="eyebrow">{esc(ui['proof_eyebrow'])}</p>
          <h2 id="proof-title">{esc(ui['proof_h2'])}</h2>
          <p class="lead">{esc(ui['proof_lead'])}</p>
        </div>
        <div class="narrow reveal">
          <ul class="systems">
{proof}
          </ul>
        </div>
      </div>
    </section>

    <section id="fit" class="centered" aria-labelledby="fit-title">
      <div class="wrap">
        <div class="stack reveal">
          <h2 id="fit-title">{esc(ui['cost_h2'])}</h2>
          <p class="svc-note">{ui['cost_p']}</p>
          <h2 id="agency-title" style="margin-top:clamp(3rem,6vw,4.5rem)">{esc(ui['fit_h2'])}</h2>
          <p class="svc-note">{esc(ui['fit_p'])}</p>
        </div>
      </div>
    </section>

    <section id="related" class="centered" aria-labelledby="related-title">
      <div class="wrap">
        <div class="stack reveal">
          <h2 id="related-title">{esc(ui['guides_h2'])}</h2>
        </div>
        <div class="narrow reveal">
          <ul class="systems">
{chr(10).join(g_items)}
          </ul>
        </div>
      </div>
    </section>

    <section id="faq" class="centered" aria-labelledby="faq-title">
      <div class="wrap">
        <div class="stack reveal">
          <h2 id="faq-title">{esc(ui['faq_h2'])}</h2>
        </div>
        <div class="faq reveal">
{faq}
        </div>
      </div>
    </section>

    <section id="book" class="contact centered" aria-labelledby="book-title">
      <div class="wrap">
        <div class="stack">
          <h2 id="book-title">{"一起开始搭建吧。" if zh else "Let's build your agent team."}</h2>
          <p class="lead">{"告诉我你的业务，以及最让你头疼的营销缺口。第一步是一份书面范围说明。" if zh else "Tell me about your business and the marketing gap that costs you most. The first step is a written scope."}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="{pre('/contact')}">{esc(ui['cta'])}</a>
            <a class="text-link" href="{pre('/sprints/')}">{"了解合作方式" if zh else "Explore how it works"}</a>
          </div>
          <p class="small">{esc(ui['end_note'])}</p>
        </div>
      </div>
    </section>
  </main>"""
    return head + chrome + main + TAIL


def main():
    load_guides()
    for page in PAGES:
        for lang in ("en", "zh"):
            rel = path_of(page, lang).lstrip("/")
            out = ROOT / (rel + "index.html" if not page["slug"] else rel + ".html")
            out.parent.mkdir(parents=True, exist_ok=True)
            text = render(page, lang)
            for bad in ("—", "–", "TODO"):
                assert bad not in text.replace("<!-- End", ""), f"{bad!r} in {out}"
            out.write_text(text)
            print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
