// Gallery works independently of the disabled draft checkout.
(function () {
  'use strict';
  document.querySelectorAll('[data-merch-gallery]').forEach(function (gallery) {
    var slides = Array.from(gallery.querySelectorAll('[data-gallery-slide]'));
    var index = 0;
    if (slides.length < 2) return;
    var status = gallery.querySelector('[data-gallery-status]');
    function show(next) {
      index = (next + slides.length) % slides.length;
      slides.forEach(function (slide, i) {
        var active = i === index;
        slide.classList.toggle('is-active', active);
        if (active) { slide.removeAttribute('aria-hidden'); slide.removeAttribute('tabindex'); }
        else { slide.setAttribute('aria-hidden', 'true'); slide.setAttribute('tabindex', '-1'); }
      });
      status.textContent = slides[index].dataset.caption + ' · ' + (index + 1) + ' / ' + slides.length;
    }
    gallery.querySelector('[data-gallery-prev]').addEventListener('click', function () { show(index - 1); });
    gallery.querySelector('[data-gallery-next]').addEventListener('click', function () { show(index + 1); });
    gallery.addEventListener('keydown', function (event) {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault(); show(index + (event.key === 'ArrowRight' ? 1 : -1));
      }
    });
    gallery.querySelector('[data-gallery-controls]').hidden = false;
    show(0);
  });
}());

/* Draft: paste the final Stripe Payment Link here only when sale details are confirmed.
   Size selection happens in Stripe; this page must not promise stock or final pricing. */
(function () {
  'use strict';
  var paymentLink = '';
  if (!paymentLink) return;
  var url;
  try { url = new URL(paymentLink); } catch (_) { return; }
  if (url.protocol !== 'https:' || url.hostname !== 'buy.stripe.com') return;
  var button = document.querySelector('.merch-buy');
  if (!button) return;
  var link = document.createElement('a');
  link.className = button.className;
  link.href = url.href;
  link.textContent = 'Koupit triko';
  button.replaceWith(link);
  document.getElementById('merch-order-note').textContent = 'Velikost vybereš při objednávce. Platba probíhá přes Stripe.';
}());
