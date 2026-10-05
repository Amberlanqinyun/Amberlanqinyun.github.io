/* "See Flow at work": an illustrative workspace with a fictional business.
   Select a run under Recents to replay it. Content is static data below. */
(function () {
  "use strict";
  var root = document.querySelector("[data-demo]");
  if (!root) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var RUNS = {
    search: {
      title: "AI search fixes", agent: "Search agent", status: "Waiting for your review",
      ask: "Find the questions people ask AI about hot water cylinders in Auckland and fix the pages that should answer them. Stage everything, publish nothing.",
      reply: "Checked 38 pages against 120 questions people ask. Rewrote 5 pages and drafted 2 new answers. Everything is staged as a draft.",
      card: "Staged changes", action: "Review all",
      rows: [["/services/hot-water-cylinders", "6 changes"], ["/services/blocked-drains", "3 changes"], ["/faq/plumber-cost-auckland", "New page"], ["/areas/north-shore", "4 changes"], ["/llms.txt", "Updated"]],
      follow: "Looks good. Hold the pricing page until I check the numbers."
    },
    content: {
      title: "October content", agent: "Content agent", status: "12 drafts ready",
      ask: "Turn this month's job notes into posts and an email. Keep my voice, no jargon.",
      reply: "Drafted 12 pieces from 4 job notes. Each one passed your voice rules before it reached you.",
      card: "Drafts", action: "Open queue",
      rows: [["LinkedIn: why your cylinder hisses", "Draft"], ["Google Business update: winter checks", "Draft"], ["Email: the five-minute winter checklist", "Draft"], ["Guide: when to replace a cylinder", "Draft"], ["Instagram: before and after, Ponsonby", "Draft"]],
      follow: "Swap the second post for the before and after photo."
    },
    outbound: {
      title: "Outbound lane", agent: "Outbound agent", status: "Sending paused",
      ask: "Find property managers in Auckland who posted about maintenance this month. Write to 20 of them, softly.",
      reply: "Found 23 with a recent signal. Drafted 20 first messages and held 3 that looked like a poor fit. Sending stays paused until you approve.",
      card: "First messages", action: "Approve 10",
      rows: [["Property manager, Mt Eden", "Hiring maintenance staff"], ["Body corporate lead, Takapuna", "Posted about leaks"], ["Portfolio manager, Grey Lynn", "New building added"], ["Facilities lead, Newmarket", "Asked for quotes"], ["Property manager, Remuera", "Held: poor fit"]],
      follow: "Approve the first 10. Any reply comes straight to me."
    },
    report: {
      title: "September report", agent: "Reporting agent", status: "Ready",
      ask: "What paid off last month, and what should change?",
      reply: "Search brought the most enquiries. Outbound booked three calls. Content drew views but few enquiries. Suggest moving two hours a week from social to the FAQ pages.",
      card: "Where enquiries came from", action: "Open report",
      bars: [["Search", 41], ["Outbound", 22], ["Referral", 19], ["Content", 11], ["Other", 7]],
      follow: "Agreed. Update the plan for November."
    }
  };

  var thread = root.querySelector(".demo__thread");
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
    timers.forEach(clearTimeout); timers = [];
    buttons.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.run === key ? "true" : "false"); });
    titleEl.textContent = r.title;
    statusEl.textContent = "Working";
    statusEl.classList.add("is-working");
    thread.innerHTML = "";

    var you = el("div", "demo__msg demo__msg--you"); you.appendChild(el("p", "", r.ask));
    thread.appendChild(you);

    var agent = el("div", "demo__msg demo__msg--agent");
    var who = el("p", "demo__who"); who.appendChild(el("b", "", r.agent)); var t = el("span", "demo__timer", "Working"); who.appendChild(t);
    agent.appendChild(who);
    later(function () { thread.appendChild(agent); }, 350);

    later(function () {
      t.textContent = "Done";
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
    }, 1500);

    later(function () {
      var f = el("div", "demo__msg demo__msg--you demo__msg--follow"); f.appendChild(el("p", "", r.follow));
      thread.appendChild(f);
    }, 2600);
  }

  buttons.forEach(function (b) { b.addEventListener("click", function () { render(b.dataset.run); }); });

  var started = false;
  function start() { if (!started) { started = true; render("search"); } }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { start(); io.disconnect(); } }, { threshold: 0.3 });
    io.observe(root);
  } else { start(); }
})();
