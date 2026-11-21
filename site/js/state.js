/*
 * Learner progress model (v0.4.0).
 *
 * Everything the learner decides is kept here, so decisions and feedback survive navigation
 * (fixes D6). State lasts for the browser session; reloading the page starts the case again.
 *
 *   selected        Set of active (selected) record IDs. Filters change visibility, not selection (A2).
 *   current         The record last opened in the details panel.
 *   decisions       Record ID -> 'A'..'F' (identity group), 'separate', 'hold', or '' (undecided).
 *                   Kept for deselected records (G5), but only ACTIVE records are grouped, checked,
 *                   proposed, or scored.
 *   check           The last "Check proposed groups" result and the decisions it was based on.
 *                   Shown again after navigation; marked out of date when decisions change.
 *   proposals       Group letter -> revisions [{ rev, members, at }]. An identical resubmission is
 *                   refused (fixes D5); a changed membership becomes a new revision.
 *   golden          Group key ('ID|ID') -> { draft, revisions } for golden records.
 *   validation      Group key -> { draft: { basis, rationale }, submissions: [...] }. A submission is
 *                   "Submitted for Governance Review" - never an approval or a merge. It is current
 *                   only while the proposal revision, golden-record revision, evidence basis, and
 *                   rationale are unchanged; any change requires revalidation and a new revision.
 *   notProposed     Record ID -> reason it was not proposed (separate and held records).
 *   heldFollowUp    Record ID -> follow-up action for a held record.
 *   finished        Set when the learner finishes the case; activities become read-only and the
 *                   debrief scores this snapshot. "Try again" starts a new attempt.
 *   attempts        Results of finished attempts in this session.
 *   events          Timestamped log of every learner decision (used by the debrief).
 */
