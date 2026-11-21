/*
 * Compact Next Step bar controls for constrained viewports (v0.4.0, decision P2-5).
 *
 * On narrow or short screens (including Edge at 200% zoom), css/compact-nav.css shrinks the
 * persistent Next Step bar to about 60 px and shows two extra controls:
 *   Menu  opens a visible panel of the activity navigation, directly above the bar, with the same
 *         items, availability, and current-page marking as the sidebar. Keyboard: Enter/Space
 *         opens it and focus moves to the first available item; Escape closes it and returns focus.
 *   Why?  shows the Next Step explanation. The explanation is always available to screen readers
 *         through aria-describedby on the Next Step button, even when it is visually collapsed.
 * On larger screens these controls are hidden and the bar looks as before.
 */
(function (A) {
  'use strict';
  A.registerModule('views/nextbar', ['util']);

  var $ = A.$;
  var esc = A.escapeHTML;

  function menuOpen() {
    return $('nsb-menu').getAttribute('aria-expanded') === 'true';
  }

  function buildMenu() {
    var panel = $('nsb-menu-panel');
    var items = Array.from(document.querySelectorAll('aside nav .nav'));
    panel.innerHTML = '<ul>' + items.map(function (b) {
      var current = b.getAttribute('aria-current') === 'page';
      return '<li><button type="button" class="nsb-item' + (current ? ' active' : '') + '" data-action="' + esc(b.getAttribute('data-action') || '') + '"' +
        (b.disabled ? ' disabled' : '') + (current ? ' aria-current="page"' : '') + (b.title ? ' title="' + esc(b.title) + '"' : '') + '>' +
        esc(b.textContent.replace(/\s+/g, ' ').trim()) + (b.disabled && b.title ? '<span class="sr-only"> (' + esc(b.title) + ')</span>' : '') + '</button></li>';
    }).join('') + '</ul>';
  }

  function openMenu() {
    closeWhy();
    buildMenu();
    $('nsb-menu-panel').hidden = false;
    $('nsb-menu').setAttribute('aria-expanded', 'true');
    var first = $('nsb-menu-panel').querySelector('button:not([disabled])');
    if (first) first.focus();
  }

  function closeMenu(returnFocus) {
    if (!menuOpen()) return;
    $('nsb-menu-panel').hidden = true;
    $('nsb-menu').setAttribute('aria-expanded', 'false');
    if (returnFocus) $('nsb-menu').focus();
  }

  function closeWhy() {
    $('next-step-bar').classList.remove('why-open');
    $('nsb-why').setAttribute('aria-expanded', 'false');
  }

  function toggleWhy() {
    closeMenu(false);
    var open = !$('next-step-bar').classList.contains('why-open');
    $('next-step-bar').classList.toggle('why-open', open);
    $('nsb-why').setAttribute('aria-expanded', String(open));
  }

  function init() {
    $('nsb-menu').addEventListener('click', function () { if (menuOpen()) closeMenu(true); else openMenu(); });
    $('nsb-why').addEventListener('click', toggleWhy);
    $('nsb-menu-panel').addEventListener('click', function (e) {
      if (e.target.closest('.nsb-item')) closeMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      if (menuOpen()) { closeMenu(true); e.preventDefault(); }
      else if ($('next-step-bar').classList.contains('why-open')) { closeWhy(); $('nsb-why').focus(); }
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('#next-step-bar')) { closeMenu(false); closeWhy(); }
    });
  }

  /** Keep an open menu in step with page changes. */
  function refresh() {
    if (menuOpen()) buildMenu();
    closeWhy();
  }

  A.views.nextbar = { init: init, refresh: refresh, openMenu: openMenu, closeMenu: closeMenu };
})(window.Aperion);
