/* Radek Rosa | Silový a kondiční trenér: veškerý skript webu, bez knihoven. */
(function () {
  "use strict";

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

  // Galerie: posuvník se šipkami, automatický posun a zvětšení po kliknutí
  document.querySelectorAll(".carousel").forEach(function (c) {
    var track = c.querySelector(".carousel-track");
    var links = Array.prototype.slice.call(track.querySelectorAll("a"));
    var step = function (dir) {
      var w = links[0].getBoundingClientRect().width + 11;
      var atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 5;
      if (dir > 0 && atEnd) track.scrollLeft = 0;
      else if (dir < 0 && track.scrollLeft <= 5) track.scrollLeft = track.scrollWidth;
      else track.scrollBy({ left: dir * w });
    };
    c.querySelector(".carousel-prev").addEventListener("click", function () { step(-1); });
    c.querySelector(".carousel-next").addEventListener("click", function () { step(1); });

    var timer, paused = false;
    var reduce = window.matchMedia("(prefers-reduced-motion:reduce)").matches;
    if (!reduce) timer = setInterval(function () { if (!paused) step(1); }, 5000);
    c.addEventListener("mouseenter", function () { paused = true; });
    c.addEventListener("mouseleave", function () { paused = false; });
    c.addEventListener("focusin", function () { paused = true; });

    var box = document.getElementById("lightbox");
    if (!box || !box.showModal) return;
    var img = box.querySelector("img"), cur = 0;
    var show = function (i) {
      cur = (i + links.length) % links.length;
      img.src = links[cur].href;
      img.alt = links[cur].querySelector("img").alt;
    };
    links.forEach(function (a, i) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        show(i);
        paused = true;
        box.showModal();
      });
    });
    box.querySelector(".lb-prev").addEventListener("click", function () { show(cur - 1); });
    box.querySelector(".lb-next").addEventListener("click", function () { show(cur + 1); });
    box.querySelector(".lb-close").addEventListener("click", function () { box.close(); });
    box.addEventListener("click", function (e) { if (e.target === box) box.close(); });
    box.addEventListener("close", function () { paused = false; });
    box.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") show(cur - 1);
      if (e.key === "ArrowRight") show(cur + 1);
    });
  });

  // Registrační formulář: odesílá se přes FormSubmit (viz README)
  document.querySelectorAll("form[data-formsubmit]").forEach(function (form) {
    var msg = form.querySelector(".form-msg");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector("button");
      btn.disabled = true;
      btn.textContent = "Odesílání...";
      fetch("https://formsubmit.co/ajax/" + form.dataset.formsubmit, {
        method: "POST",
        headers: { "Accept": "application/json" },
        body: new FormData(form)
      }).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        form.querySelectorAll("input, label, button").forEach(function (el) { el.hidden = true; });
        msg.textContent = form.dataset.success;
      }).catch(function () {
        btn.disabled = false;
        btn.textContent = "Odeslat";
        msg.textContent = "Odeslání se nepovedlo. Zkuste to prosím znovu, nebo napište na rosa.education@email.cz.";
      });
    });
  });
})();
