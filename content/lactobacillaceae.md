---
title: Lactobacillaceae
date: 2026-11-11
---


<a class="lacto-ask-fab" href="lactobacillaceae#ask" data-router-ignore data-endpoint="https://lactorador-api.onrender.com/api/ask" aria-expanded="false"><svg class="lacto-ask-icon" aria-hidden="true" viewBox="0 0 24 24" width="18" height="18"><rect x="0.5" y="9" width="11" height="6" rx="3" fill="currentColor"/><rect x="12.5" y="9" width="11" height="6" rx="3" fill="currentColor" opacity="0.7"/></svg><span>Ask <em>Lactobacillaceae</em>AI</span></a>
<script>// Copied from 11_agent/lactorador/web/lactorador_chat.js by copy_to_site.py; edit it there.
/* LactobacillaceaeAI chat for the Lactobacillaceae pages (Quartz site). No libraries.
   The "Ask LactobacillaceaeAI" button (a.lacto-ask-fab[data-endpoint]) on every Lactobacillaceae page
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
  // One question per kind of thing the database answers, each checked to answer well (2026-11-23):
  // names, original description, metabolism (gene data + the paper), lifestyle, taxonomic history.
  // Example buttons show taxon names in italics ("Lactobacillus casei"); the question sent stays plain text.
  function italicNames(h) {
    return h.replace(/\b([A-Z][a-z]*(?:bacillus|coccus|ella|nostoc))( (?!called|first|used|proposed)[a-z]{3,})?\b/g,
      function (m) { return "<em>" + m + "</em>"; });
  }
  var EXAMPLES = [
    "What is Lactobacillus casei called now?",
    "In which paper was Lactobacillus agrestimuris first described?",
    "Is the Embden–Meyerhof pathway used by homo- or heterofermentative lactobacilli?",
    "Which species are domesticated, and why?",
    "How many genera have been proposed since 2020?",
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
    // A bare link: punctuation right after it (". , ; : ! ?" or a closing quote) ends the sentence, not the link.
    h = h.replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, function (m, pre, url) {
      var tail = url.match(/[.,;:!?'"]+$/);
      tail = tail ? tail[0] : "";
      url = url.slice(0, url.length - tail.length);
      return pre + '<a href="' + url + '" target="_blank" rel="noopener">' + url + "</a>" + tail;
    });
    h = h.replace(/\*\*((?:[^*]|\*[^*\n]+\*)+?)\*\*/g, "<strong>$1</strong>"); // bold may hold *italics*
    h = h.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");
    // _underscore_ italics too: the model sometimes writes species names this way, and they showed as
    // literal underscores (2026-11-22). Only between non-word characters, so snake_case is untouched.
    h = h.replace(/(^|[\s(>])_([^_\n]+?)_(?=[\s.,;:!?)<]|$)/g, "$1<em>$2</em>");
    h = h.replace(/(^|\n)_\(([^)]*)\)_/g, '$1<span class="lr-small">($2)</span>');
    return h.split(/\n{2,}/).map(function (p) {
      if (/^\s*[-•] /.test(p)) {
        return "<ul>" + p.split(/\n/).map(function (l) { return "<li>" + l.replace(/^\s*[-•] /, "") + "</li>"; }).join("") + "</ul>";
      }
      return "<p>" + p.replace(/\n/g, "<br>") + "</p>";
    }).join("");
  }
  function welcome() {
    return '<div class="lr-msg lr-bot"><p><strong>I am <em>Lactobacillaceae</em>AI.</strong> I answer from a curated, expert-checked <em>Lactobacillaceae</em> database, with a source for every claim.</p><p>Ask me about ' +
      "<em>Lactobacillaceae</em> names, type strains and genomes, metabolism, lifestyles and where species were isolated. Try:</p><p class=\"lr-examples\">" +
      EXAMPLES.map(function (q) { return '<button type="button" data-lr-q="' + esc(q) + '">' + italicNames(esc(q)) + "</button>"; }).join(" ") +
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
          // 422: the server's input check (question 2-500 characters; a lone emoji counts as 1)
          : r.status === 422 ? "Please ask a question in words (up to 500 characters), " +
            "e.g. “What is Lactobacillus casei called now?”"
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
        wait.setAttribute("data-lr-id", r.id || ""); // the answer's id, sent back with a rating so the two join
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
        answer: h[i].content, mode: msg.getAttribute("data-lr-mode") || "",
        id: msg.getAttribute("data-lr-id") || "" }),
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
    p.setAttribute("aria-label", "Ask LactobacillaceaeAI");
    p.innerHTML =
      '<div class="lr-grip" title="Drag to resize; double-click to reset" aria-hidden="true"></div>' +
      '<div class="lr-head"><strong><svg class="lr-logo" aria-hidden="true" viewBox="0 0 24 24" width="18" height="18"><rect x="0.5" y="9" width="11" height="6" rx="3" fill="currentColor"/><rect x="12.5" y="9" width="11" height="6" rx="3" fill="currentColor" opacity="0.7"/></svg><em>Lactobacillaceae</em>AI</strong>' +
      '<button type="button" class="lr-icon" data-lr-clear title="New chat" aria-label="New chat">↺</button>' +
      '<button type="button" class="lr-icon" data-lr-close title="Close" aria-label="Close">✕</button></div>' +
      '<div class="lr-log" aria-live="polite">' + welcome() + "</div>" +
      '<form><label class="lacto-sr" for="lr-panel-q">Your question</label>' +
      '<input id="lr-panel-q" class="lr-input" type="text" maxlength="500" placeholder="Ask a question…" autocomplete="off" />' +
      '<button class="lr-send" type="submit" aria-label="Send">↑</button></form>' +
      // Update the month when a new release of the lists goes on the site.
      '<div class="lr-foot">Answers come from this site\'s curated lists (updated November 2026) and the papers ' +
      'they cite. Lifestyle is assigned per species (Qiao 2025), with Duar et al. 2017 alongside.</div>';
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

