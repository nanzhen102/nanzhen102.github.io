---
title: Lactobacillaceae genera
date: 2026-11-10
---

<nav id="top" class="lacto-tabs" aria-label="Lactobacillaceae pages"><a href="lactobacillaceae">Overview</a> <span aria-current="page">Genera</span> <a href="lactobacillaceae-species">Species</a> <a href="lactobacillaceae-names" data-router-ignore>Old → new names</a></nav>
<a class="lacto-ask-fab" href="lactobacillaceae#ask" data-router-ignore data-endpoint="https://lactorador-api.onrender.com/api/ask" aria-expanded="false"><span aria-hidden="true">🐾</span> Ask LactoRador</a>
<script>// Copied from 11_agent/lactorador/web/lactorador_chat.js by copy_to_site.py; edit it there.
/* LactoRador chat for the Lactobacillaceae pages (Quartz site). No libraries.
   The "🐾 Ask LactoRador" button (a.lacto-ask-fab[data-endpoint]) on every Lactobacillaceae page
   opens a chat box at the bottom right of the same page; any link with data-lr-open does too.
   Without this script, the button links to the overview with #ask, which opens the box there.
   Listeners sit on the document, so they keep working after Quartz's in-site navigation replaces
   the page body; the box is put back after each navigation and kept in sessionStorage, so the
   conversation survives page changes. Styles: quartz/styles/custom.scss ([data-lr-box], .lr-panel).
   Copied into the site by web/copy_to_site.py. */
