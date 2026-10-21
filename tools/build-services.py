#!/usr/bin/env python3
"""Build the AI marketing services pages, in English and Chinese.

    /ai-marketing-services                 the hub: AI marketing services for NZ and Australian businesses
    /ai-marketing-services/new-zealand
    /ai-marketing-services/australia
    /ai-marketing-services/auckland
    /ai-marketing-services/ai-automation-consultant        service pages by the job a buyer needs done
    /ai-marketing-services/ai-agent-development
    /ai-marketing-services/marketing-automation-consultant
    /ai-marketing-services/claude-code-consultant
    (and the same eight under /zh/)

Edit the PAGES data below, then run:
    python3 tools/build-services.py && python3 tools/build-llms-full.py && python3 scripts/i18n.py

The head assets, tag manager, header and footer are lifted from sprints/positioning.html on every
run, so these pages never drift from the rest of the site. scripts/i18n.py then adds the language
switch, hreflang and the Chinese header and footer.

House rules: no Amber Lan prices, no free audit, no invented clients, results or reviews.
Every service named here links to the page that describes it.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = (ROOT / "sprints" / "positioning.html").read_text()
SITE = "https://www.flowai.co.nz"
UPDATED = "2026-10-13"
DEFINITION = ("Amber Lan provides AI marketing services for businesses in New Zealand and Australia. "
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
        ("Positioning", "One page every agent works from, setting out who you serve and the claims you can prove.", "/sprints/positioning"),
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
        ("定位", "所有智能体共用的一页纸，写清你服务谁，以及你能证明的主张。", "/sprints/positioning"),
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
        ("Scope", "Together we agree in writing what we build, which data the agents may read, where your team reviews, and how we measure success. The price follows from that scope."),
        ("Build", "I build the agents with your team on your own accounts, each one building on the last. Your people approve everything before it reaches a customer."),
        ("Hand over", "A documented handover, so your team runs the system with confidence and owns every agent, prompt and file. Ongoing support stays available whenever you want it."),
    ],
    "zh": [
        ("书面范围", "我们一起用文字说清楚：搭建什么、智能体能读取哪些数据、你的团队在哪个环节审核、怎样衡量成效。价格依据这份范围确定。"),
        ("一起搭建", "我和你的团队一起，在你自己的账号里搭建智能体，每一套都建立在前一套之上。任何内容在触达客户之前，都由你的团队审核。"),
        ("交接", "完整的交接文档，让你的团队从容运行系统，每个智能体、提示词和文件都归你所有。需要持续支持时，我随时都在。"),
    ],
}

PROOF = {
    "en": [
        ("Case study", '<a class="text-link" href="/work/six-month-marketing-function">Six months of one operator running a whole marketing function on AI agents</a>, phase by phase.'),
        ("Open source", '<a class="text-link" href="/skills/">126 inspectable skills</a>, sixteen built by Amber Lan, every one linked to its source.'),
        ("Templates", '<a class="text-link" href="/templates/">Free agent templates</a>, ready to run on your own site today.'),
        ("Method", '<a class="text-link" href="/sprints/">How the agent team works</a>, with a public checklist for every sprint.'),
    ],
    "zh": [
        ("案例研究", '<a class="text-link" href="/work/six-month-marketing-function">一个人用 AI 智能体运行完整营销职能的六个月</a>，逐阶段拆解。'),
        ("开源", '<a class="text-link" href="/skills/">126 个可检查的技能</a>，其中 16 个由 Amber Lan 搭建，每一个都链接到源码。'),
        ("模板", '<a class="text-link" href="/templates/">免费智能体模板</a>，今天就能在你自己的网站上运行。'),
        ("方法", '<a class="text-link" href="/sprints/">智能体团队如何工作</a>，每个冲刺都有公开的交付清单。'),
    ],
}

UI = {
    "en": dict(
        lang="en-NZ", services_eyebrow="What the agents run", services_h2="Every part of marketing, one agent each.",
        services_lead="Together we map your whole marketing function, then bring each part online until the system runs end to end.",
        how_eyebrow="How a build runs", how_h2="Built together with your team, then yours to keep.",
        proof_eyebrow="Explore the work", proof_h2="Every system is public.",
        proof_lead="The systems behind this practice are public, so you can judge the craft before we begin.",
        fit_h2="When an agency is the better fit.",
        fit_p="Large paid media budgets and production-heavy brand campaigns belong with a full-service agency. Amber Lan is the partner for marketing that runs every week on systems your team owns and grows.",
        cost_h2="How pricing works.",
        cost_p='Each build is priced per project once the written scope is agreed, so the investment matches what your business needs. For market context, <a class="text-link" href="/blog/ai-marketing-cost-australia-new-zealand">the cost guide</a> sets out sourced ranges for tools, freelancers, agencies and hires in New Zealand and Australia.',
        guides_h2="Guides to help you choose well.", faq_h2="Questions.", cta="Work with me", step="Step",
        crumb_home="Amber Lan", crumb_hub="AI marketing services",
        end_note="The form takes a minute. I read every message myself and reply within two working days.",
    ),
    "zh": dict(
        lang="zh-Hans", services_eyebrow="智能体负责什么", services_h2="营销的每个环节，各由一个智能体负责。",
        services_lead="我们一起规划完整的营销职能，再把每个环节逐步接入，直到整套系统端到端运转。",
        how_eyebrow="搭建流程", how_h2="和你的团队一起搭建，然后由你长期拥有。",
        proof_eyebrow="探索作品", proof_h2="每个系统都是公开的。",
        proof_lead="这个工作室背后的系统都是公开的，开始合作之前，你可以先评判它的工艺。",
        fit_h2="什么时候代理机构更合适。",
        fit_p="大额付费广告预算、制作量很大的品牌活动，交给全案代理机构更合适。如果你希望营销每周都在运转，系统由自己的团队拥有并不断成长，Amber Lan 是合适的伙伴。",
        cost_h2="报价方式。",
        cost_p='每个项目在书面范围确定后单独报价，让投入与业务真正的需要相匹配。想了解市场行情，可以看<a class="text-link" href="/blog/ai-marketing-cost-australia-new-zealand">费用指南</a>，里面列出了新西兰和澳大利亚的工具、自由职业者、代理机构和内部招聘的有出处的价格区间。',
        guides_h2="帮你做出好选择的指南。", faq_h2="常见问题。", cta="与我合作", step="步骤",
        crumb_home="Amber Lan", crumb_hub="AI 营销服务",
        end_note="填写表单只需一分钟。每条留言我都亲自阅读，两个工作日内回复。",
    ),
}

NZ, AU = {"@type": "Country", "name": "New Zealand"}, {"@type": "Country", "name": "Australia"}
AKL = {"@type": "City", "name": "Auckland", "containedInPlace": NZ}

PAGES = [
    dict(
        slug="", area=[NZ, AU],
        en=dict(
            title="AI Marketing Services for NZ and Australia | Amber Lan",
            description="AI marketing services for New Zealand and Australian businesses from Amber Lan, an AI marketing engineer in Auckland: AI agents built with your team.",
            eyebrow="AI marketing services · New Zealand and Australia",
            h1="AI marketing services for New Zealand and Australian businesses.",
            answer=DEFINITION + " Each build starts with a written scope, and your team keeps every agent.",
            lead="Let's rebuild your marketing around AI agents, then hand the whole system to your team to run.",
            local=None,
            places=[("New Zealand", "/ai-marketing-services/new-zealand", "Privacy Act 2020, spam law and what Kiwi buyers search."),
                    ("Australia", "/ai-marketing-services/australia", "Spam Act and privacy rules, AUD, and working across the Tasman."),
                    ("Auckland", "/ai-marketing-services/auckland", "In-person workshops, Google Maps and local AI search.")],
            guides=["what-do-ai-marketing-services-include", "how-to-choose-an-ai-marketing-provider", "ai-marketing-services-vs-tools", "ai-marketing-scope-of-work", "first-month-of-an-ai-marketing-build", "what-is-an-ai-marketing-agent"],
            faq=[
                ("What are AI marketing services?", "AI marketing services are marketing work delivered through AI systems, such as agents for search, content, outbound and reporting, with people setting direction and approving what reaches customers. Some providers run the systems for you on a retainer. Amber Lan builds them with your team and hands them over, so you own them."),
                ("Is Amber Lan an AI marketing agency?", "Amber Lan does the work people look for when they search for an AI marketing agency: AI search, content, social, outbound and reporting. The model is a partnership. One marketing engineer builds the agents with your team, documents them and hands them over, so the system stays with your business for good."),
                ("Do you work with businesses in Australia?", "Yes. Amber Lan is based in Auckland and works with businesses across New Zealand and Australia. Builds run remotely on your own accounts, with calls scheduled across the two time zones, and Australian work follows the Spam Act 2003 and the Australian Privacy Principles."),
                ("How much do AI marketing services cost?", "Amber Lan prices each build per project once a written scope is agreed. Market ranges for AI tools, freelancers, agencies and in-house hires in New Zealand and Australia are set out, with sources, in Amber Lan's cost guide."),
                ("Who owns the agents after the build?", "You do. Every agent, prompt, workflow and document is built on your accounts and handed over with written instructions, so your team can run, change or extend the system without Amber Lan."),
                ("Where does a person review the work?", "Before anything reaches a customer. Each agent drafts, a named person on your team approves, and the scope records who reviews what. Positioning, pricing, claims and spend always stay with people."),
            ],
        ),
        zh=dict(
            title="新西兰与澳大利亚 AI 营销服务 | Amber Lan",
            description="奥克兰 AI 营销工程师 Amber Lan 为新西兰和澳大利亚企业提供 AI 营销服务：搜索、内容、主动外联和报告的 AI 智能体，与你的团队一起搭建。",
            eyebrow="AI 营销服务 · 新西兰和澳大利亚",
            h1="面向新西兰和澳大利亚企业的 AI 营销服务。",
            answer="Amber Lan 为新西兰和澳大利亚的企业提供 AI 营销服务。Amber Lan 是奥克兰的 AI 营销工程师，她和你的团队一起搭建负责搜索、内容、主动外联和报告的 AI 智能体，然后交接给你。每个项目都从书面范围说明开始，所有智能体都归你的团队所有。",
            lead="一起围绕 AI 智能体重建你的营销，再把整套系统交给你的团队运行。",
            local=None,
            places=[("新西兰", "/ai-marketing-services/new-zealand", "《2020 年隐私法》、垃圾邮件法，以及新西兰买家怎么搜索。"),
                    ("澳大利亚", "/ai-marketing-services/australia", "《垃圾邮件法》和隐私规则、澳元，以及跨塔斯曼海合作。"),
                    ("奥克兰", "/ai-marketing-services/auckland", "线下工作坊、Google 地图和本地 AI 搜索。")],
            guides=None,
            faq=[
                ("什么是 AI 营销服务？", "AI 营销服务是通过 AI 系统完成的营销工作，例如负责搜索、内容、主动外联和报告的智能体，由人来定方向，并审核所有触达客户的内容。有的服务商按月费替你运行这些系统。Amber Lan 和你的团队一起搭建，然后交接给你，系统归你所有。"),
                ("Amber Lan 是 AI 营销代理机构吗？", "人们搜索 AI 营销代理机构时想要的工作，Amber Lan 都做：AI 搜索、内容、社交媒体、主动外联和报告。合作模式是伙伴关系。一位营销工程师和你的团队一起搭建智能体，写好文档后交接给你，系统长期留在你的公司里。"),
                ("你们和澳大利亚的企业合作吗？", "合作。Amber Lan 位于奥克兰，服务新西兰和澳大利亚两地的企业。项目远程进行，在你自己的账号上搭建，通话时间兼顾两地时区。澳大利亚的项目遵守《2003 年垃圾邮件法》和澳大利亚隐私原则。"),
                ("AI 营销服务要花多少钱？", "Amber Lan 在书面范围确定后，按项目单独报价。新西兰和澳大利亚的 AI 工具、自由职业者、代理机构和内部招聘的市场价格区间，都附出处整理在 Amber Lan 的费用指南里。"),
                ("搭建完成后，智能体归谁？", "归你。每个智能体、提示词、工作流和文档都建在你的账号上，并附书面说明交接，你的团队可以自己运行、修改或扩展，不需要依赖 Amber Lan。"),
                ("人在哪个环节审核？", "在任何内容触达客户之前。智能体负责起草，你团队里一位指定的人负责批准，范围说明里写清楚谁审核什么。定位、定价、对外主张和预算，始终由人来决定。"),
            ],
        ),
    ),
    dict(
        slug="new-zealand", area=[NZ],
        en=dict(
            title="AI Marketing Services NZ | Amber Lan, AI Marketing Engineer",
            description="AI marketing services in New Zealand from Amber Lan, an AI marketing engineer in Auckland: search, content, outbound and reporting agents, built under NZ law.",
            eyebrow="AI marketing services · New Zealand",
            h1="AI marketing services in New Zealand.",
            answer="Amber Lan provides AI marketing services for businesses across New Zealand, from Auckland. Amber Lan, an AI marketing engineer, builds the AI agents that run search, content, outbound and reporting with your team, under the Privacy Act 2020 and the Unsolicited Electronic Messages Act, then hands them over.",
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
                    ("Australia", "/ai-marketing-services/australia", "For businesses that also sell across the Tasman.")],
            guides=["ai-marketing-providers-new-zealand", "do-you-need-an-ai-marketing-agency-nz", "ai-agency-vs-ai-consultant-nz", "ai-marketing-for-small-business-nz", "marketing-agency-cost-nz", "ai-marketing-privacy-law-nz-australia"],
            faq=[
                ("Who offers AI marketing services in New Zealand?", "Providers range from established digital agencies that added AI services to AI-native agencies, automation consultants, AI search specialists and build-and-handover practices such as Amber Lan. Amber Lan's guide to New Zealand providers lists them by type, using each provider's own public pages, with Amber Lan disclosed as the publisher."),
                ("Do you work with businesses outside Auckland?", "Yes. Amber Lan works with businesses anywhere in New Zealand. Builds run remotely on your own accounts, and Auckland businesses can also meet in person for the scoping workshop."),
                ("Is my customer data safe with AI marketing agents?", "The written scope names exactly what each agent may read, and customer data stays inside the tools you already use. Agents draft from what they are allowed to see, and a person on your team approves anything that reaches a customer, in line with the Privacy Act 2020."),
                ("What do AI marketing services cost in New Zealand?", "Amber Lan prices each build per project, in NZD plus GST, once the written scope is agreed. For market context, Amber Lan's cost guide sets out sourced New Zealand ranges: agency retainers, freelancer rates, in-house salaries and AI tools."),
                ("How is this different from a New Zealand marketing agency?", "An agency usually runs marketing for you on a monthly retainer. Amber Lan builds the AI agents that run it with your team and hands them over, so the system, the prompts and the know-how stay inside your business."),
                ("How do I start?", "Share a few lines about your business and the marketing gap you most want to close. Amber replies personally, and together you shape a written scope as the first step."),
            ],
        ),
        zh=dict(
            title="新西兰 AI 营销服务 | Amber Lan，AI 营销工程师",
            description="奥克兰 AI 营销工程师 Amber Lan 面向新西兰企业的 AI 营销服务：AI 搜索、内容、主动外联和报告智能体，遵守新西兰隐私法和垃圾邮件法。",
            eyebrow="AI 营销服务 · 新西兰",
            h1="新西兰的 AI 营销服务。",
            answer="Amber Lan 在奥克兰为新西兰各地的企业提供 AI 营销服务。AI 营销工程师 Amber Lan 和你的团队一起搭建负责搜索、内容、主动外联和报告的 AI 智能体，遵守《2020 年隐私法》和《未经请求电子信息法》，然后交接给你。",
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
                    ("澳大利亚", "/ai-marketing-services/australia", "适合同时在塔斯曼海对岸做生意的企业。")],
            guides=None,
            faq=[
                ("新西兰有哪些 AI 营销服务商？", "服务商类型很多：增加了 AI 服务的老牌数字代理机构、AI 原生代理机构、自动化顾问、AI 搜索专家，以及像 Amber Lan 这样搭建后交接的工作室。Amber Lan 的新西兰服务商指南按类型列出，依据各家自己的公开页面，并注明 Amber Lan 是发布方。"),
                ("你们和奥克兰以外的企业合作吗？", "合作。Amber Lan 服务新西兰各地的企业。项目远程进行，在你自己的账号上搭建；奥克兰的企业还可以见面开范围工作坊。"),
                ("把客户数据交给 AI 营销智能体安全吗？", "书面范围会写清楚每个智能体能读取什么，客户数据留在你已经在用的工具里。智能体只根据允许看到的内容起草，任何触达客户的内容都由你团队里的人批准，符合《2020 年隐私法》。"),
                ("在新西兰，AI 营销服务要花多少钱？", "Amber Lan 在书面范围确定后按项目报价，以新西兰元计，另加 GST。想了解市场行情，Amber Lan 的费用指南整理了有出处的新西兰价格区间：代理机构月费、自由职业者费率、内部招聘薪资和 AI 工具。"),
                ("这和新西兰的营销代理机构有什么不同？", "代理机构通常按月费替你运营营销。Amber Lan 和你的团队一起搭建运行营销的 AI 智能体，然后交接给你，系统、提示词和方法都留在你的公司里。"),
                ("怎么开始？", "简单介绍你的业务，以及你最想补上的营销缺口。Amber 会亲自回复，第一步是你们一起确定一份书面范围说明。"),
            ],
        ),
    ),
    dict(
        slug="australia", area=[AU],
        en=dict(
            title="AI Marketing Services Australia | Amber Lan, AI Marketing Engineer",
            description="AI marketing services for Australian businesses from Amber Lan, an AI marketing engineer: agents for search, content, outbound and reporting, Sydney to Brisbane.",
            eyebrow="AI marketing services · Australia",
            h1="AI marketing services for Australian businesses.",
            answer="Amber Lan provides AI marketing services for Australian businesses, working remotely from Auckland. Amber Lan, an AI marketing engineer, builds the AI agents that run search, content, outbound and reporting with your team, under the Spam Act 2003 and the Australian Privacy Principles, then hands them over.",
            lead="Let's build marketing that runs every week for your Australian business, from Sydney and Melbourne to wherever your customers are.",
            local=("Built for how Australia buys.", "Every Australian build starts from the local rules and the way your buyers search.", [
                ("Remote by design", "The build runs on your own accounts, with short calls placed across the two time zones. Auckland is two to three hours ahead of the east coast."),
                ("Search", 'The search agent covers Google, Bing and the AI answers buyers read before they call, from Sydney and Melbourne to regional Australia. <a class="text-link" href="/blog/what-is-answer-engine-optimisation">What answer engine optimisation is</a>.'),
                ("Email", 'Outbound follows the Spam Act 2003: consent, clear identification and a working unsubscribe on every commercial message. <a class="text-link" href="/blog/outbound-sales-automation">Outbound done properly</a>.'),
                ("Privacy", 'Agents read only the data the scope allows, in line with the Australian Privacy Principles. <a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI marketing and privacy law</a>.'),
                ("Costs", 'For Australian market ranges, read <a class="text-link" href="/blog/marketing-agency-cost-australia">what a marketing agency costs in Australia</a>.'),
                ("Pricing", "Quoted per project once the written scope is agreed."),
            ]),
            places=[("New Zealand", "/ai-marketing-services/new-zealand", "For businesses that also sell into New Zealand."),
                    ("All services", "/ai-marketing-services/", "The full agent team, in one place.")],
            guides=["ai-marketing-providers-australia", "marketing-agency-cost-australia", "how-to-choose-an-ai-marketing-provider", "ai-marketing-statistics-australia-new-zealand", "fractional-cmo-vs-ai-cmo", "ai-marketing-privacy-law-nz-australia"],
            faq=[
                ("Can a New Zealand provider deliver AI marketing services in Australia?", "Yes. The agents are built on your own accounts and tools, so the work does not depend on location. Amber Lan works with Australian businesses remotely, schedules calls across the two time zones and follows Australian rules on spam and privacy."),
                ("Who offers AI marketing services in Australia?", "Australian businesses can choose from AI-native agencies, established agencies adding AI, automation consultancies, AI search specialists and build-and-handover practices. Amber Lan's guide to Australian providers lists them by type from their own public pages, with Amber Lan disclosed as the publisher."),
                ("Do you work with businesses in Sydney and Melbourne?", "Yes, and anywhere else in Australia. Every build runs remotely, so a business in Brisbane, Perth or regional Australia gets the same process as one in Sydney or Melbourne."),
                ("Does outbound follow Australian spam law?", "Yes. Every commercial message the outbound agent drafts must meet the Spam Act 2003: consent, clear identification of the sender and a working unsubscribe. A person on your team approves the first message to every new contact."),
                ("Do you charge in Australian dollars?", "The currency is agreed in the written scope for each build, alongside the price. For Australian market context, Amber Lan's cost guides set out sourced ranges for agencies, freelancers and hires."),
                ("How do I start?", "Share a few lines about your business and the marketing gap you most want to close. Amber replies personally, and together you shape a written scope as the first step."),
            ],
        ),
        zh=dict(
            title="澳大利亚 AI 营销服务 | Amber Lan，AI 营销工程师",
            description="AI 营销工程师 Amber Lan 面向悉尼、墨尔本、布里斯班等地澳大利亚企业的 AI 营销服务：搜索、内容、主动外联和报告的 AI 智能体。",
            eyebrow="AI 营销服务 · 澳大利亚",
            h1="面向澳大利亚企业的 AI 营销服务。",
            answer="Amber Lan 从奥克兰远程为澳大利亚企业提供 AI 营销服务。AI 营销工程师 Amber Lan 和你的团队一起搭建负责搜索、内容、主动外联和报告的 AI 智能体，遵守《2003 年垃圾邮件法》和澳大利亚隐私原则，然后交接给你。",
            lead="为你在澳大利亚的业务搭建每周都在运转的营销，从悉尼、墨尔本到你的客户所在的任何地方。",
            local=("按澳大利亚买家的习惯来搭建。", "每个澳大利亚项目都从当地规则和买家的搜索习惯出发。", [
                ("远程合作", "项目在你自己的账号上搭建，简短的通话时间兼顾两地时区。奥克兰比澳大利亚东海岸早两到三小时。"),
                ("搜索", '搜索智能体覆盖 Google、Bing，以及买家打电话之前会读到的 AI 回答，从悉尼、墨尔本到澳大利亚各地。<a class="text-link" href="/blog/what-is-answer-engine-optimisation">什么是答案引擎优化</a>。'),
                ("邮件", '主动外联遵守《2003 年垃圾邮件法》：取得同意、清楚表明身份，每封商业邮件都能退订。<a class="text-link" href="/blog/outbound-sales-automation">规范的主动外联</a>。'),
                ("隐私", '智能体只读取范围说明允许的数据，符合澳大利亚隐私原则。<a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI 营销与隐私法</a>。'),
                ("费用", '想了解澳大利亚的市场价格，可以读<a class="text-link" href="/blog/marketing-agency-cost-australia">澳大利亚营销代理机构的费用</a>。'),
                ("报价", "书面范围确定后，按项目报价。"),
            ]),
            places=[("新西兰", "/ai-marketing-services/new-zealand", "适合同时在新西兰做生意的企业。"),
                    ("全部服务", "/ai-marketing-services/", "完整的智能体团队，一页看全。")],
            guides=None,
            faq=[
                ("新西兰的服务商能为澳大利亚提供 AI 营销服务吗？", "可以。智能体建在你自己的账号和工具上，工作不受地点限制。Amber Lan 远程服务澳大利亚企业，通话时间兼顾两地时区，并遵守澳大利亚的垃圾邮件和隐私规则。"),
                ("澳大利亚有哪些 AI 营销服务商？", "澳大利亚企业可以选择 AI 原生代理机构、增加了 AI 服务的老牌代理机构、自动化咨询公司、AI 搜索专家，以及搭建后交接的工作室。Amber Lan 的澳大利亚服务商指南按类型列出，依据各家自己的公开页面，并注明 Amber Lan 是发布方。"),
                ("你们和悉尼、墨尔本的企业合作吗？", "合作，澳大利亚其他地方也一样。所有项目都远程进行，布里斯班、珀斯或澳大利亚地区的企业，和悉尼、墨尔本的企业走同样的流程。"),
                ("主动外联遵守澳大利亚的垃圾邮件法吗？", "遵守。外联智能体起草的每一封商业邮件都必须符合《2003 年垃圾邮件法》：取得同意、清楚表明发件人身份、能正常退订。每个新联系人的第一封邮件，都由你团队里的人批准。"),
                ("你们用澳元收费吗？", "币种和价格一起在每个项目的书面范围里约定。想了解澳大利亚的市场行情，Amber Lan 的费用指南整理了代理机构、自由职业者和招聘的有出处的价格区间。"),
                ("怎么开始？", "简单介绍你的业务，以及你最想补上的营销缺口。Amber 会亲自回复，第一步是你们一起确定一份书面范围说明。"),
            ],
        ),
    ),
    dict(
        slug="auckland", area=[AKL],
        en=dict(
            title="AI Marketing Services Auckland | Amber Lan, AI Marketing Engineer",
            description="AI marketing services in Auckland: meet Amber Lan, an AI marketing engineer, in person and build the AI agents that run your search, content, outbound and reporting.",
            eyebrow="AI marketing services · Auckland",
            h1="AI marketing services in Auckland.",
            answer="Amber Lan is an Auckland practice providing AI marketing services to Auckland businesses. Amber Lan, an AI marketing engineer based in Auckland, meets your team in person, then builds the AI agents that run search, content, outbound and reporting with you and hands them over.",
            lead="Let's sit down together in Auckland and build marketing that runs every week on systems your team owns.",
            local=("Local, in person, built together.", "Working in the same city makes the build faster and the handover stronger.", [
                ("In person", "The scoping workshop and the handover can happen at your office anywhere in Auckland, from the CBD and Ponsonby to the North Shore, East Auckland and South Auckland."),
                ("Google Maps", 'The search agent starts with your Google Business Profile: categories, service areas, photos and a steady flow of genuine reviews. <a class="text-link" href="/blog/get-recommended-by-chatgpt-auckland">How Auckland businesses get recommended</a>.'),
                ("Local AI search", "When someone asks ChatGPT for the best provider in Auckland, it draws on the open web, maps data and reviews. The agent makes sure your business shows up accurately in all three."),
                ("Same time zone", "Your team and the person building the agents share the same working day, so reviews come back within hours."),
                ("Building in public", 'Amber shares her working notes and open-source systems as she builds. <a class="text-link" href="/about">Meet Amber</a>.'),
                ("Pricing", "Quoted in NZD, plus GST, once the written scope is agreed."),
            ]),
            places=[("New Zealand", "/ai-marketing-services/new-zealand", "The same service for the rest of New Zealand."),
                    ("Australia", "/ai-marketing-services/australia", "For businesses that also sell across the Tasman.")],
            guides=["get-recommended-by-chatgpt-auckland", "seo-for-small-business-nz", "ai-marketing-providers-new-zealand", "how-to-get-mentioned-by-chatgpt", "first-month-of-an-ai-marketing-build", "content-marketing-small-business-nz"],
            faq=[
                ("Can we meet in person in Auckland?", "Yes. Amber Lan is based in Auckland, so the scoping workshop and the handover can happen at your office. The build itself runs on your own accounts between sessions, with your team reviewing as it goes."),
                ("What are the top AI marketing services in Auckland?", "The right choice depends on the work you most want done, since Auckland has no independent ranking yet. Based in Auckland you will find Growin in Glenfield, an AI-native agency; established agencies that added AI, including Kiwi Web Design in Grey Lynn, LocaliQ NZ in the CBD, Net Branding and NiKa Consulting; AI search specialists Pead and The Optimisers; and Amber Lan, where an AI marketing engineer builds the agents with your team and hands them over. Amber Lan's guide to New Zealand providers describes each one from its own public pages, with Amber Lan disclosed as the publisher."),
                ("Can you help my Auckland business show up on Google Maps?", "Yes. The search agent sets up and maintains your Google Business Profile, keeps your business details consistent across the web and builds a steady process for asking customers for genuine reviews. Google ranks local results on relevance, distance and prominence."),
                ("How do I get my Auckland business recommended by ChatGPT?", "Make your business easy to find and confirm: clear service pages, consistent details on your site and directories, recent genuine reviews, and mentions on sites the assistants already trust. Amber Lan's guide for Auckland businesses walks through it step by step."),
                ("Do you work with businesses outside Auckland?", "Yes, across New Zealand and Australia. Auckland businesses can meet in person, and everywhere else the same service runs remotely on your own accounts."),
                ("How do I start?", "Share a few lines through the contact form. Amber replies personally, often with an invitation to meet in Auckland, and together you shape a written scope as the first step."),
            ],
        ),
        zh=dict(
            title="奥克兰 AI 营销服务 | Amber Lan，AI 营销工程师",
            description="奥克兰的 AI 营销服务：和 AI 营销工程师 Amber Lan 当面沟通，一起搭建负责搜索、内容、主动外联和报告的 AI 智能体。",
            eyebrow="AI 营销服务 · 奥克兰",
            h1="奥克兰的 AI 营销服务。",
            answer="Amber Lan 是一家奥克兰的工作室，为奥克兰企业提供 AI 营销服务。常驻奥克兰的 AI 营销工程师 Amber Lan 会和你的团队当面沟通，然后一起搭建负责搜索、内容、主动外联和报告的 AI 智能体，并交接给你。",
            lead="在奥克兰坐下来一起聊，搭建每周都在运转的营销，系统归你的团队所有。",
            local=("本地，见面，一起搭建。", "同在一个城市，搭建更快，交接也更扎实。", [
                ("当面合作", "范围工作坊和交接可以在你的办公室进行，奥克兰市中心、Ponsonby、北岸、东区、南区都可以。"),
                ("Google 地图", '搜索智能体从 Google 商家资料做起：类别、服务区域、照片，以及持续收集的真实评价。<a class="text-link" href="/blog/get-recommended-by-chatgpt-auckland">奥克兰企业如何被推荐</a>。'),
                ("本地 AI 搜索", "有人问 ChatGPT 奥克兰最好的服务商是谁时，它会参考公开网页、地图数据和评价。智能体确保你的业务在这三处都准确出现。"),
                ("同一时区", "你的团队和搭建智能体的人共享同一个工作日，审核几小时内就能往返。"),
                ("公开搭建", 'Amber 在搭建过程中公开分享工作笔记和开源系统。<a class="text-link" href="/about">认识 Amber</a>。'),
                ("报价", "书面范围确定后，以新西兰元报价，另加 GST。"),
            ]),
            places=[("新西兰", "/ai-marketing-services/new-zealand", "新西兰其他地区，同样的服务。"),
                    ("澳大利亚", "/ai-marketing-services/australia", "适合同时在塔斯曼海对岸做生意的企业。")],
            guides=None,
            faq=[
                ("可以在奥克兰见面吗？", "可以。Amber Lan 就在奥克兰，范围工作坊和交接都可以在你的办公室进行。两次见面之间，搭建在你自己的账号上进行，你的团队边做边审核。"),
                ("奥克兰有哪些好的 AI 营销服务？", "合适的选择取决于你最想补上的营销短板，因为奥克兰目前还没有独立排名。总部在奥克兰的服务商包括：Glenfield 的 AI 原生代理机构 Growin；增加了 AI 服务的老牌代理机构，如 Grey Lynn 的 Kiwi Web Design、市中心的 LocaliQ NZ、Net Branding 和 NiKa Consulting；AI 搜索专家 Pead 和 The Optimisers；以及 Amber Lan，由一位 AI 营销工程师和你的团队一起搭建智能体，再交给你们。Amber Lan 的新西兰服务商指南依据各家自己的公开页面逐一介绍，并注明 Amber Lan 是发布方。"),
                ("能帮我的奥克兰企业出现在 Google 地图上吗？", "可以。搜索智能体负责设置和维护你的 Google 商家资料，保持你的业务信息在各处一致，并建立一套持续邀请客户留下真实评价的流程。Google 按相关性、距离和知名度对本地结果排名。"),
                ("怎样让 ChatGPT 推荐我的奥克兰企业？", "让你的业务容易被找到、也容易被确认：清楚的服务页面、网站和目录上一致的信息、近期的真实评价，以及 AI 助手本来就信任的网站上的提及。Amber Lan 写给奥克兰企业的指南逐步讲解。"),
                ("你们和奥克兰以外的企业合作吗？", "合作，覆盖新西兰和澳大利亚。奥克兰的企业可以见面合作，其他地方同样的服务在你自己的账号上远程进行。"),
                ("怎么开始？", "通过联系表单简单留言。Amber 会亲自回复，常常会邀请你在奥克兰见一面，第一步是你们一起确定一份书面范围说明。"),
            ],
        ),
    ),
]

# Service pages by the job a buyer needs done (added 2026-10-16 from the hire-intent keyword gap).
# Each one lists the other three under "Guides to help you choose well", and the hub and place pages list all four.
SERVICE_PAGES = {
    "en": [
        ("AI automation consultant", "/ai-marketing-services/ai-automation-consultant", "Turn the marketing and sales work your team repeats into AI workflows."),
        ("AI agent development", "/ai-marketing-services/ai-agent-development", "Custom AI agents for marketing and sales, built on your accounts."),
        ("Marketing automation consultant", "/ai-marketing-services/marketing-automation-consultant", "HubSpot and CRM workflows, follow-up and reporting, automated with AI."),
        ("Claude Code consultant", "/ai-marketing-services/claude-code-consultant", "A Claude Code setup for your marketing team, with skills and review gates."),
    ],
    "zh": [
        ("AI 自动化顾问", "/ai-marketing-services/ai-automation-consultant", "把团队每周重复的营销和销售工作，变成 AI 工作流。"),
        ("AI 智能体开发", "/ai-marketing-services/ai-agent-development", "为营销和销售定制 AI 智能体，建在你自己的账号上。"),
        ("营销自动化顾问", "/ai-marketing-services/marketing-automation-consultant", "HubSpot 和 CRM 工作流、跟进和报告，用 AI 自动化。"),
        ("Claude Code 顾问", "/ai-marketing-services/claude-code-consultant", "为你的营销团队搭建 Claude Code，配好技能库和审核关口。"),
    ],
}


def _others(lang, slug):
    return [x for x in SERVICE_PAGES[lang] if not x[1].endswith("/" + slug)]


ALSO = {lang: {s: SERVICE_PAGES[lang] for s in ("", "new-zealand", "australia", "auckland")} for lang in ("en", "zh")}

HUB_PLACES = {
    "en": [("Auckland", "/ai-marketing-services/auckland", "Meet in person and run the build workshop on site."),
           ("New Zealand", "/ai-marketing-services/new-zealand", "Privacy Act 2020, spam law and what Kiwi buyers search.")],
    "zh": [("奥克兰", "/ai-marketing-services/auckland", "可以见面，在你的办公室开搭建工作坊。"),
           ("新西兰", "/ai-marketing-services/new-zealand", "《2020 年隐私法》、垃圾邮件法，以及新西兰买家怎么搜索。")],
}

PAGES += [
    dict(
        slug="ai-automation-consultant", area=[AKL, NZ, AU], updated="2026-10-16",
        en=dict(
            title="AI Automation Consultant in Auckland, NZ | Amber Lan",
            description="Amber Lan, AI automation consultant and marketing engineer in Auckland: map repetitive marketing and sales work, automate it with agents your team approves.",
            eyebrow="AI automation consulting · Auckland and New Zealand",
            h1="AI automation consultant in Auckland.",
            service_type="AI automation consulting",
            answer="Amber Lan is an AI automation consultant and AI marketing engineer in Auckland. She maps the marketing and sales tasks that take your team hours each week, automates them with AI agents and tools such as HubSpot, n8n and Zapier, and hands every workflow over with documentation.",
            lead="Let's turn the work your team repeats every week into AI workflows your people review and keep.",
            services_eyebrow="Where we start", services_h2="What we automate first.",
            services_lead="Together we begin with the task that costs the most hours, then add the next once the first runs well.",
            services_link="Explore what we automate",
            services=[
                ("Lead follow-up", "New enquiries researched, routed to the right person and answered with a first draft for approval.", "/sprints/outbound"),
                ("Content production", "Briefs to drafts to scheduled posts in your voice, with your team signing off.", "/sprints/content-engine"),
                ("CRM upkeep", "Records enriched, duplicates flagged and pipeline stages kept current in the CRM you already use.", "/sprints/outbound"),
                ("Outbound research", "The right accounts found and researched before anyone writes a message.", "/sprints/outbound"),
                ("AI search upkeep", "Service pages, schema and business details kept accurate for Google and AI assistants.", "/sprints/ai-search"),
                ("Reporting", "One weekly read on what moved, pulled from your analytics and CRM.", "/sprints/analytics"),
            ],
            local=("Built on the tools you already run.", "Every automation lives in your accounts, documented so your team can change it.", [
                ("Your stack", 'HubSpot, n8n, Zapier, Google Analytics and Claude Code are part of the everyday working stack. <a class="text-link" href="/about">Meet Amber</a>.'),
                ("Review points", "The written scope names where a person approves, so every message to a customer is checked first."),
                ("Privacy", 'Each workflow reads only the data the scope allows, in line with the Privacy Act 2020. <a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI marketing and privacy law</a>.'),
                ("In person", "Auckland teams can run the mapping workshop at their office, and everywhere else it runs on a call."),
                ("Choosing well", '<a class="text-link" href="/blog/ai-agency-vs-ai-consultant-nz">AI agency, AI automation agency or AI consultant</a> compares the options side by side.'),
                ("Pricing", "Quoted in NZD, plus GST, once the written scope is agreed."),
            ]),
            places=HUB_PLACES["en"],
            guides=["ai-agency-vs-ai-consultant-nz", "ai-consultant-rates-nz-australia", "ai-agent-development-cost-nz", "ai-marketing-automation-small-business", "ai-marketing-scope-of-work", "first-month-of-an-ai-marketing-build"],
            also=_others("en", "ai-automation-consultant"),
            faq=[
                ("What does an AI automation consultant do?", "An AI automation consultant finds the repetitive work in a business, decides which parts AI can draft or move safely, and builds the workflows that do it, with a person approving anything that reaches a customer. For Amber Lan that work centres on marketing and sales: enquiries, content, CRM upkeep, outbound research and reporting."),
                ("Is Amber Lan an AI automation agency?", "Amber Lan does the work people look for when they search for an AI automation agency in Auckland. The model is a partnership. One engineer maps the work with your team, builds the automations on your accounts and hands them over with documentation, so the workflows stay in your business."),
                ("Which tools do you build with?", "Usually the ones you already pay for. The working stack includes HubSpot, n8n, Zapier, Google Analytics, Google Tag Manager and Claude Code with MCP connectors. The written scope names each tool, what it may read and who owns the account."),
                ("How much does an AI automation consultant cost in NZ?", "Amber Lan prices each build per project, in NZD plus GST, once the written scope is agreed. For market context, Amber Lan's guides to AI consultant rates and AI agent development costs set out sourced ranges for New Zealand and Australia."),
                ("Can we meet in person in Auckland?", "Yes. Amber Lan is based in Auckland, so the mapping workshop and the handover can happen at your office. Between sessions the build runs on your own accounts, and your team reviews as it goes."),
                ("How do I start?", "Share a few lines about the work that takes your team the most hours each week. Amber replies personally, and together you shape a written scope as the first step."),
            ],
        ),
        zh=dict(
            title="奥克兰 AI 自动化顾问 | Amber Lan",
            description="奥克兰的 AI 自动化顾问与营销工程师 Amber Lan：梳理重复的营销和销售工作，用团队审核的 AI 智能体自动化，每个工作流都归你所有。",
            eyebrow="AI 自动化咨询 · 奥克兰和新西兰",
            h1="奥克兰的 AI 自动化顾问。",
            service_type="AI 自动化咨询",
            answer="Amber Lan 是奥克兰的 AI 自动化顾问和 AI 营销工程师。她通过 Amber Lan 梳理团队每周花大量时间的营销和销售任务，用 AI 智能体以及 HubSpot、n8n、Zapier 等工具把它们自动化，再附上文档，把每个工作流交接给你。",
            lead="一起把团队每周重复的工作，变成由你的人审核、长期拥有的 AI 工作流。",
            services_eyebrow="从哪里开始", services_h2="先自动化什么。",
            services_lead="我们一起从最花时间的任务开始，第一个运行稳定后，再加下一个。",
            services_link="看看我们自动化什么",
            services=[
                ("线索跟进", "新的咨询先做背景研究，分给合适的人，并起草第一封回复供审核。", "/sprints/outbound"),
                ("内容生产", "从简报到稿件再到排期发布，用你的语调写成，由团队签字确认。", "/sprints/content-engine"),
                ("CRM 维护", "在你已经在用的 CRM 里补全记录、标出重复、保持销售阶段准确。", "/sprints/outbound"),
                ("外联研究", "在任何人写消息之前，先找准目标客户并做好研究。", "/sprints/outbound"),
                ("AI 搜索维护", "服务页面、结构化数据和商家信息保持准确，方便 Google 和 AI 助手读取。", "/sprints/ai-search"),
                ("报告", "每周一份简报，汇总分析工具和 CRM 里的变化。", "/sprints/analytics"),
            ],
            local=("建在你已经在用的工具上。", "每个自动化都在你的账号里，附有文档，团队可以自己修改。", [
                ("工具栈", 'HubSpot、n8n、Zapier、Google Analytics 和 Claude Code 都是日常使用的工具。<a class="text-link" href="/about">认识 Amber</a>。'),
                ("审核环节", "书面范围写清楚由谁批准，每条发给客户的消息都先经过检查。"),
                ("隐私", '每个工作流只读取范围允许的数据，符合《2020 年隐私法》。<a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI 营销与隐私法</a>。'),
                ("当面合作", "奥克兰的团队可以在办公室开梳理工作坊，其他地方通过线上通话进行。"),
                ("如何选择", '<a class="text-link" href="/blog/ai-agency-vs-ai-consultant-nz">AI 代理机构、AI 自动化代理机构还是 AI 顾问</a>，逐项对比。'),
                ("报价", "书面范围确定后，以新西兰元报价，另加 GST。"),
            ]),
            places=HUB_PLACES["zh"],
            guides=None,
            also=_others("zh", "ai-automation-consultant"),
            faq=[
                ("AI 自动化顾问做什么？", "AI 自动化顾问找出企业里重复的工作，判断哪些部分可以安全地交给 AI 起草或流转，再搭建完成这些工作的工作流，任何触达客户的内容都由人批准。在 Amber Lan，这些工作集中在营销和销售：咨询、内容、CRM 维护、外联研究和报告。"),
                ("Amber Lan 是 AI 自动化代理机构吗？", "人们在奥克兰搜索 AI 自动化代理机构时想要的工作，Amber Lan 都做。合作模式是伙伴关系：一位工程师和你的团队一起梳理工作，在你的账号上搭建自动化，写好文档后交接，工作流长期留在你的公司里。"),
                ("你们用什么工具搭建？", "通常就是你已经在付费使用的工具。日常工具栈包括 HubSpot、n8n、Zapier、Google Analytics、Google 跟踪代码管理器，以及配有 MCP 连接器的 Claude Code。书面范围会写明每个工具、它能读取什么，以及账号归谁。"),
                ("在新西兰请 AI 自动化顾问要花多少钱？", "Amber Lan 在书面范围确定后按项目报价，以新西兰元计，另加 GST。想了解市场行情，Amber Lan 关于 AI 顾问费率和 AI 智能体开发成本的指南，整理了新西兰和澳大利亚有出处的价格区间。"),
                ("可以在奥克兰见面吗？", "可以。Amber Lan 就在奥克兰，梳理工作坊和交接都可以在你的办公室进行。两次见面之间，搭建在你自己的账号上进行，你的团队边做边审核。"),
                ("怎么开始？", "简单介绍团队每周最花时间的工作。Amber 会亲自回复，第一步是你们一起确定一份书面范围说明。"),
            ],
        ),
    ),
    dict(
        slug="ai-agent-development", area=[NZ, AU], updated="2026-10-16",
        en=dict(
            title="AI Agent Development for NZ and Australian Teams | Amber Lan",
            description="Custom AI agent development for NZ and Australian teams by Amber Lan, an AI marketing engineer: marketing and sales agents built on your accounts, yours to keep.",
            eyebrow="AI agent development · New Zealand and Australia",
            h1="AI agent development for marketing and sales teams.",
            service_type="AI agent development",
            answer="Amber Lan develops custom AI agents for New Zealand and Australian businesses. Amber Lan, an AI marketing engineer and AI agent developer in Auckland, builds agents for search, content, outbound and reporting on your own accounts, with a named person approving their work, then hands every agent, prompt and file to your team.",
            lead="Let's design the agents your team will rely on, and build them so your people can run and extend them.",
            services_eyebrow="Agents we build", services_h2="Agents we can build together.",
            services_lead="Each agent has one job, clear inputs and a person on your team who approves its output.",
            services_link="Explore the agents",
            services=[
                ("Search agent", "Technical SEO through to answer engine optimisation, so Google ranks you and AI assistants cite you.", "/sprints/ai-search"),
                ("Content agent", "A month of drafts in your voice, approved by your team before anything ships.", "/sprints/content-engine"),
                ("Outbound agent", "The right accounts researched, with first messages drafted for a person to send.", "/sprints/outbound"),
                ("Measurement agent", "Tracking wired properly, so every enquiry traces to a source.", "/sprints/analytics"),
                ("Reporting agent", "One short weekly read on what shipped and what comes next.", "/sprints/analytics"),
                ("Custom agent", "An agent for a job specific to your business, scoped from the hours it gives back.", "/contact"),
            ],
            local=("How each agent is built.", "The same engineering standard on every agent, whatever its job.", [
                ("Written brief", "Each agent starts from a brief: its job, the data it may read, the tools it may use and where a person reviews."),
                ("Review points", "A named person on your team approves anything an agent sends to a customer, and the scope records who reviews what."),
                ("Your accounts", "Agents run on your accounts and connectors, so your business controls every login and can end access at any time."),
                ("Open method", 'The skills behind the agents are public. <a class="text-link" href="/skills/">Explore 126 open-source skills</a>.'),
                ("Hiring well", '<a class="text-link" href="/blog/how-to-hire-an-ai-agent-developer">How to hire an AI agent developer</a> lists the questions to ask any provider.'),
                ("Pricing", "Quoted per project once the written scope is agreed."),
            ]),
            places=HUB_PLACES["en"],
            guides=["ai-agent-development-cost-nz", "how-to-hire-an-ai-agent-developer", "ai-agents-for-marketing", "what-is-an-ai-marketing-agent", "ai-marketing-scope-of-work", "ai-marketing-privacy-law-nz-australia"],
            also=_others("en", "ai-agent-development"),
            faq=[
                ("What is an AI agent developer?", "An AI agent developer designs and builds software agents that use a language model to carry out a job, such as researching accounts or drafting content, with access to specific tools and data. The work covers the brief, data access, guardrails, review points, monitoring and documentation as well as the prompts."),
                ("What kind of AI agents does Amber Lan build?", "Agents for marketing and sales work: AI search and SEO, content drafting in your voice, outbound research and first drafts, measurement and weekly reporting. Each agent has one job and a named reviewer on your team, and custom agents are scoped from the hours they give back."),
                ("Who owns the agents after the build?", "You do. Every agent, prompt, workflow and document is built on your accounts and handed over with written instructions, so your team can run, change or extend the system without Amber Lan."),
                ("How much does AI agent development cost?", "Amber Lan prices each build per project once the written scope is agreed. Amber Lan's guide to AI agent development costs in New Zealand breaks the cost into sourced parts: people time, model usage, platform subscriptions and ongoing upkeep."),
                ("Do you work with businesses in Australia?", "Yes. Amber Lan is based in Auckland and works with businesses across New Zealand and Australia. Builds run remotely on your own accounts, with calls scheduled across the two time zones, and Australian work follows the Spam Act 2003 and the Australian Privacy Principles."),
                ("How do I start?", "Share the job you would most like an agent to take on. Amber replies personally, and together you shape a written scope as the first step."),
            ],
        ),
        zh=dict(
            title="面向新西兰和澳大利亚团队的 AI 智能体开发 | Amber Lan",
            description="AI 营销工程师 Amber Lan 为新西兰和澳大利亚团队定制 AI 智能体：营销和销售智能体建在你的账号上，配有审核环节和文档，完全归你所有。",
            eyebrow="AI 智能体开发 · 新西兰和澳大利亚",
            h1="为营销和销售团队开发 AI 智能体。",
            service_type="AI 智能体开发",
            answer="Amber Lan 为新西兰和澳大利亚的企业开发定制 AI 智能体。奥克兰的 AI 营销工程师和 AI 智能体开发者 Amber Lan，在你自己的账号上搭建负责搜索、内容、主动外联和报告的智能体，由一位指定的人审核它们的工作，然后把每个智能体、提示词和文件交给你的团队。",
            lead="一起设计团队会长期依赖的智能体，并让你的人能够自己运行和扩展。",
            services_eyebrow="我们搭建的智能体", services_h2="可以一起搭建的智能体。",
            services_lead="每个智能体只做一件事，输入清楚，并由你团队里的一个人审核产出。",
            services_link="看看有哪些智能体",
            services=[
                ("搜索智能体", "从技术 SEO 到答案引擎优化，让 Google 给你排名，也让 AI 助手引用你。", "/sprints/ai-search"),
                ("内容智能体", "一个月的稿件，用你的语调写成，团队审核通过后才发布。", "/sprints/content-engine"),
                ("外联智能体", "研究目标客户，起草第一条消息，由人来发送。", "/sprints/outbound"),
                ("效果衡量智能体", "把追踪接好，每一条咨询都能追溯到来源。", "/sprints/analytics"),
                ("报告智能体", "每周一份简短报告：做了什么，下一步做什么。", "/sprints/analytics"),
                ("定制智能体", "为你的业务专门做一件事的智能体，按它能省下的时间来确定范围。", "/contact"),
            ],
            local=("每个智能体怎样搭建。", "不管负责什么，每个智能体都按同样的工程标准搭建。", [
                ("书面简报", "每个智能体都从一份简报开始：它的任务、能读取的数据、能用的工具，以及由谁审核。"),
                ("审核环节", "智能体发给客户的任何内容，都由你团队里一位指定的人批准，范围说明里写清楚谁审核什么。"),
                ("你的账号", "智能体运行在你的账号和连接器上，每个登录都由你的公司掌控，随时可以收回权限。"),
                ("公开方法", '智能体背后的技能都是公开的。<a class="text-link" href="/skills/">浏览 126 个开源技能</a>。'),
                ("如何招人", '<a class="text-link" href="/blog/how-to-hire-an-ai-agent-developer">如何聘请 AI 智能体开发者</a>，列出了该问任何服务商的问题。'),
                ("报价", "书面范围确定后，按项目报价。"),
            ]),
            places=HUB_PLACES["zh"],
            guides=None,
            also=_others("zh", "ai-agent-development"),
            faq=[
                ("什么是 AI 智能体开发者？", "AI 智能体开发者设计并搭建软件智能体，让它们借助大语言模型完成一项工作，例如研究目标客户或起草内容，并只接入指定的工具和数据。工作内容除了提示词，还包括简报、数据权限、防护规则、审核环节、监控和文档。"),
                ("Amber Lan 搭建哪些 AI 智能体？", "负责营销和销售工作的智能体：AI 搜索和 SEO、用你的语调起草内容、外联研究和初稿、效果衡量和每周报告。每个智能体只做一件事，由你团队里的指定人员审核；定制智能体按它能省下的时间来确定范围。"),
                ("搭建完成后，智能体归谁？", "归你。每个智能体、提示词、工作流和文档都建在你的账号上，并附书面说明交接，你的团队可以自己运行、修改或扩展，不需要依赖 Amber Lan。"),
                ("AI 智能体开发要花多少钱？", "Amber Lan 在书面范围确定后按项目报价。Amber Lan 关于新西兰 AI 智能体开发成本的指南，把成本拆成有出处的几部分：人工时间、模型用量、平台订阅和后续维护。"),
                ("你们和澳大利亚的企业合作吗？", "合作。Amber Lan 位于奥克兰，服务新西兰和澳大利亚两地的企业。项目远程进行，在你自己的账号上搭建，通话时间兼顾两地时区。澳大利亚的项目遵守《2003 年垃圾邮件法》和澳大利亚隐私原则。"),
                ("怎么开始？", "说说你最想交给智能体的那项工作。Amber 会亲自回复，第一步是你们一起确定一份书面范围说明。"),
            ],
        ),
    ),
    dict(
        slug="marketing-automation-consultant", area=[NZ, AU], updated="2026-10-16",
        en=dict(
            title="Marketing Automation Consultant NZ | Amber Lan, Auckland",
            description="Amber Lan, marketing automation consultant in NZ: HubSpot and CRM workflows, lead follow-up and reporting automated with AI, built with your team and handed over.",
            eyebrow="Marketing automation · New Zealand and Australia",
            h1="Marketing automation consultant in New Zealand.",
            service_type="Marketing automation consulting",
            answer="Amber Lan is a marketing automation practice in Auckland for New Zealand and Australian businesses. Amber Lan, an AI marketing engineer who has architected HubSpot from scratch, builds the workflows that follow up leads, keep the CRM current, produce content and report results, with AI agents drafting and your team approving.",
            lead="Let's connect your CRM, email and content into one system your team trusts and keeps improving.",
            services_eyebrow="What the system covers", services_h2="What we automate together.",
            services_lead="We map the whole lead journey, then connect each workflow until the system runs end to end.",
            services_link="Explore what we automate",
            services=[
                ("Lead capture and routing", "Forms and enquiries tracked into the CRM with their source, and routed to the right owner.", "/sprints/analytics"),
                ("Follow-up sequences", "Consent-based emails and tasks, with AI drafting and a person approving.", "/sprints/outbound"),
                ("CRM upkeep", "Enrichment, duplicate checks and pipeline stages kept current.", "/sprints/outbound"),
                ("Content workflows", "Brief to draft to publish, in your voice, across your channels.", "/sprints/content-engine"),
                ("Attribution", "Every enquiry traced to its source, so spend follows results.", "/sprints/analytics"),
                ("Reporting", "One short weekly read from your CRM and analytics.", "/sprints/analytics"),
            ],
            local=("Built on the platforms you already use.", "Automations live in your accounts and follow New Zealand and Australian rules.", [
                ("HubSpot and CRM", "HubSpot, Apollo and HeyReach are part of the everyday stack, with n8n and Zapier connecting the rest of your tools."),
                ("Email law", "Every sequence follows the Unsolicited Electronic Messages Act 2007 in New Zealand and the Spam Act 2003 in Australia: consent, clear identification and a working unsubscribe."),
                ("Privacy", 'Workflows read only the data the scope allows, in line with the Privacy Act 2020. <a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI marketing and privacy law</a>.'),
                ("Tool choice", '<a class="text-link" href="/blog/n8n-vs-zapier-vs-make-vs-claude-code">n8n, Zapier, Make or Claude Code</a> compares the automation tools side by side.'),
                ("Where to start", '<a class="text-link" href="/blog/ai-marketing-automation-small-business">AI marketing automation for small business</a> sets out the six automations to run first.'),
                ("Pricing", "Quoted in NZD, plus GST, once the written scope is agreed."),
            ]),
            places=HUB_PLACES["en"],
            guides=["ai-marketing-automation-small-business", "n8n-vs-zapier-vs-make-vs-claude-code", "outbound-sales-automation", "ai-agency-vs-ai-consultant-nz", "ai-marketing-privacy-law-nz-australia", "ai-marketing-scope-of-work"],
            also=_others("en", "marketing-automation-consultant"),
            faq=[
                ("What does a marketing automation consultant do?", "A marketing automation consultant designs and builds the workflows that move leads and content through a business without manual handling: capturing enquiries, routing them, sending consent-based follow-up, keeping the CRM current and reporting results. With AI added, agents draft the messages and summaries while people approve what reaches customers."),
                ("Do you work with HubSpot?", "Yes. Amber has architected HubSpot from scratch and works with it alongside Apollo, HeyReach, n8n and Zapier. If your business runs a different CRM, the written scope sets out how the workflows connect to it before the build begins."),
                ("Marketing automation or AI agents: which do I need?", "Most teams benefit from both. Automation moves data and triggers steps on a schedule, and AI agents handle the drafting and research inside those steps. The build starts with the simplest automation that closes the gap, and adds an agent where drafting or research takes the most time."),
                ("Does the automation follow NZ spam law?", "Yes. Every commercial email follows the Unsolicited Electronic Messages Act 2007: consent, clear identification of the sender and a working unsubscribe. Australian contacts follow the Spam Act 2003. A person on your team approves the first message to every new contact."),
                ("How much does marketing automation consulting cost?", "Amber Lan prices each build per project, in NZD plus GST, once the written scope is agreed. Platform subscriptions are paid directly by your business, and Amber Lan's tool comparison sets out what n8n, Zapier and Make charge."),
                ("How do I start?", "Share a few lines about where leads or content slow down in your business. Amber replies personally, and together you shape a written scope as the first step."),
            ],
        ),
        zh=dict(
            title="新西兰营销自动化顾问 | Amber Lan，AI 营销工程师",
            description="新西兰的营销自动化顾问 Amber Lan：HubSpot 和 CRM 工作流、线索跟进和报告，用 AI 自动化，与你的团队一起搭建并交接。",
            eyebrow="营销自动化 · 新西兰和澳大利亚",
            h1="新西兰的营销自动化顾问。",
            service_type="营销自动化咨询",
            answer="Amber Lan 是一家奥克兰的营销自动化工作室，服务新西兰和澳大利亚的企业。曾从零搭建 HubSpot 架构的 AI 营销工程师 Amber Lan，负责搭建跟进线索、维护 CRM、生产内容和报告结果的工作流，由 AI 智能体起草，你的团队批准。",
            lead="一起把你的 CRM、邮件和内容连成一套系统，让团队信得过，也能不断改进。",
            services_eyebrow="系统包括什么", services_h2="我们一起自动化的工作。",
            services_lead="我们先梳理完整的线索旅程，再把每个工作流接起来，直到整套系统端到端运转。",
            services_link="看看我们自动化什么",
            services=[
                ("线索获取与分配", "表单和咨询连同来源记录进 CRM，再分给合适的负责人。", "/sprints/analytics"),
                ("跟进序列", "基于同意的邮件和任务，由 AI 起草，人来批准。", "/sprints/outbound"),
                ("CRM 维护", "补全信息、检查重复、保持销售阶段准确。", "/sprints/outbound"),
                ("内容工作流", "从简报到稿件再到发布，用你的语调覆盖各个渠道。", "/sprints/content-engine"),
                ("归因", "每一条咨询都能追溯到来源，预算跟着效果走。", "/sprints/analytics"),
                ("报告", "每周一份来自 CRM 和分析工具的简短报告。", "/sprints/analytics"),
            ],
            local=("建在你已经在用的平台上。", "自动化都在你的账号里，遵守新西兰和澳大利亚的规则。", [
                ("HubSpot 和 CRM", "HubSpot、Apollo 和 HeyReach 都是日常使用的工具，n8n 和 Zapier 负责连接你的其他工具。"),
                ("邮件法规", "每个序列都遵守新西兰《2007 年未经请求电子信息法》和澳大利亚《2003 年垃圾邮件法》：取得同意、清楚表明身份、能正常退订。"),
                ("隐私", '工作流只读取范围允许的数据，符合《2020 年隐私法》。<a class="text-link" href="/blog/ai-marketing-privacy-law-nz-australia">AI 营销与隐私法</a>。'),
                ("工具选择", '<a class="text-link" href="/blog/n8n-vs-zapier-vs-make-vs-claude-code">n8n、Zapier、Make 还是 Claude Code</a>，逐项对比自动化工具。'),
                ("从哪里开始", '<a class="text-link" href="/blog/ai-marketing-automation-small-business">小企业的 AI 营销自动化</a>，列出最先要做的六个自动化。'),
                ("报价", "书面范围确定后，以新西兰元报价，另加 GST。"),
            ]),
            places=HUB_PLACES["zh"],
            guides=None,
            also=_others("zh", "marketing-automation-consultant"),
            faq=[
                ("营销自动化顾问做什么？", "营销自动化顾问设计并搭建工作流，让线索和内容在企业里流转，不用人工搬运：获取咨询、分配负责人、发送基于同意的跟进、保持 CRM 准确，以及报告结果。加入 AI 之后，智能体负责起草消息和摘要，人来批准触达客户的内容。"),
                ("你们用 HubSpot 吗？", "用。Amber 曾从零搭建 HubSpot 架构，日常和 Apollo、HeyReach、n8n、Zapier 一起使用。如果你的公司用的是其他 CRM，书面范围会在开工前写清楚工作流怎样接入。"),
                ("我需要营销自动化，还是 AI 智能体？", "大多数团队两者都用得上。自动化按计划搬运数据、触发步骤，AI 智能体负责这些步骤里的起草和研究。搭建先从能补上缺口的最简单自动化开始，再在起草或研究最花时间的地方加上智能体。"),
                ("自动化遵守新西兰的垃圾邮件法吗？", "遵守。每封商业邮件都符合《2007 年未经请求电子信息法》：取得同意、清楚表明发件人身份、能正常退订。澳大利亚的联系人遵守《2003 年垃圾邮件法》。每个新联系人的第一封邮件，都由你团队里的人批准。"),
                ("营销自动化咨询要花多少钱？", "Amber Lan 在书面范围确定后按项目报价，以新西兰元计，另加 GST。平台订阅费由你的公司直接支付，Amber Lan 的工具对比指南列出了 n8n、Zapier 和 Make 的收费。"),
                ("怎么开始？", "简单说说你的公司里，线索或内容在哪里卡住。Amber 会亲自回复，第一步是你们一起确定一份书面范围说明。"),
            ],
        ),
    ),
    dict(
        slug="claude-code-consultant", area=[NZ, AU], updated="2026-10-16",
        en=dict(
            title="Claude Code Consultant for Marketing Teams, NZ | Amber Lan",
            description="Amber Lan, Claude Code consultant in Auckland: Claude Code set up for your marketing team with skills, connectors and review gates, built on your accounts.",
            eyebrow="Claude Code consulting · New Zealand and Australia",
            h1="Claude Code consultant for marketing teams.",
            service_type="Claude Code consulting",
            answer="Amber Lan sets up Claude Code for marketing teams in New Zealand and Australia. Amber Lan, an AI marketing engineer in Auckland, runs a whole marketing function on Claude Code and builds the same structure with your team: instruction files for each area of work, a skills library, connectors to your tools and review gates, then hands it over.",
            lead="Let's give your team a Claude Code setup it trusts, shaped around the work you already do every week.",
            services_eyebrow="What the setup includes", services_h2="Every piece, built with your team.",
            services_lead="Each part is a file your team can read, change and keep.",
            services_link="Explore the setup",
            services=[
                ("Lane files", "One instruction file per area of work, so every session starts with the right context.", "/blog/running-marketing-on-claude-code"),
                ("Skills library", "Repeatable jobs written as skills your team runs on demand.", "/skills/"),
                ("Connectors", "MCP connectors to the tools you already use, with read and write access set in the scope.", "/blog/running-marketing-on-claude-code"),
                ("Review gates", "Checks for voice, facts and claims before anything ships.", "/sprints/"),
                ("Client separation", "For agencies, one workspace per client, so each client's data stays with its account.", "/blog/claude-code-for-marketing-agencies"),
                ("Team handover", "Working sessions with your people until they run and extend it with confidence.", "/sprints/"),
            ],
            local=("Built from a system in daily use.", "The setup comes from running a full marketing function on Claude Code every week.", [
                ("Working notes", '<a class="text-link" href="/blog/running-marketing-on-claude-code">How a whole marketing function runs on Claude Code</a>, written up in full.'),
                ("Open source", '<a class="text-link" href="/skills/">126 inspectable skills</a>, sixteen built by Amber Lan, every one linked to its source.'),
                ("Plans and seats", '<a class="text-link" href="/blog/claude-vs-chatgpt-business-cost-nz">Claude for business or ChatGPT Business</a> sets out what each costs a New Zealand team.'),
                ("Agencies", '<a class="text-link" href="/blog/claude-code-for-marketing-agencies">Claude Code for marketing agencies</a> covers what to build first.'),
                ("Hiring", 'Companies hiring a marketing engineer can <a class="text-link" href="/about#hire">talk to Amber about a role</a>.'),
                ("Pricing", "Quoted per project once the written scope is agreed."),
            ]),
            places=HUB_PLACES["en"],
            guides=["running-marketing-on-claude-code", "claude-code-for-marketing-agencies", "claude-vs-chatgpt-business-cost-nz", "n8n-vs-zapier-vs-make-vs-claude-code", "what-is-a-marketing-engineer", "ai-agents-for-marketing"],
            also=_others("en", "claude-code-consultant"),
            faq=[
                ("What does a Claude Code consultant do for a marketing team?", "A Claude Code consultant sets up Claude Code so a team can run repeatable marketing work through it safely: instruction files that hold context, skills for recurring jobs, connectors to the team's tools and review gates before anything ships. The consultant then works alongside the team until they run and extend it themselves."),
                ("Do we need to be technical to use Claude Code?", "Some comfort with files and a terminal helps. Skills and lane files are plain written instructions, so most of the system reads like a well-kept playbook, and the handover sessions cover the commands your team will use every day."),
                ("Is Claude Code a good fit for a marketing agency?", "It suits agencies with repeatable client work such as research, briefs, drafts, reporting and SEO or AEO audits. The key design choice is client separation: one workspace and one set of connectors per client, so each client's data stays with its account. Amber Lan's guide for agencies covers the first workflows to build."),
                ("Which Claude plan does our team need?", "That depends on team size and how heavily you use it, since Anthropic's plans differ in usage limits and admin controls. Amber Lan's guide comparing Claude for business and ChatGPT Business sets out current prices for a New Zealand team."),
                ("Who owns the setup?", "You do. Every lane file, skill and connector setting lives in your accounts and repository, documented so your team can change or extend it without Amber Lan."),
                ("How do I start?", "Share a few lines about the marketing work your team repeats most. Amber replies personally, and together you shape a written scope as the first step."),
            ],
        ),
        zh=dict(
            title="营销团队的 Claude Code 顾问，新西兰 | Amber Lan",
            description="奥克兰的 Claude Code 顾问 Amber Lan：为你的营销团队搭建 Claude Code，配好技能库、连接器和审核关口，建在你的账号上并交接给你。",
            eyebrow="Claude Code 咨询 · 新西兰和澳大利亚",
            h1="营销团队的 Claude Code 顾问。",
            service_type="Claude Code 咨询",
            answer="Amber Lan 为新西兰和澳大利亚的营销团队搭建 Claude Code。奥克兰的 AI 营销工程师 Amber Lan 自己用 Claude Code 运行完整的营销职能，并和你的团队一起搭建同样的结构：每个工作领域一份指令文件、一个技能库、连接你工具的连接器，以及审核关口，然后交接给你。",
            lead="一起为团队搭建一套信得过的 Claude Code，围绕你们每周本来就在做的工作。",
            services_eyebrow="搭建包括什么", services_h2="每一部分，都和团队一起搭建。",
            services_lead="每一部分都是团队能读、能改、能长期保留的文件。",
            services_link="看看搭建内容",
            services=[
                ("工作领域文件", "每个工作领域一份指令文件，每次开始都带着正确的背景。", "/blog/running-marketing-on-claude-code"),
                ("技能库", "把重复的工作写成技能，团队随时调用。", "/skills/"),
                ("连接器", "用 MCP 连接你已经在用的工具，读写权限在范围里写清楚。", "/blog/running-marketing-on-claude-code"),
                ("审核关口", "发布之前检查语调、事实和对外主张。", "/sprints/"),
                ("客户隔离", "对代理机构来说，每个客户一个工作区，客户数据各自留在自己的账号里。", "/blog/claude-code-for-marketing-agencies"),
                ("团队交接", "和你的团队一起实操，直到他们能从容运行和扩展。", "/sprints/"),
            ],
            local=("来自每天都在用的系统。", "这套搭建来自每周用 Claude Code 运行完整营销职能的实践。", [
                ("工作笔记", '<a class="text-link" href="/blog/running-marketing-on-claude-code">如何用 Claude Code 运行完整的营销职能</a>，完整记录。'),
                ("开源", '<a class="text-link" href="/skills/">126 个可检查的技能</a>，其中 16 个由 Amber Lan 搭建，每一个都链接到源码。'),
                ("套餐和席位", '<a class="text-link" href="/blog/claude-vs-chatgpt-business-cost-nz">Claude 商用方案还是 ChatGPT Business</a>，列出新西兰团队各要花多少钱。'),
                ("代理机构", '<a class="text-link" href="/blog/claude-code-for-marketing-agencies">营销代理机构的 Claude Code</a>，讲先搭建什么。'),
                ("招聘", '正在招聘营销工程师的公司，可以<a class="text-link" href="/about#hire">和 Amber 聊聊职位</a>。'),
                ("报价", "书面范围确定后，按项目报价。"),
            ]),
            places=HUB_PLACES["zh"],
            guides=None,
            also=_others("zh", "claude-code-consultant"),
            faq=[
                ("Claude Code 顾问能为营销团队做什么？", "Claude Code 顾问负责搭建 Claude Code，让团队能安全地用它运行重复的营销工作：保存背景的指令文件、处理固定任务的技能、连接团队工具的连接器，以及发布前的审核关口。之后顾问和团队一起实操，直到他们能自己运行和扩展。"),
                ("用 Claude Code 需要懂技术吗？", "熟悉文件和终端会有帮助。技能和工作领域文件都是用文字写成的说明，整套系统读起来像一本整理得很好的工作手册，交接时会讲清楚团队每天要用的命令。"),
                ("Claude Code 适合营销代理机构吗？", "适合有大量重复客户工作的代理机构，例如研究、简报、初稿、报告，以及 SEO 或 AEO 审查。最关键的设计是客户隔离：每个客户一个工作区、一套连接器，客户数据各自留在自己的账号里。Amber Lan 写给代理机构的指南，讲了最先要搭建的工作流。"),
                ("我们的团队需要哪个 Claude 套餐？", "这取决于团队人数和使用强度，Anthropic 的各个套餐在用量上限和管理功能上有所不同。Amber Lan 对比 Claude 商用方案和 ChatGPT Business 的指南，列出了新西兰团队的最新价格。"),
                ("搭建完成后归谁？", "归你。每个工作领域文件、技能和连接器设置都在你的账号和代码仓库里，附有文档，你的团队可以自己修改或扩展，不需要依赖 Amber Lan。"),
                ("怎么开始？", "简单说说团队最常重复的营销工作。Amber 会亲自回复，第一步是你们一起确定一份书面范围说明。"),
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
    crumbs = [("Amber Lan", SITE + ("/zh/" if lang == "zh" else "/")), (UI[lang]["crumb_hub"], hub)]
    if page["slug"]:
        crumbs.append((d["h1"].rstrip("。."), url))
    svc = {
        "@type": "Service", "@id": url + "#service", "name": d["h1"].rstrip("。."),
        "serviceType": d.get("service_type", "AI marketing services"), "description": d["answer"],
        "provider": [{"@id": f"{SITE}/#amber"}, {"@id": f"{SITE}/#flowai"}],
        "areaServed": page["area"], "url": url,
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": UI[lang]["crumb_hub"], "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "description": t}}
            for n, t, _ in (d.get("services") or SERVICES[lang])]},
        "offers": {"@type": "Offer", "description": "书面范围确定后按项目报价。附交接文档，所有智能体归客户所有。" if lang == "zh" else "Priced per project after a written scope. Documented handover; the client owns every agent."},
    }
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": url, "url": url, "name": d["title"], "description": d["description"],
         "inLanguage": UI[lang]["lang"], "dateModified": page.get("updated", UPDATED), "about": {"@id": url + "#service"},
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
    main .narrow { text-align: left; margin: clamp(2.5rem, 5vw, 3.5rem) 0 0; max-width: 52rem; }
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
  <link rel="alternate" type="application/atom+xml" title="Amber Lan" href="{SITE}/feed.xml">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <meta property="og:title" content="{esc(d['title'])}">
  <meta property="og:description" content="{esc(d['description'])}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Amber Lan">
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
<link rel="stylesheet" href="/assets/highend.css?v=11">
<link rel="stylesheet" href="/assets/liquid.css?v=1">
<script src="/assets/liquid.js?v=1" defer></script>
<script>document.documentElement.className += ' has-nav';</script>
<script src="/assets/dot.js?v=8" defer></script>
<script src="/assets/nav.js?v=1" defer onerror="document.documentElement.classList.remove('has-nav')"></script>
</head>
<body data-motion="auto">
"""
    chrome = PRE.replace('<a href="/ai-marketing-services/">', '<a href="/ai-marketing-services/" aria-current="page">', 1)
    places = " &middot; ".join(f'<a class="text-link arrow-link" href="{pre(u)}">{esc(n)}</a>' for n, u, _ in d["places"])
    services = "".join(
        f'<li><span class="vlabel">{i + 1:02d}{CHECK}</span><b><a class="text-link" href="{pre(u)}">{esc(n)}</a></b><p>{esc(t)}</p></li>'
        for i, (n, t, u) in enumerate(d.get("services") or SERVICES[lang]))
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
    for n, u, t in d.get("also") or ALSO[lang].get(page["slug"], []):
        g_items.append(f'            <li><b>{"服务" if zh else "Service"}</b><span><a class="text-link" href="{pre(u)}">{esc(n)}</a>: {esc(t)}</span></li>')
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
            <a class="text-link" href="#services">{d.get('services_link') or ("看看智能体负责什么" if zh else "Explore what the agents run")}</a>
          </div>
          <p class="svc-answer">{esc(d['answer'])}</p>
          <p class="svc-places small">{places}</p>
        </div>
      </div>
    </section>

    <section id="services" class="centered" aria-labelledby="services-title">
      <div class="wrap">
        <div class="stack">
          <p class="eyebrow">{esc(d.get('services_eyebrow', ui['services_eyebrow']))}</p>
          <h2 id="services-title">{esc(d.get('services_h2', ui['services_h2']))}</h2>
          <p class="lead">{esc(d.get('services_lead', ui['services_lead']))}</p>
        </div>
        <ul class="dgrid reveal" aria-label="{esc(d.get('services_h2', ui['services_h2']))}">{services}</ul>
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
          <h2 id="book-title">{"一起搭建你的智能体团队吧。" if zh else "Let's build your agent team together."}</h2>
          <p class="lead">{"告诉我你的业务，以及你最想补上的营销缺口。我们先一起确定一份书面范围说明。" if zh else "Tell me about your business and the marketing gap you most want to close. We begin by shaping a written scope together."}</p>
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
