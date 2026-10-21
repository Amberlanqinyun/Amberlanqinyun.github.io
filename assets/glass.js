/* Amber Lan · glass system (22 Oct 2026).
   The sheen on every glass panel follows the pointer, the way it already
   does on the two hero cards. Panels are the selectors in glass.css. */
(function () {
  if (!window.matchMedia || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var SEL = '.doors, .job, .install, .outcome, .offer, .flagship, .team__hq, .team__col, .team__review, .dgrid, ' +
            '.grid > .part.case, .proof-card, .tpl-card, .path, .glass, .compound, .poss, .rule, .split__col, .pv-card, ' +
            '.receipt, .qa-card, .work-card, .pp-card, .pp-table, .pp-contact, .post-card__figure, .article-figure, .featured, .short-answer';
  var current = null, raf = 0, px = 0, py = 0;
  function paint() {
    raf = 0;
    if (!current) return;
    var r = current.getBoundingClientRect();
    current.style.setProperty('--mx', (px - r.left).toFixed(0) + 'px');
    current.style.setProperty('--my', (py - r.top).toFixed(0) + 'px');
  }
  function clear(el) { if (!el) return; el.style.removeProperty('--mx'); el.style.removeProperty('--my'); }
  document.addEventListener('pointermove', function (e) {
    var el = e.target.closest ? e.target.closest(SEL) : null;
    if (el !== current) { clear(current); current = el; }
    if (!current) return;
    px = e.clientX; py = e.clientY;
    if (!raf) raf = requestAnimationFrame(paint);
  }, { passive: true });
  document.addEventListener('pointerleave', function () { clear(current); current = null; }, true);
}());

/* The glossary rail marks the letter you are reading. */
(function () {
  var jump = document.querySelector('.glossary__jump');
  if (!jump || !('IntersectionObserver' in window)) return;
  var links = {};
  jump.querySelectorAll('a[href^="#letter-"]').forEach(function (a) { links[a.getAttribute('href').slice(1)] = a; });
  var heads = Array.prototype.slice.call(document.querySelectorAll('.glossary__letter[id]'));
  if (!heads.length) return;
  var visible = {};
  function paint() {
    var first = heads.filter(function (h) { return visible[h.id]; })[0];
    if (!first) return;
    Object.keys(links).forEach(function (id) {
      if (id === first.id) links[id].setAttribute('aria-current', 'true'); else links[id].removeAttribute('aria-current');
    });
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
    paint();
  }, { rootMargin: '-15% 0px -70% 0px', threshold: 0 });
  heads.forEach(function (h) { io.observe(h); });
}());
