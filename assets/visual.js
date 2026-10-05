/* Flow AI visual layer: sprint explorer tabs and figure reveal. */
(function () {
  "use strict";

  // Figures animate once they scroll into view.
  var figs = document.querySelectorAll(".fig, .week");
  function show(el) { el.classList.add("is-in"); }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { show(e.target); io.unobserve(e.target); }
      });
    }, { threshold: 0.35 });
    figs.forEach(function (f) { io.observe(f); });
  } else {
    figs.forEach(show);
  }

  // Sprint explorer: ARIA tabs with arrow keys and a shareable hash.
  document.querySelectorAll("[data-sx]").forEach(function (root) {
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute("aria-controls")); });

    function select(i, opts) {
      opts = opts || {};
      tabs.forEach(function (t, j) {
        var on = i === j;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        panels[j].hidden = !on;
        panels[j].classList.toggle("is-shown", on);
      });
      var p = panels[i];
      // Replay the panel's figures so every tab feels alive.
      p.querySelectorAll(".fig, .week").forEach(function (f) {
        f.classList.remove("is-in");
        void f.offsetWidth;
        requestAnimationFrame(function () { show(f); });
      });
      if (opts.focus) tabs[i].focus();
      if (opts.hash && history.replaceState) history.replaceState(null, "", "#" + tabs[i].dataset.slug);
      if (opts.scroll) tabs[i].scrollIntoView({ block: "nearest", inline: "nearest" });
      if (window.dataLayer && opts.hash) window.dataLayer.push({ event: "sprint_tab", sprint: tabs[i].dataset.slug });
    }

    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(i, { hash: true }); });
      t.addEventListener("keydown", function (e) {
        var k = e.key, n = tabs.length, to = null;
        if (k === "ArrowRight") to = (i + 1) % n;
        else if (k === "ArrowLeft") to = (i - 1 + n) % n;
        else if (k === "Home") to = 0;
        else if (k === "End") to = n - 1;
        if (to !== null) { e.preventDefault(); select(to, { focus: true, hash: true, scroll: true }); }
      });
    });

    var start = 0;
    var h = location.hash.replace("#", "");
    tabs.forEach(function (t, i) { if (t.dataset.slug === h) start = i; });
    select(start);
    if (h && start > 0) {
      requestAnimationFrame(function () { root.scrollIntoView({ block: "start" }); });
    }
  });
})();
