/* Cheat Sheets: progressive enhancement, vanilla JS, no dependencies. */
(function () {
  "use strict";
  var doc = document;
  var root = doc.documentElement;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- theme toggle (dark is the default; choice persisted) ---------- */
  var themeBtn = $("[data-theme-toggle]");
  function applyTheme(t) {
    root.setAttribute("data-theme", t);
    if (themeBtn) themeBtn.setAttribute("aria-label", t === "dark" ? "Switch to light theme" : "Switch to dark theme");
    var meta = $('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", t === "dark" ? "#0c0f14" : "#fbf9f5");
  }
  applyTheme(root.getAttribute("data-theme") === "light" ? "light" : "dark");
  if (themeBtn) themeBtn.addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    try { localStorage.setItem("theme", next); } catch (e) { /* storage unavailable */ }
  });

  /* ---------- mobile navigation drawer ---------- */
  var menuBtn = $("[data-menu-toggle]");
  var scrim = $(".scrim");
  var sidebar = $("#sidebar");
  function setNav(open) {
    doc.body.classList.toggle("nav-open", open);
    if (menuBtn) { menuBtn.setAttribute("aria-expanded", String(open)); menuBtn.setAttribute("aria-label", open ? "Close navigation" : "Open navigation"); }
    if (scrim) scrim.hidden = !open;
    if (open) { var cur = $("a.is-current", sidebar) || $("a", sidebar); if (cur) cur.focus({ preventScroll: true }); }
  }
  if (menuBtn) menuBtn.addEventListener("click", function () { setNav(!doc.body.classList.contains("nav-open")); });
  if (scrim) scrim.addEventListener("click", function () { setNav(false); });
  if (sidebar) sidebar.addEventListener("click", function (e) { if (e.target.closest && e.target.closest("a")) setNav(false); });

  /* keep the current page visible inside the scrolling sidebar */
  var current = $("#sidebar a.is-current");
  if (current && sidebar) {
    var top = current.offsetTop - sidebar.clientHeight / 3;
    sidebar.scrollTop = Math.max(0, top);
  }

  /* ---------- back to top ---------- */
  var toTop = $("[data-to-top]");
  if (toTop) {
    var ticking = false;
    var onScroll = function () {
      ticking = false;
      var show = window.scrollY > 600;
      toTop.hidden = false;
      toTop.classList.toggle("is-visible", show);
      toTop.tabIndex = show ? 0 : -1;
      toTop.setAttribute("aria-hidden", String(!show));
    };
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
    onScroll();
    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      var m = $("#main"); if (m) m.focus({ preventScroll: true });
    });
  }

  /* ---------- table of contents: scroll-spy ---------- */
  var toc = $(".toc");
  if (toc) {
    var box = $(".toc-box", toc);
    if (box && window.matchMedia("(max-width: 1180px)").matches) box.removeAttribute("open");
    var links = $$("a[href^='#']", toc);
    var map = {};
    links.forEach(function (a) { map[decodeURIComponent(a.getAttribute("href").slice(1))] = a; });
    var heads = Object.keys(map).map(function (id) { return doc.getElementById(id); }).filter(Boolean);
    var setActive = function (id) {
      links.forEach(function (a) { a.classList.remove("is-active"); a.removeAttribute("aria-current"); });
      var a = map[id];
      if (a) {
        a.classList.add("is-active"); a.setAttribute("aria-current", "location");
        if (toc.scrollHeight > toc.clientHeight) {
          var r = a.getBoundingClientRect(), t = toc.getBoundingClientRect();
          if (r.top < t.top || r.bottom > t.bottom) a.scrollIntoView({ block: "nearest" });
        }
      }
    };
    if (heads.length && "IntersectionObserver" in window) {
      var visible = new Set();
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) visible.add(en.target.id); else visible.delete(en.target.id); });
        var first = heads.find(function (h) { return visible.has(h.id); });
        if (first) { setActive(first.id); return; }
        /* nothing in the band: use the last heading above the viewport */
        var above = null;
        heads.forEach(function (h) { if (h.getBoundingClientRect().top < 120) above = h; });
        if (above) setActive(above.id);
      }, { rootMargin: "-64px 0px -70% 0px", threshold: 0 });
      heads.forEach(function (h) { io.observe(h); });
    }
  }

  /* ---------- copy buttons on code blocks ---------- */
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve, reject) {
      var ta = doc.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", ""); ta.style.cssText = "position:fixed;opacity:0;top:0;left:0";
      doc.body.appendChild(ta); ta.select();
      try { doc.execCommand("copy") ? resolve() : reject(); } catch (e) { reject(e); }
      doc.body.removeChild(ta);
    });
  }
  $$(".codeblock").forEach(function (block) {
    var btn = $(".copy-btn", block);
    var code = $("pre code", block) || $("pre", block);
    if (!btn || !code) return;
    btn.hidden = false;
    btn.addEventListener("click", function () {
      copyText(code.innerText.replace(/\n$/, "")).then(function () {
        btn.textContent = "Copied"; btn.classList.add("is-copied");
      }, function () { btn.textContent = "Press Ctrl+C"; });
      setTimeout(function () { btn.textContent = "Copy"; btn.classList.remove("is-copied"); }, 1800);
    });
  });
  /* announce copy result politely */
  $$(".copy-btn").forEach(function (b) { b.setAttribute("aria-live", "polite"); });

  /* ---------- search (Pagefind, loaded on first open) ---------- */
  var dialog = $("#search-dialog");
  var mount = $("#search");
  var loaded = false;
  function loadPagefind() {
    if (loaded || !mount) return;
    loaded = true;
    var base = mount.getAttribute("data-bundle");
    mount.innerHTML = '<p class="search-msg">Loading search…</p>';
    var css = doc.createElement("link");
    css.rel = "stylesheet"; css.href = base + "pagefind-ui.css"; doc.head.appendChild(css);
    var s = doc.createElement("script");
    s.src = base + "pagefind-ui.js";
    s.onload = function () {
      mount.innerHTML = "";
      new window.PagefindUI({
        element: "#search", bundlePath: base, showSubResults: true, showImages: false, autofocus: true,
        resetStyles: false, pageSize: 8,
        translations: { placeholder: "Search commands, tools, topics…" }
      });
      var input = $("input", mount); if (input) input.focus();
    };
    s.onerror = function () {
      loaded = false;
      mount.innerHTML = '<p class="search-msg">Search index not found. It is built in CI by Pagefind; for local preview run <code>npx pagefind --site public</code> after <code>hugo</code>.</p>';
    };
    doc.head.appendChild(s);
  }
  function openSearch() {
    if (!dialog) return;
    if (!dialog.open) { if (dialog.showModal) dialog.showModal(); else dialog.setAttribute("open", ""); }
    loadPagefind();
    var input = $("input", mount); if (input) { input.focus(); input.select(); }
  }
  function closeSearch() { if (dialog && dialog.open) dialog.close ? dialog.close() : dialog.removeAttribute("open"); }
  $$("[data-search-open]").forEach(function (b) { b.addEventListener("click", openSearch); });
  $$("[data-search-close]").forEach(function (b) { b.addEventListener("click", closeSearch); });
  if (dialog) {
    dialog.addEventListener("click", function (e) { if (e.target === dialog) closeSearch(); });
    /* close the dialog when a result is followed within the same page */
    dialog.addEventListener("click", function (e) { if (e.target.closest && e.target.closest("a.pagefind-ui__result-link")) closeSearch(); });
  }
  doc.addEventListener("keydown", function (e) {
    var t = e.target, tag = t && t.tagName;
    var typing = tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (t && t.isContentEditable);
    if ((e.key === "k" || e.key === "K") && (e.ctrlKey || e.metaKey) && !e.altKey) { e.preventDefault(); openSearch(); return; }
    if (e.key === "/" && !typing && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); openSearch(); return; }
    if (e.key === "Escape" && doc.body.classList.contains("nav-open")) setNav(false);
  });
})();