(function () {
  if (window.__lactorador) return;
  window.__lactorador = true;
  var KEY = "lactorador-panel";
  var SIZE_KEY = "lactorador-size";
  var EXAMPLES = [
    "What is Lactobacillus plantarum called now?",
    "What is the type species of Lacticaseibacillus?",
    "Is Lactobacillus reuteri homo- or heterofermentative?",
    "List the genera in phylogenetic order.",
    "Why is Lactobacillus rogosae not in the list?",
  ];
  var panel = null; // the slide-in panel element, kept across in-site navigation
  // Simple line icons (Lucide shapes, ISC licence), drawn in the text colour.
  function icon(paths) {
    return '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths + "</svg>";
  }
  var ICON = {
    copy: icon('<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'),
    check: icon('<path d="M20 6 9 17l-5-5"/>'),
    up: icon('<path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/>'),
    down: icon('<path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z"/>'),
  };
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  // Small, safe markdown: escape everything first, then allow links, bold, italics, lists, paragraphs.
  function md(text) {
    var h = esc(text);
    h = h.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    h = h.replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
    h = h.replace(/\*\*((?:[^*]|\*[^*\n]+\*)+?)\*\*/g, "<strong>$1</strong>"); // bold may hold *italics*
    h = h.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");
    h = h.replace(/(^|\n)_\(([^)]*)\)_/g, '$1<span class="lr-small">($2)</span>');
    return h.split(/\n{2,}/).map(function (p) {
      if (/^\s*[-•] /.test(p)) {
        return "<ul>" + p.split(/\n/).map(function (l) { return "<li>" + l.replace(/^\s*[-•] /, "") + "</li>"; }).join("") + "</ul>";
      }
      return "<p>" + p.replace(/\n/g, "<br>") + "</p>";
    }).join("");
  }
  function welcome() {
    return '<div class="lr-msg lr-bot"><p>Woof woof, I am LactoRador, your personal assistant here! Ask me about ' +
      "<em>Lactobacillaceae</em> names, genera, type strains and genomes.</p><p>Try:</p><p class=\"lr-examples\">" +
      EXAMPLES.map(function (q) { return '<button type="button" data-lr-q="' + esc(q) + '">' + esc(q) + "</button>"; }).join(" ") +
      "</p></div>";
  }
  // ---- one conversation box ----
  function hist(b) { return b.lrHistory || (b.lrHistory = []); }
  function add(b, role, html, extra) {
    var log = b.querySelector(".lr-log");
    var d = document.createElement("div");
    d.className = "lr-msg lr-" + role + (extra ? " " + extra : "");
    d.innerHTML = html;
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
    return d;
  }
  function save(b) {
    if (b !== panel) return;
    try {
      sessionStorage.setItem(KEY, JSON.stringify({
        open: panel.classList.contains("lr-open"), history: hist(panel),
        log: panel.querySelector(".lr-log").innerHTML,
      }));
    } catch (e) { /* storage blocked: the panel still works, it just forgets on a full reload */ }
  }
  function ask(b, question) {
    if (!b || !question.trim()) return;
    var input = b.querySelector(".lr-input"), button = b.querySelector(".lr-send");
    if (input.disabled) return;
    add(b, "user", esc(question));
    var wait = add(b, "bot", "Looking it up…", "lr-wait");
    input.value = "";
    input.disabled = button.disabled = true;
    fetch(b.getAttribute("data-endpoint"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question, history: hist(b).slice(-6) }),
    })
      .then(function (r) {
        if (r.ok) return r.json();
        var e = new Error(r.status === 429 ? "Too many questions in the last hour; please try again later."
          : "The assistant returned an error (" + r.status + ").");
        e.shown = true;
        throw e;
      })
      .then(function (r) {
        var h = hist(b);
        h.push({ role: "user", content: question }, { role: "assistant", content: r.answer });
        var tools = (r.tool_calls || []).map(function (c) { return c.name; });
        wait.className = "lr-msg lr-bot";
        wait.setAttribute("data-lr-i", String(h.length - 1)); // the answer's place in the history, for the thumbs
        wait.setAttribute("data-lr-mode", r.mode || "");
        wait.innerHTML = md(r.answer) +
          '<div class="lr-meta">' + (r.mode === "offline" ? "offline mode · " : "") +
          (tools.length ? "looked up: " + esc(tools.join(", ")) : "no lookup") +
          (r.note ? " · " + esc(r.note) : "") + "</div>" +
          '<div class="lr-meta lr-caution">AI-generated; may contain mistakes. Check the linked sources.</div>' +
          '<div class="lr-rate">' +
          '<button type="button" data-lr-copy title="Copy" aria-label="Copy answer">' + ICON.copy + "</button>" +
          '<button type="button" data-lr-rate="up" title="Helpful" aria-label="Helpful">' + ICON.up + "</button>" +
          '<button type="button" data-lr-rate="down" title="Not helpful" aria-label="Not helpful">' + ICON.down + "</button></div>";
      })
      .catch(function (e) {
        wait.className = "lr-msg lr-bot lr-error";
        wait.innerHTML = esc(e.shown ? e.message
          : "The assistant cannot be reached right now. The name search on the Old → new names page still works.");
      })
      .finally(function () {
        input.disabled = button.disabled = false;
        if (b.offsetParent !== null) input.focus();
        b.querySelector(".lr-log").scrollTop = 1e9;
        save(b);
      });
  }
  // Thumbs up/down: sent to /api/feedback next to /api/ask. The chosen one stays highlighted, then a thank-you.
  function rate(b, btn) {
    var msg = btn.closest(".lr-msg"), row = btn.closest(".lr-rate");
    var i = Number(msg && msg.getAttribute("data-lr-i")), h = hist(b);
    if (!h[i] || !h[i - 1] || row.getAttribute("data-done")) return;
    row.setAttribute("data-done", "1");
    btn.classList.add("lr-chosen");
    fetch(b.getAttribute("data-endpoint").replace(/\/api\/ask$/, "/api/feedback"), {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rating: btn.getAttribute("data-lr-rate"), question: h[i - 1].content,
        answer: h[i].content, mode: msg.getAttribute("data-lr-mode") || "" }),
    }).catch(function () {});
    row.querySelectorAll("[data-lr-rate]").forEach(function (x) { x.disabled = true; });
    row.insertAdjacentHTML("beforeend", '<span class="lr-thanks">Thanks for the feedback.</span>');
    save(b);
  }
  // Copy: the answer's text as written (markdown), with its links.
  function copy(b, btn) {
    var msg = btn.closest(".lr-msg"), h = hist(b), i = Number(msg && msg.getAttribute("data-lr-i"));
    var text = h[i] ? h[i].content : msg.innerText;
    var done = function () {
      btn.innerHTML = ICON.check;
      setTimeout(function () { btn.innerHTML = ICON.copy; }, 1500);
    };
    var fallback = function () { // older browsers, or clipboard access refused: copy through a hidden text box
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;opacity:0;top:0;left:0";
      document.body.appendChild(ta);
      ta.select();
      try { if (document.execCommand("copy")) done(); } catch (e) { /* nothing more to try */ }
      ta.remove();
    };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, fallback);
    else fallback();
  }
  // ---- the slide-in panel ----
  function fab() { return document.querySelector(".lacto-ask-fab[data-endpoint]"); }
  function build(endpoint) {
    var p = document.createElement("aside");
    p.className = "lr-panel";
    p.setAttribute("data-lr-box", "");
    p.setAttribute("data-endpoint", endpoint);
    p.setAttribute("aria-label", "Ask LactoRador");
    p.innerHTML =
      '<div class="lr-grip" title="Drag to resize; double-click to reset" aria-hidden="true"></div>' +
      '<div class="lr-head"><strong>🐾&nbsp;&nbsp;LactoRador</strong>' +
      '<button type="button" class="lr-icon" data-lr-clear title="New chat" aria-label="New chat">↺</button>' +
      '<button type="button" class="lr-icon" data-lr-close title="Close" aria-label="Close">✕</button></div>' +
      '<div class="lr-log" aria-live="polite">' + welcome() + "</div>" +
      '<form><label class="lacto-sr" for="lr-panel-q">Your question</label>' +
      '<input id="lr-panel-q" class="lr-input" type="text" maxlength="500" placeholder="Ask a question…" autocomplete="off" />' +
      '<button class="lr-send" type="submit" aria-label="Send">↑</button></form>' +
      // Update the month when a new release of the lists goes on the site.
      '<div class="lr-foot">Answers come only from this site\'s lists (updated November 2026) and the papers ' +
      'they cite. Lifestyle and ecology: coming soon.</div>';
    try { // the size the visitor last dragged it to, if any
      var z = JSON.parse(localStorage.getItem(SIZE_KEY) || "null");
      if (z && z.w && z.h) { p.style.width = z.w + "px"; p.style.height = z.h + "px"; }
    } catch (e) { /* ignore */ }
    try {
      var s = JSON.parse(sessionStorage.getItem(KEY) || "null");
      if (s && s.history && s.history.length) {
        p.lrHistory = s.history;
        p.querySelector(".lr-log").innerHTML = s.log;
      }
    } catch (e) { /* ignore */ }
    return p;
  }
  function setOpen(open) {
    var f = fab();
    if (!f) return;
    if (!panel) panel = build(f.getAttribute("data-endpoint"));
    if (!panel.isConnected) document.body.appendChild(panel);
    panel.classList.toggle("lr-open", open);
    document.documentElement.classList.toggle("lr-panel-open", open);
    f.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      panel.querySelector(".lr-log").scrollTop = 1e9;
      setTimeout(function () { panel.querySelector(".lr-input").focus(); }, 50);
    }
    save(panel);
  }
  function wasOpen() {
    try { return !!(JSON.parse(sessionStorage.getItem(KEY) || "null") || {}).open; } catch (e) { return false; }
  }
  // After a page load or an in-site navigation: put the panel back if it was open and this page has the button.
  function restore() {
    var open = panel ? panel.classList.contains("lr-open") : wasOpen() || location.hash === "#ask";
    if (fab() && open) setOpen(true);
    else document.documentElement.classList.remove("lr-panel-open");
  }
  // Resize: drag the top-left corner; the bottom-right corner stays put. Double-click resets.
  document.addEventListener("pointerdown", function (ev) {
    var g = ev.target.closest && ev.target.closest(".lr-panel .lr-grip");
    if (!g) return;
    ev.preventDefault();
    var r = panel.getBoundingClientRect(), x0 = ev.clientX, y0 = ev.clientY;
    function move(e) {
      var w = Math.max(300, Math.min(window.innerWidth - 24, r.width + x0 - e.clientX));
      var h = Math.max(300, Math.min(window.innerHeight - 24, r.height + y0 - e.clientY));
      panel.style.width = w + "px";
      panel.style.height = h + "px";
    }
    function up() {
      document.removeEventListener("pointermove", move);
      document.removeEventListener("pointerup", up);
      document.documentElement.classList.remove("lr-resizing");
      try {
        localStorage.setItem(SIZE_KEY, JSON.stringify({ w: parseInt(panel.style.width, 10), h: parseInt(panel.style.height, 10) }));
      } catch (e) { /* ignore */ }
    }
    document.documentElement.classList.add("lr-resizing");
    document.addEventListener("pointermove", move);
    document.addEventListener("pointerup", up);
  });
  document.addEventListener("dblclick", function (ev) {
    if (!(ev.target.closest && ev.target.closest(".lr-panel .lr-grip"))) return;
    panel.style.width = panel.style.height = "";
    try { localStorage.removeItem(SIZE_KEY); } catch (e) { /* ignore */ }
  });
  // ---- events ----
  function boxOf(el) { return el.closest && el.closest("[data-lr-box]"); }
  document.addEventListener("submit", function (ev) {
    var b = boxOf(ev.target);
    if (!b) return;
    ev.preventDefault();
    ask(b, b.querySelector(".lr-input").value);
  });
  document.addEventListener("click", function (ev) {
    var t = ev.target;
    if (!t.closest) return;
    var f = t.closest(".lacto-ask-fab[data-endpoint]");
    if (!f && t.closest("[data-lr-open]") && fab()) {
      ev.preventDefault();
      return setOpen(true);
    }
    if (f) {
      ev.preventDefault();
      setOpen(!(panel && panel.isConnected && panel.classList.contains("lr-open")));
      return;
    }
    var b = boxOf(t);
    if (!b) return;
    var q = t.closest("[data-lr-q]");
    if (q) return ask(b, q.getAttribute("data-lr-q"));
    var r = t.closest("[data-lr-rate]");
    if (r) return rate(b, r);
    var c = t.closest("[data-lr-copy]");
    if (c) return copy(b, c);
    if (t.closest("[data-lr-close]")) return setOpen(false);
    if (t.closest("[data-lr-clear]")) {
      b.lrHistory = [];
      b.querySelector(".lr-log").innerHTML = welcome();
      save(b);
    }
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape" && panel && panel.classList.contains("lr-open")) setOpen(false);
  });
  document.addEventListener("nav", restore);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", restore);
  else restore();
})();</script>

