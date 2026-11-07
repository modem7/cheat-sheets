/* Cheat Sheets: progressive enhancement, vanilla JS, no dependencies. */
(function () {
  "use strict";
  var doc = document;
  var root = doc.documentElement;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* polite live region shared by the copy, filter and search features */
  var live = $("#live");
  function announce(msg) {
    if (!live) return;
    live.textContent = "";
    setTimeout(function () { live.textContent = msg; }, 30);
  }
  /* localStorage that never throws (private windows, blocked storage) */
  function store(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (e) { /* storage unavailable */ }
    return null;
  }

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

  /* ---------- sidebar: filter, remembered sections, collapse all ---------- */
  var secs = sidebar ? $$("details.nav-sec", sidebar) : [];
  if (secs.length) {
    var secName = function (d) { return $(".nav-sec-name", d).textContent.trim(); };
    var currentSec = $("details.nav-sec:has(a.is-current)", sidebar);
    var saved = {};
    try { saved = JSON.parse(store("nav-sections") || "{}") || {}; } catch (e) { saved = {}; }
    var filtering = false;
    secs.forEach(function (d) {
      var n = secName(d);
      if (d === currentSec) d.open = true;
      else if (typeof saved[n] === "boolean") d.open = saved[n];
      d.addEventListener("toggle", function () {
        if (filtering) return;
        saved[n] = d.open;
        store("nav-sections", JSON.stringify(saved));
        syncCollapse();
      });
    });

    var tools = doc.createElement("div");
    tools.className = "nav-tools";
    tools.innerHTML =
      '<input class="nav-filter" type="search" placeholder="Filter sheets…" aria-label="Filter sheets in the sidebar" autocomplete="off" spellcheck="false">' +
      '<button class="nav-collapse" type="button"></button>';
    var home = $(".nav-home", sidebar);
    sidebar.insertBefore(tools, home ? home.nextSibling : sidebar.firstChild);
    var filter = $(".nav-filter", tools);
    var collapseBtn = $(".nav-collapse", tools);
    var empty = doc.createElement("p");
    empty.className = "nav-empty"; empty.hidden = true; empty.textContent = "No matching sheets.";
    tools.insertAdjacentElement("afterend", empty);

    function syncCollapse() {
      var anyOpen = secs.some(function (d) { return d.open; });
      collapseBtn.textContent = anyOpen ? "Collapse all" : "Expand all";
      collapseBtn.setAttribute("aria-label", anyOpen ? "Collapse all sections" : "Expand all sections");
    }
    collapseBtn.addEventListener("click", function () {
      var open = !secs.some(function (d) { return d.open; });
      secs.forEach(function (d) { d.open = open; saved[secName(d)] = open; });
      store("nav-sections", JSON.stringify(saved));
      syncCollapse();
    });
    syncCollapse();

    var openBefore = null;
    function applyFilter() {
      var q = filter.value.trim().toLowerCase();
      var terms = q ? q.split(/\s+/) : [];
      if (terms.length && !filtering) { filtering = true; openBefore = secs.map(function (d) { return d.open; }); }
      var shown = 0;
      secs.forEach(function (d) {
        var hits = 0;
        $$("li", d).forEach(function (li) {
          if (li.classList.contains("nav-sub")) { li.hidden = terms.length > 0; return; }
          var t = li.textContent.toLowerCase();
          var ok = terms.every(function (w) { return t.indexOf(w) !== -1; });
          li.hidden = !ok; if (ok) hits++;
        });
        if (terms.length) { d.hidden = !hits; d.open = hits > 0; shown += hits; }
        else d.hidden = false;
      });
      if (!terms.length && filtering) {
        filtering = false;
        secs.forEach(function (d, i) { d.open = openBefore[i]; });
        $$("li[hidden]", sidebar).forEach(function (li) { li.hidden = false; });
        syncCollapse();
      }
      empty.hidden = !(terms.length && !shown);
      collapseBtn.hidden = terms.length > 0;
      if (terms.length) announce(shown ? shown + (shown === 1 ? " sheet" : " sheets") + " match" + (shown === 1 ? "es" : "") : "No matching sheets");
    }
    filter.addEventListener("input", applyFilter);
    filter.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && filter.value) { filter.value = ""; applyFilter(); e.stopPropagation(); }
      if (e.key === "Enter") { var a = $("li:not([hidden]) a", sidebar); if (a && filter.value.trim()) a.click(); }
    });
  }

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

  /* ---------- page content: re-run after every soft navigation ---------- */
  var tocIO = null;
  var cleanups = [];
  var tocSmall = window.matchMedia("(max-width: 1180px)");
  /* document-level handlers are added once and look the current TOC up when they fire */
  doc.addEventListener("click", function (e) {
    var t = $(".toc"), b = t && $(".toc-box", t);
    if (b && tocSmall.matches && b.open && !t.contains(e.target)) b.open = false;
  });
  doc.addEventListener("keydown", function (e) {
    var t = $(".toc"), b = t && $(".toc-box", t);
    if (e.key === "Escape" && b && tocSmall.matches && b.open) { b.open = false; var sm = $("summary", b); if (sm) sm.focus(); }
  });
  function initToc() {
    var toc = $(".toc");
    if (!toc) return;
    var box = $(".toc-box", toc);
    if (box && tocSmall.matches) box.removeAttribute("open");
    if (box) toc.addEventListener("click", function (e) { if (tocSmall.matches && e.target.closest && e.target.closest("a")) box.open = false; });
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
      tocIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) visible.add(en.target.id); else visible.delete(en.target.id); });
        var first = heads.find(function (h) { return visible.has(h.id); });
        if (first) { setActive(first.id); return; }
        /* nothing in the band: use the last heading above the viewport */
        var above = null;
        heads.forEach(function (h) { if (h.getBoundingClientRect().top < 120) above = h; });
        if (above) setActive(above.id);
      }, { rootMargin: "-64px 0px -70% 0px", threshold: 0 });
      heads.forEach(function (h) { tocIO.observe(h); });
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
  function initCopy() {
    /* copy buttons on code blocks */
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

    /* click-to-copy for COMMAND | DESCRIPTION tables */
    $$(".table-wrap[data-copy-col]").forEach(function (wrap) {
      var timer = null;
      $$("tbody td:first-child", wrap).forEach(function (td) { td.classList.add("copyable"); td.title = "Click to copy"; });
      wrap.addEventListener("click", function (e) {
        var td = e.target.closest && e.target.closest("td.copyable");
        if (!td || !wrap.contains(td) || (e.target.closest && e.target.closest("a"))) return;
        clearTimeout(timer);
        if (e.detail > 1) return; /* double or triple click selects text instead */
        timer = setTimeout(function () {
          var sel = window.getSelection && window.getSelection();
          if (sel && String(sel).trim()) return; /* the user is selecting: leave it alone */
          var codes = $$("code", td);
          var text = (codes.length === 1 ? codes[0].textContent : td.innerText).trim();
          copyText(text).then(function () {
            td.classList.add("is-copied");
            announce("Copied " + text);
            setTimeout(function () { td.classList.remove("is-copied"); }, 1200);
          }, function () { announce("Could not copy. Select the command and press Ctrl+C."); });
        }, 220);
      });
    });
  }

  /* edge shadows on tables that scroll sideways */
  function initTables() {
    $$(".table-scroll").forEach(function (box) {
      var w = $(".table-wrap", box), tbl = $("table", w);
      function update() {
        var max = w.scrollWidth - w.clientWidth;
        box.classList.toggle("more-left", w.scrollLeft > 2);
        box.classList.toggle("more-right", w.scrollLeft < max - 2);
      }
      w.addEventListener("scroll", update, { passive: true });
      if ("ResizeObserver" in window) {
        var ro = new ResizeObserver(update); ro.observe(w); if (tbl) ro.observe(tbl);
        cleanups.push(function () { ro.disconnect(); });
      }
      window.addEventListener("resize", update);
      cleanups.push(function () { window.removeEventListener("resize", update); });
      update();
    });
  }

  /* ---------- search (Pagefind, loaded on first open) ---------- */
  var dialog = $("#search-dialog");
  var mount = $("#search");
  var loaded = false;
  var ui = null;
  var extras = $("#search-extras");
  var chosen = [];
  var RECENT_KEY = "recent-searches";
  function recents() {
    try {
      var a = JSON.parse(store(RECENT_KEY) || "[]");
      return Array.isArray(a) ? a.filter(function (x) { return typeof x === "string"; }).slice(0, 5) : [];
    } catch (e) { return []; }
  }
  function remember(q) {
    q = (q || "").trim();
    if (q.length < 2) return;
    var a = recents().filter(function (x) { return x !== q; });
    a.unshift(q);
    store(RECENT_KEY, JSON.stringify(a.slice(0, 5)));
  }
  function searchInput() { return $(".pagefind-ui__search-input", mount) || $("input", mount); }
  function renderRecents() {
    var box = $(".search-recent", extras);
    if (!box) return;
    var input = searchInput(), list = recents();
    box.hidden = !list.length || !!(input && input.value);
    var row = $(".search-recent-list", box);
    row.innerHTML = "";
    list.forEach(function (q) {
      var b = doc.createElement("button");
      b.type = "button"; b.className = "chip"; b.textContent = q;
      b.addEventListener("click", function () { if (ui) { ui.triggerSearch(q); renderRecents(); } });
      row.appendChild(b);
    });
  }
  function buildExtras() {
    if (!extras || extras.children.length) return;
    var names = $$("#sidebar .nav-sec-name").map(function (n) { return n.textContent.trim(); });
    extras.innerHTML =
      '<div class="search-recent" hidden><span class="search-extras-label" id="recent-label">Recent</span>' +
      '<span class="search-recent-list" role="group" aria-labelledby="recent-label"></span>' +
      '<button class="chip chip-clear" type="button">Clear</button></div>' +
      '<div class="search-filters" role="group" aria-label="Filter results by section"></div>';
    var row = $(".search-filters", extras);
    names.forEach(function (n) {
      var b = doc.createElement("button");
      b.type = "button"; b.className = "chip"; b.textContent = n; b.setAttribute("aria-pressed", "false");
      b.addEventListener("click", function () {
        var i = chosen.indexOf(n);
        if (i === -1) chosen.push(n); else chosen.splice(i, 1);
        b.setAttribute("aria-pressed", String(i === -1));
        if (ui) ui.triggerFilters(chosen.length ? { section: chosen.slice() } : {});
      });
      row.appendChild(b);
    });
    $(".chip-clear", extras).addEventListener("click", function () {
      store(RECENT_KEY, "[]"); renderRecents(); announce("Recent searches cleared");
      var i = searchInput(); if (i) i.focus();
    });
    mount.addEventListener("input", function () { renderRecents(); });
    mount.addEventListener("keydown", function (e) { if (e.key === "Enter" && e.target.tagName === "INPUT") remember(e.target.value); });
    mount.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("a.pagefind-ui__result-link, a.pagefind-ui__result-title, a[href]")) {
        var i = searchInput(); if (i) remember(i.value);
      }
    });
  }
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
      ui = new window.PagefindUI({
        element: "#search", bundlePath: base, showSubResults: true, showImages: false, autofocus: true,
        resetStyles: false, pageSize: 8, highlightParam: "highlight",
        translations: { placeholder: "Search commands, tools, topics…" }
      });
      var input = $("input", mount); if (input) input.focus();
      renderRecents();
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
    buildExtras();
    loadPagefind();
    renderRecents();
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
  /* ---------- highlight search terms on the page a result led to ---------- */
  function initHighlight() {
    var term = "";
    try { term = new URLSearchParams(location.search).get("highlight") || ""; } catch (e) { return; }
    if (!term || !mount) return;
    var base = mount.getAttribute("data-bundle");
    var s = doc.createElement("script");
    s.type = "module"; /* pagefind-highlight.js is an ES module that also sets window.PagefindHighlight */
    s.src = base + "pagefind-highlight.js" + (window.PagefindHighlight ? "?" + Date.now() : "");
    s.onload = function () {
      if (!window.PagefindHighlight) return;
      var hl = new window.PagefindHighlight({ highlightParam: "highlight" });
      var first = $("#main mark");
      if (!first) return;
      var bar = doc.createElement("p");
      bar.className = "hl-bar";
      bar.innerHTML = '<span></span><button type="button">Clear highlights</button>';
      $("span", bar).textContent = "Highlighting “" + term + "”";
      $("button", bar).addEventListener("click", function () {
        if (hl && hl.removeHighlights) hl.removeHighlights();
        bar.remove();
        try { var u = new URL(location.href); u.searchParams.delete("highlight"); history.replaceState(null, "", u); } catch (e) { /* ignore */ }
      });
      var m = $("#main"); if (m) m.insertBefore(bar, m.firstChild);
      announce("Search terms highlighted on this page");
    };
    doc.head.appendChild(s);
  }

  doc.addEventListener("keydown", function (e) {
    var t = e.target, tag = t && t.tagName;
    var typing = tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (t && t.isContentEditable);
    if ((e.key === "k" || e.key === "K") && (e.ctrlKey || e.metaKey) && !e.altKey) { e.preventDefault(); openSearch(); return; }
    if (e.key === "/" && !typing && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); openSearch(); return; }
    if (e.key === "Escape" && doc.body.classList.contains("nav-open")) setNav(false);
  });

  function initContent() {
    cleanups.forEach(function (f) { f(); }); cleanups = [];
    if (tocIO) { tocIO.disconnect(); tocIO = null; }
    initToc(); initCopy(); initTables(); initHighlight();
  }
  initContent();

  /* ---------- soft navigation ----------
     Same-site links swap only <main> (plus title and the current marker in the sidebar), so the top bar and
     sidebar are never torn down: no white flash, no sidebar scroll reset, no re-run of the filter or open state.
     Anything unexpected falls back to a normal page load. */
  var mainEl = $("#main");
  var cache = new Map();           /* url -> Promise<Document> */
  var navToken = 0;
  var shown = location.pathname + location.search; /* the page currently rendered in <main> */
  var canSoft = !!(mainEl && window.fetch && window.DOMParser && history.pushState && window.URL);
  function pageUrl(a) {
    if (!a || a.target && a.target !== "_self" || a.hasAttribute("download")) return null;
    var u;
    try { u = new URL(a.href, location.href); } catch (e) { return null; }
    if (u.origin !== location.origin || (u.protocol !== "http:" && u.protocol !== "https:")) return null;
    var last = u.pathname.split("/").pop();
    if (last && /\.[a-z0-9]+$/i.test(last) && !/\.html?$/i.test(last)) return null; /* PDFs, images, feeds */
    if (/\/(pagefind|sitemap)/.test(u.pathname)) return null;
    return u;
  }
  function fetchDoc(u) {
    var key = u.pathname + u.search;
    if (!cache.has(key)) {
      cache.set(key, fetch(u.href, { credentials: "same-origin" }).then(function (r) {
        var type = r.headers.get("content-type") || "";
        if (!r.ok || type.indexOf("text/html") === -1) throw new Error("not a page");
        return r.text();
      }).then(function (html) {
        var d = new DOMParser().parseFromString(html, "text/html");
        if (!$("#main", d)) throw new Error("no main");
        return d;
      }));
      cache.get(key).catch(function () { cache.delete(key); });
    }
    return cache.get(key);
  }
  function markCurrent(u) {
    if (!sidebar) return;
    $$("a.is-current", sidebar).forEach(function (a) { a.classList.remove("is-current"); a.removeAttribute("aria-current"); });
    var hit = $$("a", sidebar).filter(function (a) { return a.pathname === u.pathname; })[0];
    if (!hit) return;
    hit.classList.add("is-current"); hit.setAttribute("aria-current", "page");
    var det = hit.closest("details.nav-sec");
    if (det && !det.open) det.open = true;
    var sr = sidebar.getBoundingClientRect(), r = hit.getBoundingClientRect();
    if (r.top < sr.top || r.bottom > sr.bottom) hit.scrollIntoView({ block: "center" });
  }
  function apply(d, u, opts) {
    var next = $("#main", d);
    shown = u.pathname + u.search;
    mainEl.innerHTML = next.innerHTML;
    doc.title = d.title;
    doc.body.className = (d.body.className || "") + (doc.body.classList.contains("nav-open") ? " nav-open" : "");
    ["link[rel=canonical]", "meta[name=description]", "meta[property='og:title']", "meta[property='og:description']", "meta[property='og:url']", "meta[property='og:type']"].forEach(function (s) {
      var a = $(s), b = $(s, d);
      if (a && b) a.setAttribute(a.tagName === "LINK" ? "href" : "content", b.getAttribute(a.tagName === "LINK" ? "href" : "content"));
    });
    markCurrent(u);
    initContent();
    if (opts.restore != null) window.scrollTo(0, opts.restore);
    else if (u.hash && doc.getElementById(decodeURIComponent(u.hash.slice(1)))) doc.getElementById(decodeURIComponent(u.hash.slice(1))).scrollIntoView();
    else window.scrollTo(0, 0);
    mainEl.focus({ preventScroll: true });
    announce("Navigated to " + (d.title || "page").split(" · ")[0]);
  }
  function go(u, opts) {
    opts = opts || {};
    var token = ++navToken;
    var samePath = u.pathname === location.pathname && u.search === location.search;
    if (samePath && !opts.pop) { /* same page: let the browser handle the hash */ location.href = u.href; return; }
    fetchDoc(u).then(function (d) {
      if (token !== navToken) return; /* a newer click won */
      var swap = function () {
        if (!opts.pop) { try { history.replaceState({ y: window.scrollY }, ""); history.pushState({ y: 0 }, "", u.href); } catch (e) { location.href = u.href; return; } }
        apply(d, u, opts);
      };
      if (doc.startViewTransition && !reduceMotion) doc.startViewTransition(swap); else swap();
    }).catch(function () { if (token === navToken) location.href = u.href; });
  }
  if (canSoft) {
    try { history.replaceState({ y: window.scrollY }, ""); } catch (e) { /* ignore */ }
    doc.addEventListener("click", function (e) {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var a = e.target.closest && e.target.closest("a[href]");
      if (!a || a.closest("#search-dialog") || a.closest(".toc")) return;
      var u = pageUrl(a);
      if (!u) return;
      if (u.pathname === location.pathname && u.search === location.search) return; /* in-page anchors */
      e.preventDefault();
      go(u);
    });
    /* warm the cache on hover or touch so the swap is instant */
    var warm = function (e) {
      var a = e.target.closest && e.target.closest("a[href]");
      var u = a && !a.closest("#search-dialog") && pageUrl(a);
      if (u && !(u.pathname === location.pathname && u.search === location.search)) fetchDoc(u).catch(function () {});
    };
    doc.addEventListener("mouseover", warm, { passive: true });
    doc.addEventListener("touchstart", warm, { passive: true });
    doc.addEventListener("focusin", warm);
    window.addEventListener("popstate", function (e) {
      var u = new URL(location.href);
      if (u.pathname + u.search === shown) return; /* hash-only entry: the browser scrolls */
      var y = e.state && typeof e.state.y === "number" ? e.state.y : 0;
      go(u, { pop: true, restore: y });
    });
    window.addEventListener("pagehide", function () { try { history.replaceState({ y: window.scrollY }, ""); } catch (e) { /* ignore */ } });
    var saveY = null;
    window.addEventListener("scroll", function () {
      clearTimeout(saveY);
      saveY = setTimeout(function () { try { history.replaceState({ y: window.scrollY }, ""); } catch (e) { /* ignore */ } }, 150);
    }, { passive: true });
  }
})();
