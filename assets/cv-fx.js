/* Interactive CV (/about): the life layer.

   1. Halo: a quiet ring of light drifting behind the portrait. The photo itself is never
      drawn over. The halo leans a little toward the pointer and warms where it passes.
   2. Receipts count up once, the first time they are seen.
   3. A soft spotlight follows the pointer across cards.

   All decorative and fail-safe: numbers are written in full in the HTML, the photo is a
   plain image, and prefers-reduced-motion gets one still frame. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(pointer: fine)').matches;
  var slice = function (l) { return Array.prototype.slice.call(l); };
  var io = 'IntersectionObserver' in window;
  var ZH = /^zh/.test(document.documentElement.lang);
  var MORE = ZH ? '展开' : 'Read more', LESS = ZH ? '收起' : 'Show less';

  /* ---------- 1. halo behind the portrait ---------- */
  slice(document.querySelectorAll('[data-halo]')).forEach(function (host) {
    var canvas = document.createElement('canvas');
    if (!canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    canvas.className = 'portrait__halo';
    canvas.setAttribute('aria-hidden', 'true');
    host.insertBefore(canvas, host.firstChild);

    var W = 0, H = 0, dpr = 1, motes = [], raf = 0, visible = true, t0 = 0;
    var lean = { x: 0, y: 0, tx: 0, ty: 0 }, ptr = { x: -9999, y: -9999, on: false };

    function build() {
      var r = host.getBoundingClientRect();
      W = Math.round(r.width); H = Math.round(r.height);
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = W * dpr; canvas.height = H * dpr;
      canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
      var n = Math.round(Math.min(220, W * 0.38));
      motes = [];
      for (var i = 0; i < n; i++) {
        motes.push({
          a: Math.random() * Math.PI * 2,
          rr: 0.62 + Math.random() * 0.5,     // distance from the head, in head radii
          sp: (0.00012 + Math.random() * 0.00022) * (Math.random() < 0.5 ? -1 : 1),
          s: 0.6 + Math.random() * 1.5,
          o: 0.12 + Math.random() * 0.38,
          w: 0
        });
      }
    }

    function frame(now) {
      if (!t0) t0 = now;
      var t = now - t0;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, W, H);
      lean.x += (lean.tx - lean.x) * 0.06; lean.y += (lean.ty - lean.y) * 0.06;
      var cx = W * 0.5 + lean.x, cy = H * 0.36 + lean.y, R = W * 0.42;
      for (var i = 0; i < motes.length; i++) {
        var m = motes[i];
        var a = m.a + (reduced ? 0 : t * m.sp);
        var wob = reduced ? 0 : Math.sin(t * 0.0006 + i) * 6;
        var x = cx + Math.cos(a) * R * m.rr + wob, y = cy + Math.sin(a) * R * m.rr * 1.08;
        if (ptr.on) {
          var dx = x - ptr.x, dy = y - ptr.y, d2 = dx * dx + dy * dy;
          if (d2 < 14400) m.w = Math.min(1, m.w + (1 - d2 / 14400) * 0.2);
        }
        m.w *= 0.97;
        var w = m.w;
        ctx.fillStyle = 'rgba(' + Math.round(250 - 22 * w) + ',' + Math.round(248 - 84 * w) + ',' + Math.round(243 - 183 * w) + ',' + (m.o + (0.9 - m.o) * w).toFixed(3) + ')';
        ctx.beginPath(); ctx.arc(x, y, m.s * (1 + w * 0.6), 0, 6.2832); ctx.fill();
      }
      raf = visible && !reduced ? requestAnimationFrame(frame) : 0;
    }

    function kick() { if (!raf && visible) raf = requestAnimationFrame(frame); }
    build(); kick();
    if (io) new IntersectionObserver(function (e) { visible = e[0].isIntersecting; if (visible) kick(); }).observe(host);
    var rt;
    window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { build(); kick(); }, 160); });
    if (fine && !reduced) {
      host.addEventListener('pointermove', function (e) {
        var r = host.getBoundingClientRect();
        ptr.x = e.clientX - r.left; ptr.y = e.clientY - r.top; ptr.on = true;
        lean.tx = (ptr.x / W - 0.5) * 18; lean.ty = (ptr.y / H - 0.5) * 12;
      });
      host.addEventListener('pointerleave', function () { ptr.on = false; lean.tx = lean.ty = 0; });
    }
  });

  /* ---------- 2. receipts count up ---------- */
  var counters = slice(document.querySelectorAll('[data-count]'));
  function countUp(el) {
    var to = parseFloat(el.getAttribute('data-count'));
    var t0 = performance.now(), dur = 1300;
    (function step(now) {
      var k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = String(Math.round(to * e));
      if (k < 1) requestAnimationFrame(step);
    }(t0));
  }
  var band = document.querySelector('.receipts');
  if (band && io && !reduced) {
    counters.forEach(function (c) { c.textContent = '0'; });
    new IntersectionObserver(function (entries, obs) {
      if (!entries[0].isIntersecting) return;
      counters.forEach(countUp);
      obs.disconnect();
    }, { threshold: 0.35 }).observe(band);
  }

  /* receipts band: mark live for the bars, even when counters are skipped */
  if (band) {
    if (io && !reduced) new IntersectionObserver(function (e, o) { if (e[0].isIntersecting) { band.classList.add('is-live'); o.disconnect(); } }, { threshold: 0.3 }).observe(band);
    else band.classList.add('is-live');
  }

  /* Q&A cards: three lines, a button to open the rest */
  slice(document.querySelectorAll('[data-qa]')).forEach(function (card, k) {
    var p = card.querySelector('p');
    if (!p) return;
    p.id = p.id || 'qa-a-' + k;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'qa-more'; b.textContent = MORE;
    b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-controls', p.id);
    b.addEventListener('click', function () {
      var open = card.classList.toggle('is-open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
      b.textContent = open ? LESS : MORE;
    });
    card.appendChild(b);
    if (p.scrollHeight <= p.clientHeight + 2) { b.hidden = true; card.classList.add('is-open'); }
  });

  /* ---------- 3. spotlight ---------- */
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
