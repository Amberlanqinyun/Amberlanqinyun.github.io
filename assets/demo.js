/* The run sheet (23 Oct 2026): one brief in, finished work out, staged for approval.
   Replaces the chat-window demo. Four runs for an accounting firm in Auckland;
   pick one under the sheet to replay it. Content is static data below. */
(function () {
  "use strict";
  var root = document.querySelector("[data-run-sheet]");
  if (!root) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var ZH = /^zh/.test(document.documentElement.lang);

  var RUNS = ZH ? {
    search: { agent: "搜索智能体", status: "已暂存，等你审核", working: "运行中",
      story: "你希望企业主向 AI 询问时，找到的是你的事务所。",
      brief: "让企业主向 AI 询问奥克兰会计师时，能找到我们。",
      steps: ["读取了 38 个服务页面", "匹配了企业主向 AI 提出的 120 个问题", "起草修改，只放入待审区"],
      outk: "返回的结果", mono: true,
      rows: [["/services/small-business-accounting", "6 处改动"], ["/services/xero-bookkeeping", "3 处改动"], ["/faq/accountant-cost-auckland", "新页面"], ["/areas/north-shore", "4 处改动"], ["/llms.txt", "已更新"]],
      note: "你批准之前，什么都不会发布。", approve: "全部批准", approved: "已批准 · 发布中", done: "已发布" },
    content: { agent: "内容智能体", status: "12 篇草稿已就绪", working: "运行中",
      story: "你希望这个月客户的问题变成帖子，用你自己的语调。",
      brief: "把这个月客户的问题整理成帖子和一封邮件，用我们的语调。",
      steps: ["读取了 14 个客户问题", "套用了你的语调规则", "起草 12 篇，已暂存"],
      outk: "返回的结果",
      rows: [["LinkedIn：暂缴税的常见误区", "草稿"], ["Google 商家动态：年终检查清单", "草稿"], ["邮件：3月31日前的五个截止日期", "草稿"], ["指南：个体经营还是注册公司？", "草稿"], ["LinkedIn：你的会计师应该问你什么", "草稿"]],
      note: "每一句都通过了你的语调规则。", approve: "批准队列", approved: "已批准 · 已排期", done: "已排期" },
    outbound: { agent: "外联智能体", status: "发送已暂停", working: "运行中",
      story: "你希望新企业主最先听到你的消息。",
      brief: "联系奥克兰刚雇了第一位员工的企业主。给其中 20 位写信，语气温和。",
      steps: ["找到 23 位有近期信号的联系人", "暂缓了 3 位不太匹配的对象", "起草了 20 条首次联系消息"],
      outk: "返回的结果",
      rows: [["咖啡馆店主，Ponsonby", "雇了第一位咖啡师"], ["建筑承包商，Henderson", "新注册了公司"], ["设计工作室，Parnell", "第二位员工入职"], ["理疗诊所，Albany", "咨询了薪资发放"], ["花店，Mt Eden", "开了第二家店"]],
      note: "你批准之前，什么都不会发送。", approve: "批准 10 条", approved: "已批准 · 发送 10 条", done: "发送中" },
    report: { agent: "报告智能体", status: "已就绪", working: "运行中",
      story: "你想知道上个月哪些投入有回报。",
      brief: "上个月哪些投入有回报，接下来应该调整什么？",
      steps: ["把 31 条咨询对应到来源", "逐月对比各个渠道", "一页报告，附一条建议"],
      outk: "咨询来源",
      bars: [["搜索", 41], ["主动外联", 22], ["转介绍", 19], ["内容", 11], ["其他", 7]],
      note: "建议每周从社媒挪出两小时，投入常见问题页面。", approve: "打开报告", approved: "已打开", done: "已打开" }
  } : {
    search: { agent: "Search agent", status: "Staged for your review", working: "Working",
      story: "You want to be the firm business owners find when they ask AI.",
      brief: "Get us found when business owners ask AI for an accountant in Auckland.",
      steps: ["Read 38 service pages", "Matched 120 questions owners ask AI", "Drafted fixes, staged only"],
      outk: "What came back", mono: true,
      rows: [["/services/small-business-accounting", "6 changes"], ["/services/xero-bookkeeping", "3 changes"], ["/faq/accountant-cost-auckland", "New page"], ["/areas/north-shore", "4 changes"], ["/llms.txt", "Updated"]],
      note: "Nothing publishes until you approve.", approve: "Approve all", approved: "Approved, publishing", done: "Published" },
    content: { agent: "Content agent", status: "12 drafts ready", working: "Working",
      story: "You want this month's client questions turned into posts, in your voice.",
      brief: "Turn this month's client questions into posts and one email, in our voice.",
      steps: ["Read 14 client questions", "Applied your voice rules", "Drafted 12 pieces, staged"],
      outk: "What came back",
      rows: [["LinkedIn: the provisional tax trap", "Draft"], ["Google Business update: year-end checklist", "Draft"], ["Email: five deadlines before 31 March", "Draft"], ["Guide: sole trader or company?", "Draft"], ["LinkedIn: what your accountant should ask you", "Draft"]],
      note: "Every line passed your voice rules.", approve: "Approve the queue", approved: "Approved, scheduled", done: "Scheduled" },
    outbound: { agent: "Outbound agent", status: "Sending paused", working: "Working",
      story: "You want new business owners to hear from you first.",
      brief: "Reach Auckland owners who just hired their first staff. Write to 20 of them, softly.",
      steps: ["Found 23 with a recent signal", "Held 3 poor fits back", "Drafted 20 first messages"],
      outk: "What came back",
      rows: [["Café owner, Ponsonby", "First barista hired"], ["Builder, Henderson", "New company registered"], ["Design studio, Parnell", "Second hire"], ["Physio clinic, Albany", "Asked about payroll"], ["Florist, Mt Eden", "Opened a second store"]],
      note: "Nothing sends until you approve.", approve: "Approve 10", approved: "Approved, sending 10", done: "Sending" },
    report: { agent: "Reporting agent", status: "Ready", working: "Working",
      story: "You want to know what paid off last month.",
      brief: "What paid off last month, and what should change?",
      steps: ["Joined 31 enquiries to their source", "Compared channels month on month", "One page, with a recommendation"],
      outk: "Where enquiries came from",
      bars: [["Search", 41], ["Outbound", 22], ["Referral", 19], ["Content", 11], ["Other", 7]],
      note: "Suggest moving two hours a week from social to the FAQ pages.", approve: "Open the report", approved: "Opened", done: "Opened" }
  };

  var sheet = root.querySelector(".rs");
  var q = function (s) { return root.querySelector(s); };
  var agentEl = q("[data-rs-agent]"), statusEl = q("[data-rs-status]"), storyEl = q("[data-story]"),
      briefEl = q("[data-rs-brief]"), rail = q("[data-rs-rail]"), outk = q("[data-rs-outk]"),
      rows = q("[data-rs-rows]"), bar = q(".rs__bar"), noteEl = q("[data-rs-note]"), approve = q("[data-rs-approve]");
  var tabs = Array.prototype.slice.call(root.querySelectorAll("[data-replay]"));
  var timers = [], current = "search";

  /* The agent's own character sits by its name (drawn by dot.js, see /dot) and
     its mood follows the run: working while the steps light, waiting at review,
     satisfied once you approve. Without dot.js the amber bead stays. */
  var AGENT = { search: "search", content: "content", outbound: "outbound", report: "reporting" };
  var dotHost = q("[data-rs-dot]"), dot = null;
  function mountDot(key) {
    var F = window.FlowDot; if (!F || !dotHost) return;
    if (dot) { dot.destroy(); dot = null; }
    dotHost.innerHTML = "";
    var svg = F.make("fdot--rs"); dotHost.appendChild(svg);
    dot = F.mount(svg, { role: "agent", agent: AGENT[key], r: 36, state: "work" });
    dot.attach(sheet);
  }
  function mood(m) { if (dot) dot.set(m); }

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function later(fn, ms) { timers.push(setTimeout(fn, reduce ? 0 : ms)); }
  function clear() { timers.forEach(clearTimeout); timers = []; }

  function render(key) {
    var r = RUNS[key]; current = key; clear();
    sheet.classList.remove("is-approved"); sheet.classList.add("is-working");
    mountDot(key);
    tabs.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-replay") === key ? "true" : "false"); });
    agentEl.textContent = r.agent; statusEl.textContent = r.working;
    if (storyEl) storyEl.textContent = r.story;
    outk.textContent = r.outk; noteEl.textContent = r.note;
    approve.textContent = r.approve; approve.disabled = false;
    bar.classList.remove("is-on");

    /* The brief, typed. */
    briefEl.textContent = "";
    var typed = 0;
    if (reduce) { briefEl.textContent = r.brief; }
    else {
      var caret = el("i", "rs__caret"); caret.setAttribute("aria-hidden", "true"); briefEl.appendChild(caret);
      var chars = Array.from(r.brief), per = ZH ? 60 : 24, t0 = 300;
      chars.forEach(function (ch, i) { later(function () { caret.insertAdjacentText("beforebegin", ch); }, t0 + i * per); });
      typed = t0 + chars.length * per + 350;
      later(function () { caret.remove(); }, typed);
    }

    /* The rail: three steps, each lit as it completes. */
    rail.innerHTML = "";
    r.steps.forEach(function (s) { rail.appendChild(el("li", "", s)); });
    var STEP = 720;
    r.steps.forEach(function (s, i) { later(function () { rail.children[i].classList.add("is-on"); }, typed + 350 + i * STEP); });
    var doneAt = typed + 350 + r.steps.length * STEP;

    /* What came back: rows, or bars for the report. */
    rows.innerHTML = "";
    var items = r.rows || r.bars;
    items.forEach(function (it, i) {
      var row;
      if (r.bars) {
        row = el("div", "rs__row rs__row--bar" + (i === 0 ? " rs__row--top" : ""));
        row.appendChild(el("span", "rs__path", it[0]));
        var track = el("span", "rs__track"); var fill = el("i"); fill.style.setProperty("--w", (it[1] * 2) + "%"); track.appendChild(fill); row.appendChild(track);
        row.appendChild(el("span", "rs__meta", it[1] + "%"));
      } else {
        row = el("div", "rs__row" + (r.mono ? " rs__row--mono" : ""));
        row.appendChild(el("span", "rs__path", it[0])); row.appendChild(el("span", "rs__meta", it[1]));
        var tick = el("i", "rs__tick"); tick.setAttribute("aria-hidden", "true"); row.appendChild(tick);
      }
      rows.appendChild(row);
      later(function () { row.classList.add("is-on"); }, doneAt + i * 110);
    });
    later(function () {
      bar.classList.add("is-on"); statusEl.textContent = r.status; sheet.classList.remove("is-working");
      mood(r.bars ? "done" : "review");
    }, doneAt + items.length * 110 + 250);
  }

  approve.addEventListener("click", function () {
    var r = RUNS[current];
    sheet.classList.add("is-approved"); approve.textContent = r.approved; approve.disabled = true;
    mood("done"); if (dot) dot.greet();
    later(function () { statusEl.textContent = r.done; }, 900);
  });
  tabs.forEach(function (b) { b.addEventListener("click", function () { render(b.getAttribute("data-replay")); }); });

  var started = false;
  function start() { if (!started) { started = true; render("search"); } }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { start(); io.disconnect(); } }, { threshold: 0.3 });
    io.observe(sheet);
  } else { start(); }
})();
