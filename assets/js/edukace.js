// Keep completed workshops marked using the event's local date in Prague.
(function () {
  var today = new Intl.DateTimeFormat('sv-SE', {timeZone: 'Europe/Prague', year: 'numeric', month: '2-digit', day: '2-digit'}).format(new Date());
  document.querySelectorAll('[data-event-end]').forEach(function (event) {
    if (event.dataset.eventEnd >= today) return;
    event.classList.add('is-past');
    var badge = event.querySelector('[data-event-status]');
    badge.textContent = window.RosaI18n ? window.RosaI18n.t('pastEvent', '✓ Již proběhlo') : '✓ Již proběhlo';
    badge.className = 'edu-badge edu-badge-past';
    var cta = event.querySelector('[data-event-cta]');
    if (cta) cta.remove();
    var price = event.querySelector('.edu-price');
    if (price) price.remove();
  });
}());
