/* Flow AI shared motion layer.

   Two jobs:
   1. Reveal page content on scroll, staggering grid children so a row of
      cards arrives in sequence instead of all at once.
   2. Fade images in as they decode, so lazy-loaded art never pops.

   Card hover states are left to each page's own stylesheet, which already
   defines them everywhere on this site.

   Pages that already ship their own reveal system (marked by .reveal or
   .pre classes) keep it. This script only adds stagger delays, image
   load-in, and hover polish there. Pages with no system of their own opt
   into full auto-reveal with data-motion="auto" on <body>.

   Nothing is hidden unless this script runs, so a failed or blocked
   script leaves the page fully readable. */

(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var supported = 'IntersectionObserver' in window;
  var STAGGER_CAP = 8; // stop compounding delay after this many siblings

  /* ---------- images ---------- */

  function initImages() {
    var images = Array.prototype.slice.call(document.querySelectorAll('img'));
    images.forEach(function (img) {
      // Eager hero art is excluded: it should paint immediately.
      if (img.getAttribute('fetchpriority') === 'high') return;
      if (!img.hasAttribute('decoding')) img.setAttribute('decoding', 'async');
      if (reduced) return;

      var reveal = function () {
        img.setAttribute('data-motion-img', 'loaded');
      };

      img.setAttribute('data-motion-img', 'loading');
      if (img.complete && img.naturalWidth > 0) {
        // Already cached: show it on the next frame so the transition runs.
        window.requestAnimationFrame(reveal);
        return;
      }
      img.addEventListener('load', reveal, { once: true });
      img.addEventListener('error', reveal, { once: true });
      // Failsafe for images that never fire either event.
      window.setTimeout(reveal, 4000);
    });
  }

  /* ---------- shared helpers ---------- */

  function isGridLike(el) {
    if (el.children.length < 2) return false;
    var display = window.getComputedStyle(el).display;
    return display === 'grid' || display === 'flex';
  }

  function setStagger(el, index) {
    el.style.setProperty('--motion-index', String(Math.min(index, STAGGER_CAP)));
  }

  /* ---------- legacy pages: stagger their existing reveals ---------- */

  function enhanceLegacy() {
    var legacy = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
    if (!legacy.length) return false;

    if (!reduced) {
      // Group siblings so each row of cards cascades rather than landing flat.
      var groups = new Map();
      legacy.forEach(function (el) {
        var parent = el.parentElement;
        if (!parent) return;
        if (!groups.has(parent)) groups.set(parent, []);
        groups.get(parent).push(el);
      });

      groups.forEach(function (items) {
        if (items.length < 2) return;
        items.forEach(function (el, i) {
          // Additive only: the page's own transition property is untouched.
          el.style.transitionDelay = Math.min(i, STAGGER_CAP) * 65 + 'ms';
        });
      });
    }
    return true;
  }

  /* ---------- auto pages: build reveal units ---------- */

  function collectUnits() {
    var units = [];
    var sections = Array.prototype.slice.call(
      document.querySelectorAll('main section, main .hero, body > section, body > .hero')
    );
    if (!sections.length) {
      sections = Array.prototype.slice.call(document.querySelectorAll('section'));
    }

    sections.forEach(function (section) {
      // Rows are the meaningful blocks inside a section, looking through a
      // single .wrap container when one is present.
      var host = section;
      var wrap = section.querySelector(':scope > .wrap');
      if (wrap) host = wrap;

      var rows = Array.prototype.slice.call(host.children);
      rows.forEach(function (row) {
        if (row.hasAttribute('data-motion-skip')) return;
        if (isGridLike(row)) {
          // Animate the cards, not the container, so they can cascade.
          Array.prototype.slice.call(row.children).forEach(function (child, i) {
            units.push({ el: child, index: i, card: true });
          });
        } else {
          units.push({ el: row, index: 0, card: false });
        }
      });
    });

    return units.filter(function (unit) {
      return unit.el.nodeType === 1 && unit.el.offsetParent !== null;
    });
  }

  function initAuto() {
    var units = collectUnits();
    if (!units.length) return;

    units.forEach(function (unit) {
      setStagger(unit.el, unit.index);
      unit.el.setAttribute('data-motion-item', 'hidden');
      if (unit.card) unit.el.setAttribute('data-motion-card', 'hidden');
    });

    var show = function (el) {
      el.setAttribute('data-motion-item', 'shown');
      el.removeAttribute('data-motion-card');
    };

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          show(entry.target);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -6% 0px' }
    );

    units.forEach(function (unit) {
      var rect = unit.el.getBoundingClientRect();
      // Anything already on screen at load reveals right away, so the first
      // viewport is never blank.
      if (rect.top < window.innerHeight * 0.92) {
        window.requestAnimationFrame(function () { show(unit.el); });
        return;
      }
      observer.observe(unit.el);
    });

    // Failsafe: never leave content hidden.
    window.setTimeout(function () {
      units.forEach(function (unit) { show(unit.el); });
      observer.disconnect();
    }, 10000);
  }

  /* ---------- card hover ---------- */

  function start() {
    initImages();
    if (!supported || reduced) return;

    var hasLegacy = enhanceLegacy();
    if (!hasLegacy && document.body.getAttribute('data-motion') === 'auto') {
      initAuto();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
}());
