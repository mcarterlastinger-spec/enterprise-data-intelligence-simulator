/* Page switching and the persistent Next Step bar (unchanged from v0.3.2). */
(function (A) {
  'use strict';
  A.registerModule('navigation', ['util', 'state', 'audio']);

  var $ = A.$;
  var S = A.state;

  var PAGE_TITLES = { work: 'Customer Record Workspace', brief: 'Mission Briefing', compare: 'Match & Compare' };

  function showPage(page) {
    var audioState = A.audio.state();
    if (audioState === 'playing' || audioState === 'paused') A.audio.stopAudio();
    ['work', 'brief', 'compare'].forEach(function (p) {
      $('page-' + p).classList.toggle('hidden', p !== page);
      $('nav-' + p).classList.toggle('active', p === page);
    });
    $('page-title').textContent = PAGE_TITLES[page];
    if (page === 'compare') A.views.compare.renderCompare();
    updateNextStep(page);
    window.scrollTo(0, 0);
  }

  function updateNextStep(page) {
    S.setActivePage(page);
    var configs = {
      brief: ['Ready to investigate?', 'You can read the transcript or listen to Maya. Audio completion is not required.', 'Next Step: Explore Customer Records →'],
      work: ['Ready to compare?', 'Select two or more records to investigate their identity evidence together.', 'Next Step: Compare Selected Records →'],
      compare: ['Review or revise your investigation', 'Return to the record inventory to inspect evidence and adjust your selection.', 'Next Step: Return to Customer Records →']
    };
    var cfg = configs[page] || configs.brief;
    $('next-step-heading').textContent = cfg[0];
    $('next-step-description').textContent = cfg[1];
    $('next-step-button').textContent = cfg[2];
    var isWork = page === 'work';
    var ready = S.selected.size >= 2;
    $('next-step-button').disabled = isWork && !ready;
    if (isWork && !ready) {
      $('next-step-description').textContent = 'Select at least two records to compare (' + S.selected.size + ' selected).';
    }
  }

  function advanceLearning() {
    var page = S.activeLearningPage;
    if (page === 'brief') showPage('work');
    else if (page === 'work' && S.selected.size >= 2) showPage('compare');
    else if (page === 'compare') showPage('work');
  }

  A.navigation = { showPage: showPage, updateNextStep: updateNextStep, advanceLearning: advanceLearning };
})(window.Aperion);
