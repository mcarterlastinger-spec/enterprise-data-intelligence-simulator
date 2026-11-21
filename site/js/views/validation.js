/*
 * Validation (v0.4.0, Step 4).
 *
 * For each current merge proposal the learner states which evidence establishes identity, writes
 * a governance rationale, and submits the proposal and its golden record for governance review.
 * An automatic checklist must pass first; evidence-consistency checks are advisory.
 * A submission is shown as "Submitted for Governance Review": it is never an approval, and no
 * merge happens. If the proposal, golden record, evidence, or rationale changes afterwards, the
 * submission is out of date and must be revalidated and resubmitted (a new revision; history kept).
 * The learner also explains why each separate or held record was not proposed, chooses a
 * follow-up for held records, and then finishes the case for the debrief.
 * Edits update only the affected parts of the page, so keyboard focus is never lost.
 */
(function (A) {
  'use strict';
  A.registerModule('views/validation', ['util', 'data/case', 'state', 'rules/identity', 'rules/golden', 'views/golden']);

  var $ = A.$;
  var esc = A.escapeHTML;
  var S = A.state;
  var D = A.data;

  function recordById(id) {
    return D.records.find(function (r) { return r.id === id; });
  }
  function slug(s) {
    return String(s).replace(/[^A-Za-z0-9]+/g, '-');
  }
  function timeLabel(ms) {
    return new Date(ms).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }
  function words(s) {
    return String(s || '').trim().split(/\s+/).filter(Boolean).length;
  }

  /** Required checks; all must pass before submission. */
  function checklist(p) {
    var golden = S.latestGolden(p.key);
    var draft = S.validationDraft(p.key);
    var verdict = A.rules.identity.evaluateGroup(p.members.map(recordById));
    var n = words(draft.rationale);
    return [
      { id: 'identity', text: 'Identity check passed: tax identifier and legal name match in every record', ok: verdict.status === 'eligible' },
      { id: 'golden-saved', text: 'Golden record saved for proposal revision ' + p.rev, ok: !!golden && golden.proposalRev === p.rev && A.views.golden.incomplete(p.key).length === 0 },
      { id: 'golden-current', text: 'No unsaved golden-record changes', ok: !!golden && !S.goldenHasUnsavedChanges(p.key) },
      { id: 'basis', text: 'Identity evidence selected', ok: draft.basis.length > 0 },
      { id: 'rationale', text: 'Governance rationale written (' + n + ' of at least ' + D.rationaleMinWords + ' words)', ok: n >= D.rationaleMinWords }
    ];
  }

  /** Advisory evidence-consistency findings for the saved golden record. */
  function advisories(p) {
    var golden = S.latestGolden(p.key);
    if (!golden) return [];
    var out = [];
    D.goldenAttributes.forEach(function (a) {
      var msg = A.rules.golden.reasonConsistency(golden.choices[a.key], p.members, a.field);
      if (msg) out.push(a.label + ': ' + msg);
    });
    return out;
  }

  function checklistHTML(p) {
    var items = checklist(p);
    var adv = advisories(p);
    return `<h4>Automatic governance checklist</h4><ul class="checklist">${items.map(function (c) {
      return `<li class="${c.ok ? 'pass' : 'fail'}"><span class="mark" aria-hidden="true">${c.ok ? '✓' : '✗'}</span><span class="sr-only">${c.ok ? 'Passed: ' : 'Not yet met: '}</span>${esc(c.text)}</li>`;
    }).join('')}</ul>${adv.length ? `<h4>Evidence consistency (advisory)</h4><ul class="advisories">${adv.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('')}</ul><p class="small muted">Advisory findings do not block submission. Review them in the Golden Record activity if you disagree.</p>` : '<p class="small muted">Evidence consistency: no issues found between the evidence you cited and the sources you chose.</p>'}`;
  }

  function statusHTML(p) {
    var state = S.submissionState(p);
    var latest = S.latestSubmission(p.key);
    if (state === 'none') return '<strong>Not yet submitted.</strong>';
    if (state === 'current') return `<strong class="submitted">Submitted for Governance Review</strong> (revision ${latest.rev}, ${timeLabel(latest.at)}). Awaiting the governance decision. No merge or approval has occurred.`;
    return `<strong class="changed">Changed since submission.</strong> Revision ${latest.rev} no longer matches your proposal, golden record, evidence, or rationale. Revalidate and resubmit.`;
  }

  function buttonState(p) {
    var state = S.submissionState(p);
    var ready = checklist(p).every(function (c) { return c.ok; });
    var latest = S.latestSubmission(p.key);
    if (state === 'current') return { label: 'Submitted for Governance Review', disabled: true };
    return { label: state === 'changed' ? `Resubmit Group ${p.letter} (revision ${latest.rev + 1})` : `Submit Group ${p.letter} for governance review`, disabled: !ready };
  }

  function historyHTML(p) {
    var subs = (S.validation[p.key] || { submissions: [] }).submissions;
    if (!subs.length) return '';
    return `<details class="sub-history"><summary>Submission history (${subs.length})</summary><ol>${subs.map(function (s) {
      return `<li>Revision ${s.rev} · ${timeLabel(s.at)} · proposal revision ${s.proposalRev}, golden record revision ${s.goldenRev}</li>`;
    }).join('')}</ol></details>`;
  }

  function proposalHTML(p) {
    var id = slug(p.key);
    var draft = S.validationDraft(p.key);
    var b = buttonState(p);
    var basis = D.identityBasisOptions.map(function (o) {
      return `<div class="choice"><input type="checkbox" id="vb-${id}-${o.id}" value="${o.id}" data-basis ${draft.basis.indexOf(o.id) !== -1 ? 'checked' : ''}><label for="vb-${id}-${o.id}">${esc(o.label)}</label></div>`;
    }).join('');
    return `<section class="validation-group" data-key="${p.key}" aria-labelledby="vh-${id}"><h3 id="vh-${id}" tabindex="-1">Group ${p.letter} · ${p.members.join(' + ')} <span class="small muted">(proposal revision ${p.rev})</span></h3><fieldset class="basis"><legend>Which evidence establishes that these records are the same entity? <span class="small muted">Select all that apply.</span></legend>${basis}</fieldset><div class="reason-row"><label for="vr-${id}">Governance rationale for Group ${p.letter}</label><p class="small muted" id="vr-${id}-hint">At least ${D.rationaleMinWords} words. Explain why these records are one entity and name the evidence a reviewer should check.</p><textarea id="vr-${id}" rows="4" data-rationale aria-describedby="vr-${id}-hint">${esc(draft.rationale)}</textarea></div><div class="vcheck" id="vc-${id}">${checklistHTML(p)}</div><p class="vstatus" id="vs-${id}" aria-live="polite">${statusHTML(p)}</p><div class="controls"><button class="primary" data-submit-review="${p.key}" ${b.disabled ? 'disabled' : ''}>${esc(b.label)}</button></div><div id="vhist-${id}">${historyHTML(p)}</div></section>`;
  }

  function notProposedHTML() {
    var recs = S.activeRecords().filter(function (r) { var d = S.decisionOf(r.id); return d === 'separate' || d === 'hold'; });
    if (!recs.length) return '';
    return `<section class="validation-group" aria-labelledby="np-h"><h3 id="np-h">Records not proposed for merge</h3><p class="muted">Explain the evidence behind each record you kept separate or held.</p>${recs.map(function (r) {
      var held = S.decisionOf(r.id) === 'hold';
      var reasons = '<option value="">Choose the reason…</option>' + D.notProposedReasons.map(function (o) {
        return `<option value="${o.id}" ${S.notProposed[r.id] === o.id ? 'selected' : ''}>${esc(o.label)}</option>`;
      }).join('');
      var follow = held ? `<div class="reason-row"><label for="nf-${r.id}">Follow-up for ${esc(r.id)}</label><select id="nf-${r.id}" data-followup="${r.id}"><option value="">Choose the follow-up…</option>${D.heldFollowUps.map(function (o) {
        return `<option value="${o.id}" ${S.heldFollowUp[r.id] === o.id ? 'selected' : ''}>${esc(o.label)}</option>`;
      }).join('')}</select></div>` : '';
      return `<div class="np-record"><p><strong>${esc(r.id)}</strong> · ${esc(r.name)} · your decision: <strong>${held ? 'Hold for verification' : 'Keep separate'}</strong></p><div class="reason-row"><label for="np-${r.id}">Why was ${esc(r.id)} not proposed?</label><select id="np-${r.id}" data-np="${r.id}">${reasons}</select></div>${follow}</div>`;
    }).join('')}</section>`;
  }

  /** What still blocks finishing the case. */
  function finishBlockers() {
    var out = [];
    var props = S.currentProposals();
    if (!props.length) out.push('Submit at least one eligible merge proposal on Match & Compare.');
    props.forEach(function (p) {
      var st = S.submissionState(p);
      if (st === 'none') out.push('Submit Group ' + p.letter + ' for governance review.');
      if (st === 'changed') out.push('Resubmit Group ' + p.letter + ': it changed after submission.');
    });
    S.activeRecords().forEach(function (r) {
      var d = S.decisionOf(r.id);
      if ((d === 'separate' || d === 'hold') && !S.notProposed[r.id]) out.push('Explain why ' + r.id + ' was not proposed.');
      if (d === 'hold' && !S.heldFollowUp[r.id]) out.push('Choose a follow-up for ' + r.id + '.');
    });
    var undecided = S.undecidedActive();
    if (undecided.length) out.push('Decide ' + undecided.join(', ') + ' on Match & Compare.');
    return out;
  }

  function finishHTML() {
    var blockers = finishBlockers();
    return `<h3 id="finish-h">Finish the case</h3><p class="muted">When every proposal is submitted for governance review, finish the case to see your debrief. Your submissions are then locked and scored; you can try the case again afterwards.</p>${blockers.length ? `<ul class="finish-blockers" id="finish-why">${blockers.map(function (b) { return '<li>' + esc(b) + '</li>'; }).join('')}</ul>` : '<p id="finish-why" class="submitted">Ready to finish.</p>'}<div class="controls"><button class="primary" id="finish-case" aria-describedby="finish-why" ${blockers.length ? 'disabled' : ''}>Finish case and view debrief</button></div>`;
  }

  function refreshProposal(p) {
    var id = slug(p.key);
    $('vc-' + id).innerHTML = checklistHTML(p);
    $('vs-' + id).innerHTML = statusHTML(p);
    var btn = document.querySelector('[data-submit-review="' + p.key + '"]');
    var b = buttonState(p);
    btn.textContent = b.label;
    btn.disabled = b.disabled;
    $('vhist-' + id).innerHTML = historyHTML(p);
    refreshFinish();
  }

  function refreshFinish() {
    var f = $('finish-panel');
    if (!f) return;
    var hadFocus = document.activeElement && document.activeElement.id === 'finish-case';
    f.innerHTML = finishHTML();
    $('finish-case').addEventListener('click', finish);
    if (hadFocus) $('finish-case').focus();
    A.navigation.refresh();
  }

  function finish() {
    if (finishBlockers().length || S.finished) return;
    S.finish();
    A.navigation.showPage('debrief');
  }

  function renderValidation() {
    var el = $('validation-content');
    var props = S.currentProposals();
    if (!props.length) {
      el.innerHTML = '<div class="notice">No current merge proposals. Submit at least one eligible group on Match &amp; Compare, then build its golden record.</div><button class="primary" data-action="showPage:compare">Go to Match &amp; Compare</button>';
      return;
    }
    el.innerHTML = props.map(proposalHTML).join('') + notProposedHTML() + '<section class="validation-group" id="finish-panel">' + finishHTML() + '</section>';
    props.forEach(function (p) {
      var sec = el.querySelector('.validation-group[data-key="' + p.key + '"]');
      sec.addEventListener('change', function (e) {
        if (e.target.hasAttribute('data-basis')) {
          var basis = Array.from(sec.querySelectorAll('[data-basis]:checked')).map(function (x) { return x.value; });
          S.setValidationDraft(p.key, { basis: basis });
          refreshProposal(p);
        }
      });
      sec.querySelector('[data-rationale]').addEventListener('input', function (e) {
        S.validationDraft(p.key).rationale = e.target.value;
        refreshProposal(p);
      });
      sec.querySelector('[data-rationale]').addEventListener('change', function (e) {
        S.setValidationDraft(p.key, { rationale: e.target.value });
      });
      sec.querySelector('[data-submit-review]').addEventListener('click', function () {
        if (!checklist(p).every(function (c) { return c.ok; })) return;
        var sub = S.submitForReview(p, checklist(p).map(function (c) { return { id: c.id, ok: c.ok }; }));
        refreshProposal(p);
        if (sub) $('vh-' + slug(p.key)).focus();
      });
    });
    el.querySelectorAll('[data-np]').forEach(function (s) {
      s.addEventListener('change', function () { S.setNotProposed(s.dataset.np, s.value); refreshFinish(); });
    });
    el.querySelectorAll('[data-followup]').forEach(function (s) {
      s.addEventListener('change', function () { S.setHeldFollowUp(s.dataset.followup, s.value); refreshFinish(); });
    });
    $('finish-case').addEventListener('click', finish);
  }

  /** Next action on this page, for the Next Step bar. */
  function progress() {
    var props = S.currentProposals();
    if (!props.length) return { state: 'none' };
    for (var i = 0; i < props.length; i++) {
      var p = props[i];
      var golden = S.latestGolden(p.key);
      if (!golden || golden.proposalRev !== p.rev || S.goldenHasUnsavedChanges(p.key)) return { state: 'golden', proposal: p };
      if (S.submissionState(p) !== 'current') {
        var missing = checklist(p).filter(function (c) { return !c.ok; });
        return { state: missing.length ? 'incomplete' : 'ready', proposal: p, missing: missing };
      }
    }
    var blockers = finishBlockers();
    return { state: blockers.length ? 'explain' : 'finish', blockers: blockers };
  }

  function focusFor(prog) {
    var p = prog.proposal;
    var target;
    if (prog.state === 'incomplete') {
      var first = prog.missing[0].id;
      var sec = document.querySelector('.validation-group[data-key="' + p.key + '"]');
      target = first === 'basis' ? sec.querySelector('[data-basis]') : first === 'rationale' ? sec.querySelector('[data-rationale]') : sec.querySelector('h3');
    } else if (prog.state === 'ready') {
      target = document.querySelector('[data-submit-review="' + p.key + '"]');
    } else if (prog.state === 'explain') {
      target = Array.from(document.querySelectorAll('[data-np],[data-followup]')).find(function (s) { return !s.value; }) || $('finish-h');
    } else {
      target = $('finish-case');
    }
    if (target) { target.scrollIntoView({ block: 'center' }); target.focus(); }
  }

  A.views.validation = { renderValidation: renderValidation, progress: progress, focusFor: focusFor, checklist: checklist, finishBlockers: finishBlockers, finish: finish };
})(window.Aperion);
