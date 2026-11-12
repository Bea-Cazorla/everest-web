/* EVEREST · shared behaviour: mobile menu, dropdowns, page index, list filters, gallery lightbox. */
(function () {
  'use strict';
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };

  /* mobile menu */
  var btn = $('#menu-btn'), nav = $('#site-nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Cerrar el menú' : 'Abrir el menú');
    });
  }

  /* dropdowns */
  var toggles = $$('.menu > li > button');
  function closeAll(except) {
    toggles.forEach(function (t) {
      if (t === except) return;
      t.setAttribute('aria-expanded', 'false');
      var s = document.getElementById(t.getAttribute('aria-controls'));
      if (s) s.classList.remove('open');
    });
  }
  toggles.forEach(function (t) {
    t.addEventListener('click', function (e) {
      e.stopPropagation();
      var s = document.getElementById(t.getAttribute('aria-controls'));
      var open = t.getAttribute('aria-expanded') !== 'true';
      closeAll(t);
      t.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (s) s.classList.toggle('open', open);
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest || !e.target.closest('.menu')) closeAll(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var openBtn = toggles.filter(function (t) { return t.getAttribute('aria-expanded') === 'true'; })[0];
    closeAll();
    if (openBtn) openBtn.focus();
  });

  /* "En esta página" index */
  var links = $$('.toc a');
  if (links.length && 'IntersectionObserver' in window) {
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove('active'); });
        var a = byId[en.target.id]; if (a) a.classList.add('active');
      });
    }, { rootMargin: '-90px 0px -65% 0px' });
    Object.keys(byId).forEach(function (id) { var s = document.getElementById(id); if (s) obs.observe(s); });
  }

  /* filters (team, news): buttons carry data-filter, items carry data-group */
  $$('[data-filter-list]').forEach(function (bar) {
    var list = document.getElementById(bar.getAttribute('data-filter-list'));
    if (!list) return;
    var buttons = $$('button', bar);
    buttons.forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-filter');
        buttons.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        $$('[data-group]', list).forEach(function (it) {
          it.hidden = !(f === 'all' || (' ' + it.getAttribute('data-group') + ' ').indexOf(' ' + f + ' ') > -1);
        });
      });
    });
  });

  /* gallery lightbox */
  var box = $('#lightbox');
  if (box && typeof box.showModal === 'function') {
    var img = $('img', box), cap = $('p', box);
    $$('.gallery button[data-full]').forEach(function (b) {
      b.addEventListener('click', function () {
        img.src = b.getAttribute('data-full');
        img.alt = $('img', b).alt;
        cap.innerHTML = b.parentNode.querySelector('figcaption').innerHTML;
        box.showModal();
      });
    });
    $('.close', box).addEventListener('click', function () { box.close(); });
    box.addEventListener('click', function (e) { if (e.target === box) box.close(); });
  }
})();
