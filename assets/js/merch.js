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