<div class="lacto-tree"><picture><source media="(prefers-reduced-motion: reduce)" srcset="lactobacillaceae-banner-20261110.png"><img src="lactobacillaceae-banner-20261110.gif" width="960" height="440" alt="Animation: the 38 genera of Lactobacillaceae appear in the order they were described, each at its place on the family's phylogenetic tree. Beside it: Lactobacillaceae: type strains, fermentation type and lifestyle, updated by Nanzhen Qiao and Michael Gänzle." decoding="async"></picture></div>

<section class="lacto-sec">
<p class="lacto-hero">38</p>
<p class="lacto-hero-label">genera currently placed in <em>Lactobacillaceae</em> family, updated on November 10, 2026.</p>
<div class="lacto-split" role="list" aria-label="Fermentation type across 38 genera: Homofermentative 19, Heterofermentative 18, Unassigned 1.">
<div class="lacto-split-part lacto-homo" style="flex: 19 1 0" tabindex="0" role="listitem" aria-label="Homofermentative: 19 genera, 50 percent"><span class="lacto-split-value">19</span><span class="lacto-tip" aria-hidden="true"><strong>Homofermentative</strong><span>19 genera &middot; 50%</span></span></div>
<div class="lacto-split-part lacto-hetero" style="flex: 18 1 0" tabindex="0" role="listitem" aria-label="Heterofermentative: 18 genera, 47 percent"><span class="lacto-split-value">18</span><span class="lacto-tip" aria-hidden="true"><strong>Heterofermentative</strong><span>18 genera &middot; 47%</span></span></div>
<div class="lacto-split-part lacto-unassigned" style="flex: 1 1 0" tabindex="0" role="listitem" aria-label="Unassigned: 1 genera, 3 percent"><span class="lacto-split-value lacto-split-value--tight">1</span><span class="lacto-tip" aria-hidden="true"><strong>Unassigned</strong><span>1 genera &middot; 3%</span></span></div>
</div>
<div class="lacto-legend">
<span class="lacto-key"><span class="lacto-dot lacto-homo"></span>Homofermentative</span>
<span class="lacto-key"><span class="lacto-dot lacto-hetero"></span>Heterofermentative</span>
<span class="lacto-key"><span class="lacto-dot lacto-unassigned"></span>Unassigned</span>
</div>
<a class="lacto-go" href="lactobacillaceae-genera">View all 38 genera <span aria-hidden="true">👉</span></a>
</section>

