/* Flow AI dot. The amber dot at the head of the mark is Flow Intelligence: a light
   core with two eyes where the light is absent. The cream dots are the agents, and
   they are solid, because agents do tangible work.

   One file, no dependencies. Mount on an <svg viewBox="0 0 100 100"> and it does the
   rest: spring gaze, saccades, eyes-lead-body-follows tilt, perspective, anticipated
   double blink, breathing, nod, the review ring, the dark state after ten at night in
   Auckland. One shared animation loop, paused for dots that are off screen.

   Decorative and fail-safe: every SVG it mounts into is empty or holds a static dot,
   so a blocked script changes nothing a visitor needs. The boot section at the end
   wires the demo window, the 404 and the night state on this site. */

window.FlowDot = (function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var INK = '#0e0e0d', CREAM = '#faf8f3', AMBER = '#e4a43c';
  function el(n, a) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); return e; }

  /* Shared gradients and filters, injected once. */
  var defsDone = false;
  function defs() {
    if (defsDone || !document.body) return; defsDone = true;
    var svg = el('svg', { width: 0, height: 0, 'aria-hidden': 'true', style: 'position:absolute;width:0;height:0' });
    svg.innerHTML =
      '<defs>' +
      '<radialGradient id="flowdot-core" cx="50%" cy="46%" r="50%"><stop offset="0" stop-color="#fff2d2"/><stop offset=".38" stop-color="#f3c572"/><stop offset=".72" stop-color="#e4a43c"/><stop offset=".9" stop-color="#e4a43c" stop-opacity=".85"/><stop offset="1" stop-color="#e4a43c" stop-opacity="0"/></radialGradient>' +
      '<radialGradient id="flowdot-halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#e4a43c" stop-opacity=".42"/><stop offset=".45" stop-color="#e4a43c" stop-opacity=".14"/><stop offset="1" stop-color="#e4a43c" stop-opacity="0"/></radialGradient>' +
      '<radialGradient id="flowdot-core-night" cx="50%" cy="46%" r="50%"><stop offset="0" stop-color="#2a2518"/><stop offset=".6" stop-color="#151410"/><stop offset=".92" stop-color="#121211" stop-opacity=".9"/><stop offset="1" stop-color="#121211" stop-opacity="0"/></radialGradient>' +
      '<radialGradient id="flowdot-halo-night" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#e4a43c" stop-opacity=".08"/><stop offset="1" stop-color="#e4a43c" stop-opacity="0"/></radialGradient>' +
      '<filter id="flowdot-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.2"/></filter>' +
      '</defs>';
    document.body.appendChild(svg);
  }

  /* Eye styles: draw one eye at the origin for base size s and scale k; pos is where
     the two eyes sit as fractions of the body radius; ratio makes the right eye larger. */
  var STYLES = {
    round:  { pos: [[-0.29, -0.12], [0.29, -0.12]], ratio: 1.2, draw: function (s, k) { return el('ellipse', { rx: s * k, ry: s * 1.06 * k }); } },
    high:   { pos: [[-0.44, -0.36], [0.14, -0.36]], ratio: 1.2, draw: function (s, k) { return el('ellipse', { rx: s * k, ry: s * 1.06 * k }); } },
    pill:   { pos: [[-0.3, -0.1], [0.3, -0.1]], ratio: 1.15, draw: function (s, k) { var w = s * 1.3 * k, h = s * 2.6 * k; return el('rect', { x: -w / 2, y: -h / 2, width: w, height: h, rx: w / 2 }); } },
    wide:   { pos: [[-0.32, -0.1], [0.32, -0.1]], ratio: 1.15, draw: function (s, k) { return el('ellipse', { rx: s * 1.5 * k, ry: s * 0.78 * k }); } },
    arc:    { pos: [[-0.3, -0.06], [0.3, -0.06]], ratio: 1.15, draw: function (s, k) { var a = s * 1.25 * k; return el('path', { d: 'M' + (-a) + ' 0A' + a + ' ' + a + ' 0 0 1 ' + a + ' 0Z' }); } },
    sly:    { pos: [[-0.3, -0.14], [0.3, -0.14]], ratio: 1.15, draw: function (s, k) { var a = s * 1.25 * k; return el('path', { d: 'M' + (-a) + ' 0A' + a + ' ' + a + ' 0 0 0 ' + a + ' 0Z' }); } },
    lens:   { pos: [[-0.32, -0.12], [0.32, -0.12]], ratio: 1.2, ring: true, draw: function (s, k) { var g = el('g', {}); g.appendChild(el('circle', { r: s * 1.15 * k, fill: 'none', 'stroke-width': s * 0.42 * k })); g.appendChild(el('circle', { r: s * 0.42 * k })); return g; } },
    slit:   { pos: [[-0.3, -0.12], [0.3, -0.12]], ratio: 1.3, draw: function (s, k) { var w = s * 2.3 * k, h = s * 0.55 * k; return el('rect', { x: -w / 2, y: -h / 2, width: w, height: h, rx: h / 2 }); } },
    bean:   { pos: [[-0.3, -0.12], [0.3, -0.12]], ratio: 1.2, draw: function (s, k, side) { return el('ellipse', { rx: s * 1.2 * k, ry: s * 0.8 * k, transform: 'rotate(' + (side === 'L' ? 28 : -28) + ')' }); } },
    odd:    { pos: [[-0.3, -0.12], [0.32, -0.12]], ratio: 2.4, draw: function (s, k) { return el('ellipse', { rx: s * 0.75 * k, ry: s * 0.8 * k }); } },
    square: { pos: [[-0.3, -0.12], [0.3, -0.12]], ratio: 1.15, draw: function (s, k) { var w = s * 1.9 * k; return el('rect', { x: -w / 2, y: -w / 2, width: w, height: w, rx: w * 0.26 }); } },
    one:    { pos: [[0, -0.12], null], ratio: 1, ring: true, draw: function (s, k) { var g = el('g', {}); g.appendChild(el('circle', { r: s * 1.7 * k, fill: 'none', 'stroke-width': s * 0.5 * k })); g.appendChild(el('circle', { r: s * 0.65 * k })); return g; } }
  };
  var AGENTS = { 'positioning': 'sly', 'ai-search': 'lens', 'search': 'lens', 'content': 'pill', 'social': 'bean', 'outbound': 'odd', 'growth': 'wide', 'launch': 'high', 'paid': 'square', 'community': 'arc', 'reporting': 'slit', 'report': 'slit', 'content-qa': 'slit' };
  var MOODS = {
    idle:   { free: true,  k: 1,    lid: 1,    tilt: 0,  body: AMBER, eye: INK,   breath: 0.012, rate: 1.6, ring: false, orbit: false, scan: false, glow: false },
    think:  { look: [-0.7, -0.9],   k: 0.92, lid: 1,    tilt: -7, body: AMBER, eye: INK,   breath: 0.01,  rate: 1.6, ring: false, orbit: false, scan: false, glow: false },
    work:   { look: [0.5, 0.6],     k: 0.9,  lid: 1,    tilt: 4,  body: AMBER, eye: INK,   breath: 0.035, rate: 9,   ring: false, orbit: true,  scan: true,  glow: false },
    review: { look: [0, 0],         k: 1.3,  lid: 1,    tilt: 0,  body: AMBER, eye: INK,   breath: 0.02,  rate: 2.2, ring: true,  orbit: false, scan: false, glow: false },
    done:   { look: [0, 0.1],       k: 1.1,  lid: 0.42, tilt: 0,  body: AMBER, eye: INK,   breath: 0.02,  rate: 1.6, ring: false, orbit: false, scan: false, glow: false },
    late:   { free: true,  k: 1.15, lid: 1,    tilt: 0,  body: '#131312', eye: CREAM, breath: 0.01, rate: 1.2, ring: false, orbit: false, scan: false, glow: true },
    error:  { look: [0.3, 0.3],     k: 1,    lid: 0.3,  tilt: 9,  body: AMBER, eye: INK,   breath: 0,     rate: 1,   ring: false, orbit: false, scan: false, glow: false }
  };
  function hash(s) { var h = 2166136261; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function paint(node, color, glow) {
    var list = node.tagName === 'g' ? Array.prototype.slice.call(node.children) : [node];
    list.forEach(function (n) {
      if (n.getAttribute('fill') === 'none') n.setAttribute('stroke', color); else n.setAttribute('fill', color);
      if (glow) n.setAttribute('filter', 'url(#flowdot-glow)'); else n.removeAttribute('filter');
    });
  }
  function spring(st, target, k, d, dt) { var a = (target - st.x) * k - st.v * d; st.v += a * dt; st.x += st.v * dt; }

  var dots = [], running = false;
  function Dot(svg, o) {
    o = o || {}; defs();
    this.svg = svg; this.role = o.role || 'flow';
    this.r = o.r || (this.role === 'flow' ? 32 : 34);
    this.cx = 50; this.cy = 50 + (o.dy || 0);
    this.fill = o.fill || (this.role === 'flow' ? AMBER : CREAM);
    var styleName = o.style || (this.role === 'agent' ? (AGENTS[o.agent] || null) : 'high');
    this.sig = { gapK: 1, yK: 0, tilt: 0, ratioK: 1 };
    if (!styleName) { var h = hash(o.agent || 'agent'), u = function (n) { return ((h >>> (n * 5)) & 31) / 31; }; styleName = 'round'; this.sig = { gapK: 0.78 + u(0) * 0.5, ratioK: 0.9 + u(1) * 0.35, yK: -0.14 + u(2) * 0.26, tilt: -8 + u(3) * 16 }; }
    this.styleName = styleName;
    this.catch = o.catchlight !== false;
    this.dbl = o.dbl !== false;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    this.glow = this.role === 'flow' && o.glow !== false;
    this.gooG = el('g', {});
    this.halo = el('circle', { cx: this.cx, cy: this.cy, r: this.r * 2.1, fill: 'url(#flowdot-halo)', opacity: this.glow ? 1 : 0 });
    this.body = el('circle', { cx: this.cx, cy: this.cy, r: this.glow ? this.r * 1.08 : this.r, fill: this.glow ? 'url(#flowdot-core)' : this.fill });
    this.sats = [];
    if (this.role === 'flow') for (var i = 0; i < 3; i++) { var s = el('circle', { cx: this.cx, cy: this.cy, r: 0, fill: CREAM }); this.sats.push(s); this.gooG.appendChild(s); }
    svg.appendChild(this.halo); svg.appendChild(this.gooG); svg.appendChild(this.body);
    if (this.glow) this.catch = false;
    this.ring = el('circle', { cx: this.cx, cy: this.cy, r: this.r, fill: 'none', stroke: AMBER, 'stroke-width': 1.5, 'stroke-opacity': 0 });
    svg.appendChild(this.ring);
    this.eyes = el('g', {}); this.L = el('g', {}); this.R = el('g', {}); this.eyes.appendChild(this.L); this.eyes.appendChild(this.R); svg.appendChild(this.eyes);
    this.gaze = { x: { x: 0, v: 0 }, y: { x: 0, v: 0 } };
    this.tiltS = { x: 0, v: 0 };
    this.target = [0, 0]; this.hold = null; this.t = Math.random() * 10; this.nextSac = 1 + Math.random() * 2; this.nextBlink = 2 + Math.random() * 3;
    this.nodT = -1; this.lidT = -1; this.mood = 'idle';
    this.setStyle(styleName);
    this.set(o.state || 'idle');
    dots.push(this); start();
  }
  Dot.prototype.setStyle = function (name) {
    var st = STYLES[name] || STYLES.round, m = MOODS[this.mood] || MOODS.idle, s = this.r * 0.17;
    this.styleName = name; this.st = st;
    while (this.L.firstChild) this.L.removeChild(this.L.firstChild);
    while (this.R.firstChild) this.R.removeChild(this.R.firstChild);
    var nL = st.draw(s, 1 * this.sig.ratioK, 'L'); paint(nL, m.eye, m.glow); this.L.appendChild(nL);
    if (st.pos[1]) { var nR = st.draw(s, st.ratio * this.sig.ratioK, 'R'); paint(nR, m.eye, m.glow); this.R.appendChild(nR); }
    if (this.catch && !st.ring && m.eye === INK) {
      this.cL = el('circle', { cx: -s * 0.36, cy: -s * 0.42, r: s * 0.2, fill: CREAM }); this.L.appendChild(this.cL);
      if (st.pos[1]) { this.cR = el('circle', { cx: -s * 0.42, cy: -s * 0.5, r: s * 0.24, fill: CREAM }); this.R.appendChild(this.cR); }
    } else { this.cL = this.cR = null; }
    return this;
  };
  Dot.prototype.set = function (mood) {
    var m = MOODS[mood] || MOODS.idle; this.mood = mood;
    if (this.glow) { var night = mood === 'late'; this.body.setAttribute('fill', night ? 'url(#flowdot-core-night)' : 'url(#flowdot-core)'); this.halo.setAttribute('fill', night ? 'url(#flowdot-halo-night)' : 'url(#flowdot-halo)'); }
    else this.body.setAttribute('fill', mood === 'late' ? m.body : (this.role === 'agent' ? this.fill : m.body));
    this.ring.setAttribute('stroke-opacity', 0);
    if (!m.orbit) this.sats.forEach(function (s) { s.setAttribute('r', 0); });
    if (mood === 'done') this.nod();
    this.setStyle(this.styleName);
    return this;
  };
  Dot.prototype.setGlow = function (on) { this.glow = !!on; this.catch = !this.glow; this.halo.setAttribute('opacity', this.glow ? 1 : 0); this.body.setAttribute('r', this.glow ? this.r * 1.08 : this.r); return this.set(this.mood); };
  Dot.prototype.lookAt = function (x, y) { this.hold = x === null ? null : [x, y]; return this; };
  Dot.prototype.nod = function () { this.nodT = 0; return this; };
  Dot.prototype.blink = function (twice) { if (!reduced) { this.lidT = 0; this.lidTwice = !!twice; } return this; };
  Dot.prototype.step = function (dt) {
    var m = MOODS[this.mood] || MOODS.idle, st = this.st, r = this.r; this.t += dt;
    var tgt;
    if (this.hold) tgt = this.hold;
    else if (m.scan && !reduced) { var u = (this.t * 0.9) % 1, line = Math.floor((this.t * 0.9) % 3); tgt = [-0.8 + u * 1.6, -0.25 + line * 0.35]; }
    else if (m.look) tgt = m.look;
    else { this.nextSac -= dt; if (this.nextSac <= 0 && !reduced) { this.target = [(Math.random() - 0.5), (Math.random() - 0.5) * 0.7]; this.nextSac = 1.5 + Math.random() * 2.5; } tgt = this.target; }
    if (reduced) { this.gaze.x.x = tgt[0]; this.gaze.y.x = tgt[1]; }
    else if (m.scan && !this.hold) { this.gaze.x.x = tgt[0]; spring(this.gaze.y, tgt[1], 140, 18, dt); }
    else { spring(this.gaze.x, tgt[0], 140, 18, dt); spring(this.gaze.y, tgt[1], 140, 18, dt); }
    var gx = Math.max(-1, Math.min(1, this.gaze.x.x)), gy = Math.max(-1, Math.min(1, this.gaze.y.x));
    spring(this.tiltS, gx * 6 + m.tilt, 40, 10, dt);
    var breathe = reduced ? 0 : Math.sin(this.t * m.rate) * m.breath;
    var nodY = 0, nodSq = 0, nodLid = 1;
    if (this.nodT >= 0) { this.nodT += dt; var p = Math.min(this.nodT / 0.6, 1), w = Math.sin(p * Math.PI); nodY = w * r * 0.1; nodSq = w * 0.1; nodLid = 1 - w * 0.6; if (this.nodT > 0.6) this.nodT = -1; }
    var sx = 1 + breathe + nodSq, sy = 1 - breathe - nodSq;
    var bodyTf = 'rotate(' + this.tiltS.x + ' ' + this.cx + ' ' + this.cy + ') translate(' + this.cx + ' ' + (this.cy + nodY) + ') scale(' + sx + ' ' + sy + ') translate(' + (-this.cx) + ' ' + (-this.cy) + ')';
    this.body.setAttribute('transform', bodyTf);
    if (this.glow) { var pulse = reduced ? 1 : 0.85 + 0.15 * Math.sin(this.t * m.rate * 0.5) + (m.ring ? 0.15 : 0); this.halo.setAttribute('opacity', pulse); this.halo.setAttribute('transform', 'translate(' + this.cx + ' ' + (this.cy + nodY) + ') scale(' + (1 + breathe * 2) + ') translate(' + (-this.cx) + ' ' + (-this.cy) + ')'); }
    var lid = 1;
    if (!reduced) {
      if (this.lidT < 0) { this.nextBlink -= dt; if (this.nextBlink <= 0) { this.lidT = 0; this.lidTwice = this.dbl; this.nextBlink = 3 + Math.random() * 3; } }
      if (this.lidT >= 0) {
        var T = this.lidT; this.lidT += dt;
        var one = function (x) { if (x < 0.06) return 1.04; if (x < 0.13) return 1 - (x - 0.06) / 0.07 * 0.92; if (x < 0.27) return 0.08 + (x - 0.13) / 0.14 * 0.92; return 1; };
        lid = one(T); if (this.lidTwice && T > 0.26) lid = one(T - 0.26);
        if (T > (this.lidTwice ? 0.54 : 0.28)) this.lidT = -1;
      }
    }
    lid = Math.min(lid, m.lid) * nodLid;
    if (gy > 0) lid *= 1 - gy * 0.15;
    var ox = gx * r * 0.18, oy = gy * r * 0.14 + nodY;
    var pL = [this.cx + st.pos[0][0] * r * this.sig.gapK, this.cy + (st.pos[0][1] + this.sig.yK) * r];
    var kL = m.k * (1 - Math.max(0, gx) * 0.12 + Math.max(0, -gx) * 0.06), kR = m.k * (1 - Math.max(0, -gx) * 0.12 + Math.max(0, gx) * 0.06);
    var rot = 'rotate(' + (this.tiltS.x + this.sig.tilt) + ' ' + this.cx + ' ' + this.cy + ') ';
    var s = r * 0.17;
    this.L.setAttribute('transform', rot + 'translate(' + (pL[0] + ox) + ' ' + (pL[1] + oy) + ') translate(0 ' + (-s) + ') scale(' + kL + ' ' + (kL * lid) + ') translate(0 ' + s + ')');
    if (st.pos[1]) { var pR = [this.cx + st.pos[1][0] * r * this.sig.gapK, this.cy + (st.pos[1][1] + this.sig.yK) * r]; this.R.setAttribute('transform', rot + 'translate(' + (pR[0] + ox) + ' ' + (pR[1] + oy) + ') translate(0 ' + (-s) + ') scale(' + kR + ' ' + (kR * lid) + ') translate(0 ' + s + ')'); }
    if (this.cL) { var cv = lid > 0.5 ? 1 : 0; this.cL.setAttribute('opacity', cv); if (this.cR) this.cR.setAttribute('opacity', cv); }
    if (m.ring) { var ph = Math.sin(this.t * 2.2); this.ring.setAttribute('r', r + 12 + ph * 6); this.ring.setAttribute('stroke-opacity', 0.55 - ph * 0.35); }
    if (m.orbit && !reduced) { var self = this; this.sats.forEach(function (sat, i) { var a = self.t * 1.4 + i * (Math.PI * 2 / 3), rad = r * 1.55 + Math.sin(self.t * 2 + i) * r * 0.15; sat.setAttribute('r', r * 0.19 + Math.sin(self.t * 3 + i) * r * 0.05); sat.setAttribute('cx', self.cx + Math.cos(a) * rad); sat.setAttribute('cy', self.cy + Math.sin(a) * rad * 0.9); }); }
  };
  var last = 0;
  function loop(now) {
    var dt = Math.min(0.05, (now - last) / 1000 || 0.016); last = now;
    for (var i = 0; i < dots.length; i++) { var d = dots[i]; var rect = d.svg.getBoundingClientRect(); if (rect.bottom < -50 || rect.top > innerHeight + 50) continue; d.step(dt); }
    requestAnimationFrame(loop);
  }
  function start() { if (running) return; running = true; requestAnimationFrame(loop); }
  function mount(svg, o) { return new Dot(svg, o); }
  function isNightNZ() { try { var h = parseInt(new Intl.DateTimeFormat('en-NZ', { hour: 'numeric', hour12: false, timeZone: 'Pacific/Auckland' }).format(new Date()), 10); return h >= 22 || h < 6; } catch (e) { return false; } }
  function autoNight(dot) {
    function check() { var n = isNightNZ(); if (n && dot.mood === 'idle') dot.set('late'); else if (!n && dot.mood === 'late') dot.set('idle'); }
    check(); setInterval(check, 60000); return dot;
  }
  function make(cls, size) { var svg = el('svg', { viewBox: '0 0 100 100', 'aria-hidden': 'true', focusable: 'false' }); svg.setAttribute('class', 'fdot ' + (cls || '')); if (size) { svg.setAttribute('width', size); svg.setAttribute('height', size); } return svg; }
  return { mount: mount, make: make, autoNight: autoNight, isNightNZ: isNightNZ, STYLES: STYLES, AGENTS: AGENTS, MOODS: MOODS, Dot: Dot };
}());

