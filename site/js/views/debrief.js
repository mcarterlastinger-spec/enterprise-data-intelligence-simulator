/*
 * Debrief (v0.4.0, Step 5).
 *
 * Scores the snapshot taken when the learner finished the case (rules/scoring.js) and shows:
 * total and per-competency points, the performance level for each competency, every criterion
 * with decision-specific feedback, the learner's decisions and submission history, and how
 * scoring works. "Try the case again" starts a new attempt; earlier attempt results are listed.
 * After finishing, the activities stay viewable but read-only, so the scored work cannot change.
 */
(function (A) {
  'use strict';
  A.registerModule('views/debrief', ['util', 'data/case', 'state', 'rules/scoring']);

  var $ = A.$;
  var esc = A.escapeHTML;
  var S = A.state;
  var D = A.data;

  var LEVEL_CLASS = { 'Proficient': 'lvl-proficient', 'Developing': 'lvl-developing', 'Needs Practice': 'lvl-practice' };

  function timeLabel(ms) {
    return new Date(ms).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }

  function decisionText(v) {
    if (!v) return 'Undecided';
    return D.decisionOptions[v] || 'Group ' + v;
  }

  var lastResult = null;

  function result() {
    if (!S.finished) return null;
    if (!lastResult || lastResult.at !== S.finished.at) {
      lastResult = A.rules.scoring.score(S.finished);
      lastResult.at = S.finished.at;
      if (!S.attempts.some(function (a) { return a.at === S.finished.at; })) S.recordAttemptResult(lastResult);
    }
    return lastResult;
  }

  function competencyHTML(c, i) {
    var id = 'comp-' + i;
    return `<section class="competency" aria-labelledby="${id}"><div class="comp-head"><h3 id="${id}">${esc(c.name)}</h3><p class="comp-score"><strong>${c.earned} of ${c.max} points</strong> <span class="level ${LEVEL_CLASS[c.level]}">${esc(c.level)}</span></p></div><p class="muted">${esc(c.summary)}</p><ul class="criteria">${c.criteria.map(function (k) {
      return `<li class="${k.met ? 'met' : 'unmet'}"><p class="crit-title"><span class="mark" aria-hidden="true">${k.met ? '✓' : '✗'}</span><span class="sr-only">${k.met ? 'Met: ' : 'Not met: '}</span>${esc(k.text)} <span class="small muted">(${k.earned}/${k.max})</span></p><p class="crit-feedback">${esc(k.feedback)}</p></li>`;
    }).join('')}</ul></section>`;
  }

  function decisionsHTML(snap) {
    return `<div class="tablewrap"><table class="decision-review"><caption class="sr-only">Your identity decisions</caption><thead><tr><th scope="col">Record</th><th scope="col">Your decision</th><th scope="col">Expected</th></tr></thead><tbody>${D.records.map(function (r) {
      var expected = D.answerKey.separate.indexOf(r.id) !== -1 ? 'Keep separate' : D.answerKey.hold.indexOf(r.id) !== -1 ? 'Hold for verification'
        : 'Merge with ' + D.answerKey.groups.find(function (g) { return g.records.indexOf(r.id) !== -1; }).records.filter(function (x) { return x !== r.id; }).join(', ');
      var mine = snap.active.indexOf(r.id) === -1 ? 'Not compared' : decisionText(snap.decisions[r.id]);
      var group = snap.proposals.find(function (p) { return p.members.indexOf(r.id) !== -1; });
      if (group) mine = 'Proposed with ' + group.members.filter(function (x) { return x !== r.id; }).join(', ');
      return `<tr><th scope="row">${esc(r.id)} <span class="small muted">${esc(r.name)}</span></th><td>${esc(mine)}</td><td>${esc(expected)}</td></tr>`;
    }).join('')}</tbody></table></div>`;
  }

  function historyHTML() {
    var items = [];
    Object.keys(S.proposals).sort().forEach(function (g) {
      S.proposals[g].forEach(function (p) { items.push({ at: p.at, text: 'Merge proposal Group ' + g + ', revision ' + p.rev + ': ' + p.members.join(', ') }); });
    });
    Object.keys(S.validation).forEach(function (k) {
      S.validation[k].submissions.forEach(function (s) { items.push({ at: s.at, text: 'Submitted for Governance Review: ' + k.replace('|', ' + ') + ', revision ' + s.rev }); });
    });
    Object.keys(S.golden).forEach(function (k) {
      S.golden[k].revisions.forEach(function (r) { items.push({ at: r.at, text: 'Golden record saved: ' + k.replace('|', ' + ') + ', revision ' + r.rev }); });
    });
    items.sort(function (a, b) { return a.at - b.at; });
    if (!items.length) return '<p class="muted">No submissions were recorded.</p>';
    return `<ol class="history">${items.map(function (x) { return `<li><span class="small muted">${timeLabel(x.at)}</span> ${esc(x.text)}</li>`; }).join('')}</ol>`;
  }

  function scoringHelpHTML(res) {
    return `<details class="scoring-help"><summary>How scoring works</summary><p>Each point comes from one decision you made, so no decision is counted twice. Points are awarded only for these criteria:</p><ul>${res.competencies.map(function (c) {
      return `<li><strong>${esc(c.name)} (${c.max} points):</strong> ${esc(c.criteria.map(function (k) { return k.text; }).filter(function (t, i, arr) { return c.name !== 'Data Reconciliation' || i < 6; }).join('; '))}${c.name === 'Data Reconciliation' ? '; the same six attributes for each golden record. Each point needs the expected value and evidence that supports it.' : '.'}</li>`;
    }).join('')}</ul><p>Performance levels for each competency: <strong>Proficient</strong> at 85% or more of its points, <strong>Developing</strong> at 50% or more, <strong>Needs Practice</strong> below 50%. Your score reflects the work you submitted when you finished the case.</p></details>`;
  }

  function renderDebrief() {
    var el = $('debrief-content');
    var res = result();
    if (!res) {
      el.innerHTML = '<div class="notice">The debrief opens when you finish the case on the Validation activity.</div>';
      return;
    }
    var snap = S.finished;
    var attempts = S.attempts.length > 1 ? `<p class="small muted">Earlier attempts this session: ${S.attempts.slice(0, -1).map(function (a) { return 'attempt ' + a.attempt + ': ' + a.earned + ' of ' + a.max + ' (' + a.level + ')'; }).join('; ')}.</p>` : '';
    el.innerHTML = `<div class="debrief-summary"><h2 id="debrief-h" tabindex="-1">Your result: ${res.earned} of ${res.max} points</h2><p>Attempt ${snap.attempt}, finished at ${timeLabel(snap.at)}. Overall level: <span class="level ${LEVEL_CLASS[res.level]}">${esc(res.level)}</span></p><ul class="comp-overview">${res.competencies.map(function (c) {
      return `<li><span>${esc(c.name)}</span><strong>${c.earned} / ${c.max}</strong><span class="level ${LEVEL_CLASS[c.level]}">${esc(c.level)}</span></li>`;
    }).join('')}</ul>${attempts}${scoringHelpHTML(res)}</div>${res.competencies.map(competencyHTML).join('')}<section class="competency" aria-labelledby="dr-h"><h3 id="dr-h">Your decisions</h3>${decisionsHTML(snap)}</section><section class="competency" aria-labelledby="hist-h"><h3 id="hist-h">Submission history</h3>${historyHTML()}</section><div class="controls"><button class="secondary" data-action="showPage:compare">Review your work (read-only)</button><button class="primary" id="retry-case">Try the case again</button></div>`;
    $('retry-case').addEventListener('click', function () {
      S.resetForRetry();
      A.views.records.resetFilters();
      A.navigation.showPage('brief');
      $('page-title').focus && $('page-title').focus();
    });
  }

  A.views.debrief = { renderDebrief: renderDebrief, result: result };
})(window.Aperion);