<section class="lacto-sec">
<p class="lacto-hero">477</p>
<p class="lacto-hero-label">species and subspecies currently placed in <em>Lactobacillaceae</em> family (442 species, 35 subspecies), updated on November 11, 2026.</p>
<div class="lacto-split" role="list" aria-label="Fermentation type across 477 species and subspecies: Homofermentative 247, Heterofermentative 229, Not yet assessed 1.">
<div class="lacto-split-part lacto-homo" style="flex: 247 1 0" tabindex="0" role="listitem" aria-label="Homofermentative: 247 species and subspecies, 52 percent"><span class="lacto-split-value">247</span><span class="lacto-tip" aria-hidden="true"><strong>Homofermentative</strong><span>247 species and subspecies &middot; 52%</span></span></div>
<div class="lacto-split-part lacto-hetero" style="flex: 229 1 0" tabindex="0" role="listitem" aria-label="Heterofermentative: 229 species and subspecies, 48 percent"><span class="lacto-split-value">229</span><span class="lacto-tip" aria-hidden="true"><strong>Heterofermentative</strong><span>229 species and subspecies &middot; 48%</span></span></div>
<div class="lacto-split-part lacto-unassigned" style="flex: 1 1 0" tabindex="0" role="listitem" aria-label="Not yet assessed: 1 species and subspecies, 0 percent"><span class="lacto-split-value lacto-split-value--tight">1</span><span class="lacto-tip" aria-hidden="true"><strong>Not yet assessed</strong><span>1 species and subspecies &middot; 0%</span></span></div>
</div>
<div class="lacto-legend">
<span class="lacto-key"><span class="lacto-dot lacto-homo"></span>Homofermentative</span>
<span class="lacto-key"><span class="lacto-dot lacto-hetero"></span>Heterofermentative</span>
<span class="lacto-key"><span class="lacto-dot lacto-unassigned"></span>Not yet assessed</span>
</div>
<a class="lacto-go" href="lactobacillaceae-species">View all 477 species and subspecies <span aria-hidden="true">👉</span></a>
</section>

<section class="lacto-sec">
<p class="lacto-hero">289</p>
<p class="lacto-hero-label">old names of lactobacilli and the name each one has now (281 are old <em>Lactobacillus</em> names), updated on November 23, 2026.</p>
<div class="lacto-rename" role="table" aria-label="What happened to the old names">
<div class="lacto-rename-row" role="row"><strong role="cell">241</strong><span role="cell">got a new genus name; the species name stayed</span><span class="lacto-rename-eg" role="cell">e.g. <em>Lactobacillus casei</em> <span class="lacto-rename-arrow" aria-hidden="true">→</span> <em>Lacticaseibacillus casei</em></span></div>
<div class="lacto-rename-row" role="row"><strong role="cell">28</strong><span role="cell">got a new genus name and a different species or subspecies name</span><span class="lacto-rename-eg" role="cell">e.g. <em>Lactobacillus cellobiosus</em> <span class="lacto-rename-arrow" aria-hidden="true">→</span> <em>Limosilactobacillus fermentum</em></span></div>
<div class="lacto-rename-row" role="row"><strong role="cell">12</strong><span role="cell">stayed in the same genus under another name</span><span class="lacto-rename-eg" role="cell">e.g. <em>Lactobacillus bulgaricus</em> <span class="lacto-rename-arrow" aria-hidden="true">→</span> <em>Lactobacillus delbrueckii</em> subsp. <em>bulgaricus</em></span></div>
<div class="lacto-rename-row" role="row"><strong role="cell">6</strong><span role="cell">are no longer in <em>Lactobacillaceae</em></span><span class="lacto-rename-eg" role="cell">e.g. <em>Lactobacillus xylosus</em> <span class="lacto-rename-arrow" aria-hidden="true">→</span> <em>Lactococcus lactis</em></span></div>
<div class="lacto-rename-row" role="row"><strong role="cell">2</strong><span role="cell">have no valid name today</span><span class="lacto-rename-eg" role="cell">e.g. <em>Lactobacillus rogosae</em></span></div>
</div>
<p class="lacto-breakdown-note">45 species and subspecies that were <em>Lactobacillus</em> before 2020 still are.</p>
<form class="lacto-sec-find" action="lactobacillaceae-names" method="get" role="search">
<input type="search" name="q" placeholder="Enter an old species name" aria-label="Old species name" autocomplete="off" autocapitalize="off" spellcheck="false" required />
<button type="submit">Find the new name</button>
</form>
<a class="lacto-go" href="lactobacillaceae-names" data-router-ignore>View all 289 old names <span aria-hidden="true">👉</span></a>
</section>

For detailed homofermentative and heterofermentative fermentation, check [Gänzle 2015](https://doi.org/10.1016/j.cofs.2015.03.001) and [Qiao & Gänzle 2026](https://doi.org/10.1016/j.fm.2025.104945). For detailed lifestyle updates, check [Qiao 2025](https://doi.org/10.7939/83003) (PhD thesis, Ch. 6), with [Duar et al. 2017](https://doi.org/10.1093/femsre/fux030) for the original categories, [Nanzhen Qiao](https://www.linkedin.com/in/nanzhen/) and [Michael Gänzle](https://scholar.google.com/citations?user=Zc29kvEAAAAJ&hl=en).

If these lists help your work, please cite our work. For questions or corrections, connect with [Nanzhen Qiao on LinkedIn](https://www.linkedin.com/in/nanzhen/).

[🐝](#top)
