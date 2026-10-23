/* Homepage-only enhancements: content stays visible without JS or observer support. */
(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches || !('IntersectionObserver' in window) || !Element.prototype.animate) return;
  var active = new Set();
  var selector = '#main > section:not(.hero) h2, .about-photo-frame, #clients .client, .testimonials .quote';
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      if (reduced.matches) return;
      var element = entry.target;
      var delay = 0;
      if (element.matches('.client, .quote')) {
        delay = Array.prototype.indexOf.call(element.parentElement.children, element) % 3 * 35;
      }
      // Individual translate leaves existing hover transforms independent.
      var animation = element.animate([
        {opacity: 0, translate: '0 20px'},
        {opacity: 1, translate: '0 0'}
      ], {duration: 450, delay: delay, easing: 'cubic-bezier(.2,.65,.3,1)', fill: 'backwards'});
      active.add(animation);
      animation.onfinish = animation.oncancel = function () { active.delete(animation); };
    });
  }, {threshold: 0.08});
  document.querySelectorAll(selector).forEach(function (element) { observer.observe(element); });
  function finishActive() { active.forEach(function (animation) { animation.finish(); }); }
  reduced.addEventListener('change', function () {
    if (reduced.matches) { observer.disconnect(); finishActive(); }
  });
  document.addEventListener('focusin', function (event) {
    active.forEach(function (animation) {
      if (animation.effect.target.contains(event.target)) animation.finish();
    });
  });
  window.addEventListener('beforeprint', finishActive);
}());
