/*
 * Competency scoring (v0.4.0, decision P2-3, approved 2026-11-11). Pure function.
 *
 * 23 points, each tied to ONE learner decision, so no decision earns credit twice:
 *   Identity Resolution  4  the identity decision for each record (grouped, separate, held)
 *   Evidence Analysis    4  the learner's interpretation of the evidence: what establishes
 *                           identity for each proposal, and why each other record was not proposed
 *   Data Reconciliation 12  each golden-record attribute: correct value AND supporting evidence
 *   Governance Judgment  3  the governance trail: every proposal submitted and current, rationale
 *                           cites the identity evidence, correct follow-up for the held record
 * Levels per competency: Proficient >= 85% of its points, Developing >= 50%, Needs Practice < 50%.
 * The scoring input is a snapshot taken when the learner finishes the case.
 */
(function (A) {
  'use strict';
  A.registerModule('rules/scoring', ['data/case']);

  var D = A.data;

  function level(earned, max) {
    var r = max ? earned / max : 0;
    return r >= 0.85 ? 'Proficient' : r >= 0.5 ? 'Developing' : 'Needs Practice';
  }

  function label(list, id) {
    var x = list.find(function (o) { return o.id === id; });
    return x ? x.label : '(none selected)';
  }

  function key(ids) {
    return ids.slice().sort().join('|');
  }

  function criterion(id, text, max, earned, feedback) {
    return { id: id, text: text, max: max, earned: earned, met: earned === max, feedback: feedback };
  }

  /**
   * snapshot: {
   *   active: [ids], decisions: {id: value},
   *   proposals: [{ letter, members, key }]                  current proposals
   *   golden: { key: { choices } }                            latest saved golden records
   *   validations: { key: { basis:[ids], rationale, current:bool } }   latest governance submissions
   *   notProposed: { id: reasonId }, heldFollowUp: { id: followUpId }
   * }
   */
  function score(snap) {
    var groupKeys = D.answerKey.groups.map(function (g) { return key(g.records); });
    var proposalKeys = snap.proposals.map(function (p) { return p.key; });
    var isActive = function (id) { return snap.active.indexOf(id) !== -1; };

    // ---- Identity Resolution -----------------------------------------------------------
    var ir = [];
    D.answerKey.groups.forEach(function (g, i) {
      var k = groupKeys[i];
      var ok = proposalKeys.indexOf(k) !== -1;
      var fb;
      if (ok) fb = g.records.join(' and ') + ' share tax identifier and legal name, and you proposed them together.';
      else if (!g.records.every(isActive)) fb = 'You did not include both ' + g.records.join(' and ') + ' in your comparison, so this match was not found.';
      else {
        var with_ = snap.proposals.find(function (p) { return g.records.some(function (id) { return p.members.indexOf(id) !== -1; }); });
        fb = with_ ? 'Your proposal ' + with_.members.join(', ') + ' does not match ' + g.label + ' (' + g.records.join(' + ') + '), the only records sharing its tax identifier and legal name.'
          : g.records.join(' and ') + ' share tax identifier and legal name, but you did not propose them together.';
      }
      ir.push(criterion('IR' + (i + 1), 'Proposed ' + g.label + ': ' + g.records.join(' + '), 1, ok ? 1 : 0, fb));
    });
    var sepId = D.answerKey.separate[0], holdId = D.answerKey.hold[0];
    var sep = snap.decisions[sepId], hold = snap.decisions[holdId];
    ir.push(criterion('IR3', 'Kept ' + sepId + ' separate', 1, isActive(sepId) && sep === 'separate' ? 1 : 0,
      !isActive(sepId) ? 'You did not include ' + sepId + ' in your comparison.'
        : sep === 'separate' ? sepId + ' has its own tax identifier and an independent parent: a distinct legal entity, correctly kept separate.'
          : sep === 'hold' ? sepId + ' is not unverified: its tax identifier conflicts with the others, which proves it is a different entity. Keep it separate rather than holding it.'
            : sepId + ' has a different tax identifier (91-9346180) and parent ("Independent"). Its similar name does not make it the same entity.'));
    ir.push(criterion('IR4', 'Held ' + holdId + ' for verification', 1, isActive(holdId) && hold === 'hold' ? 1 : 0,
      !isActive(holdId) ? 'You did not include ' + holdId + ' in your comparison.'
        : hold === 'hold' ? holdId + ' has no tax identifier or legal name. Holding it is right: missing evidence is insufficient, not proof of a mismatch.'
          : hold === 'separate' ? holdId + ' cannot be proven to be a different entity: it is missing evidence, not conflicting evidence. Hold it for verification.'
            : holdId + ' lacks a tax identifier and legal name, so its identity cannot be confirmed. Hold it for verification.'));

    // ---- Evidence Analysis ------------------------------------------------------------
    var ea = [];
    D.answerKey.groups.forEach(function (g, i) {
      var k = groupKeys[i];
      var v = snap.validations[k];
      var basis = v ? v.basis.slice().sort() : null;
      var ok = !!basis && basis.join(',') === D.identityBasisKey.slice().sort().join(',');
      var fb;
      if (!v) fb = 'No governance submission for ' + g.label + ', so your reading of its identity evidence could not be assessed.';
      else if (ok) fb = 'You identified the matching tax identifier and legal name as the evidence that establishes identity.';
      else {
        var extra = basis.filter(function (b) { return D.identityBasisKey.indexOf(b) === -1; }).map(function (b) { return label(D.identityBasisOptions, b).toLowerCase(); });
        var missing = D.identityBasisKey.filter(function (b) { return basis.indexOf(b) === -1; }).map(function (b) { return label(D.identityBasisOptions, b).toLowerCase(); });
        fb = (extra.length ? 'You also cited ' + extra.join(', ') + ': supporting evidence only, which cannot establish identity. ' : '') +
          (missing.length ? 'You did not cite ' + missing.join(' and ') + ', the evidence that does establish identity.' : '');
      }
      ea.push(criterion('EA' + (i + 1), 'Identified the identity evidence for ' + g.label, 1, ok ? 1 : 0, fb.trim()));
    });
    [sepId, holdId].forEach(function (id, j) {
      var chosen = snap.notProposed[id];
      var expected = D.notProposedKey[id];
      var ok = chosen === expected;
      var fb = !chosen ? 'You did not explain why ' + id + ' was not proposed.'
        : ok ? 'Correct: ' + label(D.notProposedReasons, expected).charAt(0).toLowerCase() + label(D.notProposedReasons, expected).slice(1) + '.'
          : 'You said: "' + label(D.notProposedReasons, chosen) + '." The deciding evidence is that ' + label(D.notProposedReasons, expected).charAt(0).toLowerCase() + label(D.notProposedReasons, expected).slice(1) + '.';
      ea.push(criterion('EA' + (j + 3), 'Explained why ' + id + ' was not proposed', 1, ok ? 1 : 0, fb));
    });

    // ---- Data Reconciliation -------------------------------------------------------------
    var dr = [];
    groupKeys.forEach(function (k, i) {
      var gl = snap.golden[k];
      D.goldenAttributes.forEach(function (a) {
        var exp = D.goldenKey[k][a.key];
        var c = gl ? gl.choices[a.key] : null;
        var valueOk = !!c && c.value === exp.value;
        var reasonOk = !!c && exp.reasons.indexOf(c.reason) !== -1;
        var fb;
        if (!gl) fb = 'No saved golden record for ' + D.answerKey.groups[i].label + '.';
        else if (valueOk && reasonOk) fb = 'Correct value and evidence. ' + exp.why;
        else if (!valueOk) fb = 'You chose "' + (c && c.value) + '". Expected "' + exp.value + '". ' + exp.why;
        else fb = 'Correct value, but the evidence you cited ("' + label(D.goldenReasons, c.reason) + '") does not support it. ' + exp.why;
        dr.push(criterion('DR-' + (i + 1) + '-' + a.key, D.answerKey.groups[i].label + ': ' + a.label, 1, valueOk && reasonOk ? 1 : 0, fb));
      });
    });

    // ---- Governance Judgment -------------------------------------------------------------
    var gj = [];
    var subs = snap.proposals.map(function (p) { return snap.validations[p.key]; });
    var allSubmitted = snap.proposals.length > 0 && subs.every(function (v) { return v && v.current; });
    gj.push(criterion('GJ1', 'Submitted every proposal for governance review, up to date', 1, allSubmitted ? 1 : 0,
      allSubmitted ? 'Every proposal has a current governance submission.'
        : !snap.proposals.length ? 'You finished without a merge proposal.'
          : 'At least one proposal was not submitted, or changed after submission and was not resubmitted.'));
    var cites = subs.length > 0 && subs.every(function (v) { return v && /\b(tax|legal|ein|tin)\b/i.test(v.rationale); });
    gj.push(criterion('GJ2', 'Rationale cites the identity evidence (mentions the tax identifier or legal name)', 1, cites ? 1 : 0,
      cites ? 'Each rationale names the identity evidence a reviewer will check.'
        : 'A governance reviewer needs the identifying evidence named. Mention the matching tax identifier or legal name in every rationale.'));
    var fu = snap.heldFollowUp[holdId];
    var fuOk = fu === D.heldFollowUpKey;
    gj.push(criterion('GJ3', 'Chose the right follow-up for ' + holdId, 1, fuOk ? 1 : 0,
      fuOk ? 'Requesting the W-9 and legal name lets the record be verified before any merge.'
        : !fu ? 'You did not choose a follow-up for ' + holdId + '.'
          : 'You chose: "' + label(D.heldFollowUps, fu) + '." The record needs its missing identity evidence before any decision: ask Commercial Operations for the W-9 and legal name.'));

    function comp(name, items, summary) {
      var earned = items.reduce(function (n, c) { return n + c.earned; }, 0);
      var max = items.reduce(function (n, c) { return n + c.max; }, 0);
      return { name: name, summary: summary, earned: earned, max: max, level: level(earned, max), criteria: items };
    }
    var comps = [
      comp('Evidence Analysis', ea, 'Interpreting what the evidence does and does not prove.'),
      comp('Identity Resolution', ir, 'Deciding which records are the same legal entity.'),
      comp('Data Reconciliation', dr, 'Choosing each golden-record value with supporting evidence.'),
      comp('Governance Judgment', gj, 'Leaving a complete, defensible governance trail.')
    ];
    var total = comps.reduce(function (n, c) { return n + c.earned; }, 0);
    var max = comps.reduce(function (n, c) { return n + c.max; }, 0);
    return { competencies: comps, earned: total, max: max, level: level(total, max) };
  }

  A.rules.scoring = { score: score, level: level };
})(window.Aperion);
