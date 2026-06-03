// read-thru reading doc — self-contained interactivity (no dependencies).
(function () {
  "use strict";
  var doc = document.documentElement;

  // ── Theme (persisted) ──────────────────────────────────────────────────
  try {
    var saved = localStorage.getItem("read-thru-theme");
    if (saved) doc.className = saved;
    else if (window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches)
      doc.className = "theme-dark";
  } catch (e) {}
  var themeBtn = document.getElementById("theme-btn");
  themeBtn && themeBtn.addEventListener("click", function () {
    doc.className = doc.className === "theme-dark" ? "theme-light" : "theme-dark";
    try { localStorage.setItem("read-thru-theme", doc.className); } catch (e) {}
  });

  // ── Mobile nav ─────────────────────────────────────────────────────────
  var menuBtn = document.getElementById("menu-btn");
  menuBtn && menuBtn.addEventListener("click", function () {
    document.body.classList.toggle("nav-open");
  });

  // ── Reading progress ───────────────────────────────────────────────────
  var bar = document.getElementById("progress");
  function onScroll() {
    var h = doc.scrollHeight - doc.clientHeight;
    var pct = h > 0 ? (doc.scrollTop || document.body.scrollTop) / h : 0;
    if (bar) bar.style.width = (pct * 100).toFixed(2) + "%";
  }
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ── Scroll-spy TOC ─────────────────────────────────────────────────────
  var items = Array.prototype.slice.call(document.querySelectorAll(".toc-item"));
  var byId = {};
  items.forEach(function (it) { byId[it.getAttribute("data-target")] = it; });
  var secs = Array.prototype.slice.call(document.querySelectorAll(".sec"));
  var current = null;
  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      var it = byId[en.target.id];
      if (!it || it === current) return;
      if (current) current.classList.remove("active");
      it.classList.add("active");
      current = it;
      // keep active item in view within the TOC
      var toc = document.getElementById("toc");
      var r = it.getBoundingClientRect();
      if (toc && (r.top < 80 || r.bottom > toc.clientHeight - 10)) {
        it.scrollIntoView({ block: "center" });
      }
    });
  }, { rootMargin: "-12% 0px -78% 0px", threshold: 0 });
  secs.forEach(function (s) { spy.observe(s); });

  // close mobile nav after picking a destination
  items.forEach(function (it) {
    it.addEventListener("click", function () {
      document.body.classList.remove("nav-open");
    });
  });

  // ── TOC filter ─────────────────────────────────────────────────────────
  var filter = document.getElementById("toc-filter");
  filter && filter.addEventListener("input", function () {
    var q = filter.value.trim().toLowerCase();
    items.forEach(function (it) {
      var t = it.textContent.toLowerCase();
      it.classList.toggle("hidden", q !== "" && t.indexOf(q) === -1);
    });
  });

  // ── Expand-all / collapse-all per code block ───────────────────────────
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest(".code-toggle");
    if (!btn) return;
    var body = btn.closest(".code-head").nextElementSibling;
    var folds = body.querySelectorAll("details.fold");
    var expanding = btn.getAttribute("data-act") === "expand";
    folds.forEach(function (f) { f.open = expanding; });
    btn.setAttribute("data-act", expanding ? "collapse" : "expand");
    btn.textContent = expanding ? "collapse all" : "expand all";
  });

  // ── Keyboard: '/' focuses the filter, 't' toggles theme ────────────────
  document.addEventListener("keydown", function (e) {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    if (e.key === "/") { e.preventDefault(); filter && filter.focus(); }
    else if (e.key === "t" && themeBtn) themeBtn.click();
  });
})();
