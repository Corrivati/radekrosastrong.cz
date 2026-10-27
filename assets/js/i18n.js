/* Only navigation preferences and small UI messages run client-side; page translations are static. */
(function () {
  'use strict';
  var data = document.getElementById('i18n-runtime');
  var messages = data ? JSON.parse(data.textContent) : {};
  window.RosaI18n = {t:function (key, fallback) { return messages[key] || fallback; }};
  document.querySelectorAll('[data-language-link]').forEach(function (link) {
    link.addEventListener('click', function () {
      var target = new URL(link.href);
      target.hash = window.location.hash;
      target.search = window.location.search;
      link.href = target.href;
      // The URL controls the language. Direct links are never automatically redirected.
    });
  });
}());
