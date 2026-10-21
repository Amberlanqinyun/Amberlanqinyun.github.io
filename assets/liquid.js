/* Amber Lan · liquid orb and glass (Oct 2026).

   The orb: a slow chrome liquid rising from the foot of the hero. Dark tinted
   glass lit like a product shot: softbox strips of warm amber above, white
   strips at the sides that draw the rim, a cool blue panel below, and a blue
   glow moving inside the body. The lights turn a little with the pointer and
   with the scroll, so the highlights slide across the surface. Raymarched
   metaballs in one WebGL shader, no dependencies.

   Mounts into every [data-liquid] element. Pages without one get a quieter
   orb behind their hero, except reading pages (guides, articles, profile).
   One WebGL context per page. Paused off screen and in background tabs,
   resolution steps down by itself on a slow device, and one still frame for
   visitors who prefer reduced motion. Without WebGL the CSS fallback in
   liquid.css draws a still orb.

   The glass: on devices with a fine pointer, glass panels carry a soft sheen
   that follows the cursor, and the floating hero cards tilt toward it. */

(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var phone = window.matchMedia('(max-width: 720px)').matches;
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  var VERT = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FRAG = [
    'precision highp float;',
    'uniform vec2 uRes;uniform float uTime;uniform vec2 uLean;uniform float uScroll;',
    'float smin(float a,float b,float k){float h=clamp(.5+.5*(b-a)/k,0.,1.);return mix(b,a,h)-k*h*(1.-h);}',
    'float map(vec3 p){',
    '  float t=uTime*.6;vec3 q=p;',
    '  q.xz+=uLean*.1*(q.y+2.4);',
    '  float d=length(q-vec3(0.,-2.7,0.))-2.45;',
    '  d=smin(d,length(q-vec3(-1.15+.22*sin(t*.53),-.5+.16*sin(t*.71),.2+.15*cos(t*.4)))-.95,.95);',
    '  d=smin(d,length(q-vec3(1.2+.18*sin(t*.47+1.3),-1.+.18*cos(t*.59),-.1))-.85,.95);',
    '  d=smin(d,length(q-vec3(-.15+.25*sin(t*.37),-.3+.14*sin(t*.83+2.),.1*sin(t*.5)))-.72,.85);',
    '  d=smin(d,length(q-vec3(.7*sin(t*.31+4.),-.6+.25*sin(t*.43),.15))-.48,1.);',
    '  return d;',
    '}',
    'vec3 nrm(vec3 p){vec2 e=vec2(.0012,-.0012);',
    '  return normalize(e.xyy*map(p+e.xyy)+e.yyx*map(p+e.yyx)+e.yxy*map(p+e.yxy)+e.xxx*map(p+e.xxx));}',
    /* A softbox: a soft-edged rectangle of light seen in direction c. */
    'float box(vec3 r,vec3 c,vec3 up,vec2 s,float soft){',
    '  float z=dot(r,c);if(z<=0.)return 0.;',
    '  vec3 u=normalize(cross(up,c));vec3 v=cross(c,u);',
    '  vec2 xy=abs(vec2(dot(r,u),dot(r,v))/z);',
    '  vec2 e=1.-smoothstep(s-soft,s,xy);return e.x*e.y;',
    '}',
    'vec3 env(vec3 r){',
    '  float a=uLean.x*.35+uScroll*.9;float ca=cos(a),sa=sin(a);',
    '  r.xz=mat2(ca,-sa,sa,ca)*r.xz;',
    '  float b=uScroll*.4;r.yz=mat2(cos(b),-sin(b),sin(b),cos(b))*r.yz;',
    '  vec3 Y=vec3(0.,1.,0.),Z=vec3(0.,0.,1.);',
    '  vec3 c=mix(vec3(.004,.004,.008),vec3(.03,.026,.05),clamp(r.y*.5+.5,0.,1.));',
    '  c+=vec3(1.,.66,.24)*box(r,normalize(vec3(-.5,.8,.35)),Z,vec2(1.,.22),.38)*2.3;',
    '  c+=vec3(1.,.8,.42)*box(r,normalize(vec3(.6,.68,.4)),Z,vec2(.5,.14),.22)*2.1;',
    '  c+=vec3(.95,.62,.25)*box(r,normalize(vec3(.05,1.,.15)),Z,vec2(.8,.35),.45)*.4;',
    '  c+=vec3(1.)*box(r,normalize(vec3(-1.,.1,-.15)),Y,vec2(.1,1.6),.08)*2.2;',
    '  c+=vec3(1.,.97,.94)*box(r,normalize(vec3(1.,-.05,-.25)),Y,vec2(.08,1.6),.07)*1.8;',
    '  c+=vec3(.12,.32,1.)*box(r,normalize(vec3(.1,-.95,.3)),Z,vec2(.9,.35),.45)*.7;',
    '  c+=vec3(.35,.25,.75)*box(r,normalize(vec3(-.2,-.3,-1.)),Y,vec2(1.,.6),.6)*.12;',
    '  return c;',
    '}',
    'void main(){',
    '  vec2 uv=(gl_FragCoord.xy-.5*uRes)/uRes.y;',
    '  vec3 ro=vec3(0.,-.7,6.4);vec3 rd=normalize(vec3(uv,-1.9));',
    '  float t=3.,dm=1e3,tm=3.;bool hit=false;',
    '  for(int i=0;i<80;i++){vec3 p=ro+rd*t;float d=map(p);',
    '    if(d<dm){dm=d;tm=t;}',
    '    if(d<.0008){hit=true;break;}',
    '    t+=d*.92;if(t>10.)break;}',
    '  float px=1.6*tm/(1.9*uRes.y);',
    '  float a=hit?1.:1.-smoothstep(0.,px,dm);',
    '  vec3 col=vec3(0.);',
    '  if(a>0.){',
    '    vec3 p=ro+rd*(hit?t:tm);vec3 n=nrm(p);',
    '    float ndv=max(dot(n,-rd),0.);float g=1.-ndv;',
    '    float F=.04+.96*pow(g,5.);',
    '    vec3 refl=env(reflect(rd,n));',
    '    vec3 tran=env(refract(rd,n,.67))*vec3(.3,.45,1.)*.1;',
    '    col=mix(tran,refl,clamp(F*1.3+.22,0.,1.));',
    /* the blue light living inside the lower body, drifting */
    '    float lo=smoothstep(-1.1,-2.5,p.y);',
    '    col+=vec3(.08,.22,1.)*lo*(.55+.45*sin(p.x*1.6+uTime*.5))*(1.-F)*.55;',
    '    col+=vec3(.9,.5,.15)*smoothstep(-.8,.5,p.y)*(.5+.5*sin(p.x*2.1-uTime*.4))*(1.-F)*.05;',
    /* thin-film colour at grazing angles, then the bright rim */
    '    vec3 film=.5+.5*cos(6.2831*(vec3(0.,.33,.67)+g*1.4+.12+uTime*.02));',
    '    col+=film*pow(g,3.)*.22;',
    '    col+=vec3(1.,.95,.88)*pow(g,7.)*1.6;',
    '  }',
    '  float glow=exp(-max(dm,0.)*8.)*.32*(1.-a);',
    '  col=(col*(2.51*col+.03))/(col*(2.43*col+.59)+.14);',
    '  vec3 gc=mix(vec3(1.,.9,.75),vec3(.75,.8,1.),smoothstep(-1.,-2.4,(ro+rd*tm).y))*glow;',
    '  gl_FragColor=vec4(clamp(col,0.,1.)*a+gc,a+glow*.7);',
    '}'
  ].join('\n');

  function compile(gl, type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null;
  }

  function mount(host) {
    var canvas = document.createElement('canvas');
    var gl = canvas.getContext('webgl', { alpha: true, premultipliedAlpha: true, antialias: false, powerPreference: 'high-performance' });
    if (!gl) { host.classList.add('liquid-orb--static'); return; }
    var vs = compile(gl, gl.VERTEX_SHADER, VERT), fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) { host.classList.add('liquid-orb--static'); return; }
    var prog = gl.createProgram();
    gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { host.classList.add('liquid-orb--static'); return; }
    gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, 'p');
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var uRes = gl.getUniformLocation(prog, 'uRes'),
        uTime = gl.getUniformLocation(prog, 'uTime'),
        uLean = gl.getUniformLocation(prog, 'uLean'),
        uScroll = gl.getUniformLocation(prog, 'uScroll');

    host.appendChild(canvas);
    host.classList.add('is-live');

    /* Start sharp; step down if frames run long, never below half. */
    var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    var quality = phone ? 0.6 : 1;
    var running = false, visible = true, raf = 0;
    function resize() {
      var w = Math.max(1, Math.round(host.clientWidth * dpr * quality)),
          h = Math.max(1, Math.round(host.clientHeight * dpr * quality));
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w; canvas.height = h;
        gl.viewport(0, 0, w, h);
        if (!running) draw();
      }
    }

    var lean = [0, 0], target = [0, 0], scroll = 0, scrollTarget = 0;
    var t0 = performance.now(), offset = 14;
    function draw() {
      var now = reduced ? offset : offset + (performance.now() - t0) / 1000;
      lean[0] += (target[0] - lean[0]) * 0.05;
      lean[1] += (target[1] - lean[1]) * 0.05;
      scroll += (scrollTarget - scroll) * 0.08;
      host.style.setProperty('--liquid-sink', (scroll * 90).toFixed(1) + 'px');
      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.uniform1f(uTime, now);
      gl.uniform2f(uLean, lean[0], lean[1]);
      gl.uniform1f(uScroll, scroll);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }

    var last = 0, slow = 0, frames = 0;
    function loop(ts) {
      if (last) {
        frames++;
        if (ts - last > 24) slow++;
        if (frames === 40) {
          if (slow > 16 && quality > 0.5) { quality = Math.max(0.5, quality * 0.8); resize(); }
          frames = 0; slow = 0;
        }
      }
      last = ts;
      draw();
      raf = requestAnimationFrame(loop);
    }
    function sync() {
      var go = visible && !document.hidden && !reduced;
      if (go && !running) { running = true; last = 0; raf = requestAnimationFrame(loop); }
      else if (!go && running) { running = false; cancelAnimationFrame(raf); }
    }

    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(host);
    else window.addEventListener('resize', resize);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; sync(); }).observe(host);
    }
    document.addEventListener('visibilitychange', sync);

    if (!reduced) {
      /* The lights follow the pointer a little, and the scroll turns them. */
      if (fine) {
        window.addEventListener('pointermove', function (e) {
          target[0] = (e.clientX / window.innerWidth - 0.5) * 2;
          target[1] = (e.clientY / window.innerHeight - 0.5) * 2;
        }, { passive: true });
      }
      window.addEventListener('scroll', function () {
        scrollTarget = Math.min(1, window.scrollY / Math.max(1, window.innerHeight));
      }, { passive: true });
    }

    resize();
    draw();
    sync();
  }

  /* Glass sheen and card tilt, for a fine pointer only. */
  var GLASS = '.shell, .outcome, .proof-card, .install, .offer, .sx__doc, .flagship, .team__hq, .dgrid, .demo__win, ' +
    '.team__col, .poss, .rule, .pp-card, .path, .glass, .tpl-card, .part.case, .split__col, .buys-band .fig, ' +
    '.pp-table, .pp-contact, .compound, .team__review, .liquid-card';
  function glass() {
    if (!fine || reduced) return;
    var current = null;
    document.addEventListener('pointermove', function (e) {
      var el = e.target.closest && e.target.closest(GLASS);
      if (current && current !== el) {
        current.style.removeProperty('--mx'); current.style.removeProperty('--my');
        current.style.removeProperty('--rx'); current.style.removeProperty('--ry');
      }
      current = el;
      if (!el) return;
      var r = el.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
      el.style.setProperty('--mx', x.toFixed(0) + 'px');
      el.style.setProperty('--my', y.toFixed(0) + 'px');
      if (el.classList.contains('liquid-card')) {
        el.style.setProperty('--rx', ((0.5 - y / r.height) * 10).toFixed(2) + 'deg');
        el.style.setProperty('--ry', ((x / r.width - 0.5) * 12).toFixed(2) + 'deg');
      }
    }, { passive: true });
  }

  function boot() {
    glass();
    var hosts = document.querySelectorAll('[data-liquid]');
    if (!hosts.length) {
      var hero = document.querySelector('.hero');
      if (!hero || hero.matches('.article-hero, .blog-hero, .hero-profile, .cv-hero')) return;
      var orb = document.createElement('div');
      orb.className = 'liquid-orb liquid-orb--quiet';
      orb.setAttribute('aria-hidden', 'true');
      hero.insertBefore(orb, hero.firstChild);
      hero.classList.add('has-orb');
      hosts = [orb];
    }
    mount(hosts[0]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
