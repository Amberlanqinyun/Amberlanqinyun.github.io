/* Marketing decision map: pick, score, map, write the rules. Runs in the browser only. */
(function () {
  "use strict";
  var ZH = /^zh/.test(document.documentElement.lang);
  /* Chinese pages keep their own saved map, so switching language never mixes the two sets. */
  var LS = ZH ? "flowai-decision-map-v1-zh" : "flowai-decision-map-v1";
  function tr(en, zh) { return ZH ? zh : en; }
  var LIB = [
    ["Who we sell to", [
      ["Which customer segment to focus on this quarter", 5, 4, 2],
      ["Which offer to lead with", 4, 3, 2],
      ["Which accounts to approach first", 3, 2, 3]]],
    ["Where the money goes", [
      ["How to split budget across channels", 5, 4, 2],
      ["Whether to hire, use an agency or automate", 4, 4, 1],
      ["When to pause a channel that is not working", 3, 3, 2]]],
    ["What we say", [
      ["Our core claim and positioning", 5, 5, 1],
      ["Which proof and case studies to feature", 3, 2, 3],
      ["How we answer a competitor", 3, 4, 2]]],
    ["How work ships", [
      ["Which channels a campaign uses", 3, 2, 3],
      ["What to post this week", 2, 2, 5],
      ["When to send emails", 1, 1, 5],
      ["Which leads get a follow-up", 3, 2, 4],
      ["When a reply goes to a person", 4, 4, 4]]]
  ];
  if (ZH) LIB = [
    ["我们卖给谁", [
      ["本季度重点聚焦哪个客户群", 5, 4, 2],
      ["主推哪一项服务", 4, 3, 2],
      ["优先接触哪些客户", 3, 2, 3]]],
    ["预算花在哪里", [
      ["预算如何在各渠道之间分配", 5, 4, 2],
      ["招人、找代理机构还是自动化", 4, 4, 1],
      ["效果不好的渠道何时暂停", 3, 3, 2]]],
    ["我们说什么", [
      ["核心主张与定位", 5, 5, 1],
      ["重点展示哪些证据和案例", 3, 2, 3],
      ["如何回应竞争对手", 3, 4, 2]]],
    ["工作如何交付", [
      ["一次营销活动用哪些渠道", 3, 2, 3],
      ["这周发什么内容", 2, 2, 5],
      ["什么时候发邮件", 1, 1, 5],
      ["哪些潜在客户需要跟进", 3, 2, 4],
      ["什么时候把回复转给人工", 4, 4, 4]]]
  ];
  var DEFAULTS = ZH ? ["核心主张与定位", "预算如何在各渠道之间分配", "重点展示哪些证据和案例", "这周发什么内容", "什么时候发邮件", "哪些潜在客户需要跟进", "什么时候把回复转给人工"] : ["Our core claim and positioning", "How to split budget across channels", "Which proof and case studies to feature", "What to post this week", "When to send emails", "Which leads get a follow-up", "When a reply goes to a person"];

  var preset = {};
  LIB.forEach(function (g) { g[1].forEach(function (d) { preset[d[0]] = { v: d[1], r: d[2], f: d[3] }; }); });

  var state = load();
  function load() {
    try { var raw = localStorage.getItem(LS); if (raw) return JSON.parse(raw); } catch (e) {}
    var s = { picked: [], scores: {}, briefs: {}, custom: [] };
    DEFAULTS.forEach(function (n) { s.picked.push(n); s.scores[n] = Object.assign({}, preset[n]); });
    return s;
  }
  function save() { try { localStorage.setItem(LS, JSON.stringify(state)); } catch (e) {} }
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function lane(s) {
    if (s.r >= 4 || (s.v >= 4 && s.r >= 3)) return "you";
    if (s.r <= 2 && s.v <= 2 && s.f >= 3) return "agent";
    return "draft";
  }
  var LANES = ZH ? {
    you: ["你来决定，智能体提供依据", "影响大或难以撤回。智能体带来证据，由人拍板。"],
    draft: ["智能体起草，你来批准", "值得人看一眼。智能体把决策准备好，由人签字确认。"],
    agent: ["智能体决定，你来抽查", "频繁且风险低。规则写一次，定期抽样复核。"]
  } : {
    you: ["You decide, the agent informs", "High stakes or hard to undo. The agent brings evidence; a person makes the call."],
    draft: ["The agent drafts, you approve", "Worth a human look. The agent prepares the decision and a person signs it off."],
    agent: ["The agent decides, you spot-check", "Frequent and low risk. Write the rule once and review a sample."]
  };

  /* Step 1: pick */
  function renderPick() {
    var html = "";
    LIB.forEach(function (g) {
      html += '<div class="dm-group"><h3>' + esc(g[0]) + '</h3><div class="dm-chips">';
      g[1].forEach(function (d) { html += chip(d[0]); });
      html += "</div></div>";
    });
    if (state.custom.length) {
      html += '<div class="dm-group"><h3>' + tr("Your own", "你自己添加的") + '</h3><div class="dm-chips">' + state.custom.map(chip).join("") + "</div></div>";
    }
    $("dm-groups").innerHTML = html;
  }
  function chip(name) {
    var on = state.picked.indexOf(name) > -1;
    return '<button type="button" class="dm-chip" aria-pressed="' + on + '" data-name="' + esc(name) + '">' + esc(name) + "</button>";
  }
  $("dm-groups").addEventListener("click", function (e) {
    var b = e.target.closest(".dm-chip"); if (!b) return;
    var n = b.getAttribute("data-name"), i = state.picked.indexOf(n);
    if (i > -1) state.picked.splice(i, 1); else { state.picked.push(n); if (!state.scores[n]) state.scores[n] = Object.assign({ v: 3, r: 3, f: 3 }, preset[n] || {}); }
    b.setAttribute("aria-pressed", i === -1);
    update();
  });
  $("dm-add").addEventListener("submit", function (e) {
    e.preventDefault();
    var inp = $("dm-add-input"), n = inp.value.trim();
    if (!n || state.custom.indexOf(n) > -1 || preset[n]) { inp.value = ""; return; }
    state.custom.push(n); state.picked.push(n); state.scores[n] = { v: 3, r: 3, f: 3 };
    inp.value = ""; renderPick(); update();
  });

  /* Step 2: score */
  function seg(name, key, val) {
    var h = '<div class="dm-seg" role="group" aria-label="' + esc(ZH ? name + "：" + ({ v: "业务价值", r: "出错的风险", f: "频率" }[key] || key) : key + " for " + name) + '">';
    for (var i = 1; i <= 5; i++) h += '<button type="button" data-name="' + esc(name) + '" data-key="' + key + '" data-val="' + i + '" aria-pressed="' + (val === i) + '">' + i + "</button>";
    return h + "</div>";
  }
  function renderScore() {
    if (!state.picked.length) { $("dm-score").innerHTML = '<p class="dm-empty">' + tr("Pick at least one decision above.", "请在上方至少选择一项决策。") + '</p>'; return; }
    var h = '<table class="dm-table"><thead><tr><th>' + tr("Decision", "决策") + '</th><th>' + tr("Business value", "业务价值") + '</th><th>' + tr("Risk if wrong", "出错的风险") + '</th><th>' + tr("How often", "频率") + '</th></tr></thead><tbody>';
    state.picked.forEach(function (n) {
      var s = state.scores[n];
      h += "<tr><td>" + esc(n) + '</td><td data-k="' + tr("Value", "价值") + '">' + seg(n, "v", s.v) + '</td><td data-k="' + tr("Risk", "风险") + '">' + seg(n, "r", s.r) + '</td><td data-k="' + tr("Frequency", "频率") + '">' + seg(n, "f", s.f) + "</td></tr>";
    });
    $("dm-score").innerHTML = h + "</tbody></table>";
  }
  $("dm-score").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-key]"); if (!b) return;
    state.scores[b.getAttribute("data-name")][b.getAttribute("data-key")] = +b.getAttribute("data-val");
    var grp = b.parentNode; Array.prototype.forEach.call(grp.children, function (x) { x.setAttribute("aria-pressed", x === b); });
    renderMap(); renderBriefs(); save();
  });

  /* Step 3: map */
  function renderMap() {
    var W = 560, H = 380, L = 44, R = 16, T = 16, B = 40;
    var x = function (r) { return L + (r - 0.5) / 5 * (W - L - R); };
    var y = function (v) { return T + (5.5 - v) / 5 * (H - T - B); };
    var svg = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + tr("Decision map: business value against risk, bubble size shows how often the decision is made.", "决策地图：纵轴为业务价值，横轴为风险，气泡大小表示决策的频率。") + '">';
    svg += '<rect class="zone" x="' + x(3.5) + '" y="' + T + '" width="' + (W - R - x(3.5)) + '" height="' + (H - T - B) + '" rx="6"/>';
    for (var i = 1; i <= 5; i++) {
      svg += '<line class="grid" x1="' + L + '" x2="' + (W - R) + '" y1="' + y(i) + '" y2="' + y(i) + '"/>';
      svg += '<text x="' + (L - 12) + '" y="' + (y(i) + 4) + '" text-anchor="end">' + i + "</text>";
      svg += '<text x="' + x(i) + '" y="' + (H - B + 18) + '" text-anchor="middle">' + i + "</text>";
    }
    svg += '<line class="ax" x1="' + L + '" x2="' + L + '" y1="' + T + '" y2="' + (H - B) + '"/><line class="ax" x1="' + L + '" x2="' + (W - R) + '" y1="' + (H - B) + '" y2="' + (H - B) + '"/>';
    svg += '<text x="' + ((L + W - R) / 2) + '" y="' + (H - 4) + '" text-anchor="middle">' + tr("Risk if wrong", "出错的风险") + '</text>';
    svg += '<text x="12" y="' + ((T + H - B) / 2) + '" text-anchor="middle" transform="rotate(-90 12 ' + ((T + H - B) / 2) + ')">' + tr("Business value", "业务价值") + '</text>';
    var seen = {};
    state.picked.forEach(function (n, k) {
      var s = state.scores[n], key = s.r + "-" + s.v, off = (seen[key] = (seen[key] || 0) + 1) - 1;
      var rr = 7 + s.f * 2.2, ang = off * 2.4, dist = off ? 14 + off * 6 : 0, cx = x(s.r) + Math.cos(ang) * dist, cy = y(s.v) - Math.sin(ang) * dist, ln = lane(s);
      var fill = ln === "you" ? "#e4a43c" : ln === "draft" ? "rgba(250,248,243,.72)" : "rgba(250,248,243,.3)";
      svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + rr + '" fill="' + fill + '" fill-opacity=".85"><title>' + esc(n) + "</title></circle>";
      svg += '<text x="' + cx + '" y="' + (cy + 4) + '" text-anchor="middle" style="fill:' + (ln === "you" ? "#0e0e0d" : ln === "draft" ? "#0e0e0d" : "#faf8f3") + ';font-size:11px;font-weight:600">' + (k + 1) + "</text>";
    });
    $("dm-chart").innerHTML = svg + "</svg>";
    var groups = { you: [], draft: [], agent: [] };
    state.picked.forEach(function (n) { groups[lane(state.scores[n])].push(n); });
    $("dm-lanes").innerHTML = ["you", "draft", "agent"].map(function (k) {
      var items = groups[k].length ? groups[k].map(function (n) { return '<li><span class="dm-num">' + (state.picked.indexOf(n) + 1) + "</span>" + esc(n) + "</li>"; }).join("") : '<li class="dm-empty">' + tr("None yet", "暂无") + '</li>';
      return '<div class="dm-lane is-' + k + '"><h3>' + LANES[k][0] + "<span>" + groups[k].length + "</span></h3><p>" + LANES[k][1] + "</p><ul>" + items + "</ul></div>";
    }).join("");
  }

  /* Step 4: briefs for the top three */
  var FIELDS = ZH ? [["owner", "负责人", "一位具体的人"], ["inputs", "决策依据", "这项决策用到的数据、调研或规则"], ["rules", "护栏规则", "始终要做…… / 绝不能做……"], ["review", "谁来审核，何时审核", "发布前、每周抽样、每月"], ["measure", "怎么判断有效", "我们关注的那一个数字"]] : [["owner", "Who owns it", "One named person"], ["inputs", "What it is based on", "Data, research or rules the decision uses"], ["rules", "Guardrails", "Always do… / never do…"], ["review", "Who reviews, and when", "Before it ships, weekly sample, monthly"], ["measure", "How we know it worked", "The one number we watch"]];
  function top() {
    return state.picked.slice().sort(function (a, b) {
      var A = state.scores[a], B = state.scores[b];
      return (B.v * 2 + B.r * 2 + B.f) - (A.v * 2 + A.r * 2 + A.f);
    }).slice(0, 3);
  }
  function renderBriefs() {
    var t = top();
    if (!t.length) { $("dm-briefs").innerHTML = '<p class="dm-empty">' + tr("Your top decisions appear here once you pick some.", "选好决策后，最重要的几项会显示在这里。") + '</p>'; return; }
    $("dm-briefs").innerHTML = t.map(function (n) {
      var b = state.briefs[n] || {};
      return '<article class="dm-brief"><h3>' + esc(n) + '</h3><span class="dm-tag">' + LANES[lane(state.scores[n])][0] + "</span>" +
        FIELDS.map(function (f) {
          var id = "f-" + btoa(unescape(encodeURIComponent(n))).replace(/[^a-z0-9]/gi, "").slice(0, 16) + "-" + f[0];
          return '<div class="dm-field"><label for="' + id + '">' + f[1] + '</label><textarea id="' + id + '" data-name="' + esc(n) + '" data-f="' + f[0] + '" placeholder="' + esc(f[2]) + '">' + esc(b[f[0]] || "") + "</textarea></div>";
        }).join("") + "</article>";
    }).join("");
  }
  $("dm-briefs").addEventListener("input", function (e) {
    var t = e.target; if (!t.dataset.f) return;
    var n = t.dataset.name; state.briefs[n] = state.briefs[n] || {}; state.briefs[n][t.dataset.f] = t.value; save();
  });

  function asText() {
    var out = tr("Marketing decision map\nMade with flowai.co.nz/tools/decision-map\n\n", "营销决策地图\n用 flowai.co.nz/zh/tools/decision-map 制作\n\n");
    ["you", "draft", "agent"].forEach(function (k) {
      var items = state.picked.filter(function (n) { return lane(state.scores[n]) === k; });
      if (!items.length) return;
      out += "## " + LANES[k][0] + "\n";
      items.forEach(function (n) { var s = state.scores[n]; out += "- " + n + (ZH ? "（价值 " + s.v + "，风险 " + s.r + "，频率 " + s.f + "）\n" : " (value " + s.v + ", risk " + s.r + ", frequency " + s.f + ")\n"); });
      out += "\n";
    });
    out += tr("## Decision briefs\n", "## 决策简报\n");
    top().forEach(function (n) {
      var b = state.briefs[n] || {};
      out += "\n### " + n + "\n";
      FIELDS.forEach(function (f) { out += "- " + f[1] + tr(": ", "：") + (b[f[0]] || "") + "\n"; });
    });
    return out;
  }
  function status(msg) { $("dm-status").textContent = msg; setTimeout(function () { $("dm-status").textContent = ""; }, 2500); }
  function track(kind) { if (window.dataLayer) window.dataLayer.push({ event: "decision_map_export", method: kind }); }
  $("dm-copy").addEventListener("click", function () {
    var txt = asText();
    if (navigator.clipboard) navigator.clipboard.writeText(txt).then(function () { status(tr("Copied.", "已复制。")); }, function () { status(tr("Copy blocked by the browser.", "浏览器阻止了复制。")); });
    track("copy");
  });
  $("dm-download").addEventListener("click", function () {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([asText()], { type: "text/markdown" }));
    a.download = tr("marketing-decision-map.md", "营销决策地图.md"); document.body.appendChild(a); a.click(); a.remove();
    track("download");
  });
  $("dm-print").addEventListener("click", function () { track("print"); window.print(); });
  $("dm-reset").addEventListener("click", function () {
    try { localStorage.removeItem(LS); } catch (e) {}
    state = load(); renderPick(); update(); status(tr("Reset to the starter set.", "已恢复为初始设置。"));
  });

  function update() { renderScore(); renderMap(); renderBriefs(); save(); }
  renderPick(); update();
})();
