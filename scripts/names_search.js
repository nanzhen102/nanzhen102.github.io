/* Search box of the Names page. Inlined into content/lactobacillaceae-names.md by build_lactobacillaceae_names.py.
   Listeners sit on the document, so they keep working after Quartz's in-site navigation replaces the page body. */
(function () {
  if (window.__lactoNames) return;
  window.__lactoNames = true;
  var data = null;

  function load() {
    var el = document.getElementById("name-data");
    if (!el) return null;
    if (!data || data.el !== el) {
      var d = JSON.parse(el.textContent);
      d.el = el;
      d.words = d.names.map(function (n) { return words(n[0]); });
      data = d;
    }
    return data;
  }
  function words(s) {
    return s.toLowerCase().replace(/[().,]/g, " ").split(/\s+/).filter(Boolean);
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  // A name with its Latin parts in italics; "subsp." and the like stay upright.
  function nameNode(name) {
    var span = el("span", "lacto-hit-name");
    name.split(" ").forEach(function (w, i) {
      if (i) span.appendChild(document.createTextNode(" "));
      if (/^(subsp|ssp|spp|sp)\.?$/.test(w) || /^[(\[]/.test(w)) span.appendChild(document.createTextNode(w));
      else span.appendChild(el("em", "", w));
    });
    return span;
  }

  // Every token must start some word of the name ("L. casei" finds Lactobacillus casei). On ties the former names come
  // first, because a visitor is usually looking for what an old name is called now.
  function search(d, q, cut) {
    var tokens = words(q).map(function (t) { return cut ? t.slice(0, cut) : t; });
    if (!tokens.length || q.trim().length < 2) return [];
    var whole = tokens.join(" "), hits = [];
    d.names.forEach(function (n, i) {
      var w = d.words[i];
      for (var t = 0; t < tokens.length; t++) {
        if (!w.some(function (x) { return x.indexOf(tokens[t]) === 0; })) return;
      }
      var joined = w.join(" ");
      hits.push({ i: i, rank: joined === whole ? 0 : joined.indexOf(whole) === 0 ? 1 : 2, current: n[2] === "current name" ? 1 : 0, len: w.length, name: n[0] });
    });
    hits.sort(function (a, b) {
      return a.rank - b.rank || a.current - b.current || a.len - b.len || (a.name < b.name ? -1 : 1);
    });
    return hits;
  }

  function render() {
    var d = load(), input = document.getElementById("name-search"), out = document.getElementById("name-results");
    if (!d || !input || !out) return;
    var q = input.value, hits = search(d, q), LIMIT = 6, close = false;
    if (!hits.length && q.trim().length >= 4) {
      hits = search(d, q, 5);  // a misspelling: match on the first five letters of each word
      close = hits.length > 0;
    }
    out.textContent = "";
    if (q.trim().length < 2) {
      out.appendChild(el("p", "lacto-find-hint", "Type at least two letters."));
      return;
    }
    if (!hits.length) {
      out.appendChild(el("p", "lacto-find-none", "No name like “" + q.trim() + "”. Try a shorter part of it, such as the species epithet."));
      return;
    }
    if (close) out.appendChild(el("p", "lacto-find-more", "No exact match. Closest names:"));
    var list = el("ul", "lacto-hits");
    hits.slice(0, LIMIT).forEach(function (h) {
      var n = d.names[h.i], c = d.cur[n[1]], li = el("li", "lacto-hit"), line = el("p", "lacto-hit-line");
      var same = n[0] === c[0];
      line.appendChild(nameNode(n[0]));
      if (!same) {
        line.appendChild(el("span", "lacto-hit-arrow", " → "));
        var now = nameNode(c[0]);
        now.className += " lacto-hit-now";
        line.appendChild(now);
      }
      if (n[2] !== "old name" && n[2] !== "synonym") line.appendChild(el("span", "lacto-hit-kind", n[2]));
      li.appendChild(line);
      li.appendChild(el("p", "lacto-hit-what", c[1].charAt(0).toUpperCase() + c[1].slice(1)));
      if (c[2]) {
        var links = el("p", "lacto-hit-links");
        var b = el("a", "", "Type strain, genome and publication");
        b.href = "lactobacillaceae-species#" + c[2];
        links.appendChild(b);
        li.appendChild(links);
      }
      list.appendChild(li);
    });
    out.appendChild(list);
    if (hits.length > LIMIT) out.appendChild(el("p", "lacto-find-more", hits.length - LIMIT + " more. Type more of the name to narrow it down."));
  }

  document.addEventListener("input", function (e) {
    if (e.target && e.target.id === "name-search") render();
  });
  document.addEventListener("click", function (e) {
    var b = e.target && e.target.closest ? e.target.closest("[data-name-q]") : null;
    if (!b) return;
    var input = document.getElementById("name-search");
    if (!input) return;
    input.value = b.getAttribute("data-name-q");
    render();
    input.focus();
  });
  // Arriving from the overview's box: lactobacillaceae-names?q=Lactobacillus casei
  var asked = new URLSearchParams(window.location.search).get("q"), box = document.getElementById("name-search");
  if (asked && box) {
    box.value = asked;
    render();
  }
})();