/* ---------- boot: this site ---------- */
(function () {
  'use strict';
  function ready(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn, { once: true }); else fn(); }
  ready(function () {
    var F = window.FlowDot; if (!F) return;

    /* The demo window: Flow Intelligence beside the run status, a core in the sidebar
       that keeps Auckland hours, and each run under Recents carrying its agent's dot. */
    var demo = document.querySelector('[data-demo]');
    if (demo) {
      demo.classList.add('has-fdot');
      var statusEl = demo.querySelector('.demo__status');
      if (statusEl && statusEl.parentNode) {
        var sv = F.make('fdot--status'); statusEl.parentNode.insertBefore(sv, statusEl);
        var fi = F.mount(sv, { role: 'flow', style: 'high', r: 36, state: 'review' });
        var moodFor = function (text) {
          var t = (text || '').trim();
          if (/working|running|运行中/i.test(t)) return 'work';
          if (/review|审核/i.test(t)) return 'review';
          if (/paused|暂停/i.test(t)) return 'think';
          return 'done';
        };
        var apply = function () { var mood = moodFor(statusEl.textContent); if (fi.mood !== mood) { fi.set(mood); if (mood === 'done') setTimeout(function () { if (fi.mood === 'done') fi.set('idle'); }, 2600); } };
        apply();
        new MutationObserver(apply).observe(statusEl, { childList: true, characterData: true, subtree: true });
      }
      var here = demo.querySelector('.demo__nav.is-here');
      if (here) { var hv = F.make('fdot--side'); here.insertBefore(hv, here.firstChild); F.autoNight(F.mount(hv, { role: 'flow', style: 'high', r: 36 })); }
      Array.prototype.slice.call(demo.querySelectorAll('[data-run]')).forEach(function (b) {
        var key = b.getAttribute('data-run'), av = F.make('fdot--run'); b.insertBefore(av, b.firstChild);
        var d = F.mount(av, { role: 'agent', agent: key, r: 36 });
        b.addEventListener('mouseenter', function () { d.lookAt(0, 0.2); d.blink(true); setTimeout(function () { d.lookAt(null); }, 1200); });
      });
    }

    /* The 404: it looks left, then right, then at you. */
    var lost = document.querySelector('[data-fdot-lost]');
    if (lost) {
      var d = F.mount(lost, { role: 'flow', style: 'high', r: 30 });
      var seq = [[-0.9, 0], [0.9, 0], [0, 0], null], i = 0;
      setInterval(function () { var s = seq[i % 4]; if (s) d.lookAt(s[0], s[1]); else d.lookAt(null); i++; }, 1100);
      F.autoNight(d);
    }

    /* Any other opt-in: <svg data-fdot="flow|agent" data-agent="ai-search" data-state="idle"> */
    Array.prototype.slice.call(document.querySelectorAll('svg[data-fdot]')).forEach(function (svg) {
      F.mount(svg, { role: svg.getAttribute('data-fdot') === 'agent' ? 'agent' : 'flow', agent: svg.getAttribute('data-agent') || undefined, style: svg.getAttribute('data-style') || undefined, state: svg.getAttribute('data-state') || 'idle', r: 34 });
    });
  });
}());
