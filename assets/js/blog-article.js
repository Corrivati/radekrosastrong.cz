/* Optional article interactions. The complete article and question list work without JS. */
(function () {
  'use strict';
  function ui(key, fallback) { return window.RosaI18n ? window.RosaI18n.t(key, fallback) : fallback; }
  var article = document.querySelector('[data-article]');
  if (!article) return;

  // Study visuals are fully rendered by default, including when JS is disabled.
  var motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (article.querySelector('[data-study-reveal]') && !motion.matches && 'IntersectionObserver' in window && Element.prototype.animate) {
    var animations = new Set();
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        if (motion.matches) return;
        var element = entry.target;
        var isBar = element.hasAttribute('data-study-bar');
        var frames = isBar ? [{transform: 'scaleX(0)'}, {transform: 'scaleX(1)'}] : [{opacity: 0, translate: '0 20px'}, {opacity: 1, translate: '0 0'}];
        var delay = element.classList.contains('blog-study-stat') ? Array.prototype.indexOf.call(element.parentElement.children, element) % 2 * 60 : 0;
        var animation = element.animate(frames, {duration: 450, delay: delay, easing: 'cubic-bezier(.2,.65,.3,1)', fill: 'backwards'});
        animations.add(animation);
        animation.onfinish = animation.oncancel = function () { animations.delete(animation); };
      });
    }, {threshold: 0.12});
    article.querySelectorAll('[data-study-reveal], [data-study-bar]').forEach(function (element) { observer.observe(element); });
    function finishAnimations() { animations.forEach(function (animation) { animation.finish(); }); }
    motion.addEventListener('change', function () {
      if (motion.matches) { observer.disconnect(); finishAnimations(); }
    });
    window.addEventListener('beforeprint', finishAnimations);
  }
  article.querySelectorAll('[data-checklist]').forEach(function (checklist) {
    var inputs = Array.from(checklist.querySelectorAll('input[type="checkbox"]'));
    var counter = checklist.querySelector('[data-checklist-count]');
    var progress = checklist.querySelector('progress');
    var reset = checklist.querySelector('[data-checklist-reset]');
    var update = function () {
      var count = inputs.filter(function (input) { return input.checked; }).length;
      counter.textContent = count;
      progress.value = count;
      reset.disabled = count === 0;
    };
    checklist.querySelector('.blog-checklist-progress').hidden = false;
    reset.hidden = false;
    checklist.addEventListener('change', update);
    reset.addEventListener('click', function () {
      inputs.forEach(function (input) { input.checked = false; });
      update();
    });
    update();
  });

  var contents = article.querySelector('[data-article-contents]');
  var desktop = window.matchMedia('(min-width: 1200px)');
  var adaptContents = function () { contents.open = desktop.matches; };
  adaptContents();
  if (desktop.addEventListener) desktop.addEventListener('change', adaptContents);
  else desktop.addListener(adaptContents);
  var body = article.querySelector('[data-article-body]');
  var headings = Array.from(body.querySelectorAll('.blog-chapter>h2'));
  var links = Array.from(contents.querySelectorAll('a[href^="#"]'));
  var bar = article.querySelector('[data-reading-progress]');
  var fill = bar.querySelector('span');
  var active = null;
  var scheduled = false;
  bar.hidden = false;
  var updateReading = function () {
    scheduled = false;
    var rect = body.getBoundingClientRect();
    var distance = rect.height - window.innerHeight;
    var amount = distance > 0 ? Math.max(0, Math.min(1, -rect.top / distance)) : (rect.bottom <= window.innerHeight ? 1 : 0);
    var current = headings[0];
    headings.forEach(function (heading) {
      if (heading.getBoundingClientRect().top <= 160) current = heading;
    });
    fill.style.transform = 'scaleX(' + amount + ')';
    if (current && active !== current.id) {
      active = current.id;
      links.forEach(function (link) {
        if (link.hash === '#' + active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }
  };
  var schedule = function () {
    if (!scheduled) {
      scheduled = true;
      window.requestAnimationFrame(updateReading);
    }
  };
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  if ('ResizeObserver' in window) new ResizeObserver(schedule).observe(body);
  updateReading();

  var canonical = document.querySelector('link[rel="canonical"]').href;
  var copy = article.querySelector('[data-copy-link]');
  var status = article.querySelector('.blog-tool-status');
  var fallback = article.querySelector('.blog-copy-fallback');
  copy.hidden = false;
  copy.addEventListener('click', function () {
    var manualCopy = function () {
      fallback.hidden = false;
      fallback.querySelector('input').focus();
      fallback.querySelector('input').select();
      status.textContent = ui('manualCopy', 'Odkaz je označený. Zkopíruj ho pomocí nabídky zařízení nebo Ctrl+C.');
    };
    if (!navigator.clipboard || !navigator.clipboard.writeText) { manualCopy(); return; }
    navigator.clipboard.writeText(canonical).then(function () {
      fallback.hidden = true;
      status.textContent = ui('copied', 'Odkaz byl zkopírován.');
    }).catch(manualCopy);
  });
  var share = article.querySelector('[data-article-share]');
  if (navigator.share) share.addEventListener('click', function (event) {
    event.preventDefault();
    navigator.share({ title: article.querySelector('h1').textContent, url: canonical }).catch(function (error) {
      if (error.name !== 'AbortError') status.textContent = ui('shareError', 'Sdílení se nepodařilo. Můžeš zkopírovat odkaz.');
    });
  });
})();
