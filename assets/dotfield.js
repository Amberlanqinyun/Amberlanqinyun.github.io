/* Flow AI dot field.

   A perspective-projected wave surface drawn as dots on a canvas: the web
   version of the particle layer in the card kit. Nearer dots are larger and
   brighter, far dots recede into the ground, and the surface drifts slowly.

   A section opts in with data-dotfield="hero" or data-dotfield="closer".
   The dots keep clear of the section's [data-dotfield-clear] element (its
   type zone) and fade out at the section's top and bottom edges, so the
   field reads as ground the content sits on, never as noise behind it.

   Pure decoration. The canvas is aria-hidden and ignores the pointer, the
   surface holds one static frame under prefers-reduced-motion, it draws only
   while its section is on screen, and the page never depends on it: a
   blocked script simply leaves the plain ground. */

(function () {
  'use strict';

  var hosts = Array.prototype.slice.call(document.querySelectorAll('[data-dotfield]'));
  if (!hosts.length) return;
  var probe = document.createElement('canvas');
  if (!probe.getContext) return;

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var TAU = Math.PI * 2;
  var D2R = Math.PI / 180;
  var INK = 'rgb(250, 248, 243)';
  var AMBER = 'rgb(228, 164, 60)';

  /* One surface per placement. Angles in degrees, positions as fractions of
     the host, dot radii in CSS pixels, alphas 0..1. */
  var PRESETS = {
    /* The hero: a wide surface seen from above, its far edge a ghost behind
       the flanks of the title, its near edge a bright band under the buttons
       that the portrait then rises out of. */
    hero: {
      cols: 160, rows: 64, amp: 0.26, f0: 1.3, f1: 0.9,
      yaw: -14, pitch: 34, cam: 2.3, fov: 0.95, rotate: -9,
      cx: 0.5, cy: 0.4, dx: 0.04, dy: 0, span: 8, depth: 5.6,
      rNear: 3.0, rFar: 0.5, aNear: 1, aFar: 0.12, crest: 0.8, speed: 0.04,
      top: [0, 0.12], bottom: [0.9, 1], pad: 32, fall: 120,
      signal: { row: 0.62, speed: 0.045 }
    },
    /* The split hero on the home page: short and wide, type left, portrait
       right. The surface is a ground under both, seen from a little higher,
       its bright edge running along the foot of the section. */
    'hero-wide': {
      cols: 190, rows: 60, amp: 0.26, f0: 1.3, f1: 0.9,
      yaw: -10, pitch: 32, cam: 2.4, fov: 0.9, rotate: -4,
      cx: 0.5, cy: 0.72, dx: 0.02, dy: 0, span: 9.5, depth: 3.8,
      rNear: 3.0, rFar: 0.5, aNear: 1, aFar: 0.12, crest: 0.8, speed: 0.04,
      top: [0.04, 0.3], bottom: [0.92, 1], pad: 28, fall: 110,
      signal: { row: 0.58, speed: 0.04 }
    },
    /* The closer: a floor of dots under the one amber button, rising to a
       horizon just behind it and dying out before the footer. */
    closer: {
      cols: 150, rows: 48, amp: 0.22, f0: 1.3, f1: 0.9,
      yaw: -8, pitch: 26, cam: 2.4, fov: 0.9, rotate: 0,
      cx: 0.5, cy: 1.02, dx: 0, dy: 0, span: 9.5, depth: 2.6,
      rNear: 2.8, rFar: 0.45, aNear: 0.9, aFar: 0.06, crest: 0.8, speed: 0.035,
      top: [0.5, 0.74], bottom: [0.96, 1], pad: 24, fall: 90,
      signal: { row: 0.5, speed: 0.05 }
    }
  };

  function smooth(x, a, b) {
    var t = (x - a) / (b - a);
    t = t < 0 ? 0 : t > 1 ? 1 : t;
    return t * t * (3 - 2 * t);
  }

  /* The union of the line boxes of every text node under el, relative to
     the host, so the clear zone hugs the ink rather than the element boxes. */
  function textExtent(el, rect) {
    if (!el || !document.createRange) return null;
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    var range = document.createRange(), node, box = null;
    while ((node = walker.nextNode())) {
      if (!/\S/.test(node.nodeValue)) continue;
      range.selectNodeContents(node);
      var rs = range.getClientRects();
      for (var i = 0; i < rs.length; i++) {
        var r = rs[i];
        if (!r.width || !r.height) continue;
        if (!box) box = { l: r.left, r: r.right, t: r.top, b: r.bottom };
        else {
          if (r.left < box.l) box.l = r.left; if (r.right > box.r) box.r = r.right;
          if (r.top < box.t) box.t = r.top; if (r.bottom > box.b) box.b = r.bottom;
        }
      }
    }
    if (!box) return null;
    return { l: box.l - rect.left, r: box.r - rect.left, t: box.t - rect.top, b: box.b - rect.top };
  }

  function Field(host) {
    var name = host.getAttribute('data-dotfield') || 'hero';
    this.host = host;
    this.p = PRESETS[name] || PRESETS.hero;
    this.clear = host.querySelector('[data-dotfield-clear]');
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'dotfield';
    this.canvas.setAttribute('aria-hidden', 'true');
    host.insertBefore(this.canvas, host.firstChild);
    this.ctx = this.canvas.getContext('2d');
    this.t = 0;
    this.ddx = 0; this.ddy = 0;   /* eased drift toward the pointer */
    this.lx = null; this.ly = null; /* pointer, in host pixels */
    this.resize();
  }

  Field.prototype.resize = function () {
    var rect = this.host.getBoundingClientRect();
    this.w = Math.max(1, Math.round(rect.width));
    this.h = Math.max(1, Math.round(rect.height));
    this.dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    this.canvas.width = Math.round(this.w * this.dpr);
    this.canvas.height = Math.round(this.h * this.dpr);
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);

    this.zone = textExtent(this.clear, rect);

    var small = this.w < 720;
    this.cols = small ? Math.round(this.p.cols * 0.55) : this.p.cols;
    this.rows = small ? Math.round(this.p.rows * 0.65) : this.p.rows;
    var n = this.cols * this.rows;
    this.zc = new Float32Array(n);
    this.yy = new Float32Array(n);
    this.sx = new Float32Array(n);
    this.sy = new Float32Array(n);
    this.jitter = new Float32Array(n);
    for (var i = 0; i < n; i++) this.jitter[i] = 0.85 + 0.15 * Math.random();
    this.draw();
  };

  Field.prototype.draw = function () {
    var p = this.p, w = this.w, h = this.h, ctx = this.ctx;
    var cols = this.cols, rows = this.rows, n = cols * rows;
    var ph = this.t * p.speed * TAU;
    var S = Math.max(w, h) * 1.15;
    var f = p.fov * S;
    var cy_ = Math.cos(p.yaw * D2R), sy_ = Math.sin(p.yaw * D2R);
    var cp = Math.cos(p.pitch * D2R), sp = Math.sin(p.pitch * D2R);
    var cr = Math.cos(p.rotate * D2R), sr = Math.sin(p.rotate * D2R);
    var lit = this.lx !== null;
    var tdx = lit ? (this.lx / w - 0.5) * 0.035 : 0;
    var tdy = lit ? (this.ly / h - 0.5) * 0.02 : 0;
    this.ddx += (tdx - this.ddx) * 0.05;
    this.ddy += (tdy - this.ddy) * 0.05;
    var ox = w * (p.cx + p.dx + this.ddx), oy = h * (p.cy + p.dy + this.ddy);
    var LR = 260, lx = this.lx, ly = this.ly;
    var zc = this.zc, yy = this.yy, sx = this.sx, sy = this.sy;
    var zmin = Infinity, zmax = -Infinity, ymin = Infinity, ymax = -Infinity;
    var i = 0, r, c;

    /* Pass one: the surface, projected. */
    for (r = 0; r < rows; r++) {
      var Z = (r / (rows - 1)) * p.depth;
      for (c = 0; c < cols; c++, i++) {
        var X = (c / (cols - 1) - 0.5) * p.span;
        var Y = p.amp * Math.sin(X * p.f0 * 1.9 + Z * 1.1 + ph)
              + p.amp * 0.55 * Math.sin(Z * p.f1 * 3.1 - X * 0.7 + ph)
              + p.amp * 0.25 * Math.sin((X + Z) * 4.3 + ph * 2);
        var Zh = Z - p.depth / 2;
        var Xr = X * cy_ - Zh * sy_;
        var Zr = X * sy_ + Zh * cy_ + p.depth / 2;
        var Yc = Y * cp - Zr * sp;
        var Zc = Y * sp + Zr * cp + p.cam;
        var x0 = Xr * f / Zc, y0 = -Yc * f / Zc;
        sx[i] = x0 * cr - y0 * sr + ox;
        sy[i] = x0 * sr + y0 * cr + oy;
        zc[i] = Zc; yy[i] = Y;
        if (Zc < zmin) zmin = Zc; if (Zc > zmax) zmax = Zc;
        if (Y < ymin) ymin = Y; if (Y > ymax) ymax = Y;
      }
    }

    /* Pass two: depth, crest, masks, then paint. Bloom first so the dots
       sit on top of their own glow. */
    var zr = zmax - zmin + 1e-6, yr = ymax - ymin + 1e-6;
    var zone = this.zone, pad = p.pad, fall = p.fall;
    var alpha = this.alpha || (this.alpha = new Float32Array(n));
    var rad = this.rad || (this.rad = new Float32Array(n));
    var mask = this.mask || (this.mask = new Float32Array(n));

    for (i = 0; i < n; i++) {
      var x = sx[i], y = sy[i];
      if (x < -6 || y < -6 || x > w + 6 || y > h + 6) { alpha[i] = 0; mask[i] = 0; continue; }
      var near = (zmax - zc[i]) / zr;
      var crest = (yy[i] - ymin) / yr;
      var a = p.aFar + (p.aNear - p.aFar) * Math.pow(near, 1.3) * (0.45 + p.crest * 0.55 * crest);
      a *= this.jitter[i];
      var rr = p.rFar + (p.rNear - p.rFar) * Math.pow(near, 1.6);
      if (lit) {
        /* a light under the cursor: dots nearby brighten and swell */
        var ex = x - lx, ey = y - ly, dd = ex * ex + ey * ey;
        if (dd < LR * LR) {
          var k = 1 - Math.sqrt(dd) / LR; k *= k;
          a += (1 - a) * k * 0.9;
          rr *= 1 + 0.9 * k;
        }
      }
      var fy = y / h;
      var m = smooth(fy, p.top[0], p.top[1]) * (1 - smooth(fy, p.bottom[0], p.bottom[1]));
      if (zone) {
        var ddx = Math.max(0, (zone.l - pad) - x, x - (zone.r + pad));
        var ddy = Math.max(0, (zone.t - pad) - y, y - (zone.b + pad));
        m *= smooth(Math.sqrt(ddx * ddx + ddy * ddy), 0, fall);
      }
      alpha[i] = a * m;
      mask[i] = m;
      rad[i] = rr;
    }

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = INK;
    for (i = 0; i < n; i++) {
      if (alpha[i] < 0.5) continue;
      ctx.globalAlpha = alpha[i] * 0.12;
      ctx.beginPath(); ctx.arc(sx[i], sy[i], rad[i] * 2.6, 0, TAU); ctx.fill();
    }
    for (i = 0; i < n; i++) {
      if (alpha[i] < 0.02) continue;
      ctx.globalAlpha = alpha[i];
      ctx.beginPath(); ctx.arc(sx[i], sy[i], rad[i], 0, TAU); ctx.fill();
    }

    /* The live signal: one amber point riding a crest of the surface with
       a short tail, the site's "amber is the live signal" idea made literal.
       It respects the same mask as the dots, so it never crosses the type. */
    if (p.signal) {
      var row = Math.min(rows - 1, Math.round(rows * p.signal.row));
      var prog = ((this.t * p.signal.speed) % 1 + 1) % 1;
      var head = prog * (cols - 1);
      ctx.fillStyle = AMBER;
      for (var k = 0; k < 9; k++) {
        var cpos = head - k * 1.3;
        if (cpos < 0) break;
        var ci = Math.floor(cpos), fr = cpos - ci;
        var i0 = row * cols + ci, i1 = Math.min(i0 + 1, row * cols + cols - 1);
        var mk = Math.min(mask[i0], mask[i1]);
        if (mk < 0.04) continue;
        var ax = sx[i0] + (sx[i1] - sx[i0]) * fr, ay = sy[i0] + (sy[i1] - sy[i0]) * fr;
        var fade = 1 - k / 9;
        if (k === 0) {
          ctx.globalAlpha = mk * 0.35;
          ctx.beginPath(); ctx.arc(ax, ay, 11, 0, TAU); ctx.fill();
        }
        ctx.globalAlpha = mk * fade;
        ctx.beginPath(); ctx.arc(ax, ay, (k === 0 ? 3.4 : 2.2) * fade + 0.6, 0, TAU); ctx.fill();
      }
      ctx.fillStyle = INK;
    }
    ctx.globalAlpha = 1;
  };

  /* ---------- the system: the agent team as one object ----------
     A master agent at the centre (a disc of rings, turning slowly), the
     three outcomes as dotted arcs around it, the specialist agents as
     nodes on the outer ring, each briefed down a spoke from the centre,
     and the review pass circulating the rim in amber. The labels live in
     the figure as a list; the script places them on the geometry, and
     whichever one is hovered or focused lights its spoke and its arc. */
  function System(host) {
    this.host = host;
    var fig = host.parentElement, self = this;
    var items = fig ? Array.prototype.slice.call(fig.querySelectorAll('.system__agents > li')) : [];
    this.core = null; this.agents = [];
    items.forEach(function (li) { if (li.classList.contains('is-core')) self.core = li; else self.agents.push(li); });
    this.arcs = fig ? Array.prototype.slice.call(fig.querySelectorAll('.system__arcs > li')) : [];
    this.active = null; this.fps60 = true;
    if (fig && !reduced) fig.classList.add('is-staged');
    /* number the agents in reading order, in the annotation layer */
    this.agents.forEach(function (li, n) {
      var b = li.querySelector('b'); if (!b || b.querySelector('.agent-num')) return;
      var num = document.createElement('i'); num.className = 'agent-num'; num.setAttribute('aria-hidden', 'true');
      num.textContent = (n < 9 ? '0' : '') + (n + 1); b.appendChild(num);
    });
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'dotfield';
    this.canvas.setAttribute('aria-hidden', 'true');
    host.insertBefore(this.canvas, host.firstChild);
    this.ctx = this.canvas.getContext('2d');
    this.t = 0; this.lx = null; this.ly = null;
    function activate(li) {
      if (self.active === li) return;
      if (self.active) self.active.classList.remove('is-active');
      self.active = li;
      if (li) li.classList.add('is-active');
      if (fig) { fig.classList.toggle('has-active', !!li); fig.classList.toggle('core-active', !!li && li === self.core); }
      var grp = li && li.getAttribute('data-group');
      self.arcs.forEach(function (a, n) { a.classList.toggle('is-quiet', !!grp && !!self.groupSpans[n] && self.groupSpans[n].key !== grp); });
      if (reduced) self.draw();
    }
    items.forEach(function (li) {
      li.setAttribute('tabindex', '0');
      li.addEventListener('pointerenter', function () { activate(li); });
      li.addEventListener('pointerleave', function () { if (self.active === li) activate(null); });
      li.addEventListener('focusin', function () { activate(li); });
      li.addEventListener('focusout', function (e) {
        if (li.contains(e.relatedTarget)) return;
        if (self.active === li) activate(null);
      });
      li.addEventListener('click', function (e) {
        if (e.target.closest && e.target.closest('a')) return;
        activate(self.active === li ? null : li);
      });
    });
    this.resize();
  }

  var SPANS = { found: [-144, 108], leads: [-36, 144], keep: [108, 108] };

  System.prototype.resize = function () {
    var rect = this.host.getBoundingClientRect(), self = this;
    this.w = Math.max(1, Math.round(rect.width));
    this.h = Math.max(1, Math.round(rect.height));
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.canvas.width = Math.round(this.w * this.dpr);
    this.canvas.height = Math.round(this.h * this.dpr);
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.tilt = 0.9;
    this.R = Math.min(this.w * 0.28, this.h * 0.42 / this.tilt);
    this.cx = this.w / 2; this.cy = this.h / 2;
    var byGroup = {}, order = [];
    this.agents.forEach(function (li) {
      var g = li.getAttribute('data-group') || 'found';
      if (!byGroup[g]) { byGroup[g] = []; order.push(g); }
      byGroup[g].push(li);
    });
    this.nodes = []; this.groupSpans = [];
    order.forEach(function (g) {
      var sp = SPANS[g] || [0, 120], list = byGroup[g];
      self.groupSpans.push({ key: g, start: sp[0] * D2R, span: sp[1] * D2R });
      var gi = self.groupSpans.length - 1;
      if (self.arcs[gi]) self.arcs[gi].setAttribute('data-count', list.length);
      list.forEach(function (li, i) {
        var th = (sp[0] + (i + 0.5) * sp[1] / list.length) * D2R;
        var x = self.cx + self.R * Math.cos(th), y = self.cy + self.R * self.tilt * Math.sin(th);
        self.nodes.push({ li: li, th: th, x: x, y: y, g: g, gi: gi, k: i });
        li.style.left = x.toFixed(1) + 'px'; li.style.top = y.toFixed(1) + 'px';
        var s = Math.sin(th), c = Math.cos(th);
        li.classList.remove('is-top', 'is-right', 'is-bottom', 'is-left');
        li.classList.add(s < -0.72 ? 'is-top' : s > 0.72 ? 'is-bottom' : c > 0 ? 'is-right' : 'is-left');
      });
    });
    /* how far each card unfolds: its description's height plus a margin */
    (this.core ? [this.core] : []).concat(this.agents).forEach(function (li) {
      var p = li.querySelector('p'); if (p) li.style.setProperty('--drop', (p.offsetHeight + 12) + 'px');
    });
    if (this.core) { this.core.style.left = this.cx + 'px'; this.core.style.top = this.cy + 'px'; }
    this.arcs.forEach(function (li, i) {
      var gs = self.groupSpans[i]; if (!gs) return;
      var mid = gs.start + gs.span / 2, rr = self.R * 0.6;
      li.style.left = (self.cx + rr * Math.cos(mid)).toFixed(1) + 'px';
      li.style.top = (self.cy + rr * self.tilt * Math.sin(mid)).toFixed(1) + 'px';
    });
    this.draw();
  };

  /* Easing for the build and the packets */
  function clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function easeOut(x) { x = clamp01(x); return 1 - (1 - x) * (1 - x) * (1 - x); }
  function easeInOut(x) { x = clamp01(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
  var LAP = 0.06, TRIP = 1.8, STAMP = 0.8;

  System.prototype.draw = function () {
    var ctx = this.ctx, w = this.w, h = this.h, R = this.R, tilt = this.tilt, cx = this.cx, cy = this.cy, t = this.t;
    var active = this.active, coreActive = !!active && active === this.core, activeNode = null, activeGroup = null, i, j, nd;
    if (active && !coreActive) for (i = 0; i < this.nodes.length; i++) if (this.nodes[i].li === active) { activeNode = this.nodes[i]; activeGroup = activeNode.g; }
    /* the build: the figure assembles in the order the system works. The
       master settles, its briefs draw out, the sections are ruled, each
       outcome's agents arrive in turn, and last the review rim closes. */
    if (this.bornT == null && !reduced) { var hr = this.host.getBoundingClientRect(); if (hr.top + hr.height * 0.35 < window.innerHeight) this.bornT = t; }
    var bt = reduced ? 99 : this.bornT == null ? -1 : t - this.bornT - 0.2;
    function k(start, dur) { return easeOut((bt - start) / dur); }
    ctx.clearRect(0, 0, w, h);
    var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 0.9);
    g.addColorStop(0, 'rgba(250, 248, 243, 0.1)'); g.addColorStop(1, 'rgba(250, 248, 243, 0)');
    ctx.globalAlpha = k(0, 1.4); ctx.fillStyle = g;
    ctx.beginPath(); ctx.ellipse(cx, cy, R * 1.2, R * 1.2 * tilt, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = INK;
    var lit = this.lx !== null, LR = 150, lx = this.lx, ly = this.ly;
    function dot(x, y, r, a) {
      if (a < 0.02) return;
      if (lit) { var ex = x - lx, ey = y - ly, dd = ex * ex + ey * ey; if (dd < LR * LR) { var kk = 1 - Math.sqrt(dd) / LR; kk *= kk; a += (1 - a) * kk * 0.7; r *= 1 + 0.6 * kk; } }
      ctx.globalAlpha = a > 1 ? 1 : a; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
    }
    function ring(x, y, r, a, color) {
      if (a < 0.02) return;
      ctx.strokeStyle = color; ctx.globalAlpha = a; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.stroke(); ctx.strokeStyle = INK;
    }
    if (this.core && bt >= 0.3) this.core.classList.add('is-in');
    /* the master: a disc of rings, turning, breathing */
    var coreR = R * 0.3, rot = t * 0.03 * TAU, breathe = 0.85 + 0.15 * Math.sin(t * 0.5 * TAU);
    for (var rg = 0; rg < 7; rg++) {
      var kr = k(0.04 * (6 - rg), 0.9);
      var rr = coreR * (0.18 + 0.82 * rg / 6) * (0.75 + 0.25 * kr), n = Math.max(8, Math.round(TAU * rr / 7));
      var ra = kr * (coreActive ? 1 : 0.9 * breathe) * (1 - 0.45 * rg / 6) * (active && !coreActive ? 0.7 : 1);
      for (j = 0; j < n; j++) { var th = j * TAU / n + rot * (1 + 0.3 * (6 - rg) / 6); dot(cx + rr * Math.cos(th), cy + rr * tilt * Math.sin(th), 1.1 + 0.9 * (1 - rg / 6), ra); }
    }
    /* a live brief on the hovered spoke (or every spoke when the master is hovered) */
    for (i = 0; i < this.nodes.length; i++) {
      nd = this.nodes[i];
      if (!(nd === activeNode || coreActive)) continue;
      var pulse = (t * 0.55 + i * 0.13) % 1, f = 0.34 + 0.6 * pulse;
      dot(cx + (nd.x - cx) * f, cy + (nd.y - cy) * f, nd === activeNode ? 2.4 : 1.5, 0.95 * k(2.6, 0.5));
    }
    /* the outcomes: a hairline arc at 0.6R and the outer ring at R, per
       group, drawn as lines with a sparse dotted echo so they read as drafted */
    ctx.strokeStyle = INK; ctx.lineWidth = 0.7;
    for (i = 0; i < this.groupSpans.length; i++) {
      var gs = this.groupSpans[i], gActive = activeGroup === gs.key, gap = 6 * D2R;
      var ka = k(1.0 + i * 0.18, 0.9);
      var a1 = gs.start + gap, a2 = a1 + (gs.span - 2 * gap) * ka;
      if (ka <= 0) continue;
      var cfgs = [[0.6, 0.22], [1, 0.42]];
      for (var c = 0; c < 2; c++) {
        var cr = R * cfgs[c][0];
        ctx.globalAlpha = cfgs[c][1] * (active ? (gActive ? 1.8 : 0.3) : 1);
        ctx.beginPath(); ctx.ellipse(cx, cy, cr, cr * tilt, 0, a1, a2); ctx.stroke();
      }
      var en = Math.max(8, Math.round((a2 - a1) * R / 26));
      for (j = 0; j <= en; j++) {
        var ta = a1 + (a2 - a1) * j / en, flow = 0.5 + 0.5 * Math.sin(ta * 3 - t * 0.5 * TAU);
        dot(cx + R * Math.cos(ta), cy + R * tilt * Math.sin(ta), 1.1, (active ? (gActive ? 0.7 : 0.15) : 0.35) * flow);
      }
      if (this.arcs[i] && bt >= 1.3 + i * 0.18) this.arcs[i].classList.add('is-in');
    }
    /* the sections: a solid rule at each boundary between outcomes, from
       the master's edge out past the rim, with a short tick where it lands */
    ctx.lineWidth = 1;
    for (i = 0; i < this.groupSpans.length; i++) {
      var bs = this.groupSpans[i], ba = bs.start, prev = this.groupSpans[(i + this.groupSpans.length - 1) % this.groupSpans.length];
      var edge = activeGroup === bs.key || activeGroup === prev.key, kd = k(0.85 + i * 0.1, 0.8);
      if (kd <= 0) continue;
      var bc = Math.cos(ba), bsn = Math.sin(ba), r0 = R * 0.36, r1 = r0 + (R * 1.12 - r0) * kd;
      ctx.globalAlpha = active ? (edge ? 0.7 : 0.14) : 0.45;
      ctx.beginPath(); ctx.moveTo(cx + r0 * bc, cy + r0 * tilt * bsn); ctx.lineTo(cx + r1 * bc, cy + r1 * tilt * bsn); ctx.stroke();
      var tx = -bsn, ty = bc * tilt, tl = Math.sqrt(tx * tx + ty * ty), tk = 5 * kd * kd / tl, ex = cx + r1 * bc, ey = cy + r1 * tilt * bsn;
      ctx.beginPath(); ctx.moveTo(ex - tx * tk, ey - ty * tk); ctx.lineTo(ex + tx * tk, ey + ty * tk); ctx.stroke();
    }
    /* the spokes, drawn out from the master in order */
    ctx.lineWidth = 0.7;
    for (i = 0; i < this.nodes.length; i++) {
      nd = this.nodes[i];
      var isA2 = nd === activeNode, ks = k(0.5 + i * 0.05, 0.7);
      if (ks <= 0) continue;
      ctx.globalAlpha = isA2 ? 0.55 : coreActive ? 0.3 : 0.1 * (active ? 0.6 : 1);
      var s1 = 0.32 + 0.64 * ks;
      ctx.beginPath(); ctx.moveTo(cx + (nd.x - cx) * 0.32, cy + (nd.y - cy) * 0.32); ctx.lineTo(cx + (nd.x - cx) * s1, cy + (nd.y - cy) * s1); ctx.stroke();
    }
    /* the agents, arriving outcome by outcome, each with a short leader
       line out toward its label */
    var isA;
    for (i = 0; i < this.nodes.length; i++) {
      nd = this.nodes[i]; isA = nd === activeNode;
      var ap = 1.2 + nd.gi * 0.24 + nd.k * 0.08, kn = k(ap, 0.5);
      if (bt >= ap + 0.08) nd.li.classList.add('is-in');
      if (kn <= 0) continue;
      var pz = 0.5 + 0.5 * Math.sin((t * 0.16 - i * 0.1) * TAU), nr = (isA ? 5.5 : 3.6 + 0.6 * pz) * kn;
      if (kn < 1) ring(nd.x, nd.y, 5 + 14 * kn, 0.4 * (1 - kn), INK);
      if (isA) { ctx.globalAlpha = 0.18; ctx.beginPath(); ctx.arc(nd.x, nd.y, 18, 0, TAU); ctx.fill(); }
      ctx.globalAlpha = (active && !isA && !coreActive ? 0.25 : 0.95) * kn;
      ctx.beginPath(); ctx.arc(nd.x, nd.y, nr, 0, TAU); ctx.fill();
      ring(nd.x, nd.y, nr + 5, (isA ? 0.5 : 0.18) * kn, INK);
      var ux = (nd.x - cx) / R, uy = (nd.y - cy) / (R * tilt), ul = Math.sqrt(ux * ux + uy * uy) || 1;
      ux /= ul; uy /= ul;
      ctx.globalAlpha = (isA ? 0.5 : 0.22) * kn;
      ctx.beginPath(); ctx.moveTo(nd.x + ux * (nr + 9), nd.y + uy * (nr + 9)); ctx.lineTo(nd.x + ux * (nr + 17), nd.y + uy * (nr + 17)); ctx.stroke();
    }
    /* the work: a brief leaves the master, the agent works it, and the
       result goes out to the rim timed to meet the review pass, which
       stamps it in amber as it goes by. Every agent, every lap. */
    var head = -Math.PI / 2 + ((t * LAP) % 1) * TAU, kp = k(2.8, 0.6), rimR = R * 1.2;
    if (kp > 0) {
      for (i = 0; i < this.nodes.length; i++) {
        nd = this.nodes[i];
        var dim = (active && nd !== activeNode && !coreActive ? 0.12 : 1) * kp;
        var phase = (((nd.th + Math.PI / 2) / TAU - t * LAP) % 1 + 1) % 1, rem = phase / LAP, since = (1 - phase) / LAP;
        var vx = nd.x - cx, vy = nd.y - cy, q, m;
        if (rem < TRIP) {
          var p = 1 - rem / TRIP;
          if (p < 0.5) {
            q = easeInOut(p / 0.5);
            for (m = 0; m < 4; m++) { var qm = Math.max(0, q - m * 0.035), fm = 0.32 + 0.68 * qm; dot(cx + vx * fm, cy + vy * fm, 1.9 - m * 0.35, 0.95 * dim * (1 - m / 4)); }
          } else if (p < 0.62) {
            var sw = (p - 0.5) / 0.12;
            ring(nd.x, nd.y, 6 + 9 * easeOut(sw), 0.45 * (1 - sw) * dim, INK);
          } else {
            q = easeInOut((p - 0.62) / 0.38);
            for (m = 0; m < 4; m++) { var qo = Math.max(0, q - m * 0.08), fo = 1 + 0.2 * qo; dot(cx + vx * fo, cy + vy * fo, 1.9 - m * 0.35, 0.95 * dim * (1 - m / 4)); }
          }
        }
        if (since < STAMP) {
          var ss = since / STAMP, sx = cx + vx * 1.2, sy = cy + vy * 1.2;
          ctx.lineWidth = 1;
          ring(sx, sy, 3 + 15 * easeOut(ss), 0.6 * (1 - ss) * dim, AMBER);
          ctx.lineWidth = 0.7;
          ctx.fillStyle = AMBER; dot(sx, sy, 2.2, 0.9 * (1 - ss) * dim); ctx.fillStyle = INK;
        }
      }
    }
    /* the review pass: the rim, turning, with the amber signal on it */
    var kr2 = k(1.9, 0.9);
    ctx.globalAlpha = (active ? 0.08 : 0.14) * kr2; ctx.lineWidth = 0.7; ctx.setLineDash([2, 6]); ctx.lineDashOffset = -t * 6;
    ctx.beginPath(); ctx.ellipse(cx, cy, rimR, rimR * tilt, 0, -Math.PI / 2, -Math.PI / 2 + TAU * kr2); ctx.stroke(); ctx.setLineDash([]);
    var kh = k(2.3, 0.7);
    ctx.fillStyle = AMBER;
    for (var mm = 0; mm < 16; mm++) {
      var ha = head - mm * 0.009 * TAU, fade = 1 - mm / 16;
      var hx = cx + rimR * Math.cos(ha), hy = cy + rimR * tilt * Math.sin(ha);
      if (mm === 0) { ctx.globalAlpha = 0.3 * kh; ctx.beginPath(); ctx.arc(hx, hy, 12, 0, TAU); ctx.fill(); }
      ctx.globalAlpha = fade * kh; ctx.beginPath(); ctx.arc(hx, hy, (mm === 0 ? 3.6 : 2.2) * fade + 0.5, 0, TAU); ctx.fill();
    }
    ctx.fillStyle = INK; ctx.globalAlpha = 1;
  };

  var fields = hosts.map(function (host) {
    return host.getAttribute('data-dotfield') === 'system' ? new System(host) : new Field(host);
  });
  window.flowDotField = { fields: fields, presets: PRESETS };

  /* Keep the surface and its type zone honest through reflows: fonts
     swapping in, the portrait decoding, the viewport changing. */
  var resizeQueued = false;
  function queueResize() {
    if (resizeQueued) return;
    resizeQueued = true;
    window.requestAnimationFrame(function () {
      resizeQueued = false;
      fields.forEach(function (fl) { fl.resize(); });
    });
  }
  if ('ResizeObserver' in window) {
    var ro = new ResizeObserver(queueResize);
    fields.forEach(function (fl) {
      ro.observe(fl.host);
      if (fl.clear) ro.observe(fl.clear);
    });
  } else {
    window.addEventListener('resize', queueResize);
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(queueResize);

  if (reduced) return;

  /* The pointer, handed to whichever field it is over */
  function setPointer(x, y) {
    fields.forEach(function (fl) {
      var r = fl.host.getBoundingClientRect();
      var inside = x !== null && x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
      fl.lx = inside ? x - r.left : null;
      fl.ly = inside ? y - r.top : null;
    });
  }
  if (window.matchMedia('(pointer: fine)').matches) {
    window.addEventListener('pointermove', function (e) { setPointer(e.clientX, e.clientY); }, { passive: true });
    document.addEventListener('pointerleave', function () { setPointer(null, null); });
    window.addEventListener('blur', function () { setPointer(null, null); });
  }

  /* The surfaces draw at 30fps; the system draws every frame so its
     fine motion stays smooth. */
  function tick(now) {
    window.requestAnimationFrame(tick);
    if (document.hidden) return;
    fields.forEach(function (fl) {
      if (fl.last && now - fl.last < (fl.fps60 ? 0 : 33)) return;
      var dt = fl.last ? Math.min(now - fl.last, 100) / 1000 : 0.016;
      fl.last = now;
      var r = fl.host.getBoundingClientRect();
      if (r.bottom < 0 || r.top > window.innerHeight) return;
      fl.t += dt;
      fl.draw();
    });
  }
  window.requestAnimationFrame(tick);
}());
