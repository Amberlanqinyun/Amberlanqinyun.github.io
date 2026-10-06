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
    statusEl.textContent = "Working";
    statusEl.classList.add("is-working");
    thread.innerHTML = "";

    var you = el("div", "demo__msg demo__msg--you"); you.appendChild(el("p", "", r.ask));
    thread.appendChild(you);

    var agent = el("div", "demo__msg demo__msg--agent");
    var who = el("p", "demo__who"); who.appendChild(el("b", "", "Flow Intelligence")); var t = el("span", "demo__timer", ""); who.appendChild(t);
    agent.appendChild(who);
    var think = el("div", "demo__think");
    think.innerHTML = '<span class="demo__dots" aria-hidden="true"><i></i><i></i><i></i></span>';
    var stepEl = el("span", "demo__step", "Thinking");
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
      t.textContent = "Thought for " + Math.max(1, Math.round((Date.now() - start) / 1000)) + "s";
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
