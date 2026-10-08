/* Interactive CV (/about): the life layer.

   1. Dot portrait: the operator photo redrawn as a halftone of light. Dots gather
      into the portrait on load, part around the pointer and settle back, and warm
      to amber where the pointer passes.
   2. Receipts count up once, the first time they are seen, and their dot meters light.
   3. Career rules draw in as the sheet comes into view.
   4. A soft spotlight follows the pointer across cards.

   All decorative and fail-safe. The static portrait image stays in the page until the
   canvas has drawn, numbers are written in full in the HTML, and prefers-reduced-motion
   gets the finished state with no movement. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(pointer: fine)').matches;
  var slice = function (l) { return Array.prototype.slice.call(l); };
  var io = 'IntersectionObserver' in window;

  /* ---------- 1. dot portrait ---------- */
  slice(document.querySelectorAll('[data-dotportrait]')).forEach(function (host) {
    var canvas = document.createElement('canvas');
    if (!canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var img = new Image();
    var fx = parseFloat(host.getAttribute('data-focus-x') || '0.5');
    var fy = parseFloat(host.getAttribute('data-focus-y') || '0.4');
    var dots = [], W = 0, H = 0, dpr = 1, raf = 0, start = 0, visible = true;
    var pointer = { x: -9999, y: -9999, on: false };
    var STEP = 7;

    canvas.className = 'dotportrait__canvas';
    canvas.setAttribute('aria-hidden', 'true');

    function build() {
      var r = host.getBoundingClientRect();
      W = Math.round(r.width); H = Math.round(r.height);
      if (!W || !H) return;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = W * dpr; canvas.height = H * dpr;
      canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
      STEP = W < 420 ? 4.6 : 5.4;

      // sample the photo with object-fit: cover around the focus point
      var cols = Math.floor(W / STEP), rows = Math.floor(H / STEP);
      var off = document.createElement('canvas'); off.width = cols; off.height = rows;
      var o = off.getContext('2d');
      var s = Math.max(cols / img.naturalWidth, rows / img.naturalHeight) * parseFloat(host.getAttribute('data-zoom') || '1');
      var dw = img.naturalWidth * s, dh = img.naturalHeight * s;
      var ox = (cols - dw) * fx, oy = (rows - dh) * fy;
      o.drawImage(img, ox, oy, dw, dh);
      var data = o.getImageData(0, 0, cols, rows).data;

      dots = [];
      var max = STEP * 0.6;
      // mask mode: a studio photo on a light backdrop. The backdrop is read from a point
      // beside the head and dropped, so only the person is drawn, hair and shirt included.
      var mode = host.getAttribute('data-mode'), alpha = mode === 'alpha', mask = mode === 'mask', bg = null;
      if (mask) {
        var bi = (Math.floor(rows * 0.22) * cols + Math.floor(cols * 0.12)) * 4;
        bg = [data[bi], data[bi + 1], data[bi + 2]];
      }
      for (var y = 0; y < rows; y++) {
        for (var x = 0; x < cols; x++) {
          var i = (y * cols + x) * 4;
          var l = (0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2]) / 255;
          var rad;
          if (alpha) {
            if (data[i + 3] < 60) continue;
            rad = max * (0.22 + 0.78 * Math.pow(l, 1.25));
          } else if (mask) {
            var dr = data[i] - bg[0], dg = data[i + 1] - bg[1], db = data[i + 2] - bg[2];
            if (dr * dr + dg * dg + db * db < 30 * 30 || l > 0.975 || data[i + 3] < 30) continue;
            // the source photo sits in a drawn circle: keep only what is inside it
            var sx = (x + 0.5 - ox) / dw - 0.5, sy = (y + 0.5 - oy) / dh - 0.5;
            if (sx * sx + sy * sy > 0.455 * 0.455) continue;
            rad = max * (0.22 + 0.78 * Math.pow(l, 1.4));
          } else {
            rad = max * Math.pow(Math.max(0, l - 0.08) / 0.92, 1.15);
          }
          if (rad < 0.45) continue;
          var hx = x * STEP + STEP / 2, hy = y * STEP + STEP / 2;
          var a = Math.random() * Math.PI * 2, d = 40 + Math.random() * Math.max(W, H) * 0.6;
          dots.push({ hx: hx, hy: hy, x: hx + Math.cos(a) * d, y: hy + Math.sin(a) * d, vx: 0, vy: 0, r: rad, l: l, warm: 0, delay: Math.random() * 520 });
        }
      }
      if (reduced) dots.forEach(function (p) { p.x = p.hx; p.y = p.hy; });
    }

    function draw(now) {
      if (!start) start = now;
      var t = now - start, moving = false;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, W, H);
      var R = W < 420 ? 80 : 120, R2 = R * R;
      for (var k = 0; k < dots.length; k++) {
        var p = dots[k];
        if (!reduced) {
          var gather = t > p.delay ? 0.085 : 0;
          var ax = (p.hx - p.x) * gather, ay = (p.hy - p.y) * gather;
          if (pointer.on) {
            var dx = p.x - pointer.x, dy = p.y - pointer.y, d2 = dx * dx + dy * dy;
            if (d2 < R2) {
              var f = (1 - d2 / R2), dd = Math.sqrt(d2) || 1;
              ax += dx / dd * f * 2.4; ay += dy / dd * f * 2.4;
              p.warm = Math.min(1, p.warm + f * 0.35);
            }
          }
          p.vx = (p.vx + ax) * 0.82; p.vy = (p.vy + ay) * 0.82;
          p.x += p.vx; p.y += p.vy;
          p.warm *= 0.965;
          if (Math.abs(p.vx) + Math.abs(p.vy) > 0.02 || Math.abs(p.hx - p.x) > 0.3 || p.warm > 0.02) moving = true;
        }
        var w = p.warm, base = 0.42 + p.l * 0.58;
        ctx.fillStyle = 'rgba(' + Math.round(250 - 22 * w) + ',' + Math.round(248 - 84 * w) + ',' + Math.round(243 - 183 * w) + ',' + (base + (1 - base) * w).toFixed(3) + ')';
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r * (1 + w * 0.35), 0, 6.2832); ctx.fill();
      }
      if (!host.classList.contains('is-drawn')) host.classList.add('is-drawn');
      raf = (moving || pointer.on || t < 1600) && visible && !reduced ? requestAnimationFrame(draw) : 0;
    }

    function kick() { if (!raf && visible) raf = requestAnimationFrame(draw); }

    img.onload = function () {
      build();
      host.appendChild(canvas);
      kick();
      if (io) new IntersectionObserver(function (e) { visible = e[0].isIntersecting; if (visible) kick(); }).observe(host);
      var resizeT;
      window.addEventListener('resize', function () { clearTimeout(resizeT); resizeT = setTimeout(function () { build(); start = 0; kick(); }, 180); });
      if (!reduced) {
        host.addEventListener('pointermove', function (e) {
          var r = canvas.getBoundingClientRect();
          pointer.x = e.clientX - r.left; pointer.y = e.clientY - r.top; pointer.on = true; kick();
        });
        host.addEventListener('pointerleave', function () { pointer.on = false; pointer.x = pointer.y = -9999; kick(); });
      }
    };
    img.src = host.getAttribute('data-src');
  });

  /* ---------- 2. receipts: count up and light the meter ---------- */
  var counters = slice(document.querySelectorAll('[data-count]'));
  var meters = slice(document.querySelectorAll('[data-meter]'));
  meters.forEach(function (m) {
    var lit = parseInt(m.getAttribute('data-meter'), 10) || 0;
    for (var i = 0; i < 20; i++) {
      var d = document.createElement('i');
      if (i < lit) { d.className = 'on'; d.style.setProperty('--i', i); }
      m.appendChild(d);
    }
  });
  function countUp(el) {
    var to = parseFloat(el.getAttribute('data-count'));
    if (reduced) { el.textContent = String(to); return; }
    var t0 = performance.now(), dur = 1300;
    (function step(now) {
      var k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = String(Math.round(to * e));
      if (k < 1) requestAnimationFrame(step);
    }(t0));
  }
  var band = document.querySelector('.receipts');
  if (band) {
    if (io && !reduced) {
      counters.forEach(function (c) { c.textContent = '0'; });
      new IntersectionObserver(function (entries, obs) {
        if (!entries[0].isIntersecting) return;
        band.classList.add('is-live');
        counters.forEach(countUp);
        obs.disconnect();
      }, { threshold: 0.35 }).observe(band);
    } else {
      band.classList.add('is-live');
    }
  }

  /* ---------- 3. career rules draw in ---------- */
  var sheet = document.querySelector('.cvsheet');
  if (sheet) {
    if (io && !reduced) {
      sheet.classList.add('is-waiting');
      new IntersectionObserver(function (entries, obs) {
        if (!entries[0].isIntersecting) return;
        sheet.classList.remove('is-waiting'); sheet.classList.add('is-drawn');
        obs.disconnect();
      }, { threshold: 0.15 }).observe(sheet);
    }
  }

  /* ---------- 4. spotlight ---------- */
  if (fine && !reduced) {
    document.addEventListener('pointermove', function (e) {
      var card = e.target && e.target.closest ? e.target.closest('[data-spot]') : null;
      if (!card) return;
      var r = card.getBoundingClientRect();
      card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      card.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }
}());
