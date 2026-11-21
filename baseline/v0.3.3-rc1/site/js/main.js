/*
 * Startup. Runs once all files have loaded, in the same order as the end of v0.3.2's script:
 *   1. audio setup (voice list after 200 ms),
 *   2. search and filter listeners,
 *   3. first render of the record table,
 *   4. open Mission Briefing.
 */
(function (A) {
  'use strict';
  A.registerModule('main', ['util', 'data/records', 'data/attributes', 'state', 'rules/matching',
    'rules/governance', 'audio', 'navigation', 'views/records', 'views/compare', 'bindings']);

  var $ = A.$;

  A.audio.init();
  A.bindings.init();
  $('search').addEventListener('input', A.views.records.render);
  $('system').addEventListener('change', A.views.records.render);
  $('status').addEventListener('change', A.views.records.render);
  A.views.records.render();
  A.navigation.showPage('brief');
})(window.Aperion);
