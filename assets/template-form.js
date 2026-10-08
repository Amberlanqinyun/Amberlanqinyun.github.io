/* Flow AI agent templates: the "run it on my site" form and the copy button.

   A template page carries one form marked [data-template-form] with the
   template's id and name on it. Submitting sends the request to Amber's
   inbox through FormSubmit, the same service the contact page uses, and
   tags it with the template so every lead arrives with its intent. If the
   service fails, the visitor gets a prefilled email instead, so nothing is
   lost. Analytics events go to Google Tag Manager's dataLayer. */

(function () {
  'use strict';

  var TO = 'amber.lan.growth.digital@gmail.com';
  /* Chinese pages (/zh/) get Chinese messages and a Chinese auto-reply. The template name in
     the request stays English, so every lead arrives in Amber's inbox tagged the same way. */
  var ZH = /^zh/.test(document.documentElement.lang);
  window.dataLayer = window.dataLayer || [];
  function track(event, data) {
    var payload = { event: event };
    for (var k in data) payload[k] = data[k];
    window.dataLayer.push(payload);
  }

  var page = document.querySelector('[data-template-id]');
  if (page) track('template_view', { template_id: page.getAttribute('data-template-id') });

  /* ---------- copy buttons ---------- */

  document.addEventListener('click', function (event) {
    var button = event.target.closest ? event.target.closest('[data-copy]') : null;
    if (!button) return;
    var original = button.textContent;
    var done = function () {
      button.textContent = ZH ? '已复制' : 'Copied';
      window.setTimeout(function () { button.textContent = original; }, 1600);
    };
    if (page) track('template_install_copy', { template_id: page.getAttribute('data-template-id') });
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(button.getAttribute('data-copy')).then(done, function () { legacyCopy(button, done); });
      return;
    }
    legacyCopy(button, done);
  });

  function legacyCopy(button, done) {
    var field = document.createElement('textarea');
    field.value = button.getAttribute('data-copy');
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.opacity = '0';
    document.body.appendChild(field);
    field.select();
    document.execCommand('copy');
    field.remove();
    done();
  }

  /* ---------- the run form ---------- */

  Array.prototype.slice.call(document.querySelectorAll('[data-template-form]')).forEach(function (form) {
    var id = form.getAttribute('data-template-id');
    var name = form.getAttribute('data-template-name');
    var button = form.querySelector('button[type="submit"]');
    var status = form.querySelector('.form-status');
    var label = button.textContent;
    var email = form.elements.email;
    var site = form.elements.site;
    var trap = form.elements['company-role'];

    function show(kind, html) {
      status.className = 'form-status is-visible is-' + kind;
      status.innerHTML = html;
    }
    function clear(field) {
      field.removeAttribute('aria-invalid');
      if (status.classList.contains('is-error')) { status.className = 'form-status'; status.innerHTML = ''; }
    }
    [email, site].forEach(function (field) {
      field.addEventListener('input', function () { clear(field); });
    });

    function problem() {
      var e = email.value.trim(), s = site.value.trim();
      if (!e) return { field: email, say: ZH ? '请填写你的邮箱，方便把结果发给你。' : 'Could you add your email, so the result can reach you?' };
      if (e.indexOf('@') < 1 || e.indexOf('.', e.indexOf('@')) < 0) return { field: email, say: ZH ? '这个邮箱地址好像不完整，可以再确认一下吗？' : 'That email looks incomplete. Worth a second look?' };
      if (!s) return { field: site, say: site.getAttribute('data-missing') || (ZH ? '要在哪个网站上运行？' : 'Which site should it run on?') };
      return null;
    }

    function fallback(e, s) {
      var body = 'Please run the ' + name + ' template on ' + s + '.\n\nSend the result to ' + e + '.';
      var href = 'mailto:' + TO + '?subject=' + encodeURIComponent('Template run: ' + name) + '&body=' + encodeURIComponent(body);
      show('error', ZH
        ? '这次没有发送成功，但内容都还在：<a href="' + href + '">用你的邮箱应用发送同样的请求</a>，或直接发邮件到 <a href="mailto:' + TO + '">' + TO + '</a>。'
        : 'That did not send, and nothing was lost: <a href="' + href + '">send the same request from your email app</a>, or email <a href="mailto:' + TO + '">' + TO + '</a> directly.');
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (trap && trap.value) return; /* a bot filled the hidden field */
      var p = problem();
      if (p) {
        p.field.setAttribute('aria-invalid', 'true');
        p.field.focus();
        show('error', p.say);
        return;
      }
      var e = email.value.trim(), s = site.value.trim();
      button.disabled = true;
      button.textContent = ZH ? '发送中' : 'Sending';
      fetch('https://formsubmit.co/ajax/' + TO, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          _subject: 'Template run: ' + name + ' for ' + s + (ZH ? ' [中文]' : ''),
          _template: 'table',
          _captcha: 'false',
          _autoresponse: ZH
            ? '感谢你让 Flow AI 在 ' + s + ' 上运行这个模板。每一份结果都会先由 Amber 审核再发出，你会在两个工作日内收到。如有任何疑问，直接回复这封邮件即可。'
            : 'Thanks for asking Flow AI to run the ' + name + ' on ' + s + '. Amber reviews every result before it is sent, and yours will reach you within two working days. If anything is unclear, just reply to this email.',
          language: ZH ? 'zh' : 'en',
          template: name,
          template_id: id,
          email: e,
          site: s,
          page: window.location.href
        })
      }).then(function (response) {
        return response.json();
      }).then(function (result) {
        if (!result || String(result.success) !== 'true') throw new Error(result && result.message || 'rejected');
        track('template_request_submit', { template_id: id });
        form.reset();
        button.textContent = ZH ? '请求已发送' : 'Request sent';
        show('ok', ZH
          ? '<b>已加入运行队列。</b>Flow AI 会在 ' + s.replace(/</g, '&lt;') + ' 上运行这个模板，Amber 审核后，结果会在两个工作日内发到你的邮箱。'
          : '<b>Your run is queued.</b> Flow AI runs the ' + name + ' on ' + s.replace(/</g, '&lt;') + ', Amber reviews it, and the result reaches you within two working days.');
      }).catch(function () {
        button.disabled = false;
        button.textContent = label;
        fallback(e, s);
      });
    });
  });
}());