(function (A) {
  'use strict';
  A.registerModule('state', ['namespace']);

  var S = {
    selected: new Set(),
    current: null,
    decisions: {},
    check: null,
    proposals: {},
    golden: {},
    validation: {},
    notProposed: {},
    heldFollowUp: {},
    finished: null,
    attempts: [],
    activeLearningPage: 'brief',
    visited: {},
    events: []
  };

  function record(type, detail) {
    S.events.push({ type: type, detail: detail, at: Date.now() });
  }

  function sortIds(ids) {
    return ids.slice().sort();
  }

  S.groupKey = function (ids) {
    return sortIds(ids).join('|');
  };

  // ---- selection --------------------------------------------------------------------------
  S.select = function (id) {
    if (!S.selected.has(id)) { S.selected.add(id); record('select', { id: id }); }
  };
  S.deselect = function (id) {
    if (S.selected.has(id)) { S.selected.delete(id); record('deselect', { id: id }); }
  };
  S.clearSelection = function () {
    S.selected.clear();
    record('clear-selection', {});
  };
  S.setCurrent = function (rec) {
    S.current = rec;
    record('open-record', { id: rec ? rec.id : null });
  };
  S.markVisited = function (page) {
    S.visited[page] = true;
  };

  /** Active records in dataset order. */
  S.activeRecords = function () {
    return A.data.records.filter(function (r) { return S.selected.has(r.id); });
  };

  // ---- identity decisions -----------------------------------------------------------------
  S.setDecision = function (id, value) {
    if ((S.decisions[id] || '') === value) return;
    S.decisions[id] = value;
    record('decide', { id: id, value: value });
  };

  /** Clears decisions for the given (active) records only; inactive records keep theirs (B2). */
  S.clearDecisions = function (ids) {
    ids.forEach(function (id) { delete S.decisions[id]; });
    record('clear-groups', { ids: ids.slice() });
  };

  S.decisionOf = function (id) {
    return S.decisions[id] || '';
  };

  /** Identity groups formed by ACTIVE records: [{ letter, members: [ids] }] in letter order. */
  S.activeGroups = function () {
    var active = S.activeRecords();
    return A.data.groupLetters.map(function (g) {
      return { letter: g, members: active.filter(function (r) { return S.decisions[r.id] === g; }).map(function (r) { return r.id; }) };
    }).filter(function (x) { return x.members.length; });
  };

  /** A fingerprint of the active decisions, used to tell whether a check is out of date. */
  S.decisionSignature = function () {
    return S.activeRecords().map(function (r) { return r.id + '=' + (S.decisions[r.id] || ''); }).join(';');
  };

  S.undecidedActive = function () {
    return S.activeRecords().filter(function (r) { return !S.decisions[r.id]; }).map(function (r) { return r.id; });
  };

  // ---- group check ------------------------------------------------------------------------
  S.saveCheck = function (results) {
    S.check = { signature: S.decisionSignature(), results: results, at: Date.now() };
    record('check-groups', { results: results.map(function (x) { return { letter: x.letter, members: x.members, status: x.verdict.status }; }) });
  };

  S.checkIsCurrent = function () {
    return !!S.check && S.check.signature === S.decisionSignature();
  };

  // ---- proposals --------------------------------------------------------------------------
  S.latestProposal = function (letter) {
    var revs = S.proposals[letter];
    return revs && revs.length ? revs[revs.length - 1] : null;
  };

  /** Returns 'new', 'revision', 'duplicate' for submitting these members under this letter. */
  S.proposalKind = function (letter, members) {
    var key = S.groupKey(members);
    var dup = Object.keys(S.proposals).some(function (g) {
      var latest = S.latestProposal(g);
      return latest && S.groupKey(latest.members) === key;
    });
    if (dup) return 'duplicate';
    return S.latestProposal(letter) ? 'revision' : 'new';
  };

  /** Records a proposal revision. Returns the revision, or null for a duplicate. */
  S.submitProposal = function (letter, members) {
    if (S.proposalKind(letter, members) === 'duplicate') return null;
    var revs = S.proposals[letter] || (S.proposals[letter] = []);
    var rev = { rev: revs.length + 1, members: sortIds(members), at: Date.now() };
    revs.push(rev);
    record('submit-proposal', { letter: letter, rev: rev.rev, members: rev.members });
    return rev;
  };

  /**
   * Proposals whose latest revision still matches an active, eligible group.
   * These are the groups that need golden records. [{ letter, rev, members, key }]
   */
  S.currentProposals = function () {
    var groups = S.activeGroups();
    var out = [];
    groups.forEach(function (g) {
      var latest = S.latestProposal(g.letter);
      if (!latest || S.groupKey(latest.members) !== S.groupKey(g.members)) return;
      var items = g.members.map(function (id) { return A.data.records.find(function (r) { return r.id === id; }); });
      if (!A.rules.identity.evaluateGroup(items).submittable) return;
      out.push({ letter: g.letter, rev: latest.rev, members: latest.members, key: S.groupKey(latest.members) });
    });
    return out;
  };

  // ---- golden records ---------------------------------------------------------------------
  function goldenEntry(key) {
    return S.golden[key] || (S.golden[key] = { draft: {}, revisions: [] });
  }

  S.goldenDraft = function (key) {
    return goldenEntry(key).draft;
  };

  S.setGoldenChoice = function (key, attr, patch) {
    var draft = goldenEntry(key).draft;
    var prev = draft[attr] || {};
    draft[attr] = Object.assign({}, prev, patch);
    record('golden-choice', { key: key, attr: attr, patch: patch });
  };

  S.latestGolden = function (key) {
    var revs = goldenEntry(key).revisions;
    return revs.length ? revs[revs.length - 1] : null;
  };

  function sameChoices(a, b) {
    return JSON.stringify(a) === JSON.stringify(b);
  }

  /** Saves the draft as a new revision. Returns the revision, or null if nothing changed. */
  S.saveGolden = function (key, proposalRev) {
    var entry = goldenEntry(key);
    var choices = JSON.parse(JSON.stringify(entry.draft));
    var latest = S.latestGolden(key);
    if (latest && sameChoices(latest.choices, choices) && latest.proposalRev === proposalRev) return null;
    var rev = { rev: entry.revisions.length + 1, proposalRev: proposalRev, choices: choices, at: Date.now() };
    entry.revisions.push(rev);
    record('save-golden', { key: key, rev: rev.rev });
    return rev;
  };

  /** True when the draft differs from the last saved revision. */
  S.goldenHasUnsavedChanges = function (key) {
    var latest = S.latestGolden(key);
    return !latest || !sameChoices(latest.choices, goldenEntry(key).draft);
  };

  // ---- validation -------------------------------------------------------------------------
  function validationEntry(key) {
    return S.validation[key] || (S.validation[key] = { draft: { basis: [], rationale: '' }, submissions: [] });
  }

  S.validationDraft = function (key) {
    return validationEntry(key).draft;
  };

  S.setValidationDraft = function (key, patch) {
    Object.assign(validationEntry(key).draft, patch);
    record('validation-edit', { key: key, fields: Object.keys(patch) });
  };

  S.latestSubmission = function (key) {
    var subs = validationEntry(key).submissions;
    return subs.length ? subs[subs.length - 1] : null;
  };

  /** Fingerprint of everything a governance submission depends on. */
  S.submissionFingerprint = function (proposal) {
    var golden = S.latestGolden(proposal.key);
    var d = validationEntry(proposal.key).draft;
    return JSON.stringify({ p: proposal.rev, g: golden ? golden.rev : 0, b: d.basis.slice().sort(), r: d.rationale.trim() });
  };

  /** 'none' | 'current' | 'changed' for a proposal's governance submission. */
  S.submissionState = function (proposal) {
    var latest = S.latestSubmission(proposal.key);
    if (!latest) return 'none';
    return latest.fingerprint === S.submissionFingerprint(proposal) ? 'current' : 'changed';
  };

  /** Records a governance submission. Returns it, or null if nothing changed since the last one. */
  S.submitForReview = function (proposal, checklist) {
    if (S.submissionState(proposal) === 'current') return null;
    var entry = validationEntry(proposal.key);
    var golden = S.latestGolden(proposal.key);
    var sub = {
      rev: entry.submissions.length + 1, proposalRev: proposal.rev, goldenRev: golden ? golden.rev : 0,
      basis: entry.draft.basis.slice(), rationale: entry.draft.rationale.trim(), checklist: checklist,
      fingerprint: S.submissionFingerprint(proposal), at: Date.now()
    };
    entry.submissions.push(sub);
    record('submit-for-review', { key: proposal.key, rev: sub.rev });
    return sub;
  };

  S.setNotProposed = function (id, reason) {
    S.notProposed[id] = reason;
    record('not-proposed-reason', { id: id, reason: reason });
  };

  S.setHeldFollowUp = function (id, action) {
    S.heldFollowUp[id] = action;
    record('held-follow-up', { id: id, action: action });
  };

  // ---- finishing and retrying -----------------------------------------------------------------
  /** Freezes the case for scoring. Returns the snapshot. */
  S.finish = function () {
    var active = S.activeRecords().map(function (r) { return r.id; });
    var proposals = S.currentProposals();
    var golden = {}, validations = {};
    proposals.forEach(function (p) {
      var g = S.latestGolden(p.key);
      if (g && g.proposalRev === p.rev) golden[p.key] = { choices: g.choices, rev: g.rev };
      var v = S.latestSubmission(p.key);
      if (v) validations[p.key] = { basis: v.basis, rationale: v.rationale, rev: v.rev, current: S.submissionState(p) === 'current' };
    });
    var decisions = {};
    active.forEach(function (id) { decisions[id] = S.decisions[id] || ''; });
    var notProposed = {}, held = {};
    active.forEach(function (id) {
      if (S.notProposed[id] && (decisions[id] === 'separate' || decisions[id] === 'hold')) notProposed[id] = S.notProposed[id];
      if (S.heldFollowUp[id] && decisions[id] === 'hold') held[id] = S.heldFollowUp[id];
    });
    var snapshot = { active: active, decisions: decisions, proposals: proposals, golden: golden, validations: validations,
      notProposed: notProposed, heldFollowUp: held, at: Date.now(), attempt: S.attempts.length + 1 };
    record('finish', { attempt: snapshot.attempt });
    S.finished = snapshot;
    return snapshot;
  };

  S.recordAttemptResult = function (result) {
    S.attempts.push({ attempt: S.finished.attempt, earned: result.earned, max: result.max, level: result.level, at: S.finished.at });
  };

  /** Starts a new attempt: clears all work but keeps the list of earlier attempt results. */
  S.resetForRetry = function () {
    S.selected = new Set();
    S.current = null;
    S.decisions = {};
    S.check = null;
    S.proposals = {};
    S.golden = {};
    S.validation = {};
    S.notProposed = {};
    S.heldFollowUp = {};
    S.finished = null;
    S.events = [];
    record('new-attempt', { attempt: S.attempts.length + 1 });
  };

  S.setActivePage = function (page) {
    S.activeLearningPage = page;
  };

  A.state = S;
})(window.Aperion);
