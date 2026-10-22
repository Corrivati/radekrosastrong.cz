(function () {
  var section = document.getElementById('clients');
  if (!section) return;
  var track = section.querySelector('.clients-track');
  var prev = section.querySelector('.clients-prev');
  var next = section.querySelector('.clients-next');
  section.querySelector('.clients-controls').hidden = false;
  function update() {
    prev.disabled = track.scrollLeft < 2;
    next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
  }
  function move(direction) {
    var card = track.querySelector('.client');
    var step = card.getBoundingClientRect().width + parseFloat(getComputedStyle(track).columnGap);
    track.scrollBy({left: direction * step, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  }
  prev.addEventListener('click', function () { move(-1); });
  next.addEventListener('click', function () { move(1); });
  track.addEventListener('keydown', function (event) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault(); move(event.key === 'ArrowLeft' ? -1 : 1);
  });
  track.addEventListener('scroll', update, {passive: true});
  window.addEventListener('resize', update);
  update();
}());
