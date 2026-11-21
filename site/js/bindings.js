/*
 * Connects buttons to actions.
 *
 * v0.3.2 used inline onclick="..." attributes that called global functions. Those globals no
 * longer exist, so each such button now carries data-action="name" or data-action="name:argument",
 * and one click listener on the document runs the matching action below. The same functions
 * run with the same arguments, so behavior is unchanged. Disabled buttons do not fire clicks,
 * exactly as before.
 */
(function (A) {
  'use strict';
  A.registerModule('bindings', ['navigation', 'views/records', 'views/compare', 'views/golden', 'views/validation', 'views/debrief', 'views/nextbar', 'audio']);

  var actions = {
    showPage: function (page) { A.navigation.showPage(page); },
    advanceLearning: function () { A.navigation.advanceLearning(); },
    resetFilters: function () { A.views.records.resetFilters(); },
    closeDetails: function () { A.views.records.closeDetails(); },
    selectAllVisible: function () { A.views.records.selectAllVisible(); },
    selectAllRecords: function () { A.views.records.selectAllRecords(); },
    clearSelection: function () { A.views.records.clearSelection(); },
    toggleAudio: function (source) { A.audio.toggleAudio(source); },
    replayAudio: function (source) { A.audio.replayAudio(source); }
  };

  function onClick(event) {
    var el = event.target.closest ? event.target.closest('[data-action]') : null;
    if (!el) return;
    var spec = el.getAttribute('data-action');
    var sep = spec.indexOf(':');
    var name = sep === -1 ? spec : spec.slice(0, sep);
    var arg = sep === -1 ? undefined : spec.slice(sep + 1);
    if (!actions[name]) throw new Error('Aperion: unknown data-action "' + name + '"');
    actions[name](arg);
  }

  function init() {
    document.addEventListener('click', onClick);
  }

  A.bindings = { init: init, actions: actions };
})(window.Aperion);
