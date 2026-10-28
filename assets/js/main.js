/* Radek Rosa | Silový a kondiční trenér: veškerý skript webu, bez knihoven. */
(function () {
  "use strict";

  // Hover opens the native desktop disclosure; touch and keyboard retain click control.
  document.querySelectorAll(".menu-services details").forEach(function (menu) {
    var hoverOpened = false;
    menu.addEventListener("pointerenter", function (event) {
      if (!menu.closest(".site-header") || event.pointerType !== "mouse" || !window.matchMedia("(hover: hover)").matches) return;
      hoverOpened = !menu.open;
      menu.open = true;
    });
    menu.addEventListener("pointerleave", function () {
      if (hoverOpened && !menu.contains(document.activeElement)) menu.open = false;
      hoverOpened = false;
    });
    menu.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        event.stopPropagation();
        menu.open = false;
        menu.querySelector("summary").focus();
      }
    });
  });

  function ui(key, fallback) { return window.RosaI18n ? window.RosaI18n.t(key, fallback) : fallback; }

  // Mobilní menu
  var panel = document.getElementById("offcanvas");
  var toggle = document.querySelector(".menu-toggle");
  if (panel && toggle) {
    var setOpen = function (open) {
      panel.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", open);
      document.body.style.overflow = open ? "hidden" : "";
      if (open) panel.querySelector(".offcanvas-close").focus();
      else toggle.focus();
    };
    toggle.addEventListener("click", function () { setOpen(true); });
    panel.addEventListener("click", function (e) {
      if (e.target.closest(".offcanvas-close, .offcanvas-backdrop, a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.classList.contains("open")) setOpen(false);
    });
  }

  // Tlačítko zpět nahoru
  var top = document.querySelector(".to-top");
  if (top) {
    window.addEventListener("scroll", function () {
      top.classList.toggle("show", window.scrollY > 600);
    }, { passive: true });
  }

  // YouTube: náhled se načte hned, přehrávač až po kliknutí
  document.querySelectorAll(".yt").forEach(function (el) {
    var id = el.dataset.id;
    el.style.backgroundImage = "url(https://i.ytimg.com/vi/" + id + "/hqdefault.jpg)";
    el.addEventListener("click", function () {
      var q = "autoplay=1&rel=0";
      if (el.dataset.start) q += "&start=" + el.dataset.start;
      if (el.dataset.end) q += "&end=" + el.dataset.end;
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + id + "?" + q;
      f.title = el.getAttribute("aria-label") || "Video";
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      f.allowFullscreen = true;
      el.appendChild(f);
      el.classList.add("playing");
    }, { once: true });
  });

  // Galerie: původní posun po 5 s, různé šířky fotek a necropovaný lightbox.
  document.querySelectorAll(".carousel").forEach(function (c) {
    var track = c.querySelector(".carousel-track");
    var links = Array.prototype.slice.call(track.querySelectorAll("a"));
    if (!links.length) return;
    var motion = window.matchMedia("(prefers-reduced-motion:reduce)");
    var hovered = false, focused = false, modal = false, pending = false;
    var inView = !("IntersectionObserver" in window), timer;
    function position(link) {
      return link.getBoundingClientRect().left - track.getBoundingClientRect().left + track.scrollLeft;
    }
    function prepare(left) {
      // Decode the next viewport before scrolling; full-resolution photos load only in the dialog.
      var first = links[0].getBoundingClientRect().width;
      var longMove = Math.abs(left - track.scrollLeft) > track.clientWidth;
      var start = longMove ? Math.min(left, track.scrollLeft) : left;
      var end = (longMove ? Math.max(left, track.scrollLeft) : left) + track.clientWidth + first + 11;
      return Promise.all(links.filter(function (link) {
        var x = position(link);
        return x + link.getBoundingClientRect().width > start - 1 && x < end;
      }).map(function (link) {
        var image = link.querySelector("img");
        image.loading = "eager";
        if (image.complete && image.naturalWidth) return Promise.resolve();
        if (image.decode) return image.decode().catch(function () {});
        return new Promise(function (resolve) {
          image.addEventListener("load", resolve, {once:true});
          image.addEventListener("error", resolve, {once:true});
        });
      }));
    }
    function canAutoplay() {
      return !motion.matches && inView && !document.hidden && !hovered && !focused && !modal;
    }
    function step(dir, automatic) {
      if (pending || (automatic && !canAutoplay())) return;
      var left = track.scrollLeft, max = track.scrollWidth - track.clientWidth;
      var target;
      if (dir > 0 && left >= max - 5) target = 0;
      else if (dir < 0 && left <= 5) target = max;
      else {
        var candidates = links.map(position).filter(function (x) { return dir > 0 ? x > left + 5 : x < left - 5; });
        target = candidates.length ? (dir > 0 ? candidates[0] : candidates[candidates.length - 1]) : (dir > 0 ? max : 0);
        target = Math.max(0, Math.min(max, target));
      }
      pending = true;
      prepare(target).then(function () {
        if (!automatic || canAutoplay()) track.scrollTo({left:target, behavior:motion.matches ? "auto" : "smooth"});
      }).finally(function () { pending = false; });
    }
    c.querySelector(".carousel-prev").addEventListener("click", function () { step(-1, false); });
    c.querySelector(".carousel-next").addEventListener("click", function () { step(1, false); });
    function startTimer() {
      clearInterval(timer);
      if (!motion.matches) timer = setInterval(function () { step(1, true); }, 5000);
    }
    startTimer();
    motion.addEventListener("change", startTimer);
    c.addEventListener("mouseenter", function () { hovered = window.matchMedia("(hover:hover)").matches; });
    c.addEventListener("mouseleave", function () { hovered = false; });
    c.addEventListener("focusin", function (event) { focused = event.target.matches(":focus-visible"); });
    c.addEventListener("focusout", function (event) { focused = c.contains(event.relatedTarget) && event.relatedTarget.matches(":focus-visible"); });
    if ("IntersectionObserver" in window) new IntersectionObserver(function (entries) {
      inView = entries[0].isIntersecting;
      if (inView) prepare(track.scrollLeft);
    }, {threshold:0.02}).observe(c);

    var box = document.getElementById("lightbox");
    if (!box || !box.showModal) return;
    var img = box.querySelector("img"), cur = 0, request = 0;
    var show = function (i) {
      cur = (i + links.length) % links.length;
      var chosen = cur, token = ++request;
      var photo = new Image();
      photo.src = links[chosen].href;
      function display() {
        if (token !== request || !photo.naturalWidth) return;
        img.src = photo.src;
        img.alt = links[chosen].querySelector("img").alt;
        var next = new Image();
        next.src = links[(chosen + 1) % links.length].href;
      }
      if (photo.decode) photo.decode().then(display).catch(function () {});
      else photo.addEventListener("load", display, {once:true});
    };
    links.forEach(function (a, i) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        show(i);
        modal = true;
        box.showModal();
      });
    });
    box.querySelector(".lb-prev").addEventListener("click", function () { show(cur - 1); });
    box.querySelector(".lb-next").addEventListener("click", function () { show(cur + 1); });
    box.querySelector(".lb-close").addEventListener("click", function () { box.close(); });
    box.addEventListener("click", function (e) { if (e.target === box) box.close(); });
    box.addEventListener("close", function () { modal = false; });
    box.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") show(cur - 1);
      if (e.key === "ArrowRight") show(cur + 1);
    });
  });

  // Registrační formulář: odesílá se přes FormSubmit (viz README)
  document.querySelectorAll("form[data-formsubmit]").forEach(function (form) {
    var msg = form.querySelector(".form-msg");
    if (document.documentElement.lang === "en") {
      form.addEventListener("invalid", function (event) {
        var input = event.target;
        if (input.validity.valueMissing) input.setCustomValidity(ui("required", "Please complete this field."));
        else if (input.validity.typeMismatch) input.setCustomValidity(ui("email", "Please enter a valid email address."));
      }, true);
      form.addEventListener("input", function (event) { if (event.target.setCustomValidity) event.target.setCustomValidity(""); });
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector("button");
      btn.disabled = true;
      btn.textContent = ui("sending", "Odesílání...");
      fetch("https://formsubmit.co/ajax/" + form.dataset.formsubmit, {
        method: "POST",
        headers: { "Accept": "application/json" },
        body: new FormData(form)
      }).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      }).then(function (result) {
        if (result.success !== true && result.success !== "true") throw new Error("Registration rejected");
        form.querySelectorAll("input, label, button").forEach(function (el) { el.hidden = true; });
        msg.textContent = form.dataset.success;
      }).catch(function () {
        btn.disabled = false;
        btn.textContent = ui("send", "Odeslat");
        msg.textContent = ui("formError", "Odeslání se nepovedlo. Zkuste to prosím znovu, nebo napište na info@radekrosastrong.cz.");
      });
    });
  });
})();
