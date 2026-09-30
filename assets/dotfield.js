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
      rNear: 2.8, rFar: 0.45, aNear: 0.9, aFar: 0.1, crest: 0.8, speed: 0.04,
      top: [0, 0.12], bottom: [0.9, 1], pad: 32, fall: 120
    },
    /* The closer: a floor of dots under the one amber button, rising to a
       horizon just behind it and dying out before the footer. */
    closer: {
      cols: 150, rows: 48, amp: 0.22, f0: 1.3, f1: 0.9,
      yaw: -8, pitch: 26, cam: 2.4, fov: 0.9, rotate: 0,
      cx: 0.5, cy: 1.02, dx: 0, dy: 0, span: 9.5, depth: 2.6,
      rNear: 2.7, rFar: 0.4, aNear: 0.85, aFar: 0.04, crest: 0.8, speed: 0.035,
      top: [0.5, 0.74], bottom: [0.96, 1], pad: 24, fall: 90
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
    var ox = w * (p.cx + p.dx), oy = h * (p.cy + p.dy);
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

    for (i = 0; i < n; i++) {
      var x = sx[i], y = sy[i];
      if (x < -6 || y < -6 || x > w + 6 || y > h + 6) { alpha[i] = 0; continue; }
      var near = (zmax - zc[i]) / zr;
      var crest = (yy[i] - ymin) / yr;
      var a = p.aFar + (p.aNear - p.aFar) * Math.pow(near, 1.3) * (0.45 + p.crest * 0.55 * crest);
      a *= this.jitter[i];
      var fy = y / h;
      a *= smooth(fy, p.top[0], p.top[1]) * (1 - smooth(fy, p.bottom[0], p.bottom[1]));
      if (zone) {
        var ddx = Math.max(0, (zone.l - pad) - x, x - (zone.r + pad));
        var ddy = Math.max(0, (zone.t - pad) - y, y - (zone.b + pad));
        a *= smooth(Math.sqrt(ddx * ddx + ddy * ddy), 0, fall);
      }
      alpha[i] = a;
      rad[i] = p.rFar + (p.rNear - p.rFar) * Math.pow(near, 1.6);
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
    ctx.globalAlpha = 1;
  };

  var fields = hosts.map(function (host) { return new Field(host); });
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

  var last = 0;
  function tick(now) {
    window.requestAnimationFrame(tick);
    if (document.hidden || now - last < 33) return;
    var dt = Math.min(now - last, 100) / 1000;
    last = now;
    fields.forEach(function (fl) {
      var r = fl.host.getBoundingClientRect();
      if (r.bottom < 0 || r.top > window.innerHeight) return;
      fl.t += dt;
      fl.draw();
    });
  }
  window.requestAnimationFrame(tick);
}());
