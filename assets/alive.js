/* Flow AI life layer.

   Three small jobs, all decorative, all fail-safe:
   1. Split a [data-words] heading into words so the entrance in
      texture.css can raise them one at a time. Text content is unchanged.
   2. Hand the cursor position to glass panels, so the light inside each
      one follows the pointer.
   3. Ease [data-parallax] elements a few pixels against the pointer, so
      the hero has depth.

   The inline flag in <head> (html.js) is what lets the entrance states
   apply at all; without this script the page sits at rest, fully visible. */

(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  Array.prototype.slice.call(document.querySelectorAll('[data-words]')).forEach(function (el) {
    if (el.getAttribute('data-words') === 'ready') return;
    var words = el.textContent.trim().split(/\s+/);
    el.textContent = '';
    words.forEach(function (word, i) {
      var outer = document.createElement('span');
      outer.className = 'w';
      var inner = document.createElement('span');
      inner.textContent = word;
      inner.style.setProperty('--i', String(i));
      outer.appendChild(inner);
      el.appendChild(outer);
      if (i < words.length - 1) el.appendChild(document.createTextNode(' '));
    });
    el.setAttribute('data-words', 'ready');
  });

  if (reduced || !window.matchMedia('(pointer: fine)').matches) return;

  document.addEventListener('pointermove', function (e) {
    var card = e.target && e.target.closest ? e.target.closest('.glass') : null;
    if (!card) return;
    var r = card.getBoundingClientRect();
    card.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
    card.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
  }, { passive: true });

  var items = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
  if (!items.length) return;
  var tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
  function step() {
    raf = null;
    cx += (tx - cx) * 0.08;
    cy += (ty - cy) * 0.08;
    items.forEach(function (el) {
      var depth = parseFloat(el.getAttribute('data-parallax')) || 10;
      el.style.translate = (-cx * depth).toFixed(2) + 'px ' + (-cy * depth).toFixed(2) + 'px';
    });
    if (Math.abs(tx - cx) > 0.002 || Math.abs(ty - cy) > 0.002) raf = window.requestAnimationFrame(step);
  }
  window.addEventListener('pointermove', function (e) {
    tx = e.clientX / window.innerWidth - 0.5;
    ty = e.clientY / window.innerHeight - 0.5;
    if (!raf) raf = window.requestAnimationFrame(step);
  }, { passive: true });
}());
