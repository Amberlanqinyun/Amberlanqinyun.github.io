/* "See Flow at work": an illustrative workspace with a fictional business.
   Select a run under Recents to replay it. Content is static data below. */
(function () {
  "use strict";
  var root = document.querySelector("[data-demo]");
  if (!root) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var RUNS = {
    search: {
      steps: ["Reading your 38 service pages", "Matching 120 questions people ask AI", "Checking which pages AI cites today", "Drafting fixes, staged only"],
      title: "AI search fixes", agent: "Search agent", status: "Waiting for your review",
      ask: "Find the questions people ask AI about hot water cylinders in Auckland and fix the pages that should answer them. Stage everything, publish nothing.",
      reply: "Checked 38 pages against 120 questions people ask. Rewrote 5 pages and drafted 2 new answers. Everything is staged as a draft.",
      card: "Staged changes", action: "Review all",
      rows: [["/services/hot-water-cylinders", "6 changes"], ["/services/blocked-drains", "3 changes"], ["/faq/plumber-cost-auckland", "New page"], ["/areas/north-shore", "4 changes"], ["/llms.txt", "Updated"]],
      follow: "Looks good. Hold the pricing page until I check the numbers."
    },
    content: {
      steps: ["Reading four job notes", "Applying your voice rules", "Drafting 12 pieces across channels", "Checking each line against the voice gate"],
      title: "October content", agent: "Content agent", status: "12 drafts ready",
      ask: "Turn this month's job notes into posts and an email. Keep my voice, no jargon.",
      reply: "Drafted 12 pieces from 4 job notes. Each one passed your voice rules before it reached you.",
      card: "Drafts", action: "Open queue",
      rows: [["LinkedIn: why your cylinder hisses", "Draft"], ["Google Business update: winter checks", "Draft"], ["Email: the five-minute winter checklist", "Draft"], ["Guide: when to replace a cylinder", "Draft"], ["Instagram: before and after, Ponsonby", "Draft"]],
      follow: "Swap the second post for the before and after photo."
    },
    outbound: {
      steps: ["Scanning Auckland property managers", "Finding a recent maintenance signal", "Holding poor fits back", "Drafting 20 first messages in your voice"],
      title: "Outbound lane", agent: "Outbound agent", status: "Sending paused",
      ask: "Find property managers in Auckland who posted about maintenance this month. Write to 20 of them, softly.",
      reply: "Found 23 with a recent signal. Drafted 20 first messages and held 3 that looked like a poor fit. Sending stays paused until you approve.",
      card: "First messages", action: "Approve 10",
      rows: [["Property manager, Mt Eden", "Hiring maintenance staff"], ["Body corporate lead, Takapuna", "Posted about leaks"], ["Portfolio manager, Grey Lynn", "New building added"], ["Facilities lead, Newmarket", "Asked for quotes"], ["Property manager, Remuera", "Held: poor fit"]],
      follow: "Approve the first 10. Any reply comes straight to me."
    },
    report: {
      steps: ["Joining enquiries to their source", "Comparing channels month on month", "Checking what each hour produced", "Writing one page with a recommendation"],
      title: "September report", agent: "Reporting agent", status: "Ready",
      ask: "What paid off last month, and what should change?",
      reply: "Search brought the most enquiries. Outbound booked three calls. Content drew views but few enquiries. Suggest moving two hours a week from social to the FAQ pages.",
      card: "Where enquiries came from", action: "Open report",
      bars: [["Search", 41], ["Outbound", 22], ["Referral", 19], ["Content", 11], ["Other", 7]],
      follow: "Agreed. Update the plan for November."
    }
  };

  /* Chinese pages (/zh/) replay the same runs in Chinese. Same business, same numbers. */
  var ZH = /^zh/.test(document.documentElement.lang);
  if (ZH) RUNS = {
    search: {
      steps: ["正在读取你的 38 个服务页面", "匹配大家向 AI 提出的 120 个问题", "检查 AI 目前引用了哪些页面", "起草修改，只放入待审区"],
      title: "AI 搜索优化", agent: "搜索智能体", status: "等待你审核",
      ask: "找出大家向 AI 询问奥克兰热水器时会问的问题，并修改应该回答这些问题的页面。全部放入待审区，先不要发布。",
      reply: "已用 120 个常见问题核对 38 个页面。改写了 5 个页面，并起草了 2 个新回答。所有内容都已保存为草稿。",
      card: "待审改动", action: "全部审核",
      rows: [["/services/hot-water-cylinders", "6 处改动"], ["/services/blocked-drains", "3 处改动"], ["/faq/plumber-cost-auckland", "新页面"], ["/areas/north-shore", "4 处改动"], ["/llms.txt", "已更新"]],
      follow: "看起来不错。价格页面先别动，等我核对一下数字。"
    },
    content: {
      steps: ["正在阅读四份工单记录", "套用你的品牌语调规则", "为各个渠道起草 12 篇内容", "逐句通过语调关卡检查"],
      title: "10月内容", agent: "内容智能体", status: "12 篇草稿已就绪",
      ask: "把这个月的工单记录整理成社媒帖子和一封邮件。保持我的语调，不要用行话。",
      reply: "根据 4 份工单记录起草了 12 篇内容。每一篇在交给你之前都通过了你的语调规则。",
      card: "草稿", action: "打开队列",
      rows: [["LinkedIn：热水器为什么会嘶嘶作响", "草稿"], ["Google 商家动态：冬季检查", "草稿"], ["邮件：五分钟冬季检查清单", "草稿"], ["指南：什么时候该换热水器", "草稿"], ["Instagram：Ponsonby 维修前后对比", "草稿"]],
      follow: "把第二篇换成那张维修前后的对比照片。"
    },
    outbound: {
      steps: ["正在筛选奥克兰的物业经理", "寻找近期的维修需求信号", "暂缓不太匹配的对象", "用你的语调起草 20 条首次联系消息"],
      title: "主动外联", agent: "外联智能体", status: "发送已暂停",
      ask: "找出本月发过维修相关内容的奥克兰物业经理。给其中 20 位写信，语气温和一些。",
      reply: "找到 23 位有近期信号的联系人。起草了 20 条首次联系消息，另有 3 位看起来不太匹配，已暂缓。在你批准之前不会发送。",
      card: "首次联系消息", action: "批准 10 条",
      rows: [["物业经理，Mt Eden", "正在招聘维修人员"], ["业主委员会负责人，Takapuna", "发帖提到漏水"], ["资产组合经理，Grey Lynn", "新增一栋楼"], ["设施负责人，Newmarket", "正在询价"], ["物业经理，Remuera", "已暂缓：不太匹配"]],
      follow: "先批准前 10 条。有任何回复都直接转给我。"
    },
    report: {
      steps: ["把每条咨询对应到来源", "逐月对比各个渠道", "核算每小时投入带来的产出", "写成一页报告并附上建议"],
      title: "9月报告", agent: "报告智能体", status: "已就绪",
      ask: "上个月哪些投入有回报，接下来应该调整什么？",
      reply: "搜索带来的咨询最多。主动外联约到了三次通话。内容获得了浏览量，但咨询不多。建议每周从社媒挪出两小时，投入到常见问题页面。",
      card: "咨询来源", action: "打开报告",
      bars: [["搜索", 41], ["主动外联", 22], ["转介绍", 19], ["内容", 11], ["其他", 7]],
      follow: "同意。更新一下11月的计划。"
    }
  };

  var thread = root.querySelector(".demo__thread");
  /* Keep the newest message in view, like a real chat. */
  if ("MutationObserver" in window) {
    new MutationObserver(function () { thread.scrollTo({ top: thread.scrollHeight, behavior: reduce ? "auto" : "smooth" }); })
      .observe(thread, { childList: true, subtree: true });
  }
  var titleEl = root.querySelector(".demo__title");
  var statusEl = root.querySelector(".demo__status");
  var buttons = Array.prototype.slice.call(root.querySelectorAll("[data-run]"));
  var timers = [];

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  function later(fn, ms) { timers.push(setTimeout(fn, reduce ? 0 : ms)); }

  function render(key) {
    var r = RUNS[key];
    timers.forEach(function (x) { clearTimeout(x); clearInterval(x); }); timers = [];
    buttons.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.run === key ? "true" : "false"); });
    titleEl.textContent = r.title;
    statusEl.textContent = ZH ? "运行中" : "Working";
    statusEl.classList.add("is-working");
    thread.innerHTML = "";

    var you = el("div", "demo__msg demo__msg--you"); you.appendChild(el("p", "", r.ask));
    thread.appendChild(you);

    var agent = el("div", "demo__msg demo__msg--agent");
    var who = el("p", "demo__who"); who.appendChild(el("b", "", "Flow Intelligence")); var t = el("span", "demo__timer", ""); who.appendChild(t);
    agent.appendChild(who);
    var think = el("div", "demo__think");
    think.innerHTML = '<span class="demo__dots" aria-hidden="true"><i></i><i></i><i></i></span>';
    var stepEl = el("span", "demo__step", ZH ? "思考中" : "Thinking");
    think.appendChild(stepEl);
    var log = el("ol", "demo__log");
    agent.appendChild(think); agent.appendChild(log);
    later(function () { thread.appendChild(agent); }, 350);
    var start = Date.now(), tick = setInterval(function () { t.textContent = Math.round((Date.now() - start) / 1000) + "s"; }, 250);
    timers.push(tick);
    var STEP = 650;
    r.steps.forEach(function (s, i) {
      later(function () {
        stepEl.textContent = s;
        if (i > 0) { var li = el("li", "", r.steps[i - 1]); log.appendChild(li); }
      }, 500 + i * STEP);
    });
    var doneAt = 500 + r.steps.length * STEP;

    later(function () {
      clearInterval(tick);
      log.appendChild(el("li", "", r.steps[r.steps.length - 1]));
      think.remove();
      agent.classList.add("is-done");
      t.textContent = (ZH ? "思考了 " : "Thought for ") + Math.max(1, Math.round((Date.now() - start) / 1000)) + (ZH ? " 秒" : "s");
      who.querySelector("b").textContent = "Flow Intelligence · " + r.agent;
      statusEl.textContent = r.status; statusEl.classList.remove("is-working");
      agent.appendChild(el("p", "demo__reply", r.reply));
      var card = el("div", "demo__card");
      var head = el("div", "demo__cardhead"); head.appendChild(el("span", "", r.card)); head.appendChild(el("span", "demo__btn", r.action));
      card.appendChild(head);
      if (r.rows) {
        r.rows.forEach(function (row, i) {
          var li = el("div", "demo__row");
          li.appendChild(el("span", "demo__path", row[0])); li.appendChild(el("span", "demo__meta", row[1]));
          li.style.animationDelay = (reduce ? 0 : i * 90) + "ms";
          card.appendChild(li);
        });
      } else {
        r.bars.forEach(function (b, i) {
          var li = el("div", "demo__row demo__row--bar");
          li.appendChild(el("span", "demo__path", b[0]));
          var track = el("span", "demo__track"); var fill = el("i"); fill.style.width = b[1] * 2 + "%"; if (i === 0) fill.className = "is-top";
          track.appendChild(fill); li.appendChild(track); li.appendChild(el("span", "demo__meta", b[1] + "%"));
          li.style.animationDelay = (reduce ? 0 : i * 90) + "ms";
          card.appendChild(li);
        });
      }
      agent.appendChild(card);
    }, doneAt);

    later(function () {
      var f = el("div", "demo__msg demo__msg--you demo__msg--follow"); f.appendChild(el("p", "", r.follow));
      thread.appendChild(f);
    }, doneAt + 1100);
  }

  buttons.forEach(function (b) { b.addEventListener("click", function () { render(b.dataset.run); }); });

  var started = false;
  function start() { if (!started) { started = true; render("search"); } }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { start(); io.disconnect(); } }, { threshold: 0.3 });
    io.observe(root);
  } else { start(); }
})();
