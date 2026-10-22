document.documentElement.classList.add('has-glass');

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

/* The hero is the run: scroll progress through the pinned hero, written as --p. */
(function () {
  var tracks = Array.prototype.slice.call(document.querySelectorAll('.hero--run, .rise-track, .scene'));
  if (!tracks.length || !window.matchMedia) return;
  var mq = window.matchMedia('(min-width: 901px) and (prefers-reduced-motion: no-preference)');
  var raf = 0;
  function paint() {
    raf = 0;
    tracks.forEach(function (hero) {
      if (!mq.matches) { hero.style.removeProperty('--p'); hero.classList.remove('is-run'); return; }
      var r = hero.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var p = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 0;
      hero.style.setProperty('--p', p.toFixed(4));
      hero.classList.toggle('is-run', p > 0.5);
    });
  }
  function ask() { if (!raf) raf = requestAnimationFrame(paint); }
  window.addEventListener('scroll', ask, { passive: true });
  window.addEventListener('resize', ask);
  if (mq.addEventListener) mq.addEventListener('change', ask);
  paint();
}());

/* The chapter rail on How it works marks the scene in view. */
(function () {
  var rail = document.querySelector('.chapters');
  if (!rail || !('IntersectionObserver' in window)) return;
  var links = {}; rail.querySelectorAll('a[data-for]').forEach(function (a) { links[a.getAttribute('data-for')] = a; });
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { Object.keys(links).forEach(function (k) { links[k].classList.toggle('is-here', k === e.target.id); }); } });
  }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });
  document.querySelectorAll('.scene[id]').forEach(function (sc) { io.observe(sc); });
}());

