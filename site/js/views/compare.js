/*
 * Match & Compare (v0.4.0): evidence matrix, identity decisions, group check, proposals.
 *
 * - The matrix reports conflicts and missing values together (D2) and shows which records share
 *   a value ("Set 1", "Set 2"); system and verification dates are context (D3).
 * - Each active record gets a decision: an identity group, Keep separate, or Hold for verification.
 * - "Check proposed groups" applies the identity rules (rules/identity.js). Results are kept in
 *   the state store and shown again after navigation (D6); they are marked out of date when the
 *   decisions change.
 * - Only eligible groups can be proposed; an identical resubmission is refused and changes are
 *   recorded as revisions (D5). Deselected records keep their decisions but are ignored (G5).
 */
(function (A) {
  'use strict';
  A.registerModule('views/compare', ['util', 'data/records', 'data/attributes', 'data/case', 'state', 'rules/matching', 'rules/identity']);

  var $ = A.$;
  var esc = A.escapeHTML;
  var S = A.state;
  var attrs = A.data.attrs;
  var matching = A.rules.matching;
  var identity = A.rules.identity;

  var ROLE_LABEL = { identity: 'Identity evidence', supporting: 'Supporting evidence', context: 'Context' };
  var STATUS_CLASS = { eligible: 'is-eligible', blocked: 'is-blocked', verification: 'is-verification', single: 'is-single' };

  function recordById(id) {
    return A.data.records.find(function (r) { return r.id === id; });
  }

  function timeLabel(ms) {
    return new Date(ms).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }

  function decisionLabel(value) {
    if (!value) return 'Undecided';
    if (A.data.decisionOptions[value]) return A.data.decisionOptions[value];
    return 'Group ' + value;
  }

  function matrixHTML(arr) {
    var rows = attrs.map(function (pair) {
      var label = pair[0], key = pair[1];
      var a = matching.attributeAssessment(arr, key);
      var showSets = a.role !== 'context' && a.distinct > 1;
      return `<tr class="row-${a.role}"><th scope="row">${label}<div class="small role-tag">${ROLE_LABEL[a.role]}</div><div class="small state-label state-${a.state}">${esc(a.label)}</div></th>${arr.map(function (r) {
        var set = a.sets[r.id];
        var tag = showSets && set ? `<span class="valueset">Set ${set}</span>` : '';
        return `<td class="${matching.cellClass(r, key, a)}">${esc(r[key] || 'Missing')}${tag}</td>`;
      }).join('')}</tr>`;
    }).join('');
    return `<div class="tablewrap"><table class="matrix"><caption class="sr-only">Evidence for ${arr.length} selected records</caption><thead><tr><th scope="col">Attribute</th>${arr.map(function (r) {
      return `<th scope="col">${esc(r.id)}<div class="small">${esc(r.name)}</div></th>`;
    }).join('')}</tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  function decisionSelect(r) {
    var v = S.decisionOf(r.id);
    var opts = '<option value="">Undecided</option>' +
      A.data.groupLetters.map(function (g) { return `<option value="${g}" ${v === g ? 'selected' : ''}>Group ${g}</option>`; }).join('') +
      Object.keys(A.data.decisionOptions).map(function (k) { return `<option value="${k}" ${v === k ? 'selected' : ''}>${esc(A.data.decisionOptions[k])}</option>`; }).join('');
    return `<select aria-label="Identity decision for ${esc(r.id)}" data-group="${r.id}">${opts}</select>`;
  }

  function renderCompare() {
    var arr = S.activeRecords();
    if (arr.length < 2) {
      $('compare-content').innerHTML = '<div class="notice">Select at least two records. You can evaluate the entire dataset simultaneously.</div><button class="primary" data-action="showPage:work">Select records</button>';
      return;
    }
    $('compare-content').innerHTML = `<div class="notice">All ${arr.length} selected records are evaluated together. Records that share a value are marked with the same set number. Differences are not automatically identity conflicts, and grouping does not merge records.</div>${matrixHTML(arr)}<h2 style="margin-top:26px" id="decisions-heading">Identity decisions</h2><p class="muted">Decide for each record: put records you believe are the same legal entity in the same group, keep a distinct entity separate, or hold a record whose identity cannot be confirmed. Changes are reversible.</p><div class="tablewrap"><table class="decisions"><thead><tr><th scope="col">Record</th><th scope="col">Tax identifier</th><th scope="col">Legal name</th><th scope="col">Decision</th></tr></thead><tbody>${arr.map(function (r) {
      return `<tr><td>${esc(r.id)} · ${esc(r.name)}</td><td>${esc(r.tax || 'Missing')}</td><td>${esc(r.legal || 'Missing')}</td><td>${decisionSelect(r)}</td></tr>`;
    }).join('')}</tbody></table></div><div class="controls" style="margin-top:15px"><button class="primary" id="review-groups">Check proposed groups</button><button class="secondary" id="clear-groups">Clear groups</button></div><div id="governance-output" aria-live="polite"></div><div id="audit"></div>`;
    document.querySelectorAll('[data-group]').forEach(function (el) {
      el.addEventListener('change', function () {
        S.setDecision(el.dataset.group, el.value);
        renderResults();
        A.navigation.refresh();
      });
    });
    $('review-groups').addEventListener('click', validateGroups);
    $('clear-groups').addEventListener('click', function () {
      S.clearDecisions(arr.map(function (r) { return r.id; }));
      renderCompare();
      A.navigation.refresh();
      $('clear-groups').focus();
    });
    renderResults();
  }

  /** Runs the identity rules on the active decisions and stores the result. */
  function validateGroups() {
    var results = S.activeGroups().map(function (g) {
      return { letter: g.letter, members: g.members, verdict: identity.evaluateGroup(g.members.map(recordById)) };
    });
    S.saveCheck(results);
    renderResults();
    A.navigation.refresh();
  }

  function proposalControl(res) {
    if (!res.verdict.submittable) return '';
    var kind = S.proposalKind(res.letter, res.members);
    var latest = S.latestProposal(res.letter);
    if (kind === 'duplicate') {
      var where = Object.keys(S.proposals).find(function (g) {
        var l = S.latestProposal(g);
        return l && S.groupKey(l.members) === S.groupKey(res.members);
      });
      var rev = S.latestProposal(where).rev;
      return `<p class="proposal-state"><strong>Proposal submitted</strong> (Group ${where}, revision ${rev}). This exact group is already under review; change the group to submit a revision.</p><button class="secondary" disabled aria-disabled="true">Submitted</button>`;
    }
    var label = kind === 'revision' ? `Submit revision ${latest.rev + 1} for Group ${res.letter}` : `Submit merge proposal for Group ${res.letter}`;
    return `<button class="primary" data-propose="${res.letter}">${label}</button>`;
  }

  function renderResults() {
    var out = $('governance-output');
    if (!out) return;
    var arr = S.activeRecords();
    var check = S.check;
    var html = '<h2 style="margin-top:20px" id="check-heading" tabindex="-1">Governance identity check</h2>';
    if (!check) {
      html += '<p class="muted">Make a decision for each record, then select <strong>Check proposed groups</strong>.</p>';
    } else {
      var current = S.checkIsCurrent();
      if (!current) html += '<div class="notice stale-notice"><strong>Out of date.</strong> Your decisions changed after this check (' + timeLabel(check.at) + '). Check again before submitting. The earlier results are shown for reference.</div>';
      html += `<div class="${current ? '' : 'is-stale'}">`;
      if (!check.results.length) html += '<div class="notice">No identity groups were proposed in that check. Assign at least two records to the same group to propose a merge.</div>';
      check.results.forEach(function (res) {
        var v = res.verdict;
        html += `<section class="groupresult ${STATUS_CLASS[v.status]}" aria-labelledby="gr-${res.letter}"><strong id="gr-${res.letter}">Group ${res.letter} · ${res.members.length} record(s)</strong><p class="verdict">${esc(v.title)}</p><ul class="reasons">${v.reasons.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('')}${v.warnings.map(function (x) { return '<li class="warning">' + esc(x) + '</li>'; }).join('')}</ul><p class="small muted">${res.members.join(', ')}</p>${current ? proposalControl(res) : ''}</section>`;
      });
      var held = arr.filter(function (r) { return S.decisionOf(r.id) === 'hold'; }).map(function (r) { return r.id; });
      var separate = arr.filter(function (r) { return S.decisionOf(r.id) === 'separate'; }).map(function (r) { return r.id; });
      var undecided = S.undecidedActive();
      if (held.length) html += `<p class="decision-summary"><strong>Held for verification:</strong> ${held.join(', ')}. Not proposed for merge until identity evidence is provided.</p>`;
      if (separate.length) html += `<p class="decision-summary"><strong>Kept separate:</strong> ${separate.join(', ')}.</p>`;
      if (undecided.length) html += `<p class="decision-summary"><strong>Not yet decided:</strong> ${undecided.join(', ')}.</p>`;
      html += '</div>';
    }
    html += '<p class="small muted">This simulation records merge proposals only. No source data is changed, merged, or published. Additional evidence and approval are required.</p>';
    out.innerHTML = html;
    out.querySelectorAll('[data-propose]').forEach(function (b) {
      b.addEventListener('click', function () {
        var letter = b.dataset.propose;
        var res = S.check.results.find(function (x) { return x.letter === letter; });
        var rev = S.submitProposal(letter, res.members);
        renderResults();
        A.navigation.refresh();
        var msg = rev ? `Group ${letter} proposal ${rev.rev > 1 ? 'revision ' + rev.rev + ' ' : ''}logged for governance review. No merge has occurred.` : 'This group is already under review.';
        var live = $('audit-live');
        if (live) live.textContent = msg;
        var heading = $('gr-' + letter);
        if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus(); }
      });
    });
    renderHistory();
  }

  function renderHistory() {
    var audit = $('audit');
    if (!audit) return;
    var letters = Object.keys(S.proposals).sort();
    var total = letters.reduce(function (n, g) { return n + S.proposals[g].length; }, 0);
    var currentKeys = S.currentProposals().map(function (p) { return p.letter + ':' + p.rev; });
    var html = '<div id="audit-live" class="sr-only" aria-live="polite"></div>';
    if (total) {
      html += `<h3>Proposal history</h3><p class="small muted">${total} submission(s) this session. Earlier revisions are kept as a record of your reasoning.</p><ol class="history">`;
      letters.forEach(function (g) {
        S.proposals[g].forEach(function (p) {
          var isCurrent = currentKeys.indexOf(g + ':' + p.rev) !== -1;
          var latest = S.latestProposal(g).rev === p.rev;
          var status = isCurrent ? 'Current' : latest ? 'No longer matches your decisions' : 'Superseded by revision ' + (p.rev + 1);
          html += `<li><strong>Group ${g}, revision ${p.rev}</strong>: ${p.members.join(', ')} <span class="small muted">· submitted ${timeLabel(p.at)} · ${status}</span></li>`;
        });
      });
      html += '</ol>';
    }
    audit.innerHTML = html;
  }

  A.views.compare = { renderCompare: renderCompare, validateGroups: validateGroups, decisionLabel: decisionLabel };
})(window.Aperion);
