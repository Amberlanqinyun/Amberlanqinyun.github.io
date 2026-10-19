/* Amber Lan island navigation.

   On small screens the header's links fold into a full-screen menu behind a
   hamburger that turns into a cross. The menu is built here from the
   header's own links, so nothing is written twice in the HTML and the two
   languages stay in step. Without this script the links stay in a row under
   the brand (assets/highend.css), fully usable. */
(function () {
  'use strict';

  var header = document.querySelector('.site-header');
  var inner = header && header.querySelector('.site-header__inner');
  var nav = header && header.querySelector('.site-header__nav');
  if (!inner || !nav) return;

  var root = document.documentElement;
  var zh = /^zh/.test(root.lang);
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var phone = window.matchMedia('(max-width: 820px)');

  /* ---------- the button ---------- */

  var button = document.createElement('button');
  button.type = 'button';
  button.className = 'site-header__menu';
  button.setAttribute('aria-expanded', 'false');
  button.setAttribute('aria-controls', 'site-menu');
  button.setAttribute('aria-label', zh ? '菜单' : 'Menu');
  button.innerHTML = '<span></span><span></span>';
  inner.appendChild(button);

  /* ---------- the menu, cloned from the header ---------- */

  var menu = document.createElement('div');
  menu.id = 'site-menu';
  menu.className = 'site-menu';
  menu.hidden = true;
  menu.setAttribute('role', 'dialog');
  menu.setAttribute('aria-modal', 'true');
  menu.setAttribute('aria-label', zh ? '导航' : 'Navigation');

  var list = document.createElement('ul');
  list.className = 'site-menu__links';
  var links = Array.prototype.slice.call(nav.children).filter(function (el) {
    return el.tagName === 'A' && !el.classList.contains('site-header__cta');
  });
  links.forEach(function (a, i) {
    var li = document.createElement('li');
    var copy = a.cloneNode(true);
    copy.style.setProperty('--i', String(i));
    li.appendChild(copy);
    list.appendChild(li);
  });

  var foot = document.createElement('div');
  foot.className = 'site-menu__foot';
  var sw = nav.querySelector('.lang-switch');
  if (sw) foot.appendChild(sw.cloneNode(true));
  var cta = nav.querySelector('.site-header__cta');
  if (cta) foot.appendChild(cta.cloneNode(true));

  menu.appendChild(list);
  menu.appendChild(foot);
  header.appendChild(menu);
  root.classList.add('has-nav');

  /* ---------- open and close ---------- */

  var open = false;
  var lastFocus = null;
  var closing = null;

  function setOpen(next) {
    if (next === open) return;
    open = next;
    button.setAttribute('aria-expanded', String(next));
    if (closing) { window.clearTimeout(closing); closing = null; }

    if (next) {
      lastFocus = document.activeElement;
      menu.hidden = false;
      root.classList.add('menu-open');
      // two frames, so the menu is laid out before it fades in
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () { menu.classList.add('is-open'); });
      });
      var first = menu.querySelector('a');
      if (first) first.focus({ preventScroll: true });
      return;
    }

    menu.classList.remove('is-open');
    root.classList.remove('menu-open');
    var done = function () { closing = null; if (!open) menu.hidden = true; };
    if (reduced) done(); else closing = window.setTimeout(done, 460);
    var back = lastFocus && lastFocus.focus ? lastFocus : button;
    back.focus({ preventScroll: true });
  }

  button.addEventListener('click', function () { setOpen(!open); });
  menu.addEventListener('click', function (event) {
    if (event.target.closest('a')) setOpen(false);
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && open) setOpen(false);
  });

  // Keep Tab inside the menu while it is open: button, links, footer, button.
  function focusable() {
    return Array.prototype.slice.call(menu.querySelectorAll('a'));
  }
  menu.addEventListener('keydown', function (event) {
    if (event.key !== 'Tab' || !open) return;
    var items = focusable();
    if (!items.length) return;
    if (event.shiftKey && document.activeElement === items[0]) {
      event.preventDefault(); button.focus();
    } else if (!event.shiftKey && document.activeElement === items[items.length - 1]) {
      event.preventDefault(); button.focus();
    }
  });
  button.addEventListener('keydown', function (event) {
    if (!open || event.key !== 'Tab') return;
    var items = focusable();
    if (!items.length) return;
    event.preventDefault();
    (event.shiftKey ? items[items.length - 1] : items[0]).focus();
  });

  // The menu belongs to the phone layout; a wider viewport closes it.
  var onChange = function (event) { if (!event.matches) setOpen(false); };
  if (phone.addEventListener) phone.addEventListener('change', onChange);
  else if (phone.addListener) phone.addListener(onChange);
}());
