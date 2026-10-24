/* Native details works without JS; explicitly mirror its state when JS is active. */
(function () {
  var details = document.querySelector('.certs-more');
  if (!details) return;
  var summary = details.querySelector('summary');
  function updateState() { summary.setAttribute('aria-expanded', String(details.open)); }
  updateState();
  details.addEventListener('toggle', updateState);
}());
