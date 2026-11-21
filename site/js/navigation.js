/*
 * Page switching and the persistent, progress-aware Next Step bar (v0.4.0).
 *
 * Next Step always names the learner's actual next action, worked out from the state store,
 * not just from the current page. When the action is on the same page (decide a record, check
 * groups, submit a proposal, complete an attribute), the button moves keyboard focus there.
 * When the next action is not available yet, the button is disabled and the description,
 * linked with aria-describedby, says why.
 */
(function (A) {
  'use strict';
  A.registerModule('navigation', ['util', 'state', 'audio']);

  var $ = A.$;
  var S = A.state;

  var PAGES = ['work', 'brief', 'compare', 'golden', 'validation', 'debrief'];
  var PAGE_TITLES = { work: 'Customer Record Workspace', brief: 'Mission Briefing', compare: 'Match & Compare', golden: 'Golden Record', validation: 'Validation', debrief: 'Debrief' };
  var ACTIVITY_CONTENT = { work: 'page-work', compare: 'compare-content', golden: 'golden-content', validation: 'validation-content' };

  function showPage(page) {
    var audioState = A.audio.state();
    if (audioState === 'playing' || audioState === 'paused') A.audio.stopAudio();
    PAGES.forEach(function (p) {
      $('page-' + p).classList.toggle('hidden', p !== page);
      var nav = $('nav-' + p);
      nav.classList.toggle('active', p === page);
      if (p === page) nav.setAttribute('aria-current', 'page'); else nav.removeAttribute('aria-current');
    });
    $('page-title').textContent = PAGE_TITLES[page];
    S.markVisited(page);
    if (page === 'compare') A.views.compare.renderCompare();
    if (page === 'golden') A.views.golden.renderGolden();
    if (page === 'validation') A.views.validation.renderValidation();
    if (page === 'debrief') A.views.debrief.renderDebrief();
    if (page === 'work') A.views.records.render();
    lockIfFinished(page);
    if (A.views.stakeholders) A.views.stakeholders.show(page);
    updateNextStep(page);
    window.scrollTo(0, 0);
  }

  /** After the case is finished, activities stay viewable but cannot be changed (scored work). */
  function lockIfFinished(page) {
    document.querySelectorAll('.locked-notice').forEach(function (n) { n.remove(); });
    if (!S.finished || !ACTIVITY_CONTENT[page]) return;
    var root = $(ACTIVITY_CONTENT[page]);
    root.querySelectorAll('input, select, textarea, button:not([data-action^="showPage"]):not([data-open]):not(.audio-toggle):not(.audio-replay)').forEach(function (c) {
      if (page === 'work' && !c.closest('#rows') && !c.matches('[data-action^="select"],[data-action="clearSelection"]')) return;
      c.disabled = true;
    });
    var note = document.createElement('div');
    note.className = 'notice locked-notice';
    note.setAttribute('role', 'note');
    note.innerHTML = '<strong>Case finished (attempt ' + S.finished.attempt + ').</strong> Your work is locked for scoring and shown read-only. To make changes, select <strong>Try the case again</strong> on the Debrief.';
    var host = page === 'work' ? $('page-work') : root;
    host.insertBefore(note, host.firstChild);
  }

  function focusEl(el) {
    if (!el) return;
    el.scrollIntoView({ block: 'center' });
    el.focus();
  }

  /** Works out the learner's next action for a page. */
  function nextStep(page) {
    var n = S.selected.size;
    var compareLabel = 'Compare selected records (' + n + ')';
    if (page === 'brief') {
      return { heading: 'Ready to investigate?', description: 'You can read the transcript or listen to Maya. Audio completion is not required.', label: 'Next Step: Explore Customer Records →', run: function () { showPage('work'); } };
    }
    if (page === 'work') {
      if (n < 2) return { heading: 'Ready to compare?', description: 'Select at least two records to compare (' + n + ' selected).', label: 'Next Step: ' + compareLabel + ' →', disabled: true };
      return { heading: 'Ready to compare?', description: 'Compare all ' + n + ' selected records together to investigate their identity evidence.', label: 'Next Step: ' + compareLabel + ' →', run: function () { showPage('compare'); } };
    }
    if (page === 'compare') {
      if (n < 2) return { heading: 'Select records to compare', description: 'Return to Customer Records and select at least two records.', label: 'Next Step: Return to Customer Records →', run: function () { showPage('work'); } };
      var undecided = S.undecidedActive();
      if (undecided.length) {
        return { heading: 'Decide each record', description: undecided.length + ' of ' + n + ' selected records still need a decision: an identity group, Keep separate, or Hold for verification.', label: 'Next Step: Go to the next undecided record', run: function () { focusEl(document.querySelector('select[data-group="' + undecided[0] + '"]')); } };
      }
      if (!S.checkIsCurrent()) {
        return { heading: 'Check your proposed groups', description: 'Run the governance identity check on your current decisions.', label: 'Next Step: Check proposed groups', run: function () { A.views.compare.validateGroups(); focusEl($('check-heading')); } };
      }
      var pending = S.check.results.filter(function (r) { return r.verdict.submittable && S.proposalKind(r.letter, r.members) !== 'duplicate'; });
      if (pending.length) {
        return { heading: 'Submit eligible proposals', description: 'Group ' + pending[0].letter + ' is eligible. Review the check result, then submit its merge proposal.', label: 'Next Step: Go to Group ' + pending[0].letter + '’s proposal', run: function () { focusEl(document.querySelector('[data-propose="' + pending[0].letter + '"]')); } };
      }
      if (!S.currentProposals().length) {
        return { heading: 'Revise your decisions', description: 'No group is eligible yet. Use the check results to revise your decisions, then check again.', label: 'Next Step: Review the check results', run: function () { focusEl($('check-heading')); } };
      }
      return { heading: 'Build golden records', description: 'Create a golden record for each of your ' + S.currentProposals().length + ' proposed group(s).', label: 'Next Step: Build golden records →', run: function () { showPage('golden'); } };
    }
    if (page === 'golden') {
      var prog = A.views.golden.progress();
      if (prog.state === 'none') return { heading: 'No proposals yet', description: 'Submit at least one eligible merge proposal on Match & Compare.', label: 'Next Step: Return to Match & Compare →', run: function () { showPage('compare'); } };
      if (prog.state === 'incomplete') return { heading: 'Complete the golden record', description: 'Group ' + prog.proposal.letter + ': ' + prog.left + ' of ' + A.data.goldenAttributes.length + ' attributes still need a value and evidence.', label: 'Next Step: Go to the next incomplete attribute', run: function () { A.views.golden.focusFirstIncomplete(prog.proposal.key); } };
      if (prog.state === 'unsaved') return { heading: 'Save the golden record', description: 'Group ' + prog.proposal.letter + ' is complete but not saved.', label: 'Next Step: Go to Save for Group ' + prog.proposal.letter, run: function () { A.views.golden.focusSave(prog.proposal.key); } };
      return { heading: 'Golden records saved', description: 'Submit each proposal and its golden record for governance review.', label: 'Next Step: Continue to Validation →', run: function () { showPage('validation'); } };
    }
    if (page === 'validation') {
      var v = A.views.validation.progress();
      if (v.state === 'none') return { heading: 'No proposals yet', description: 'Submit at least one eligible merge proposal on Match & Compare.', label: 'Next Step: Return to Match & Compare →', run: function () { showPage('compare'); } };
      if (v.state === 'golden') return { heading: 'Golden record needed', description: 'Save the golden record for Group ' + v.proposal.letter + ' before submitting it for review.', label: 'Next Step: Go to the Golden Record →', run: function () { showPage('golden'); } };
      if (v.state === 'incomplete') return { heading: 'Complete the governance checklist', description: 'Group ' + v.proposal.letter + ' still needs: ' + v.missing.map(function (c) { return c.text.replace(/ \(.*\)$/, '').toLowerCase(); }).join('; ') + '.', label: 'Next Step: Complete the checklist for Group ' + v.proposal.letter, run: function () { A.views.validation.focusFor(v); } };
      if (v.state === 'ready') return { heading: 'Ready to submit', description: 'Group ' + v.proposal.letter + ' passes the checklist. Submit it for governance review.', label: 'Next Step: Go to Submit for Group ' + v.proposal.letter, run: function () { A.views.validation.focusFor(v); } };
      if (v.state === 'explain') return { heading: 'Finish your governance notes', description: v.blockers[0], label: 'Next Step: Go to the next unanswered item', run: function () { A.views.validation.focusFor(v); } };
      return { heading: 'Ready to finish', description: 'Every proposal is submitted for governance review. Finish the case to see your debrief.', label: 'Next Step: Finish case and view debrief', run: function () { A.views.validation.finish(); } };
    }
    if (page === 'debrief') {
      if (!S.finished) return { heading: 'Debrief not available yet', description: 'Finish the case on the Validation activity first.', label: 'Next Step: Go to Validation →', run: function () { showPage('validation'); } };
      return { heading: 'Case complete', description: 'Review the feedback above, or try the case again as a new attempt.', label: 'Next Step: Try the case again', run: function () { var b = $('retry-case'); if (b) b.click(); } };
    }
    return nextStep('brief');
  }

  var currentRun = null;

  function updateNextStep(page) {
    S.setActivePage(page);
    var step = S.finished && page !== 'debrief'
      ? { heading: 'Case finished', description: 'Your work is locked for scoring. Your debrief is ready.', label: 'Next Step: View your debrief →', run: function () { showPage('debrief'); } }
      : nextStep(page);
    $('next-step-heading').textContent = step.heading;
    $('next-step-description').textContent = step.description;
    $('next-step-button').textContent = step.label;
    $('next-step-button').disabled = !!step.disabled;
    currentRun = step.run || null;
    syncCompareButton();
    updateNavAvailability();
    if (A.views.nextbar) A.views.nextbar.refresh();
  }

  /** Both comparison buttons share wording, count, enabled state, and action. */
  function syncCompareButton() {
    var b = $('compare-btn');
    if (!b) return;
    var n = S.selected.size;
    b.textContent = 'Compare selected records (' + n + ')';
    b.disabled = n < 2;
  }

  function updateNavAvailability() {
    var available = S.currentProposals().length > 0 || !!S.finished;
    [['nav-golden', available, 'Submit an eligible merge proposal first'],
     ['nav-validation', available, 'Submit an eligible merge proposal first'],
     ['nav-debrief', !!S.finished, 'Finish the case on Validation first']].forEach(function (x) {
      var b = $(x[0]);
      if (!b) return;
      b.disabled = !x[1];
      if (x[1]) b.removeAttribute('title'); else b.title = x[2];
    });
  }

  function refresh() {
    updateNextStep(S.activeLearningPage);
  }

  function advanceLearning() {
    if (currentRun) currentRun();
  }

  A.navigation = { showPage: showPage, updateNextStep: updateNextStep, advanceLearning: advanceLearning, refresh: refresh, nextStep: nextStep };
})(window.Aperion);
