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
      '<filter id="flowdot-goo" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur in="SourceGraphic" stdDeviation="2.2" result="b"/><feColorMatrix in="b" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -10" result="g"/><feComposite in="SourceGraphic" in2="g" operator="atop"/></filter>' +
      '</defs>';
    document.body.appendChild(svg);
  }

  /* Eye styles: draw one eye at the origin for base size s and scale k; pos is where
     the two eyes sit as fractions of the body radius; ratio makes the right eye larger. */
  var STYLES = {
    round:  { pos: [[-0.29, -0.12], [0.29, -0.12]], ratio: 1.2, draw: function (s, k) { return el('ellipse', { rx: s * k, ry: s * 1.06 * k }); } },
    high:   { pos: [[-0.44, -0.36], [0.14, -0.36]], ratio: 1.2, draw: function (s, k) { return el('ellipse', { rx: s * k, ry: s * 1.06 * k }); } },
    /* The cute one: big round eyes, set low and wide, a touch left of centre. */
    cute:   { pos: [[-0.36, -0.02], [0.24, -0.02]], ratio: 1.18, size: 1.34, draw: function (s, k) { return el('ellipse', { rx: s * k, ry: s * 1.08 * k }); } },
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
    done:   { look: [0, 0.1],       k: 1.1,  lid: 1,    tilt: 0,  body: AMBER, eye: INK,   breath: 0.02,  rate: 1.6, ring: false, orbit: false, scan: false, glow: false, eyeStyle: 'arc' },
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
    var styleName = o.style || (this.role === 'agent' ? (AGENTS[o.agent] || null) : 'cute');
    this.sig = { gapK: 1, yK: 0, tilt: 0, ratioK: 1 };
    if (!styleName) { var h = hash(o.agent || 'agent'), u = function (n) { return ((h >>> (n * 5)) & 31) / 31; }; styleName = 'round'; this.sig = { gapK: 0.78 + u(0) * 0.5, ratioK: 0.9 + u(1) * 0.35, yK: -0.14 + u(2) * 0.26, tilt: -8 + u(3) * 16 }; }
    this.styleName = styleName;
    this.catch = o.catchlight !== false;
    this.dbl = o.dbl !== false;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    this.glow = this.role === 'flow' && o.glow !== false;
    this.gooG = el('g', {});
    if (o.goo) this.gooG.setAttribute('filter', 'url(#flowdot-goo)');
    this.halo = el('circle', { cx: this.cx, cy: this.cy, r: this.r * 2.1, fill: 'url(#flowdot-halo)', opacity: this.glow ? 1 : 0 });
    this.body = el('circle', { cx: this.cx, cy: this.cy, r: this.glow ? this.r * 1.08 : this.r, fill: this.glow ? 'url(#flowdot-core)' : this.fill });
    this.sats = [];
    if (this.role === 'flow') for (var i = 0; i < 3; i++) { var s = el('circle', { cx: this.cx, cy: this.cy, r: 0, fill: CREAM }); this.sats.push(s); this.gooG.appendChild(s); }
    svg.appendChild(this.halo); svg.appendChild(this.gooG); svg.appendChild(this.body);
    if (this.glow) this.catch = false;
    /* cheeks: a lighter amber, only when it is pleased */
    this.cheeks = el('g', { opacity: 0 });
    this.cheeks.appendChild(el('ellipse', { cx: this.cx - this.r * 0.46, cy: this.cy + this.r * 0.3, rx: this.r * 0.2, ry: this.r * 0.11, fill: '#f7d08a' }));
    this.cheeks.appendChild(el('ellipse', { cx: this.cx + this.r * 0.46, cy: this.cy + this.r * 0.3, rx: this.r * 0.2, ry: this.r * 0.11, fill: '#f7d08a' }));
    svg.appendChild(this.cheeks);
    this.cheekA = 0; this.wob = { x: 0, v: 0 }; this.trails = []; this.curious = 0; this.ticUntil = 0; this.nextTic = 8 + Math.random() * 8; this.seen = false;
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
    var st = STYLES[name] || STYLES.round, m = MOODS[this.mood] || MOODS.idle, s = this.r * 0.17 * (st.size || 1);
    var shape = (m.eyeStyle && STYLES[m.eyeStyle]) || st; /* a mood may borrow another style's eye shape, keeping this style's placement */
    this.styleName = name; this.st = st; this.gL = this.gR = null;
    while (this.L.firstChild) this.L.removeChild(this.L.firstChild);
    while (this.R.firstChild) this.R.removeChild(this.R.firstChild);
    var nL = shape.draw(s, 1 * this.sig.ratioK, 'L'); paint(nL, m.eye, m.glow); this.L.appendChild(nL);
    if (st.pos[1]) { var nR = shape.draw(s, st.ratio * this.sig.ratioK, 'R'); paint(nR, m.eye, m.glow); this.R.appendChild(nR); }
    if (this.catch && !st.ring && m.eye === INK) {
      this.cL = el('circle', { cx: -s * 0.36, cy: -s * 0.42, r: s * 0.2, fill: CREAM }); this.L.appendChild(this.cL);
      if (st.pos[1]) { this.cR = el('circle', { cx: -s * 0.42, cy: -s * 0.5, r: s * 0.24, fill: CREAM }); this.R.appendChild(this.cR); }
    } else { this.cL = this.cR = null; }
    /* the glint: the light reflected in the eye, one small cream point, upper left */
    if (this.glow && !st.ring && !shape.ring && m.eye === INK) {
      this.gL = el('circle', { cx: -s * 0.3, cy: -s * 0.34, r: s * 0.24, fill: CREAM }); this.L.appendChild(this.gL);
      if (st.pos[1]) { this.gR = el('circle', { cx: -s * 0.34, cy: -s * 0.4, r: s * 0.27, fill: CREAM }); this.R.appendChild(this.gR); }
    }
    return this;
  };
  Dot.prototype.set = function (mood) {
    var m = MOODS[mood] || MOODS.idle; this.mood = mood;
    if (this.glow) { var night = mood === 'late'; this.body.setAttribute('fill', night ? 'url(#flowdot-core-night)' : 'url(#flowdot-core)'); this.halo.setAttribute('fill', night ? 'url(#flowdot-halo-night)' : 'url(#flowdot-halo)'); }
    else this.body.setAttribute('fill', mood === 'late' ? m.body : (this.role === 'agent' ? this.fill : m.body));
    this.ring.setAttribute('stroke-opacity', 0);
    if (!m.orbit) this.sats.forEach(function (s) { s.setAttribute('r', 0); });
    if (mood === 'done') this.nod();
    if (this.st) { this.wob.v += 2.4; if (mood === 'work' || mood === 'done') this.trail(); }
    this.setStyle(this.styleName);
    return this;
  };
  /* the signature: when it moves, it leaves the mark's trail behind for a moment */
  Dot.prototype.trail = function () {
    if (reduced) return this;
    var self = this, now = performance.now();
    [[0.95, 0.3], [1.55, 0.22], [2.15, 0.15]].forEach(function (q, i) {
      var c = el('circle', { cx: self.cx, cy: self.cy, r: 0, fill: CREAM, opacity: 0 }); self.gooG.appendChild(c);
      self.trails.push({ el: c, t0: now + i * 70, d: q[0] * self.r, rr: q[1] * self.r });
    });
    return this;
  };
  Dot.prototype.greet = function () { this.nod(); this.blink(true); this.wob.v += 3; this.trail(); return this; };
  Dot.prototype.hover = function (on) { this.curious = on ? 1 : 0; return this; };
  /* the shy glance: looks at you, looks away, looks back */
  Dot.prototype.shy = function () {
    var self = this; self.lookAt(0, 0.12); self.blink(true);
    setTimeout(function () { if (self.curious) self.lookAt(-0.95, 0.4); }, 700);
    setTimeout(function () { if (self.curious) self.lookAt(0.05, 0); }, 1350);
    setTimeout(function () { if (self.curious) self.blink(false); }, 1500);
    return this;
  };
  Dot.prototype.attach = function (host) {
    var self = this;
    host.addEventListener('pointerenter', function () { self.hover(true); self.shy(); });
    host.addEventListener('pointerleave', function () { self.hover(false); self.lookAt(null); });
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
    else {
      this.nextSac -= dt; this.nextTic -= dt;
      if (this.nextTic <= 0 && !reduced) { this.ticUntil = this.t + 0.9; this.nextTic = 10 + Math.random() * 8; }
      if (this.t < this.ticUntil) tgt = [-0.6, -0.85];
      else { if (this.nextSac <= 0 && !reduced) { this.target = [(Math.random() - 0.5), (Math.random() - 0.5) * 0.7]; this.nextSac = 1.5 + Math.random() * 2.5; } tgt = this.target; }
    }
    if (reduced) { this.gaze.x.x = tgt[0]; this.gaze.y.x = tgt[1]; }
    else if (m.scan && !this.hold) { this.gaze.x.x = tgt[0]; spring(this.gaze.y, tgt[1], 140, 18, dt); }
    else { spring(this.gaze.x, tgt[0], 140, 18, dt); spring(this.gaze.y, tgt[1], 140, 18, dt); }
    var gx = Math.max(-1, Math.min(1, this.gaze.x.x)), gy = Math.max(-1, Math.min(1, this.gaze.y.x));
    spring(this.tiltS, gx * 6 + m.tilt + this.curious * 9, 40, 10, dt);
    spring(this.wob, 0, 90, 7, dt);
    var breathe = reduced ? 0 : Math.sin(this.t * m.rate) * m.breath;
    var wobble = reduced ? 0 : this.wob.x * 0.05;
    var cheekTarget = (this.mood === 'done' ? 0.6 : 0) + this.curious * 0.45; this.cheekA += (Math.min(0.6, cheekTarget) - this.cheekA) * Math.min(1, dt * 6); this.cheeks.setAttribute('opacity', this.cheekA);
    var nodY = 0, nodSq = 0, nodLid = 1;
    if (this.nodT >= 0) { this.nodT += dt; var p = Math.min(this.nodT / 0.6, 1), w = Math.sin(p * Math.PI); nodY = w * r * 0.1; nodSq = w * 0.1; nodLid = 1 - w * 0.6; if (this.nodT > 0.6) this.nodT = -1; }
    var sx = 1 + breathe + nodSq + wobble, sy = 1 - breathe - nodSq - wobble;
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
    var kc = m.k * (1 + this.curious * 0.1);
    var kL = kc * (1 - Math.max(0, gx) * 0.12 + Math.max(0, -gx) * 0.06), kR = kc * (1 - Math.max(0, -gx) * 0.12 + Math.max(0, gx) * 0.06);
    var rot = 'rotate(' + (this.tiltS.x + this.sig.tilt) + ' ' + this.cx + ' ' + this.cy + ') ';
    var s = r * 0.17 * (st.size || 1);
    this.cheeks.setAttribute('transform', 'translate(0 ' + nodY + ')');
    this.L.setAttribute('transform', rot + 'translate(' + (pL[0] + ox) + ' ' + (pL[1] + oy) + ') translate(0 ' + (-s) + ') scale(' + kL + ' ' + (kL * lid) + ') translate(0 ' + s + ')');
    if (st.pos[1]) { var pR = [this.cx + st.pos[1][0] * r * this.sig.gapK, this.cy + (st.pos[1][1] + this.sig.yK) * r]; this.R.setAttribute('transform', rot + 'translate(' + (pR[0] + ox) + ' ' + (pR[1] + oy) + ') translate(0 ' + (-s) + ') scale(' + kR + ' ' + (kR * lid) + ') translate(0 ' + s + ')'); }
    if (this.cL) { var cv = lid > 0.5 ? 1 : 0; this.cL.setAttribute('opacity', cv); if (this.cR) this.cR.setAttribute('opacity', cv); }
    if (this.gL) { var gv = lid > 0.5 ? 1 : 0; this.gL.setAttribute('opacity', gv); if (this.gR) this.gR.setAttribute('opacity', gv); }
    if (this.trails.length) {
      var now = performance.now(), keep = [];
      for (var ti = 0; ti < this.trails.length; ti++) {
        var tr = this.trails[ti], pp = (now - tr.t0) / 850;
        if (pp < 0) { keep.push(tr); continue; }
        if (pp >= 1) { if (tr.el.parentNode) tr.el.parentNode.removeChild(tr.el); continue; }
        var dd = tr.d + pp * r * 0.5, ease = pp < 0.25 ? pp / 0.25 : 1 - (pp - 0.25) / 0.75;
        tr.el.setAttribute('cx', this.cx - dd * 0.83); tr.el.setAttribute('cy', this.cy + dd * 0.56 + nodY);
        tr.el.setAttribute('r', tr.rr * (0.6 + 0.4 * ease)); tr.el.setAttribute('opacity', 0.9 * ease);
        keep.push(tr);
      }
      this.trails = keep;
    }
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
  function greetOnSight(dot) {
    if (!('IntersectionObserver' in window)) return dot;
    var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { setTimeout(function () { dot.greet(); }, 350); io.disconnect(); } }, { threshold: 0.6 });
    io.observe(dot.svg); return dot;
  }
  function make(cls, size) { var svg = el('svg', { viewBox: '0 0 100 100', 'aria-hidden': 'true', focusable: 'false' }); svg.setAttribute('class', 'fdot ' + (cls || '')); if (size) { svg.setAttribute('width', size); svg.setAttribute('height', size); } return svg; }
  return { mount: mount, make: make, autoNight: autoNight, greetOnSight: greetOnSight, isNightNZ: isNightNZ, STYLES: STYLES, AGENTS: AGENTS, MOODS: MOODS, Dot: Dot };
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
        var fi = F.mount(sv, { role: 'flow', r: 36, state: 'review' }); fi.attach(statusEl.parentNode); F.greetOnSight(fi);
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
      if (here) { var hv = F.make('fdot--side'); here.insertBefore(hv, here.firstChild); var sd = F.autoNight(F.mount(hv, { role: 'flow', r: 36 })); sd.attach(here); F.greetOnSight(sd); }
      Array.prototype.slice.call(demo.querySelectorAll('[data-run]')).forEach(function (b) {
        var key = b.getAttribute('data-run'), av = F.make('fdot--run'); b.insertBefore(av, b.firstChild);
        var d = F.mount(av, { role: 'agent', agent: key, r: 36 });
        b.addEventListener('mouseenter', function () { d.lookAt(0, 0.2); d.blink(true); setTimeout(function () { d.lookAt(null); }, 1200); });
      });
    }

    /* The run: the first time the demo window comes into view, one job is told by the
       character alone, over the window, then it fades out and the live window takes over.
       Once per visit, never under reduced motion, skippable. */
    var win = demo && demo.querySelector('.demo__win');
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var seen = false; try { seen = sessionStorage.getItem('flowai-run') === '1'; } catch (e) {}
    if (win && !reduce && !seen && 'IntersectionObserver' in window) {
      var NS = 'http://www.w3.org/2000/svg';
      function sel(n, a) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); return e; }
      var ZH = /^zh/.test(document.documentElement.lang);
      var S = ZH ? {
        you: '找出人们向 AI 询问奥克兰热水缸的问题，修好应该回答这些问题的页面。全部暂存，先不发布。',
        reply: '三个页面已暂存。等待你审核。', ok: '看起来不错。定价页先留着，等我核对数字。', skip: '跳过', eyebrow: 'FLOW INTELLIGENCE · 一次运行',
        caps: ['收到指令', '阅读网站', '交代三个智能体', '智能体工作中', '智能体返回', '已暂存，等你', '已批准', '休息'],
        cards: [['/services/hot-water-cylinders', '6 处修改'], ['/faq/plumber-cost-auckland', '新页面'], ['/areas/north-shore', '4 处修改']]
      } : {
        you: 'Find the questions people ask AI about hot water cylinders in Auckland and fix the pages that should answer them. Stage everything, publish nothing.',
        reply: 'Three pages staged. Waiting for your review.', ok: 'Looks good. Hold the pricing page until I check the numbers.', skip: 'Skip', eyebrow: 'FLOW INTELLIGENCE · ONE RUN',
        caps: ['brief received', 'reading the site', 'briefing three agents', 'agents at work', 'agents return', 'staged, waiting for you', 'approved', 'rest'],
        cards: [['/services/hot-water-cylinders', '6 changes'], ['/faq/plumber-cost-auckland', 'New page'], ['/areas/north-shore', '4 changes']]
      };
      var ov = document.createElement('div'); ov.className = 'demo__run'; ov.setAttribute('role', 'presentation');
      ov.innerHTML = '<div class="demo__run-stage"><svg viewBox="0 0 100 100" aria-hidden="true" focusable="false"></svg>' +
        '<div class="demo__run-msg demo__run-msg--you">' + S.you + '</div>' +
        '<div class="demo__run-cards">' + S.cards.map(function (c) { return '<div class="demo__run-card"><span>' + c[0] + '</span><em>' + c[1] + '</em></div>'; }).join('') + '</div>' +
        '<div class="demo__run-msg demo__run-msg--dot">' + S.reply + '</div>' +
        '<div class="demo__run-msg demo__run-msg--ok">' + S.ok + '</div></div>' +
        '<div class="demo__run-foot"><div class="demo__run-row"><span class="demo__run-eyebrow">' + S.eyebrow + '</span><span class="demo__run-cap"></span><button type="button" class="demo__run-skip">' + S.skip + '</button></div><span class="demo__run-bar"><b></b></span></div>';
      win.appendChild(ov); document.documentElement.classList.add('fdot-run');
      var rsvg = ov.querySelector('svg'), m1 = ov.querySelector('.demo__run-msg--you'), m2 = ov.querySelector('.demo__run-msg--dot'), m3 = ov.querySelector('.demo__run-msg--ok');
      var cards = Array.prototype.slice.call(ov.querySelectorAll('.demo__run-card'));
      var capEl = ov.querySelector('.demo__run-cap'), barEl = ov.querySelector('.demo__run-bar b');
      var run = F.mount(rsvg, { role: 'flow', r: 15, dy: 6, goo: true });
      /* a flat amber disc inside the goo group, under the light core, so the agents pull
         off the core with a liquid neck instead of appearing beside it */
      run.gooG.insertBefore(sel('circle', { cx: run.cx, cy: run.cy, r: run.r * 0.98, fill: '#e4a43c' }), run.gooG.firstChild);
      /* the page it reads: six hairlines to the right of the core, one lit at a time */
      var lines = sel('g', { opacity: 0 }); rsvg.insertBefore(lines, rsvg.firstChild);
      var lineEls = [];
      for (var li = 0; li < 6; li++) { var ln = sel('rect', { x: 66, y: 36 + li * 5.2, width: li % 3 === 2 ? 18 : 26, height: 1.3, rx: 0.65, fill: '#faf8f3', 'fill-opacity': 0.16 }); lines.appendChild(ln); lineEls.push(ln); }
      var sats = run.sats, satT = [[22, 44, 5.5], [80, 40, 5], [30, 82, 4.5]], satAnim = null, t0 = -1, LEN = 19.5, fired = [], done = false, lineT = -1, lit = -1;
      var agentKeys = ['ai-search', 'content', 'outbound'], faces = [];
      function easeOut(x) { return 1 - Math.pow(1 - x, 3); }
      function showFaces(on) {
        if (on && !faces.length) {
          satT.forEach(function (p, i) {
            var inner = sel('svg', { x: p[0] - p[2] * 1.45, y: p[1] - p[2] * 1.45, width: p[2] * 2.9, height: p[2] * 2.9, viewBox: '0 0 100 100' });
            rsvg.appendChild(inner); var fd = F.mount(inner, { role: 'agent', agent: agentKeys[i], r: 34, state: 'work' }); faces.push({ svg: inner, dot: fd });
          });
        } else faces.forEach(function (f, i) { f.svg.setAttribute('opacity', on ? 1 : 0); if (!on) f.dot.set('idle'); });
        if (on) sats.forEach(function (s) { s.setAttribute('r', 0); });
      }
      var SCRIPT = [
        { at: 0,    i: 0, fn: function () { m1.classList.add('is-on'); run.lookAt(0.8, -0.9); setTimeout(function () { run.nod(); run.lookAt(null); }, 900); } },
        { at: 1.5,  i: 1, fn: function () { F.MOODS.work.orbit = false; run.set('work'); lines.setAttribute('opacity', 1); lineT = performance.now(); } },
        { at: 4.8,  i: 2, fn: function () { lines.setAttribute('opacity', 0); run.set('think'); satAnim = { t0: performance.now(), dir: 1 }; } },
        { at: 7.2,  i: 3, fn: function () { run.set('idle'); showFaces(true); faces.forEach(function (f) { f.dot.set('work'); }); } },
        { at: 10.6, i: 4, fn: function () { faces.forEach(function (f) { f.dot.set('done'); }); setTimeout(function () { showFaces(false); sats.forEach(function (s, i) { s.setAttribute('cx', satT[i][0]); s.setAttribute('cy', satT[i][1]); s.setAttribute('r', satT[i][2]); }); satAnim = { t0: performance.now(), dir: -1 }; }, 500); } },
        { at: 12.8, i: 5, fn: function () { run.trail(); run.set('review'); ov.classList.add('is-staged'); m2.classList.add('is-on'); cards.forEach(function (c, i) { setTimeout(function () { c.classList.add('is-on'); }, 150 + i * 160); }); } },
        { at: 16.2, i: 6, fn: function () { m2.classList.remove('is-on'); m3.classList.add('is-on'); run.lookAt(0.9, 0.6); setTimeout(function () { run.set('done'); run.lookAt(null); cards.forEach(function (c, i) { setTimeout(function () { c.classList.add('is-ok'); }, i * 140); }); }, 700); } },
        { at: 18.3, i: 7, fn: function () { run.set('idle'); } }
      ];
      function satFrame(now) {
        if (!satAnim) return;
        var tt = (now - satAnim.t0) / 1000;
        sats.forEach(function (s, i) {
          var local = Math.max(0, Math.min(1, (tt - i * 0.4) / 1.1)), e = easeOut(local), p = satAnim.dir > 0 ? e : 1 - e;
          var wob = Math.sin(now / 400 + i) * 1.5 * p;
          s.setAttribute('cx', run.cx + (satT[i][0] - run.cx) * p + wob); s.setAttribute('cy', run.cy + (satT[i][1] - run.cy) * p + Math.cos(now / 500 + i) * p); s.setAttribute('r', satT[i][2] * Math.min(1, 0.4 + p * 0.9));
        });
        if (tt > 2.2) { if (satAnim.dir < 0) { sats.forEach(function (s) { s.setAttribute('r', 0); }); run.wob.v += 2.5; } satAnim = null; }
      }
      function lineFrame(now) {
        if (lineT < 0) return;
        var idx = Math.floor((now - lineT) / 520) % 6;
        if (idx !== lit) { lit = idx; lineEls.forEach(function (l, i) { l.setAttribute('fill-opacity', i === idx ? 0.9 : (i < idx ? 0.42 : 0.16)); }); }
      }
      function finish() {
        if (done) return; done = true;
        try { sessionStorage.setItem('flowai-run', '1'); } catch (e) {}
        F.MOODS.work.orbit = true;
        ov.classList.add('is-done'); document.documentElement.classList.remove('fdot-run');
        setTimeout(function () { if (ov.parentNode) ov.parentNode.removeChild(ov); }, 700);
      }
      function frame(now) {
        if (done) return;
        if (t0 < 0) t0 = now;
        var tt = (now - t0) / 1000;
        barEl.style.width = Math.min(100, tt / LEN * 100) + '%';
        SCRIPT.forEach(function (s, i) { if (tt >= s.at && !fired[i]) { fired[i] = true; s.fn(); capEl.textContent = S.caps[s.i]; if (s.i !== 1) lineT = -1; } });
        satFrame(now); lineFrame(now);
        if (tt < LEN) requestAnimationFrame(frame); else finish();
      }
      ov.querySelector('.demo__run-skip').addEventListener('click', finish);
      var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { io.disconnect(); setTimeout(function () { requestAnimationFrame(frame); }, 400); } }, { threshold: 0.2 });
      io.observe(win);
    }

    /* The 404: it looks left, then right, then at you. */
    var lost = document.querySelector('[data-fdot-lost]');
    if (lost) {
      var d = F.mount(lost, { role: 'flow', r: 30 }); d.attach(lost.parentNode || lost); F.greetOnSight(d);
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