<p class="lacto-hero">38</p>
<p class="lacto-hero-label">genera currently placed in <em>Lactobacillaceae</em> family, updated on November 10, 2026.</p>

For detailed homofermentative and heterofermentative fermentation, check
[Gänzle 2015](https://doi.org/10.1016/j.cofs.2015.03.001) and
[Qiao & Gänzle 2026](https://doi.org/10.1016/j.fm.2025.104945).

Today's family is the union of two. _Lactobacillus_ (1901), _Pediococcus_ (1903), and _Paralactobacillus_ (2000) made up _Lactobacillaceae_; _Leuconostoc_ (1878), _Weissella_ (1994), _Oenococcus_ (1995), _Fructobacillus_ (2008), and _Convivina_ (2015) sat in _Leuconostocaceae_. [Zheng et al. 2020](https://doi.org/10.1099/ijsem.0.004107) merged the two and split the old, sprawling _Lactobacillus_ into 22 genera on whole-genome evidence.

## All 38 genera

<div class="lacto-order">
<div class="lacto-order-controls" role="group" aria-label="Table order">
<span>Order</span>
<input class="lacto-order-radio" type="radio" name="lacto-order" id="lacto-order-tree" checked />
<label for="lacto-order-tree">Phylogenetic</label>
<input class="lacto-order-radio" type="radio" name="lacto-order" id="lacto-order-az" />
<label for="lacto-order-az">A–Z</label>
</div>
<p class="lacto-caption lacto-view-tree">The order they sit in on the tree. The two genera not yet placed on it are listed last.</p>
<p class="lacto-caption lacto-view-az">Alphabetical by genus name.</p>
<div class="lacto-table-wrap lacto-view-tree"><table class="lacto-table"><thead><tr><th scope="col">Genus</th><th scope="col">No. of species<span class="lacto-th-hint"><span aria-hidden="true">👇</span> Click to see species info.</span></th><th scope="col">Type species</th><th scope="col">Fermentation</th><th scope="col">Proposed</th></tr></thead><tbody><tr><td class="lacto-genus"><em>Lactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lactobacillus">56</a></td><td><em>L. delbrueckii</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth">Beijerinck 1901<span class="lacto-auth-note">(<a href="https://doi.org/10.1099/00207713-30-1-225">Approved Lists 1980</a>)</span></td></tr><tr><td class="lacto-genus"><em>Amylolactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#amylolactobacillus">2</a></td><td><em>Am. amylophilus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Holzapfeliella</em></td><td class="lacto-count"><a href="lactobacillaceae-species#holzapfeliella">2</a></td><td><em>H. floricola</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.005688">Deshmukh and Oren 2023</a></td></tr><tr><td class="lacto-genus"><em>Xylocopilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#xylocopilactobacillus">2</a></td><td><em>X. apis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1128/spectrum.00782-23">Kawasaki et al. 2024</a></td></tr><tr><td class="lacto-genus"><em>Bombilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#bombilactobacillus">6</a></td><td><em>Bo. mellifer</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Companilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#companilactobacillus">37</a></td><td><em>Co. alimentarius</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Lapidilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lapidilactobacillus">9</a></td><td><em>Ld. concavus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Agrilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#agrilactobacillus">3</a></td><td><em>Ag. composti</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Schleiferilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#schleiferilactobacillus">3</a></td><td><em>S. perolens</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Lacticaseibacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lacticaseibacillus">39</a></td><td><em>Lc. casei</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Paralactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#paralactobacillus">1</a></td><td><em>Pa. selangorensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/00207713-50-1-19">Leisner et al. 2000</a></td></tr><tr><td class="lacto-genus"><em>Latilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#latilactobacillus">8</a></td><td><em>Lt. sakei</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Loigolactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#loigolactobacillus">9</a></td><td><em>Lo. coryniformis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Dellaglioa</em></td><td class="lacto-count"><a href="lactobacillaceae-species#dellaglioa">3</a></td><td><em>De. algida</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Liquorilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#liquorilactobacillus">13</a></td><td><em>Lq. mali</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Ligilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#ligilactobacillus">20</a></td><td><em>Lg. salivarius</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Pediococcus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#pediococcus">11</a></td><td><em>Pc. damnosus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth">Claussen 1903<span class="lacto-auth-note">(<a href="https://doi.org/10.1099/00207713-30-1-225">Approved Lists 1980</a>)</span></td></tr><tr><td class="lacto-genus"><em>Lactiplantibacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lactiplantibacillus">22</a></td><td><em>Lp. plantarum</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Fructilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#fructilactobacillus">11</a></td><td><em>Fl. fructivorans</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Acetilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#acetilactobacillus">1</a></td><td><em>Ac. jinshanensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Philodulcilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#philodulcilactobacillus">1</a></td><td><em>Ph. myokonensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1371/journal.pone.0286677">Kouya et al. 2023</a></td></tr><tr><td class="lacto-genus"><em>Nicoliella</em></td><td class="lacto-count"><a href="lactobacillaceae-species#nicoliella">2</a></td><td><em>N. spurrieriana</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.005806">Deshmukh and Oren 2023</a></td></tr><tr><td class="lacto-genus"><em>Apilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#apilactobacillus">14</a></td><td><em>Ap. kunkeei</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Lentilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lentilactobacillus">22</a></td><td><em>Ln. buchneri</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Secundilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#secundilactobacillus">16</a></td><td><em>Sc. malefermentans</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Levilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#levilactobacillus">32</a></td><td><em>Lv. brevis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Paucilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#paucilactobacillus">8</a></td><td><em>Pl. vaccinostercus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Limosilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#limosilactobacillus">45</a></td><td><em>Lm. fermentum</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Furfurilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#furfurilactobacillus">7</a></td><td><em>Fu. rossiae</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Periweissella</em></td><td class="lacto-count"><a href="lactobacillaceae-species#periweissella">5</a></td><td><em>Pw. ghanensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.005284">Bello et al. 2022</a></td></tr><tr><td class="lacto-genus"><em>Weissella</em></td><td class="lacto-count"><a href="lactobacillaceae-species#weissella">22</a></td><td><em>W. viridescens</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1111/j.1365-2672.1993.tb01600.x">Collins et al. 1994</a></td></tr><tr><td class="lacto-genus"><em>Oenococcus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#oenococcus">4</a></td><td><em>O. oeni</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/00207713-45-2-395">Dicks et al. 1995</a></td></tr><tr><td class="lacto-genus"><em>Eupransor</em></td><td class="lacto-count"><a href="lactobacillaceae-species#eupransor">1</a></td><td><em>E. demetentiae</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.006409">Botero et al. 2024</a></td></tr><tr><td class="lacto-genus"><em>Convivina</em></td><td class="lacto-count"><a href="lactobacillaceae-species#convivina">2</a></td><td><em>Cn. intestini</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1007/s10482-015-0429-z">Praet et al. 2015</a></td></tr><tr><td class="lacto-genus"><em>Fructobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#fructobacillus">13</a></td><td><em>Fr. fructosus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijs.0.65609-0">Endo and Okada 2008</a></td></tr><tr><td class="lacto-genus"><em>Leuconostoc</em></td><td class="lacto-count"><a href="lactobacillaceae-species#leuconostoc">23</a></td><td><em>Lu. mesenteroides</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth">van Tieghem 1878<span class="lacto-auth-note">(<a href="https://doi.org/10.1099/00207713-30-1-225">Approved Lists 1980</a>)</span></td></tr><tr><td class="lacto-genus"><em>Candidatus Gallilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#candidatus-gallilactobacillus">1</a></td><td><em>Ca. G. intestinavium</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-unassigned"></span>—<span class="lacto-sr">not assigned</span></td><td class="lacto-auth"><a href="https://doi.org/10.7717/peerj.10941">Gilroy et al. 2021</a></td></tr><tr><td class="lacto-genus"><em>Daquilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#daquilactobacillus">1</a></td><td><em>Da. linshuiensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.007157">Huang et al. 2026</a></td></tr></tbody></table></div>
<div class="lacto-table-wrap lacto-view-az"><table class="lacto-table"><thead><tr><th scope="col">Genus</th><th scope="col">No. of species<span class="lacto-th-hint"><span aria-hidden="true">👇</span> Click to see species info.</span></th><th scope="col">Type species</th><th scope="col">Fermentation</th><th scope="col">Proposed</th></tr></thead><tbody><tr><td class="lacto-genus"><em>Acetilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#acetilactobacillus">1</a></td><td><em>Ac. jinshanensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Agrilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#agrilactobacillus">3</a></td><td><em>Ag. composti</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Amylolactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#amylolactobacillus">2</a></td><td><em>Am. amylophilus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Apilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#apilactobacillus">14</a></td><td><em>Ap. kunkeei</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Bombilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#bombilactobacillus">6</a></td><td><em>Bo. mellifer</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Companilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#companilactobacillus">37</a></td><td><em>Co. alimentarius</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Convivina</em></td><td class="lacto-count"><a href="lactobacillaceae-species#convivina">2</a></td><td><em>Cn. intestini</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1007/s10482-015-0429-z">Praet et al. 2015</a></td></tr><tr><td class="lacto-genus"><em>Daquilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#daquilactobacillus">1</a></td><td><em>Da. linshuiensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.007157">Huang et al. 2026</a></td></tr><tr><td class="lacto-genus"><em>Dellaglioa</em></td><td class="lacto-count"><a href="lactobacillaceae-species#dellaglioa">3</a></td><td><em>De. algida</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Eupransor</em></td><td class="lacto-count"><a href="lactobacillaceae-species#eupransor">1</a></td><td><em>E. demetentiae</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.006409">Botero et al. 2024</a></td></tr><tr><td class="lacto-genus"><em>Fructilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#fructilactobacillus">11</a></td><td><em>Fl. fructivorans</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Fructobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#fructobacillus">13</a></td><td><em>Fr. fructosus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijs.0.65609-0">Endo and Okada 2008</a></td></tr><tr><td class="lacto-genus"><em>Furfurilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#furfurilactobacillus">7</a></td><td><em>Fu. rossiae</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Candidatus Gallilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#candidatus-gallilactobacillus">1</a></td><td><em>Ca. G. intestinavium</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-unassigned"></span>—<span class="lacto-sr">not assigned</span></td><td class="lacto-auth"><a href="https://doi.org/10.7717/peerj.10941">Gilroy et al. 2021</a></td></tr><tr><td class="lacto-genus"><em>Holzapfeliella</em></td><td class="lacto-count"><a href="lactobacillaceae-species#holzapfeliella">2</a></td><td><em>H. floricola</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.005688">Deshmukh and Oren 2023</a></td></tr><tr><td class="lacto-genus"><em>Lacticaseibacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lacticaseibacillus">39</a></td><td><em>Lc. casei</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Lactiplantibacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lactiplantibacillus">22</a></td><td><em>Lp. plantarum</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Lactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lactobacillus">56</a></td><td><em>L. delbrueckii</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth">Beijerinck 1901<span class="lacto-auth-note">(<a href="https://doi.org/10.1099/00207713-30-1-225">Approved Lists 1980</a>)</span></td></tr><tr><td class="lacto-genus"><em>Lapidilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lapidilactobacillus">9</a></td><td><em>Ld. concavus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Latilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#latilactobacillus">8</a></td><td><em>Lt. sakei</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Lentilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#lentilactobacillus">22</a></td><td><em>Ln. buchneri</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Leuconostoc</em></td><td class="lacto-count"><a href="lactobacillaceae-species#leuconostoc">23</a></td><td><em>Lu. mesenteroides</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth">van Tieghem 1878<span class="lacto-auth-note">(<a href="https://doi.org/10.1099/00207713-30-1-225">Approved Lists 1980</a>)</span></td></tr><tr><td class="lacto-genus"><em>Levilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#levilactobacillus">32</a></td><td><em>Lv. brevis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Ligilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#ligilactobacillus">20</a></td><td><em>Lg. salivarius</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Limosilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#limosilactobacillus">45</a></td><td><em>Lm. fermentum</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Liquorilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#liquorilactobacillus">13</a></td><td><em>Lq. mali</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Loigolactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#loigolactobacillus">9</a></td><td><em>Lo. coryniformis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Nicoliella</em></td><td class="lacto-count"><a href="lactobacillaceae-species#nicoliella">2</a></td><td><em>N. spurrieriana</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.005806">Deshmukh and Oren 2023</a></td></tr><tr><td class="lacto-genus"><em>Oenococcus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#oenococcus">4</a></td><td><em>O. oeni</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/00207713-45-2-395">Dicks et al. 1995</a></td></tr><tr><td class="lacto-genus"><em>Paralactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#paralactobacillus">1</a></td><td><em>Pa. selangorensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/00207713-50-1-19">Leisner et al. 2000</a></td></tr><tr><td class="lacto-genus"><em>Paucilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#paucilactobacillus">8</a></td><td><em>Pl. vaccinostercus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Pediococcus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#pediococcus">11</a></td><td><em>Pc. damnosus</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth">Claussen 1903<span class="lacto-auth-note">(<a href="https://doi.org/10.1099/00207713-30-1-225">Approved Lists 1980</a>)</span></td></tr><tr><td class="lacto-genus"><em>Periweissella</em></td><td class="lacto-count"><a href="lactobacillaceae-species#periweissella">5</a></td><td><em>Pw. ghanensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.005284">Bello et al. 2022</a></td></tr><tr><td class="lacto-genus"><em>Philodulcilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#philodulcilactobacillus">1</a></td><td><em>Ph. myokonensis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1371/journal.pone.0286677">Kouya et al. 2023</a></td></tr><tr><td class="lacto-genus"><em>Schleiferilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#schleiferilactobacillus">3</a></td><td><em>S. perolens</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Secundilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#secundilactobacillus">16</a></td><td><em>Sc. malefermentans</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1099/ijsem.0.004107">Zheng et al. 2020</a></td></tr><tr><td class="lacto-genus"><em>Weissella</em></td><td class="lacto-count"><a href="lactobacillaceae-species#weissella">22</a></td><td><em>W. viridescens</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-hetero"></span>Hetero</td><td class="lacto-auth"><a href="https://doi.org/10.1111/j.1365-2672.1993.tb01600.x">Collins et al. 1994</a></td></tr><tr><td class="lacto-genus"><em>Xylocopilactobacillus</em></td><td class="lacto-count"><a href="lactobacillaceae-species#xylocopilactobacillus">2</a></td><td><em>X. apis</em></td><td class="lacto-ferm"><span class="lacto-dot lacto-homo"></span>Homo</td><td class="lacto-auth"><a href="https://doi.org/10.1128/spectrum.00782-23">Kawasaki et al. 2024</a></td></tr></tbody></table></div>
<p class="lacto-caption">Type species carry the genus abbreviations from <a href="https://doi.org/10.3168/jdsc.2021-0183">Qiao et al. 2022</a>, which separate the twelve genera whose names begin with L. The number of species includes subspecies. Each proposing authority links to its paper; for the three genera validated by the Approved Lists of 1980, the link is on that note.</p>
</div>

<p class="lacto-source">Source file: <code>genus_20261110.csv</code>, request from
<a href="mailto:nanzhen.qiao@gmail.com"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7" /><rect x="2" y="4" width="20" height="16" rx="2" /></svg>nanzhen.qiao@gmail.com</a>.
The tree itself is built with
<a href="https://github.com/nanzhen102/core-genome-phylogeny">core-genome-phylogeny</a>.</p>

[🐝](#top)
