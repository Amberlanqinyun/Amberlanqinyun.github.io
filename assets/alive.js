/* Flow AI life layer.

   Four small jobs, all decorative, all fail-safe:
   1. Split headlines into words, then group the words by line, so the
      entrance in texture.css can raise each line as a unit, top to bottom.
      The hero h1 carries data-words; every h2 in main is taken too. Text
      content is unchanged, and a heading with inline markup is left alone.
   2. Build the ticker loop from a single list ([data-ticker]).
   3. Hand the cursor position to glass panels, so the light inside each
      one follows the pointer.
   4. Ease [data-parallax] elements a few pixels against the pointer, so
      the hero has depth.

   The inline flag in <head> (html.js) is what lets the entrance states
   apply at all; without this script the page sits at rest, fully visible. */

(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var slice = function (list) { return Array.prototype.slice.call(list); };

  /* ---------- headlines, line by line ---------- */

  function splitLines(el) {
    if (el.getAttribute('data-words') === 'ready') return;
    if (el.children.length) { el.setAttribute('data-words', 'ready'); return; }
    var text = el.textContent.trim(), words, gap = ' ';
    /* Chinese has no spaces between words. Break headlines at phrase boundaries instead:
       each clause, with its punctuation, is one unit, so a line never splits a word in two
       or starts with 。or ，. A clause wider than the column still wraps inside itself. */
    if (/^zh/.test(document.documentElement.lang) && /[\u3400-\u9fff]/.test(text)) {
      gap = '';
      words = text.match(/[^，。、；：？！,;:?]+[，。、；：？！,;:?]*\s*/g) || [text];
    } else {
      words = text.split(/\s+/);
    }
    el.textContent = '';
    words.forEach(function (word, i) {
      if (word === ' ') { el.appendChild(document.createTextNode(' ')); return; }
      var outer = document.createElement('span');
      outer.className = 'w';
      var inner = document.createElement('span');
      inner.textContent = word;
      outer.appendChild(inner);
      el.appendChild(outer);
      if (gap && i < words.length - 1) el.appendChild(document.createTextNode(gap));
    });
    var line = -1, lastTop = null;
    slice(el.querySelectorAll('.w')).forEach(function (w) {
      var top = w.offsetTop;
      if (top !== lastTop) { line += 1; lastTop = top; }
      w.firstChild.style.setProperty('--i', String(line));
    });
    el.setAttribute('data-words', 'ready');
  }

  function prepareHeadlines() {
    var targets = slice(document.querySelectorAll('[data-words], main h2'));
    targets.forEach(function (el) {
      if (!el.hasAttribute('data-words')) el.setAttribute('data-words', '');
      splitLines(el);
    });
  }
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(prepareHeadlines, prepareHeadlines);
  } else {
    prepareHeadlines();
  }

  /* ---------- ticker ---------- */

  slice(document.querySelectorAll('[data-ticker]')).forEach(function (host) {
    var list = host.firstElementChild;
    if (!list || !list.children.length) return;
    var first = list.children[0].getBoundingClientRect();
    var last = list.children[list.children.length - 1].getBoundingClientRect();
    var width = Math.max(1, last.right - first.left + 48);
    var copies = Math.max(2, Math.ceil(window.innerWidth * 1.1 / width));
    var inner = document.createElement('div');
    inner.className = 'ticker__inner';
    function group(withOriginal) {
      var g = document.createElement('div');
      g.className = 'ticker__group';
      for (var i = 0; i < copies; i++) {
        var node = (withOriginal && i === 0) ? list : list.cloneNode(true);
        if (node !== list) node.setAttribute('aria-hidden', 'true');
        g.appendChild(node);
      }
      return g;
    }
    inner.appendChild(group(true));
    inner.appendChild(group(false));
    host.appendChild(inner);
    host.classList.add('ticker');
    host.style.setProperty('--ticker-duration', Math.round(copies * width / 38) + 's');
  });

  if (reduced || !window.matchMedia('(pointer: fine)').matches) return;

  /* ---------- glass spotlight ---------- */

  document.addEventListener('pointermove', function (e) {
    var card = e.target && e.target.closest ? e.target.closest('.glass') : null;
    if (!card) return;
    var r = card.getBoundingClientRect();
    card.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
    card.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
  }, { passive: true });

  /* ---------- parallax ---------- */

  var items = slice(document.querySelectorAll('[data-parallax]'));
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
