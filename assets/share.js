(function () {
  'use strict';

  var shareButtons = '[data-share]';

  function resolvedUrl(value) {
    var url = new URL(value || window.location.href, window.location.href);
    url.search = '';
    return url.href;
  }

  async function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value);
      return;
    }

    var field = document.createElement('textarea');
    field.value = value;
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.opacity = '0';
    document.body.appendChild(field);
    field.select();
    var copied = document.execCommand('copy');
    field.remove();
    if (!copied) throw new Error('Copy failed');
  }

  function feedback(button, label, state) {
    if (!button.dataset.defaultLabel) {
      button.dataset.defaultLabel = button.textContent.trim();
    }
    window.clearTimeout(Number(button.dataset.feedbackTimer || 0));
    button.textContent = label;
    button.dataset.state = state || 'success';
    button.dataset.feedbackTimer = String(window.setTimeout(function () {
      button.textContent = button.dataset.defaultLabel;
      delete button.dataset.state;
      delete button.dataset.feedbackTimer;
    }, 1800));
  }

  async function share(button) {
    var payload = {
      title: button.dataset.shareTitle || document.title,
      text: button.dataset.shareText || '',
      url: resolvedUrl(button.dataset.shareUrl)
    };

    if (typeof navigator.share === 'function') {
      try {
        await navigator.share(payload);
        feedback(button, 'Shared');
        return;
      } catch (error) {
        if (error && error.name === 'AbortError') return;
      }
    }

    try {
      await copyText(payload.url);
      feedback(button, 'Link copied');
    } catch (error) {
      feedback(button, 'Copy failed', 'error');
    }
  }

  document.addEventListener('click', function (event) {
    var button = event.target.closest(shareButtons);
    if (!button) return;
    share(button);
  });
}());
