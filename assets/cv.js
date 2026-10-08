/* Interactive CV (/about): the lane switchboard and the print button.
   The board plays through its lanes while it is on screen, pauses under the pointer,
   and hands over for good the moment someone picks a lane. Each lane replays its
   small working surface when it opens. Without this script every lane renders in full,
   one after another, and printing still works through the browser's own command. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var board = document.querySelector('[data-board]');
  if (board) {
    var tabs = Array.prototype.slice.call(board.querySelectorAll('[role="tab"]'));
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });
    var counter = board.querySelector('[data-board-count]');
    var DWELL = 7000, current = 0, timer = 0, auto = !reduced, paused = false, inView = false;

    function play(panel) {
      if (!panel) return;
      panel.classList.remove('play');
      void panel.offsetWidth;
      panel.classList.add('play');
    }

    function select(i, focus) {
      current = i;
      tabs.forEach(function (t, j) {
        var on = j === i;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        t.classList.remove('is-timing');
        if (panels[j]) panels[j].hidden = !on;
      });
      if (counter) counter.textContent = String(i + 1).padStart(2, '0') + ' / ' + String(tabs.length).padStart(2, '0');
      play(panels[i]);
      if (focus) tabs[i].focus();
      schedule();
    }

    function schedule() {
      clearTimeout(timer);
      if (!auto || paused || !inView) return;
      var t = tabs[current];
      t.style.setProperty('--dwell', DWELL + 'ms');
      void t.offsetWidth;
      t.classList.add('is-timing');
      timer = setTimeout(function () { select((current + 1) % tabs.length, false); }, DWELL);
    }

    function stop() { auto = false; clearTimeout(timer); tabs.forEach(function (t) { t.classList.remove('is-timing'); }); board.classList.add('is-manual'); }

    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { stop(); select(i, false); });
      t.addEventListener('keydown', function (e) {
        var next = null;
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') next = (i + 1) % tabs.length;
        if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') next = (i - 1 + tabs.length) % tabs.length;
        if (e.key === 'Home') next = 0;
        if (e.key === 'End') next = tabs.length - 1;
        if (next !== null) { e.preventDefault(); stop(); select(next, true); }
      });
    });
    board.addEventListener('pointerenter', function () { paused = true; clearTimeout(timer); tabs[current].classList.remove('is-timing'); });
    board.addEventListener('pointerleave', function () { paused = false; schedule(); });
    board.addEventListener('focusin', function () { paused = true; clearTimeout(timer); });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (e) {
        var was = inView; inView = e[0].isIntersecting;
        if (inView && !was) { play(panels[current]); schedule(); }
        if (!inView) { clearTimeout(timer); tabs[current].classList.remove('is-timing'); }
      }, { threshold: 0.4 }).observe(board);
    }
    select(0, false);
  }

  /* career: a track of years; each segment opens its role. The current role starts open. */
  var career = document.querySelector('[data-career]');
  if (career) {
    var segs = Array.prototype.slice.call(career.querySelectorAll('[role="tab"]'));
    var rpanels = segs.map(function (s) { return document.getElementById(s.getAttribute('aria-controls')); });
    var open = function (i, focus) {
      segs.forEach(function (s, j) {
        var on = j === i;
        s.setAttribute('aria-selected', on ? 'true' : 'false');
        s.tabIndex = on ? 0 : -1;
        if (rpanels[j]) { rpanels[j].hidden = !on; rpanels[j].classList.toggle('play', on); }
      });
      if (focus) segs[i].focus();
    };
    segs.forEach(function (s, i) {
      s.addEventListener('click', function () { open(i, false); });
      s.addEventListener('mouseenter', function () { if (window.matchMedia('(pointer: fine)').matches) open(i, false); });
      s.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = (i + 1) % segs.length;
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = (i - 1 + segs.length) % segs.length;
        if (e.key === 'Home') n = 0;
        if (e.key === 'End') n = segs.length - 1;
        if (n !== null) { e.preventDefault(); open(n, true); }
      });
    });
    open(segs.length - 1, false);
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-print]'), function (b) {
    b.addEventListener('click', function () {
      if (window.dataLayer) window.dataLayer.push({ event: 'cv_print' });
      window.print();
    });
  });
}());
