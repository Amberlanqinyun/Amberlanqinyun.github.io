/* Flow AI dot. The amber dot at the head of the mark is Flow Intelligence: a glass orb
   with the amber light inside it. The agents are made of the same glass, each its own
   soft shape, carrying that light into the work.

   One material for the whole family, drawn the way glass is lit rather than outlined:
   a translucent body, a bright rim where the edge catches the light, a soft highlight
   up top, and warm light pooling at the bottom. No strokes around bodies or eyes.

   Faces: googly eyes (a white eye, a glossy pupil that rolls inside it with a little
   weight), calm and happy arcs, a flat line, and a mouth that follows the state.

   One file, no dependencies. Mount on an <svg viewBox="0 0 100 100"> and it does the
   rest: spring gaze, saccades, eyes-lead-body-follows tilt, perspective, the double
   blink as a lid, breathing, nod, the review ring, the dark state after ten at night in
   Auckland. One shared animation loop, paused for dots that are off screen. Under
   56 px rendered, agents switch to a solid cream body so the face still reads.

   Decorative and fail-safe: every SVG it mounts into is empty or holds a static dot,
   so a blocked script changes nothing a visitor needs. The boot section at the end
   wires the demo window, the 404 and the night state on this site. */

window.FlowDot = (function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var INK = '#0e0e0d', CREAM = '#faf8f3', AMBER = '#e4a43c';
  var uid = 0;
  function el(n, a) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); return e; }

  /* Shared gradients and filters, injected once. */
  var defsDone = false;
  function defs() {
    if (defsDone || !document.body) return; defsDone = true;
    var svg = el('svg', { width: 0, height: 0, 'aria-hidden': 'true', style: 'position:absolute;width:0;height:0' });
    svg.innerHTML =
      '<defs>' +
      /* the light inside Flow Intelligence, and the glow it throws */
      '<radialGradient id="flowdot-core" cx="50%" cy="60%" r="55%"><stop offset="0" stop-color="#fbe0a8"/><stop offset=".5" stop-color="#f1bb5a"/><stop offset=".85" stop-color="#df9c36"/><stop offset="1" stop-color="#c47f27"/></radialGradient>' +
      '<radialGradient id="flowdot-halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#e4a43c" stop-opacity=".42"/><stop offset=".45" stop-color="#e4a43c" stop-opacity=".14"/><stop offset="1" stop-color="#e4a43c" stop-opacity="0"/></radialGradient>' +
      '<radialGradient id="flowdot-core-night" cx="50%" cy="58%" r="50%"><stop offset="0" stop-color="#3a301c"/><stop offset=".7" stop-color="#1d1a13"/><stop offset="1" stop-color="#141311"/></radialGradient>' +
      '<radialGradient id="flowdot-halo-night" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#e4a43c" stop-opacity=".08"/><stop offset="1" stop-color="#e4a43c" stop-opacity="0"/></radialGradient>' +
      /* glass: body, rim light (top bright, sides gone, a little bounce at the bottom), warm pool */
      '<linearGradient id="flowdot-glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".3"/><stop offset=".5" stop-color="#ffffff" stop-opacity=".1"/><stop offset="1" stop-color="#ffffff" stop-opacity=".16"/></linearGradient>' +
      '<linearGradient id="flowdot-rim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".9"/><stop offset=".28" stop-color="#ffffff" stop-opacity=".16"/><stop offset=".62" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#ffe2ad" stop-opacity=".5"/></linearGradient>' +
      '<radialGradient id="flowdot-pool" cx="60%" cy="96%" r="70%"><stop offset="0" stop-color="#f3c572" stop-opacity=".62"/><stop offset="1" stop-color="#e4a43c" stop-opacity="0"/></radialGradient>' +
      '<radialGradient id="flowdot-sheen" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffffff" stop-opacity=".75"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>' +
      /* eyes: a white with a soft fall-off at the bottom, a glossy pupil */
      '<radialGradient id="flowdot-white" cx="44%" cy="36%" r="66%"><stop offset="0" stop-color="#ffffff"/><stop offset=".72" stop-color="#f7f3ec"/><stop offset="1" stop-color="#ddd4c4"/></radialGradient>' +
      '<radialGradient id="flowdot-pupil" cx="38%" cy="32%" r="72%"><stop offset="0" stop-color="#45433f"/><stop offset="1" stop-color="#0e0e0d"/></radialGradient>' +
      '<filter id="flowdot-soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.1"/></filter>' +
      '<filter id="flowdot-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.2"/></filter>' +
      '<filter id="flowdot-goo" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur in="SourceGraphic" stdDeviation="2.2" result="b"/><feColorMatrix in="b" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -10" result="g"/><feComposite in="SourceGraphic" in2="g" operator="atop"/></filter>' +
      '</defs>';
    document.body.appendChild(svg);
  }

  /* Bodies, drawn in a 100 box around (50, 52). Every corner is round. eyes and mouth
     are anchors in the same box; tone is the solid cream used at small sizes; sheen is
     where the soft highlight sits. */
  function rr(x, y, w, h, r) { return 'M' + (x + r) + ' ' + y + 'H' + (x + w - r) + 'A' + r + ' ' + r + ' 0 0 1 ' + (x + w) + ' ' + (y + r) + 'V' + (y + h - r) + 'A' + r + ' ' + r + ' 0 0 1 ' + (x + w - r) + ' ' + (y + h) + 'H' + (x + r) + 'A' + r + ' ' + r + ' 0 0 1 ' + x + ' ' + (y + h - r) + 'V' + (y + r) + 'A' + r + ' ' + r + ' 0 0 1 ' + (x + r) + ' ' + y + 'Z'; }
  var SHAPES = {
    orb:      { d: 'M16 52a34 34 0 1 0 68 0a34 34 0 1 0 -68 0Z', eyes: [[41, 47], [59, 47]], mouth: [50, 62], sheen: [40, 31, 13, 7], tone: AMBER },
    circle:   { d: 'M20 52a30 30 0 1 0 60 0a30 30 0 1 0 -60 0Z', eyes: [[41, 49], [59, 49]], mouth: [50, 63], sheen: [40, 34, 11, 6], tone: CREAM },
    pill:     { d: rr(18, 38, 64, 30, 15), tf: 'rotate(-14 50 53)', eyes: [[40, 52], [57, 49]], mouth: [50, 60], sheen: [36, 41, 12, 3.5], tone: '#e9e3d6' },
    triangle: { d: 'M50 24C56 24 59 27 62 32L76 57C80 64 76 76 66 76L34 76C24 76 20 64 24 57L38 32C41 27 44 24 50 24Z', eyes: [[41, 56], [59, 56]], mouth: [50, 68], sheen: [45, 33, 6, 4], tone: CREAM },
    blob:     { d: 'M50 22C69 21 81 36 79 54C77 73 62 81 46 79C29 77 19 62 23 45C26 31 36 23 50 22Z', eyes: [[40, 49], [59, 48]], mouth: [50, 62], sheen: [38, 31, 11, 5], tone: CREAM },
    bean:     { d: 'M22 54C22 38 34 30 46 33C50 34 54 34 58 32C71 26 80 38 78 54C76 70 64 78 50 78C33 78 22 68 22 54Z', eyes: [[41, 52], [59, 52]], mouth: [50, 64], sheen: [34, 38, 8, 4], tone: '#d9d1c1' },
    arch:     { d: 'M24 70V50A26 26 0 0 1 76 50V70Q76 82 64 82H36Q24 82 24 70Z', eyes: [[42, 54], [58, 54]], mouth: [51, 68], sheen: [40, 31, 11, 4.5], tone: '#e9e3d6' },
    squircle: { d: rr(25, 27, 50, 50, 20), eyes: [[40, 50], [60, 50]], mouth: [50, 61], sheen: [40, 32, 11, 3.5], tone: CREAM },
    capsule:  { d: rr(32, 16, 36, 68, 18), eyes: [[43, 42], [57, 42]], mouth: [50, 59], sheen: [44, 22, 7, 4], tone: '#d9d1c1' },
    egg:      { d: 'M50 22C63 22 74 40 74 57C74 71 63 80 50 80C37 80 26 71 26 57C26 40 37 22 50 22Z', eyes: [[42, 55], [58, 55]], mouth: [50, 69], sheen: [43, 31, 7, 5], tone: '#e9e3d6' },
    square:   { d: rr(28, 30, 44, 44, 15), tf: 'rotate(12 50 52)', eyes: [[42, 49], [58, 51]], mouth: [51, 64], sheen: [42, 35, 10, 3.5], tone: CREAM },
    cloud:    { d: 'M32 72C22 72 18 60 26 55C24 45 34 38 43 42C46 32 62 30 66 40C76 38 84 48 79 57C86 62 82 73 72 72Z', eyes: [[45, 55], [61, 54]], mouth: [53, 66], sheen: [52, 38, 8, 3.5], tone: '#d9d1c1' }
  };

  /* Eye types, drawn at the origin. Googly eyes share one size everywhere: a 7-unit
     white and a 3.3-unit pupil. Line eyes share one stroke. */
  var EYE_R = 7, PUPIL_R = 3.3, LINE_W = 2.8, MOUTH_W = 2.4;
  var STYLES = {
    googly: { label: 'Googly', note: 'A white eye and a glossy pupil that rolls inside it, with a little weight. The default for open eyes.' },
    calm:   { label: 'Calm arcs', note: 'Closed and content. For agents that work quietly.', d: 'M-5.5 -1.5Q0 4.5 5.5 -1.5' },
    happy:  { label: 'Happy arcs', note: 'Eyes smiling. Every face wears them when a run is done.', d: 'M-5.5 2Q0 -5.5 5.5 2' },
    flat:   { label: 'Flat line', note: 'Unhurried and certain. Positioning wears it.', d: 'M-4.5 0H4.5' },
    sleepy: { label: 'Sleepy', note: 'After ten at night in Auckland.', d: 'M-5 -.5Q0 3.5 5 -.5' },
    lens:   { label: 'Lens', note: 'A ring of glass around one googly eye. AI search reads through it.' }
  };
  var MOUTHS = {
    smile: 'M-6 -2Q0 4 6 -2', small: 'M-4.5 -1Q0 2.4 4.5 -1', wide: 'M-8 -3Q0 5 8 -3', side: 'M-3 0Q2 2 7 -2',
    flat: 'M-4 0H4', grin: 'M-12 -4Q0 9 12 -4', wobble: 'M-7 0Q-3.5 -3 0 0Q3.5 3 7 0', o: 'o'
  };
  /* Each agent: a body, its eyes (left, right), its resting mouth. The ten match the
     ten agents on /sprints/; positioning is Flow Intelligence's own job. Older keys stay
     as aliases so nothing that mounts them breaks. */
  var AGENTS = {
    'search':      { shape: 'triangle', eyes: ['lens', 'googly'], mouth: 'smile' },
    'content':     { shape: 'pill', eyes: ['calm', 'calm'], mouth: 'smile' },
    'social':      { shape: 'blob', eyes: ['happy', 'googly'], mouth: 'wide' },
    'outbound':    { shape: 'arch', eyes: ['googly', 'googly'], mouth: 'smile' },
    'conversion':  { shape: 'egg', eyes: ['googly', 'googly'], mouth: 'small' },
    'launch':      { shape: 'capsule', eyes: ['googly', 'googly'], mouth: 'o' },
    'paid':        { shape: 'square', eyes: ['googly', 'googly'], mouth: 'smile' },
    'community':   { shape: 'cloud', eyes: ['googly', 'googly'], mouth: 'small' },
    'measurement': { shape: 'squircle', eyes: ['flat', 'flat'], mouth: 'small' },
    'reporting':   { shape: 'bean', eyes: ['happy', 'happy'], mouth: 'wide' }
  };
  AGENTS['ai-search'] = AGENTS.search; AGENTS.report = AGENTS.reporting; AGENTS.growth = AGENTS.conversion;
  AGENTS.positioning = AGENTS.measurement; AGENTS.analytics = AGENTS.measurement; AGENTS['content-qa'] = AGENTS.measurement;
  var MOODS = {
    idle:   { free: true,  k: 1,    tilt: 0,  breath: 0.012, rate: 1.6, mouth: 'smile', ring: false, orbit: false, scan: false },
    think:  { look: [-0.7, -0.8], k: 0.96, tilt: -7, breath: 0.01, rate: 1.6, mouth: 'side', ring: false, orbit: false, scan: false },
    work:   { look: [0.5, 0.6],   k: 0.96, tilt: 4,  breath: 0.035, rate: 9, mouth: 'flat', ring: false, orbit: true, scan: true },
    review: { look: [0, 0],       k: 1.08, tilt: 0,  breath: 0.02, rate: 2.2, mouth: 'small', ring: true, orbit: false, scan: false },
    done:   { look: [0, 0.1],     k: 1,    tilt: 0,  breath: 0.02, rate: 1.6, mouth: 'grin', eye: 'happy', ring: false, orbit: false, scan: false },
    late:   { free: true,  k: 1,    tilt: 0,  breath: 0.01, rate: 1.2, mouth: 'small', eye: 'sleepy', night: true, ring: false, orbit: false, scan: false },
    error:  { daze: [[0.7, -0.65], [-0.65, 0.7]], k: 1, tilt: 9, breath: 0, rate: 1, mouth: 'wobble', ring: false, orbit: false, scan: false }
  };
  function spring(st, target, k, d, dt) { var a = (target - st.x) * k - st.v * d; st.v += a * dt; st.x += st.v * dt; }

  var dots = [], running = false;
  function Dot(svg, o) {
    o = o || {}; defs();
    this.svg = svg; this.role = o.role || 'flow'; this.id = 'fd' + (++uid);
    var def = this.role === 'flow' ? { shape: 'orb', eyes: ['googly', 'googly'], mouth: 'smile' } : (AGENTS[o.agent] || { shape: 'circle', eyes: ['googly', 'googly'], mouth: 'smile' });
    if (o.shape) def = { shape: o.shape, eyes: def.eyes, mouth: def.mouth };
    if (o.eyes) def = { shape: def.shape, eyes: o.eyes, mouth: o.mouth || def.mouth };
    this.def = def; this.sh = SHAPES[def.shape] || SHAPES.circle;
    this.r = o.r || (this.role === 'flow' ? 32 : 34);
    this.k = this.r / (this.role === 'flow' ? 34 : 30);
    this.cx = 50; this.cy = 50 + (o.dy || 0);
    this.material = o.material || 'auto'; this.solid = this.material === 'solid';
    this.dbl = o.dbl !== false; this.glow = this.role === 'flow';
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (this.role === 'flow') svg.style.overflow = 'visible'; /* the glow fades past the box, never into a square */
    var sh = this.sh, gid = this.id + '-g';

    /* geometry once, used by every layer */
    var lib = el('defs', {}); var geo = el('path', { id: gid, d: sh.d }); if (sh.tf) geo.setAttribute('transform', sh.tf); lib.appendChild(geo);
    var clip = el('clipPath', { id: this.id + '-c' }); var cu = el('use', { href: '#' + gid }); clip.appendChild(cu); lib.appendChild(clip);
    svg.appendChild(lib);

    this.halo = el('circle', { cx: this.cx, cy: this.cy, r: this.r * 2.1, fill: 'url(#flowdot-halo)', opacity: this.glow ? 1 : 0 });
    this.gooG = el('g', {}); if (o.goo) this.gooG.setAttribute('filter', 'url(#flowdot-goo)');
    this.sats = [];
    if (this.role === 'flow') for (var i = 0; i < 3; i++) { var s = el('circle', { cx: this.cx, cy: this.cy, r: 0, fill: CREAM }); this.sats.push(s); this.gooG.appendChild(s); }
    svg.appendChild(this.halo); svg.appendChild(this.gooG);

    /* the body: glass layers, or one solid layer when small */
    this.body = el('g', {});
    var use = function (fill, extra) { var u = el('use', { href: '#' + gid, fill: fill }); for (var key in extra) u.setAttribute(key, extra[key]); return u; };
    this.glass = el('g', {});
    if (this.role === 'flow') {
      /* the light fills the orb; the glass shows only where it catches the light */
      this.core = use('url(#flowdot-core)');
      this.glass.appendChild(this.core);
    } else {
      this.glass.appendChild(use(sh.tone, { 'fill-opacity': 0.16 }));
      this.glass.appendChild(use('url(#flowdot-glass)'));
      this.glass.appendChild(use('url(#flowdot-pool)'));
    }
    /* rim light: the edge catching the light, clipped inside the body so it never reads as a line */
    var rimG = el('g', { 'clip-path': 'url(#' + this.id + '-c)' });
    rimG.appendChild(use('none', { stroke: 'url(#flowdot-rim)', 'stroke-width': 3.2 }));
    this.glass.appendChild(rimG);
    var sn = sh.sheen; this.sheen = el('ellipse', { cx: sn[0], cy: sn[1], rx: sn[2], ry: sn[3], fill: 'url(#flowdot-sheen)', opacity: this.role === 'flow' ? 0.8 : 0.75 });
    if (sh.tf) this.sheen.setAttribute('transform', sh.tf);
    rimG.appendChild(this.sheen);
    this.solidL = use(sh.tone);
    this.body.appendChild(this.glass); this.body.appendChild(this.solidL);
    svg.appendChild(this.body);

    this.ring = el('circle', { cx: this.cx, cy: this.cy, r: this.r, fill: 'none', stroke: AMBER, 'stroke-width': 1.5, 'stroke-opacity': 0 });
    svg.appendChild(this.ring);

    /* the face rides on its own group so it can lead the body */
    this.face = el('g', {});
    this.cheeks = el('g', { opacity: 0 });
    this.cheeks.appendChild(el('ellipse', { cx: sh.eyes[0][0] - 4, cy: sh.mouth[1] - 1, rx: 5, ry: 2.8, fill: '#f7d08a' }));
    this.cheeks.appendChild(el('ellipse', { cx: sh.eyes[1][0] + 4, cy: sh.mouth[1] - 1, rx: 5, ry: 2.8, fill: '#f7d08a' }));
    this.face.appendChild(this.cheeks);
    this.E = [el('g', {}), el('g', {})]; this.face.appendChild(this.E[0]); this.face.appendChild(this.E[1]);
    this.mouthG = el('g', { transform: 'translate(' + sh.mouth[0] + ' ' + sh.mouth[1] + ')' }); this.face.appendChild(this.mouthG);
    svg.appendChild(this.face);

    this.cheekA = 0; this.wob = { x: 0, v: 0 }; this.trails = []; this.curious = 0; this.ticUntil = 0; this.nextTic = 8 + Math.random() * 8;
    this.gaze = { x: { x: 0, v: 0 }, y: { x: 0, v: 0 } };
    this.pup = [{ x: 0, y: 0.3, vx: 0, vy: 0 }, { x: 0, y: 0.3, vx: 0, vy: 0 }];
    this.tiltS = { x: 0, v: 0 };
    this.target = [0, 0]; this.hold = null; this.t = Math.random() * 10; this.nextSac = 1 + Math.random() * 2; this.nextBlink = 2 + Math.random() * 3;
    this.nodAt = -1; this.lidAt = -1; this.mood = 'idle'; this.sized = this.material !== 'auto';
    if (!this.sized) { var w0 = svg.getBoundingClientRect().width; if (w0 > 0) { this.sized = true; this.solid = w0 < 56; } }
    this.applyMaterial();
    this.set(o.state || 'idle');
    dots.push(this); start();
  }

  Dot.prototype.applyMaterial = function () {
    var solid = this.solid && this.role !== 'flow';
    this.glass.style.display = solid ? 'none' : '';
    this.solidL.style.display = solid ? '' : 'none';
    if (this.role === 'flow') this.solidL.style.display = 'none';
    this.line = (this.role === 'flow' || solid) ? INK : CREAM;
    return this;
  };

  /* Draw both eyes and the mouth for the current mood. */
  Dot.prototype.drawFace = function () {
    var m = MOODS[this.mood] || MOODS.idle, self = this, sh = this.sh, night = !!m.night;
    var line = night ? CREAM : this.line;
    this.parts = [];
    [0, 1].forEach(function (i) {
      var g = self.E[i]; while (g.firstChild) g.removeChild(g.firstChild);
      var type = m.eye || self.def.eyes[i], p = { type: type, g: g, at: sh.eyes[i] };
      if (type === 'googly' || type === 'lens') {
        var lid = el('clipPath', { id: self.id + '-l' + i }); p.lidRect = el('rect', { x: -EYE_R - 2, y: -EYE_R - 2, width: EYE_R * 2 + 4, height: EYE_R * 2 + 4 }); lid.appendChild(p.lidRect); g.appendChild(lid);
        var inner = el('g', { 'clip-path': 'url(#' + self.id + '-l' + i + ')' });
        inner.appendChild(el('ellipse', { cx: 0, cy: 1.1, rx: EYE_R * 0.92, ry: EYE_R * 0.8, fill: '#000', opacity: 0.32, filter: 'url(#flowdot-soft)' }));
        inner.appendChild(el('circle', { r: EYE_R, fill: 'url(#flowdot-white)' }));
        p.pupil = el('circle', { r: PUPIL_R, fill: 'url(#flowdot-pupil)' }); inner.appendChild(p.pupil);
        inner.appendChild(el('circle', { cx: -2.4, cy: -2.6, r: 1.5, fill: '#fff' }));
        g.appendChild(inner);
        p.shut = el('path', { d: STYLES.calm.d, fill: 'none', stroke: line, 'stroke-width': LINE_W, 'stroke-linecap': 'round', opacity: 0 }); g.appendChild(p.shut);
        if (type === 'lens') g.appendChild(el('circle', { r: EYE_R + 2.8, fill: 'none', stroke: self.line === INK ? INK : 'rgba(250,248,243,.75)', 'stroke-width': 1.8, opacity: 0.85 }));
        if (night) inner.setAttribute('opacity', 0.9);
      } else {
        var d = (STYLES[type] || STYLES.calm).d;
        g.appendChild(el('path', { d: d, fill: 'none', stroke: line, 'stroke-width': LINE_W, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
      }
      self.parts.push(p);
    });
    var mg = this.mouthG; while (mg.firstChild) mg.removeChild(mg.firstChild);
    var mk = this.role === 'flow' ? m.mouth : ((this.mood === 'done' || this.mood === 'error' || this.mood === 'work') ? m.mouth : this.def.mouth);
    if (MOUTHS[mk] === 'o') mg.appendChild(el('circle', { r: 3.2, fill: 'none', stroke: line, 'stroke-width': MOUTH_W }));
    else mg.appendChild(el('path', { d: MOUTHS[mk] || MOUTHS.smile, fill: 'none', stroke: line, 'stroke-width': MOUTH_W, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
    return this;
  };

  /* Kept for the page's face kit: try an eye type on both eyes. */
  Dot.prototype.setStyle = function (name) {
    if (STYLES[name]) this.def = { shape: this.def.shape, eyes: [name, name === 'lens' ? 'googly' : name], mouth: this.def.mouth };
    return this.drawFace();
  };
  Dot.prototype.set = function (mood) {
    var m = MOODS[mood] || MOODS.idle; this.mood = mood;
    if (this.role === 'flow') {
      this.core.setAttribute('fill', m.night ? 'url(#flowdot-core-night)' : 'url(#flowdot-core)');
      this.halo.setAttribute('fill', m.night ? 'url(#flowdot-halo-night)' : 'url(#flowdot-halo)');
    } else this.body.setAttribute('opacity', m.night ? 0.6 : 1);
    this.ring.setAttribute('stroke-opacity', 0);
    if (!m.orbit) this.sats.forEach(function (s) { s.setAttribute('r', 0); });
    if (mood === 'done') this.nod();
    this.wob.v += 2.4; if (this.role === 'flow' && (mood === 'work' || mood === 'done')) this.trail();
    return this.drawFace();
  };
  /* the signature: when it moves, it leaves the mark's trail behind for a moment */
  Dot.prototype.trail = function () {
    if (reduced) return this;
    var self = this, now = performance.now();
    [[0.95, 0.3], [1.55, 0.22], [2.15, 0.15]].forEach(function (q, i) {
      var c = el('circle', { cx: self.cx, cy: self.cy, r: 0, fill: CREAM, opacity: 0 }); self.gooG.appendChild(c);
      self.trails.push({ el: c, t0: now + i * 70, d: q[0] * self.r, rr: q[1] * self.r });
    });
    return this;
  };
  Dot.prototype.greet = function () { this.nod(); this.blink(true); this.wob.v += 3; this.trail(); return this; };
  Dot.prototype.hover = function (on) { this.curious = on ? 1 : 0; return this; };
  /* the shy glance: looks at you, looks away, looks back */
  Dot.prototype.shy = function () {
    var self = this; self.lookAt(0, 0.12); self.blink(true);
    setTimeout(function () { if (self.curious) self.lookAt(-0.95, 0.4); }, 700);
    setTimeout(function () { if (self.curious) self.lookAt(0.05, 0); }, 1350);
    setTimeout(function () { if (self.curious) self.blink(false); }, 1500);
    return this;
  };
  Dot.prototype.attach = function (host) {
    var self = this;
    host.addEventListener('pointerenter', function () { self.hover(true); self.shy(); });
    host.addEventListener('pointerleave', function () { self.hover(false); self.lookAt(null); });
    return this;
  };
  Dot.prototype.setGlow = function (on) { this.halo.setAttribute('opacity', on ? 1 : 0); return this; };
  Dot.prototype.setMaterial = function (mat) { this.material = mat; this.solid = mat === 'solid'; this.sized = true; this.applyMaterial(); return this.drawFace(); };
  /* Stop animating this dot, for pages that swap one character for another in place. */
  Dot.prototype.destroy = function () { var i = dots.indexOf(this); if (i >= 0) dots.splice(i, 1); return this; };
  Dot.prototype.lookAt = function (x, y) { this.hold = x === null ? null : [x, y]; return this; };
  Dot.prototype.nod = function () { this.nodAt = performance.now(); return this; };
  Dot.prototype.blink = function (twice) { if (!reduced) { this.lidAt = performance.now(); this.lidTwice = !!twice; } return this; };

  Dot.prototype.step = function (dt, w) {
    if (!this.sized && w > 0) { this.sized = true; var small = w < 56; if (small !== this.solid) { this.solid = small; this.applyMaterial(); this.drawFace(); } }
    var m = MOODS[this.mood] || MOODS.idle, r = this.r, k = this.k; this.t += dt;
    var tgt;
    if (this.hold) tgt = this.hold;
    else if (m.scan && !reduced) { var u = (this.t * 0.9) % 1, ln = Math.floor((this.t * 0.9) % 3); tgt = [-0.8 + u * 1.6, -0.25 + ln * 0.35]; }
    else if (m.look) tgt = m.look;
    else if (m.daze) tgt = [0, 0];
    else {
      this.nextSac -= dt; this.nextTic -= dt;
      if (this.nextTic <= 0 && !reduced) { this.ticUntil = this.t + 0.9; this.nextTic = 10 + Math.random() * 8; }
      if (this.t < this.ticUntil) tgt = [-0.6, -0.85];
      else { if (this.nextSac <= 0 && !reduced) { this.target = [(Math.random() - 0.5) * 1.6, (Math.random() - 0.5) * 1.1]; this.nextSac = 1.5 + Math.random() * 2.5; } tgt = this.target; }
    }
    if (reduced) { this.gaze.x.x = tgt[0]; this.gaze.y.x = tgt[1]; }
    else if (m.scan && !this.hold) { this.gaze.x.x = tgt[0]; spring(this.gaze.y, tgt[1], 140, 18, dt); }
    else { spring(this.gaze.x, tgt[0], 140, 18, dt); spring(this.gaze.y, tgt[1], 140, 18, dt); }
    var gx = Math.max(-1, Math.min(1, this.gaze.x.x)), gy = Math.max(-1, Math.min(1, this.gaze.y.x));
    spring(this.tiltS, gx * 5 + m.tilt + this.curious * 8, 40, 10, dt);
    spring(this.wob, 0, 90, 7, dt);
    var breathe = reduced ? 0 : Math.sin(this.t * m.rate) * m.breath;
    var wobble = reduced ? 0 : this.wob.x * 0.05;
    var cheekTarget = (this.mood === 'done' ? 0.6 : 0) + this.curious * 0.45; this.cheekA += (Math.min(0.6, cheekTarget) - this.cheekA) * Math.min(1, dt * 6); this.cheeks.setAttribute('opacity', this.cheekA);
    /* nod and blink run on the wall clock, so a starved tab never freezes them mid-way */
    var nowMs = performance.now(), nodY = 0, nodSq = 0, nodLid = 1;
    if (this.nodAt >= 0) { var nt = (nowMs - this.nodAt) / 1000; if (nt > 0.6) this.nodAt = -1; else { var wv = Math.sin(Math.min(nt / 0.6, 1) * Math.PI); nodY = wv * r * 0.1; nodSq = wv * 0.1; nodLid = 1 - wv * 0.6; } }
    var sx = 1 + breathe + nodSq + wobble, sy = 1 - breathe - nodSq - wobble, tilt = this.tiltS.x;
    var base = 'translate(' + this.cx + ' ' + (this.cy + nodY) + ') rotate(' + tilt + ') ';
    this.body.setAttribute('transform', base + 'scale(' + (k * sx) + ' ' + (k * sy) + ') translate(-50 -52)');
    if (this.glow) { var pulse = reduced ? 1 : 0.85 + 0.15 * Math.sin(this.t * m.rate * 0.5) + (m.ring ? 0.15 : 0); this.halo.setAttribute('opacity', pulse); this.halo.setAttribute('transform', 'translate(' + this.cx + ' ' + (this.cy + nodY) + ') scale(' + (1 + breathe * 2) + ') translate(' + (-this.cx) + ' ' + (-this.cy) + ')'); }
    /* the face leads: it shifts toward the gaze inside the body */
    var ox = gx * 1.8, oy = gy * 1.3;
    this.face.setAttribute('transform', base + 'scale(' + k + ') translate(' + (-50 + ox) + ' ' + (-52 + oy) + ')');
    var lid = 1;
    if (!reduced) {
      if (this.lidAt < 0) { this.nextBlink -= dt; if (this.nextBlink <= 0) { this.lidAt = nowMs; this.lidTwice = this.dbl; this.nextBlink = 3 + Math.random() * 3; } }
      if (this.lidAt >= 0) {
        var T = (nowMs - this.lidAt) / 1000;
        var one = function (x) { if (x < 0.06) return 1; if (x < 0.13) return 1 - (x - 0.06) / 0.07; if (x < 0.27) return (x - 0.13) / 0.14; return 1; };
        lid = one(T); if (this.lidTwice && T > 0.26) lid = one(T - 0.26);
        if (T > (this.lidTwice ? 0.54 : 0.28)) { this.lidAt = -1; lid = 1; }
      }
    }
    lid = Math.max(0, Math.min(lid * nodLid, 1));
    if (gy > 0) lid *= 1 - gy * 0.12;
    var kc = m.k * (1 + this.curious * 0.06);
    var kk = [kc * (1 - Math.max(0, gx) * 0.06 + Math.max(0, -gx) * 0.03), kc * (1 - Math.max(0, -gx) * 0.06 + Math.max(0, gx) * 0.03)];
    var M = EYE_R - PUPIL_R - 0.7, self = this;
    this.parts.forEach(function (p, i) {
      p.g.setAttribute('transform', 'translate(' + p.at[0] + ' ' + p.at[1] + ') scale(' + kk[i] + ')');
      if (!p.pupil) return;
      var tx = gx, ty = gy;
      if (m.daze) { tx = m.daze[i][0]; ty = m.daze[i][1]; }
      ty += 0.18;
      var q = self.pup[i];
      if (reduced) { q.x = tx; q.y = ty; }
      else { q.vx += ((tx - q.x) * 170 - q.vx * 8) * dt; q.vy += ((ty - q.y) * 170 - q.vy * 8) * dt; q.x += q.vx * dt; q.y += q.vy * dt; }
      var L = Math.hypot(q.x, q.y); if (L > 1) { q.x /= L; q.y /= L; var n = q.vx * q.x + q.vy * q.y; if (n > 0) { q.vx -= 1.5 * n * q.x; q.vy -= 1.5 * n * q.y; } }
      p.pupil.setAttribute('cx', (q.x * M).toFixed(2)); p.pupil.setAttribute('cy', (q.y * M).toFixed(2));
      /* the lid comes down from the top; at the bottom of the blink a calm arc stands in */
      var h = (EYE_R * 2 + 4) * lid; p.lidRect.setAttribute('y', (EYE_R + 2 - h).toFixed(2)); p.lidRect.setAttribute('height', h.toFixed(2));
      p.shut.setAttribute('opacity', lid < 0.2 ? 1 : 0);
    });
    if (this.trails.length) {
      var now = performance.now(), keep = [];
      for (var ti = 0; ti < this.trails.length; ti++) {
        var tr = this.trails[ti], pp = (now - tr.t0) / 850;
        if (pp < 0) { keep.push(tr); continue; }
        if (pp >= 1) { if (tr.el.parentNode) tr.el.parentNode.removeChild(tr.el); continue; }
        var dd = tr.d + pp * r * 0.5, ease = pp < 0.25 ? pp / 0.25 : 1 - (pp - 0.25) / 0.75;
        tr.el.setAttribute('cx', this.cx - dd * 0.83); tr.el.setAttribute('cy', this.cy + dd * 0.56 + nodY);
        tr.el.setAttribute('r', tr.rr * (0.6 + 0.4 * ease)); tr.el.setAttribute('opacity', 0.9 * ease);
        keep.push(tr);
      }
      this.trails = keep;
    }
    if (m.ring) { var ph = Math.sin(this.t * 2.2); this.ring.setAttribute('r', r + 12 + ph * 6); this.ring.setAttribute('stroke-opacity', 0.55 - ph * 0.35); }
    if (m.orbit && !reduced) { this.sats.forEach(function (sat, i) { var a = self.t * 1.4 + i * (Math.PI * 2 / 3), rad = r * 1.55 + Math.sin(self.t * 2 + i) * r * 0.15; sat.setAttribute('r', r * 0.13 + Math.sin(self.t * 3 + i) * r * 0.03); sat.setAttribute('cx', self.cx + Math.cos(a) * rad); sat.setAttribute('cy', self.cy + Math.sin(a) * rad * 0.9); }); }
  };
  var last = 0;
  function loop(now) {
    var dt = Math.min(0.05, (now - last) / 1000 || 0.016); last = now;
    for (var i = 0; i < dots.length; i++) { var d = dots[i]; var rect = d.svg.getBoundingClientRect(); if (rect.bottom < -50 || rect.top > innerHeight + 50) continue; d.step(dt, rect.width); }
    requestAnimationFrame(loop);
  }
  function start() { if (running) return; running = true; requestAnimationFrame(loop); }
  function mount(svg, o) { return new Dot(svg, o); }
  function isNightNZ() { try { var h = parseInt(new Intl.DateTimeFormat('en-NZ', { hour: 'numeric', hour12: false, timeZone: 'Pacific/Auckland' }).format(new Date()), 10); return h >= 22 || h < 6; } catch (e) { return false; } }
  function autoNight(dot) {
    function check() { var n = isNightNZ(); if (n && dot.mood === 'idle') dot.set('late'); else if (!n && dot.mood === 'late') dot.set('idle'); }
    check(); setInterval(check, 60000); return dot;
  }
  function greetOnSight(dot) {
    if (!('IntersectionObserver' in window)) return dot;
    var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { setTimeout(function () { dot.greet(); }, 350); io.disconnect(); } }, { threshold: 0.6 });
    io.observe(dot.svg); return dot;
  }
  function make(cls, size) { var svg = el('svg', { viewBox: '0 0 100 100', 'aria-hidden': 'true', focusable: 'false' }); svg.setAttribute('class', 'fdot ' + (cls || '')); if (size) { svg.setAttribute('width', size); svg.setAttribute('height', size); } return svg; }
  return { mount: mount, make: make, autoNight: autoNight, greetOnSight: greetOnSight, isNightNZ: isNightNZ, STYLES: STYLES, SHAPES: SHAPES, AGENTS: AGENTS, MOODS: MOODS, MOUTHS: MOUTHS, Dot: Dot };
}());

/* ---------- boot: this site ---------- */
(function () {
  'use strict';
  function ready(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn, { once: true }); else fn(); }
  ready(function () {
    var F = window.FlowDot; if (!F) return;


    /* The demo window: Flow Intelligence beside the run status, a core in the sidebar
       that keeps Auckland hours, and each run under Recents carrying its agent's dot. */
    var demo = document.querySelector('[data-demo]');
    if (demo) {
      demo.classList.add('has-fdot');
      var statusEl = demo.querySelector('.demo__status');
      if (statusEl && statusEl.parentNode) {
        var sv = F.make('fdot--status'); statusEl.parentNode.insertBefore(sv, statusEl);
        var fi = F.mount(sv, { role: 'flow', r: 36, state: 'review' }); fi.attach(statusEl.parentNode); F.greetOnSight(fi);
        var moodFor = function (text) {
          var t = (text || '').trim();
          if (/working|running|运行中/i.test(t)) return 'work';
          if (/review|审核/i.test(t)) return 'review';
          if (/paused|暂停/i.test(t)) return 'think';
          return 'done';
        };
        var apply = function () { var mood = moodFor(statusEl.textContent); if (fi.mood !== mood) { fi.set(mood); if (mood === 'done') setTimeout(function () { if (fi.mood === 'done') fi.set('idle'); }, 2600); } };
        apply();
        new MutationObserver(apply).observe(statusEl, { childList: true, characterData: true, subtree: true });
      }
      var here = demo.querySelector('.demo__nav.is-here');
      if (here) { var hv = F.make('fdot--side'); here.insertBefore(hv, here.firstChild); var sd = F.autoNight(F.mount(hv, { role: 'flow', r: 36 })); sd.attach(here); F.greetOnSight(sd); }
      Array.prototype.slice.call(demo.querySelectorAll('[data-run]')).forEach(function (b) {
        var key = b.getAttribute('data-run'), av = F.make('fdot--run'); b.insertBefore(av, b.firstChild);
        var d = F.mount(av, { role: 'agent', agent: key, r: 36 });
        b.addEventListener('mouseenter', function () { d.lookAt(0, 0.2); d.blink(true); setTimeout(function () { d.lookAt(null); }, 1200); });
      });
    }

    /* The run: the first time the demo window comes into view, one job is told by the
       character alone, over the window, then it fades out and the live window takes over.
       Once per visit, never under reduced motion, skippable. */
    var win = demo && demo.querySelector('.demo__win');
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var seen = false; try { seen = sessionStorage.getItem('flowai-run') === '1'; } catch (e) {}
    if (win && !reduce && !seen && 'IntersectionObserver' in window) {
      var NS = 'http://www.w3.org/2000/svg';
      function sel(n, a) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); return e; }
      var ZH = /^zh/.test(document.documentElement.lang);
      var S = ZH ? {
        you: '找出人们向 AI 询问热水缸的问题，修好应该回答的页面。全部暂存。',
        reply: '三个页面已暂存。等待你审核。', ok: '看起来不错。定价页先留着。', skip: '跳过', eyebrow: 'FLOW INTELLIGENCE · 一次运行',
        caps: ['一句大白话的指令', '它逐行读你的网站', '它给合适的智能体交代任务', '智能体去干活', '把成果带回来', '一切先暂存，等你审核', '没有你的同意，什么都不会发出', '你得到的是'],
        incl: ['掌握你定位的 Flow Intelligence', '十个智能体：搜索、内容、外联、报告等', '每一次发送都先暂存，等你批准', '每月一份报告'],
        cards: [['/services/hot-water-cylinders', '6 处修改'], ['/faq/plumber-cost-auckland', '新页面'], ['/areas/north-shore', '4 处修改']]
      } : {
        you: 'Find the questions people ask AI about hot water cylinders and fix the pages that answer them. Stage everything.',
        reply: 'Three pages staged. Waiting for your review.', ok: 'Looks good. Hold the pricing page for now.', skip: 'Skip', eyebrow: 'FLOW INTELLIGENCE · ONE RUN',
        caps: ['A brief, in plain words', 'It reads your site, line by line', 'It briefs the right agents', 'The agents do the work', 'They bring it back', 'Everything is staged for your review', 'Nothing ships without your yes', 'What you get'],
        incl: ['Flow Intelligence that holds your positioning', 'Ten agents: search, content, outbound, reporting and more', 'Every send staged for your approval', 'One report a month'],
        cards: [['/services/hot-water-cylinders', '6 changes'], ['/faq/plumber-cost-auckland', 'New page'], ['/areas/north-shore', '4 changes']]
      };
      var ov = document.createElement('div'); ov.className = 'demo__run'; ov.setAttribute('role', 'presentation');
      ov.innerHTML = '<div class="demo__run-stage"><svg viewBox="0 0 100 100" aria-hidden="true" focusable="false"></svg>' +
        '<div class="demo__run-msg demo__run-msg--you">' + S.you + '</div>' +
        '<div class="demo__run-cards">' + S.cards.map(function (c) { return '<div class="demo__run-card"><span>' + c[0] + '</span><em>' + c[1] + '</em></div>'; }).join('') + '</div>' +
        '<div class="demo__run-incl">' + S.incl.map(function (x) { return '<div class="demo__run-card is-ok"><span>' + x + '</span></div>'; }).join('') + '</div>' +
        '<div class="demo__run-msg demo__run-msg--dot">' + S.reply + '</div>' +
        '<div class="demo__run-msg demo__run-msg--ok">' + S.ok + '</div></div>' +
        '<div class="demo__run-foot"><div class="demo__run-row"><span class="demo__run-eyebrow">' + S.eyebrow + '</span><span class="demo__run-cap"></span><button type="button" class="demo__run-skip">' + S.skip + '</button></div><span class="demo__run-bar"><b></b></span></div>';
      win.appendChild(ov); document.documentElement.classList.add('fdot-run');
      var rsvg = ov.querySelector('svg'), m1 = ov.querySelector('.demo__run-msg--you'), m2 = ov.querySelector('.demo__run-msg--dot'), m3 = ov.querySelector('.demo__run-msg--ok');
      var cards = Array.prototype.slice.call(ov.querySelectorAll('.demo__run-cards .demo__run-card'));
      var incl = ov.querySelector('.demo__run-incl'), inclRows = Array.prototype.slice.call(incl.querySelectorAll('.demo__run-card'));
      var capEl = ov.querySelector('.demo__run-cap'), barEl = ov.querySelector('.demo__run-bar b');
      var run = F.mount(rsvg, { role: 'flow', r: 15, dy: 6, goo: true });
      /* a flat amber disc inside the goo group, under the light core, so the agents pull
         off the core with a liquid neck instead of appearing beside it */
      run.gooG.insertBefore(sel('circle', { cx: run.cx, cy: run.cy, r: run.r * 0.98, fill: '#e4a43c' }), run.gooG.firstChild);
      /* the page it reads: six hairlines to the right of the core, one lit at a time */
      var lines = sel('g', { opacity: 0 }); rsvg.insertBefore(lines, rsvg.firstChild);
      var lineEls = [];
      for (var li = 0; li < 6; li++) { var ln = sel('rect', { x: 66, y: 36 + li * 5.2, width: li % 3 === 2 ? 18 : 26, height: 1.3, rx: 0.65, fill: '#faf8f3', 'fill-opacity': 0.16 }); lines.appendChild(ln); lineEls.push(ln); }
      var sats = run.sats, satT = [[22, 44, 5.5], [80, 40, 5], [30, 82, 4.5]], satAnim = null, t0 = -1, LEN = 17.5, fired = [], done = false, lineT = -1, lit = -1;
      var agentKeys = ['ai-search', 'content', 'outbound'], faces = [];
      function easeOut(x) { return 1 - Math.pow(1 - x, 3); }
      function showFaces(on) {
        if (on && !faces.length) {
          satT.forEach(function (p, i) {
            var inner = sel('svg', { x: p[0] - p[2] * 1.45, y: p[1] - p[2] * 1.45, width: p[2] * 2.9, height: p[2] * 2.9, viewBox: '0 0 100 100' });
            rsvg.appendChild(inner); var fd = F.mount(inner, { role: 'agent', agent: agentKeys[i], r: 34, state: 'work' }); faces.push({ svg: inner, dot: fd });
          });
        } else faces.forEach(function (f, i) { f.svg.setAttribute('opacity', on ? 1 : 0); if (!on) f.dot.set('idle'); });
        if (on) sats.forEach(function (s) { s.setAttribute('r', 0); });
      }
      var SCRIPT = [
        { at: 0,    i: 0, fn: function () { m1.classList.add('is-on'); run.lookAt(0.8, -0.9); setTimeout(function () { run.nod(); run.lookAt(null); }, 700); } },
        { at: 1.1,  i: 1, fn: function () { F.MOODS.work.orbit = false; run.set('work'); lines.setAttribute('opacity', 1); lineT = performance.now(); } },
        { at: 3.4,  i: 2, fn: function () { lines.setAttribute('opacity', 0); run.set('think'); satAnim = { t0: performance.now(), dir: 1 }; } },
        { at: 5.4,  i: 3, fn: function () { run.set('idle'); showFaces(true); faces.forEach(function (f) { f.dot.set('work'); }); } },
        { at: 7.2,  i: 4, fn: function () { faces.forEach(function (f) { f.dot.set('done'); }); setTimeout(function () { showFaces(false); sats.forEach(function (s, i) { s.setAttribute('cx', satT[i][0]); s.setAttribute('cy', satT[i][1]); s.setAttribute('r', satT[i][2]); }); satAnim = { t0: performance.now(), dir: -1 }; }, 350); } },
        { at: 8.6,  i: 5, fn: function () { run.trail(); run.set('review'); ov.classList.add('is-staged'); m1.classList.remove('is-on'); m2.classList.add('is-on'); cards.forEach(function (c, i) { setTimeout(function () { c.classList.add('is-on'); }, 120 + i * 140); }); } },
        { at: 10.8, i: 6, fn: function () { m2.classList.remove('is-on'); m3.classList.add('is-on'); run.lookAt(0.9, 0.6); setTimeout(function () { run.set('done'); run.lookAt(null); cards.forEach(function (c, i) { setTimeout(function () { c.classList.add('is-ok'); }, i * 120); }); }, 600); } },
        { at: 12.6, i: 7, fn: function () { m3.classList.remove('is-on'); cards.forEach(function (c) { c.classList.remove('is-on'); }); incl.classList.add('is-on'); inclRows.forEach(function (c, i) { setTimeout(function () { c.classList.add('is-on'); }, 150 + i * 130); }); run.set('done'); } }
      ];
      function satFrame(now) {
        if (!satAnim) return;
        var tt = (now - satAnim.t0) / 1000;
        sats.forEach(function (s, i) {
          var local = Math.max(0, Math.min(1, (tt - i * 0.3) / 0.9)), e = easeOut(local), p = satAnim.dir > 0 ? e : 1 - e;
          var wob = Math.sin(now / 400 + i) * 1.5 * p;
          s.setAttribute('cx', run.cx + (satT[i][0] - run.cx) * p + wob); s.setAttribute('cy', run.cy + (satT[i][1] - run.cy) * p + Math.cos(now / 500 + i) * p); s.setAttribute('r', satT[i][2] * Math.min(1, 0.4 + p * 0.9));
        });
        if (tt > 1.9) { if (satAnim.dir < 0) { sats.forEach(function (s) { s.setAttribute('r', 0); }); run.wob.v += 2.5; } satAnim = null; }
      }
      function lineFrame(now) {
        if (lineT < 0) return;
        var idx = Math.floor((now - lineT) / 360) % 6;
        if (idx !== lit) { lit = idx; lineEls.forEach(function (l, i) { l.setAttribute('fill-opacity', i === idx ? 0.9 : (i < idx ? 0.42 : 0.16)); }); }
      }
      function finish() {
        if (done) return; done = true;
        try { sessionStorage.setItem('flowai-run', '1'); } catch (e) {}
        F.MOODS.work.orbit = true;
        ov.classList.add('is-done'); document.documentElement.classList.remove('fdot-run');
        setTimeout(function () { if (ov.parentNode) ov.parentNode.removeChild(ov); }, 700);
      }
      function frame(now) {
        if (done) return;
        if (t0 < 0) t0 = now;
        var tt = (now - t0) / 1000;
        barEl.style.width = Math.min(100, tt / LEN * 100) + '%';
        SCRIPT.forEach(function (s, i) { if (tt >= s.at && !fired[i]) { fired[i] = true; s.fn(); capEl.textContent = S.caps[s.i]; if (s.i !== 1) lineT = -1; } });
        satFrame(now); lineFrame(now);
        if (tt < LEN) requestAnimationFrame(frame); else finish();
      }
      ov.querySelector('.demo__run-skip').addEventListener('click', finish);
      var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { io.disconnect(); setTimeout(function () { requestAnimationFrame(frame); }, 400); } }, { threshold: 0.2 });
      io.observe(win);
    }

    /* The 404: it looks left, then right, then at you. */
    var lost = document.querySelector('[data-fdot-lost]');
    if (lost) {
      var d = F.mount(lost, { role: 'flow', r: 30 }); d.attach(lost.parentNode || lost); F.greetOnSight(d);
      var seq = [[-0.9, 0], [0.9, 0], [0, 0], null], i = 0;
      setInterval(function () { var s = seq[i % 4]; if (s) d.lookAt(s[0], s[1]); else d.lookAt(null); i++; }, 1100);
      F.autoNight(d);
    }

    /* Any page can place a character with markup alone:
       <svg class="fdot" data-fdot="search" viewBox="0 0 100 100"></svg> for an agent,
       data-fdot="flow" for Flow Intelligence (the older data-fdot="agent" data-agent="…"
       form still works). It looks up when you come near its block ([data-fdot-host], or
       the parent), and Flow Intelligence keeps Auckland hours. */
    Array.prototype.slice.call(document.querySelectorAll('svg[data-fdot]')).forEach(function (svg) {
      var v = svg.getAttribute('data-fdot'), r = parseFloat(svg.getAttribute('data-r')) || 34;
      var flow = v === 'flow', agent = v === 'agent' ? svg.getAttribute('data-agent') : v;
      var d = F.mount(svg, flow ? { role: 'flow', r: r, state: svg.getAttribute('data-state') || 'idle' } : { role: 'agent', agent: agent, r: r, state: svg.getAttribute('data-state') || 'idle' });
      if (flow && !svg.getAttribute('data-state')) F.autoNight(d);
      d.attach(svg.closest('[data-fdot-host]') || svg.parentNode); F.greetOnSight(d);
    });
  });
}());
