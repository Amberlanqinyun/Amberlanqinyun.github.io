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
      button.textContent = 'Copied';
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
      if (!e) return { field: email, say: 'Could you add your email, so the result can reach you?' };
      if (e.indexOf('@') < 1 || e.indexOf('.', e.indexOf('@')) < 0) return { field: email, say: 'That email looks incomplete. Worth a second look?' };
      if (!s) return { field: site, say: site.getAttribute('data-missing') || 'Which site should it run on?' };
      return null;
    }

    function fallback(e, s) {
      var body = 'Please run the ' + name + ' template on ' + s + '.\n\nSend the result to ' + e + '.';
      var href = 'mailto:' + TO + '?subject=' + encodeURIComponent('Template run: ' + name) + '&body=' + encodeURIComponent(body);
      show('error', 'That did not send, and nothing was lost: <a href="' + href + '">send the same request from your email app</a>, or email <a href="mailto:' + TO + '">' + TO + '</a> directly.');
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
      button.textContent = 'Sending';
      fetch('https://formsubmit.co/ajax/' + TO, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          _subject: 'Template run: ' + name + ' for ' + s,
          _template: 'table',
          _captcha: 'false',
          _autoresponse: 'Thanks for asking Flow AI to run the ' + name + ' on ' + s + '. Amber reviews every result before it is sent, and yours will reach you within two working days. If anything is unclear, just reply to this email.',
          template: name,
          template_id: id,
          email: e,
          site: s,
          page: window.location.href
        })
      }).then(function (response) {
        return response.json();
      }).then(function (result) {
        if (!result || result.success !== true) throw new Error('rejected');
        track('template_request_submit', { template_id: id });
        form.reset();
        button.textContent = 'Request sent';
        show('ok', '<b>Your run is queued.</b> Flow AI runs the ' + name + ' on ' + s.replace(/</g, '&lt;') + ', Amber reviews it, and the result reaches you within two working days.');
      }).catch(function () {
        button.disabled = false;
        button.textContent = label;
        fallback(e, s);
      });
    });
  });
}());
