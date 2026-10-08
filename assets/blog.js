/* Flow AI guides: index filters (state in the address) and the article contents rail. */
(function () {
  'use strict';
  var ZH = /^zh/.test(document.documentElement.lang);

  /* ---------------- index: topic, sort, view */
  var grid = document.querySelector('[data-posts]');
  if (grid) {
    var topicSel = document.querySelector('[data-filter="topic"]');
    var sortSel = document.querySelector('[data-filter="sort"]');
    var count = document.querySelector('[data-count]');
    var empty = document.querySelector('[data-empty]');
    var viewBtns = document.querySelectorAll('[data-view]');
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.post-card'));
    var params = new URLSearchParams(location.search);

    var view = params.get('view') === 'list' ? 'list' : 'grid';
    if (topicSel) topicSel.value = params.get('topic') || '';
    if (sortSel) sortSel.value = params.get('sort') || 'new';
    if (topicSel && topicSel.value !== (params.get('topic') || '')) topicSel.value = '';

    function apply(push) {
      var topic = topicSel ? topicSel.value : '';
      var sort = sortSel ? sortSel.value : 'new';
      var shown = 0;
      cards.forEach(function (c) {
        var on = !topic || c.dataset.topic === topic;
        c.hidden = !on;
        if (on) shown++;
      });
      var sorted = cards.slice().sort(function (a, b) {
        if (sort === 'az') return a.dataset.title.localeCompare(b.dataset.title);
        if (sort === 'short') return (+a.dataset.minutes) - (+b.dataset.minutes);
        return b.dataset.date.localeCompare(a.dataset.date);
      });
      sorted.forEach(function (c) { grid.appendChild(c); });
      grid.setAttribute('data-view', view);
      viewBtns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.view === view)); });
      document.querySelectorAll('[data-topic-link]').forEach(function (a) {
        a.setAttribute('aria-current', String(a.dataset.topicLink === topic));
      });
      if (count) count.textContent = ZH ? shown + ' 篇指南' : shown + (shown === 1 ? ' guide' : ' guides');
      if (empty) empty.hidden = shown !== 0;
      if (push) {
        var p = new URLSearchParams();
        if (topic) p.set('topic', topic);
        if (sort !== 'new') p.set('sort', sort);
        if (view !== 'grid') p.set('view', view);
        var q = p.toString();
        history.replaceState(null, '', location.pathname + (q ? '?' + q : '') + location.hash);
      }
    }

    if (topicSel) topicSel.addEventListener('change', function () { apply(true); });
    if (sortSel) sortSel.addEventListener('change', function () { apply(true); });
    viewBtns.forEach(function (b) {
      b.addEventListener('click', function () { view = b.dataset.view; apply(true); });
    });
    document.querySelectorAll('[data-topic-link]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        topicSel.value = topicSel.value === a.dataset.topicLink ? '' : a.dataset.topicLink;
        apply(true);
        document.getElementById('posts').scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
    apply(false);
  }

  /* ---------------- article: contents states, progress, minutes left */
  var toc = document.querySelector('.toc__list');
  var article = document.querySelector('.article-main');
  if (toc && article) {
    var links = Array.prototype.slice.call(toc.querySelectorAll('a[data-toc]'));
    var targets = links.map(function (a) { return document.getElementById(a.dataset.toc); });
    var bar = document.querySelector('[data-progress]');
    var left = document.querySelector('[data-minutes-left]');
    var total = parseInt((document.querySelector('.rail__facts dd:last-child') || {}).textContent, 10) || 0;
    var box = document.querySelector('.toc__box');
    var narrow = window.matchMedia('(max-width: 860px)');
    function fitBox() { if (box) box.open = !narrow.matches; }
    if (box) {
      fitBox();
      if (narrow.addEventListener) narrow.addEventListener('change', fitBox);
      // On wide screens the contents stay open: the summary is a label, not a toggle.
      box.querySelector('summary').addEventListener('click', function (e) { if (!narrow.matches) e.preventDefault(); });
      toc.addEventListener('click', function (e) { if (narrow.matches && e.target.closest('a')) box.open = false; });
    }

    var ticking = false;
    function update() {
      ticking = false;
      var rect = article.getBoundingClientRect();
      var h = rect.height - window.innerHeight * 0.6;
      var p = Math.min(1, Math.max(0, -rect.top / (h > 0 ? h : 1)));
      if (bar) bar.style.width = (p * 100).toFixed(1) + '%';
      if (left && total) {
        var m = Math.ceil(total * (1 - p));
        left.textContent = ZH ? (p >= 0.98 ? '已读完' : '还剩 ' + m + ' 分钟') : (p >= 0.98 ? 'Done' : m + ' min left');
      }
      var line = window.innerHeight * 0.3;
      var current = -1;
      targets.forEach(function (t, i) { if (t && t.getBoundingClientRect().top <= line) current = i; });
      links.forEach(function (a, i) {
        a.dataset.state = i < current ? 'read' : (i === current ? 'current' : 'ahead');
        if (i === current) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
      });
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update);
    update();
  }
})();
