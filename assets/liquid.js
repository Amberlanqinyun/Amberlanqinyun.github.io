/* Amber Lan · liquid orb (Oct 2026).

   A slow chrome liquid rising from the foot of the hero: a dark body that
   mirrors warm amber light from above, cool blue from below, and a bright rim
   where the edge catches the light. Raymarched metaballs in one WebGL shader,
   no dependencies.

   Mounts into every [data-liquid] element. Pages without one get a quieter
   orb behind their hero, except reading pages (guides, articles, profile).
   One WebGL context per page. Paused off screen and in background tabs; one
   still frame for visitors who prefer reduced motion. Decorative and
   fail-safe: without WebGL the CSS fallback in liquid.css draws a still orb. */

(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var phone = window.matchMedia('(max-width: 720px)').matches;

  var VERT = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FRAG = [
    'precision highp float;',
    'uniform vec2 uRes;uniform float uTime;uniform vec2 uLean;',
    'float smin(float a,float b,float k){float h=clamp(.5+.5*(b-a)/k,0.,1.);return mix(b,a,h)-k*h*(1.-h);}',
    'float map(vec3 p){',
    '  float t=uTime;vec3 q=p;',
    '  q.xz+=uLean*.12*(q.y+2.);',
    '  float d=length(q-vec3(0.,-2.6,0.))-2.4;',
    '  d=smin(d,length(q-vec3(-1.2+.14*sin(t*.41),-.45+.1*sin(t*.53),.25))-.95,.9);',
    '  d=smin(d,length(q-vec3(1.2+.12*sin(t*.37+1.),-.95+.12*cos(t*.45),-.1))-.85,.9);',
    '  d=smin(d,length(q-vec3(-.2+.12*sin(t*.29),-.25+.09*sin(t*.6+2.),0.))-.75,.8);',
    '  d+=.025*sin(q.x*3.1+t*.7)*sin(q.y*2.7-t*.5)*sin(q.z*2.3+t*.4);',
    '  return d;',
    '}',
    'vec3 nrm(vec3 p){vec2 e=vec2(.0015,-.0015);',
    '  return normalize(e.xyy*map(p+e.xyy)+e.yyx*map(p+e.yyx)+e.yxy*map(p+e.yxy)+e.xxx*map(p+e.xxx));}',
    'vec3 env(vec3 r){',
    '  vec3 c=vec3(.006,.006,.014);',
    '  c+=vec3(1.,.64,.2)*pow(max(dot(r,normalize(vec3(-.45,.85,.3))),0.),22.)*4.;',
    '  c+=vec3(.9,.58,.22)*pow(max(dot(r,normalize(vec3(-.2,1.,.25))),0.),9.)*.25;',
    '  c+=vec3(1.,.78,.36)*pow(max(dot(r,normalize(vec3(.55,.75,.35))),0.),30.)*3.5;',
    '  c+=vec3(1.)*pow(max(dot(r,normalize(vec3(-1.,0.,-.1))),0.),14.)*2.;',
    '  c+=vec3(1.)*pow(max(dot(r,normalize(vec3(1.,-.05,-.15))),0.),14.)*1.7;',
    '  c+=vec3(.1,.28,1.)*pow(max(dot(r,normalize(vec3(.1,-.85,.5))),0.),5.)*1.6;',
    '  c+=vec3(.28,.22,.45)*smoothstep(-.2,1.,r.y)*.1;',
    '  return c;',
    '}',
    'void main(){',
    '  vec2 uv=(gl_FragCoord.xy-.5*uRes)/uRes.y;',
    '  vec3 ro=vec3(0.,-.7,6.4);vec3 rd=normalize(vec3(uv,-1.9));',
    '  float t=3.,dm=1e3,tm=3.;bool hit=false;',
    '  for(int i=0;i<72;i++){vec3 p=ro+rd*t;float d=map(p);',
    '    if(d<dm){dm=d;tm=t;}',
    '    if(d<.001){hit=true;break;}',
    '    t+=d*.9;if(t>10.)break;}',
    '  float px=2.2*tm/(1.9*uRes.y);',
    '  float a=hit?1.:1.-smoothstep(0.,px,dm);',
    '  vec3 col=vec3(0.);',
    '  if(a>0.){',
    '    vec3 p=ro+rd*(hit?t:tm);vec3 n=nrm(p);',
    '    float fr=pow(1.-max(dot(n,-rd),0.),3.);',
    '    col=env(reflect(rd,n))*(.35+.65*fr);',
    '    col+=vec3(.08,.2,.85)*smoothstep(-1.2,-2.5,p.y)*(1.-fr)*.7;',
    '    col+=vec3(.7,.42,.12)*smoothstep(-.7,.4,p.y)*(1.-fr)*.06;',
    '    vec3 film=.5+.5*cos(6.2831*(fr*1.2+vec3(0.,.33,.67))+uTime*.1);',
    '    col=mix(col,col*film*1.6,.25*fr);',
    '    col+=vec3(1.,.97,.92)*pow(fr,2.5)*.9;',
    '  }',
    '  float glow=exp(-max(dm,0.)*7.)*.22*(1.-a);',
    '  col=1.-exp(-col*1.35);',
    '  vec3 g=vec3(1.,.93,.82)*glow;',
    '  gl_FragColor=vec4(col*a+g,a+glow*.8);',
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
    var gl = canvas.getContext('webgl', { alpha: true, premultipliedAlpha: true, antialias: false, powerPreference: 'low-power' });
    if (!gl) { host.classList.add('liquid-orb--static'); return; }
    var vs = compile(gl, gl.VERTEX_SHADER, VERT), fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) { host.classList.add('liquid-orb--static'); return; }
    var prog = gl.createProgram();
    gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { host.classList.add('liquid-orb--static'); return; }
    gl.useProgram(prog);
    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, 'p');
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var uRes = gl.getUniformLocation(prog, 'uRes'),
        uTime = gl.getUniformLocation(prog, 'uTime'),
        uLean = gl.getUniformLocation(prog, 'uLean');

    host.appendChild(canvas);
    host.classList.add('is-live');

    /* Render below device resolution: the orb is soft, the GPU is not free. */
    var scale = Math.min(window.devicePixelRatio || 1, 1.5) * (phone ? 0.55 : 0.8);
    function resize() {
      var w = Math.max(1, Math.round(host.clientWidth * scale)),
          h = Math.max(1, Math.round(host.clientHeight * scale));
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w; canvas.height = h;
        gl.viewport(0, 0, w, h);
        if (!running) draw();
      }
    }

    var lean = [0, 0], target = [0, 0], t0 = performance.now(), offset = 14;
    function draw() {
      var now = reduced ? offset : offset + (performance.now() - t0) / 1000;
      lean[0] += (target[0] - lean[0]) * 0.04;
      lean[1] += (target[1] - lean[1]) * 0.04;
      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.uniform1f(uTime, now);
      gl.uniform2f(uLean, lean[0], lean[1]);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }

    var running = false, visible = true, raf = 0;
    function loop() { draw(); raf = requestAnimationFrame(loop); }
    function sync() {
      var go = visible && !document.hidden && !reduced;
      if (go && !running) { running = true; raf = requestAnimationFrame(loop); }
      else if (!go && running) { running = false; cancelAnimationFrame(raf); }
    }

    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(host);
    else window.addEventListener('resize', resize);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; sync(); }).observe(host);
    }
    document.addEventListener('visibilitychange', sync);

    /* The liquid leans a little toward the pointer. */
    if (!reduced && !phone) {
      window.addEventListener('pointermove', function (e) {
        target[0] = (e.clientX / window.innerWidth - 0.5) * 2;
        target[1] = (e.clientY / window.innerHeight - 0.5) * 2;
      }, { passive: true });
    }

    resize();
    draw();
    sync();
  }

  function boot() {
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
