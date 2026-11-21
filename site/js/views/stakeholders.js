/*
 * Contextual stakeholders (v0.4.0, D8, decision P2-4).
 * The full gallery appears on Mission Briefing only. Each activity shows one relevant
 * stakeholder's guidance as accessible text (no audio for Priya, Daniel, or Marcus, so no
 * mismatched voices). Portrait images are taken from the gallery so they also work in the
 * standalone build, where images are embedded.
 */
(function (A) {
  'use strict';
  A.registerModule('views/stakeholders', ['util', 'data/case']);

  var $ = A.$;
  var esc = A.escapeHTML;

  function portraitSrc(name) {
    var img = document.querySelector('#cast img[alt^="' + name + '"]');
    return img ? img.getAttribute('src') : '';
  }

  function show(page) {
    var cast = $('cast');
    var box = $('stakeholder-prompt');
    if (cast) cast.classList.toggle('hidden', page !== 'brief');
    var p = A.data.stakeholderPrompts[page];
    if (!box) return;
    if (!p || page === 'brief') {
      box.classList.add('hidden');
      box.innerHTML = '';
      return;
    }
    box.innerHTML = `<img src="${portraitSrc(p.name)}" alt="" width="48" height="48"><div><p class="sp-name"><strong>${esc(p.name)}</strong> <span class="small muted">${esc(p.role)}</span></p><p class="sp-text">“${esc(p.text)}”</p></div>`;
    box.setAttribute('aria-label', 'Guidance from ' + p.name + ', ' + p.role);
    box.classList.remove('hidden');
  }

  A.views.stakeholders = { show: show };
})(window.Aperion);
