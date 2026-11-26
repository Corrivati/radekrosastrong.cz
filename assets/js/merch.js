// Manual thumbnail gallery, independent of the draft checkout.
(function () {
  'use strict';
  document.querySelectorAll('[data-merch-gallery]').forEach(function (gallery) {
    var images = Array.from(gallery.querySelectorAll('[data-gallery-image]'));
    var thumbs = Array.from(gallery.querySelectorAll('[data-gallery-thumb]'));
    var main = gallery.querySelector('[data-gallery-main]');
    var status = gallery.querySelector('[data-gallery-status]');
    var zoom = gallery.querySelector('[data-gallery-zoom]');
    var zoomImage = gallery.querySelector('[data-gallery-zoom-image]');
    var detail = gallery.querySelector('[data-gallery-detail]');
    var active = images[0];
    function show(view) {
      active = images.find(function (image) { return image.dataset.view === view; });
      images.forEach(function (image) {
        var selected = image === active;
        image.classList.toggle('is-active', selected);
        if (selected) image.removeAttribute('aria-hidden');
        else image.setAttribute('aria-hidden', 'true');
      });
      thumbs.forEach(function (thumb) { thumb.setAttribute('aria-pressed', String(thumb.dataset.view === view)); });
      var label = view === 'back' ? 'zadní strany' : 'přední strany';
      main.href = active.src;
      main.setAttribute('aria-label', 'Zvětšit fotografii ' + label + ' trika');
      status.textContent = view === 'back' ? 'Zadní strana' : 'Přední strana';
    }
    thumbs.forEach(function (thumb) {
      thumb.addEventListener('click', function () { show(thumb.dataset.view); });
      thumb.addEventListener('keydown', function (event) {
        if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
        event.preventDefault();
        var other = thumbs.find(function (candidate) { return candidate !== thumb; });
        show(other.dataset.view); other.focus();
      });
    });
    main.addEventListener('click', function (event) {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || typeof zoom.showModal !== 'function') return;
      event.preventDefault();
      zoomImage.src = active.src; zoomImage.alt = active.alt;
      detail.setAttribute('aria-pressed', 'false');
      detail.setAttribute('aria-label', 'Přiblížit fotografii na původní velikost');
      zoom.showModal();
    });
    gallery.querySelector('[data-gallery-close]').addEventListener('click', function () { zoom.close(); });
    zoom.addEventListener('click', function (event) { if (event.target === zoom) zoom.close(); });
    detail.addEventListener('click', function () {
      var enlarged = detail.getAttribute('aria-pressed') !== 'true';
      detail.setAttribute('aria-pressed', String(enlarged));
      detail.setAttribute('aria-label', enlarged ? 'Zobrazit celou fotografii' : 'Přiblížit fotografii na původní velikost');
    });
    show('back');
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
