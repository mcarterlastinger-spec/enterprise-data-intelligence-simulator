/*
 * Identity and merge-eligibility rules (v0.4.0, decision P2-1). Pure function.
 *
 * A proposed group is ELIGIBLE for a merge proposal only when every record carries a tax
 * identifier and a legal name, and all of them agree. Nothing else can establish eligibility:
 * similar names, shared addresses, and shared parent organizations are supporting evidence only.
 *
 *   blocked       tax identifiers, legal names, or parent organizations contradict each other
 *   verification  no contradiction, but a record lacks a tax identifier or legal name; missing
 *                 evidence is insufficient, not proof of a mismatch
 *   eligible      tax identifier and legal name present and matching in every record
 *   single        one record; there is nothing to merge
 *
 * Fixes D1 (unrelated entities eligible) and D4 (one-record group called eligible).
 */
(function (A) {
  'use strict';
  A.registerModule('rules/identity', ['rules/matching']);

  var m = A.rules.matching;

  function distinctValues(items, key, normFn) {
    var seen = {}, out = [];
    items.forEach(function (r) {
      if (!r[key]) return;
      var n = normFn(r[key]);
      if (!seen[n]) { seen[n] = true; out.push(r[key]); }
    });
    return out;
  }

  function list(values) {
    return values.map(function (v) { return '“' + v + '”'; }).join(', ');
  }

  /**
   * Evaluates the records in one proposed group.
   * Returns { status, title, reasons[], warnings[], submittable }.
   */
  function evaluateGroup(items) {
    if (items.length < 2) {
      return {
        status: 'single', title: 'No merge needed: a single record',
        reasons: ['A group needs at least two records to propose a merge.'], warnings: [], submittable: false
      };
    }
    var taxes = distinctValues(items, 'tax', m.normTax);
    var legals = distinctValues(items, 'legal', m.normLegal);
    var parents = distinctValues(items, 'parent', function (v) { return m.norm('parent', v); });
    var addresses = distinctValues(items, 'address', m.normAddress);

    var blockers = [];
    if (taxes.length > 1) blockers.push('Different tax identifiers (' + list(taxes) + ') indicate separate legal entities.');
    if (legals.length > 1) blockers.push('Different legal names (' + list(legals) + ') indicate separate legal entities.');
    if (parents.length > 1) blockers.push('Different parent organizations (' + list(parents) + ') contradict a single corporate identity.');
    if (blockers.length) {
      return { status: 'blocked', title: 'Blocked: the evidence shows different entities', reasons: blockers, warnings: [], submittable: false };
    }

    var missing = [];
    items.forEach(function (r) {
      var gaps = [];
      if (!r.tax) gaps.push('tax identifier');
      if (!r.legal) gaps.push('legal name');
      if (gaps.length) missing.push(r.id + ' has no ' + gaps.join(' or ') + '.');
    });
    if (missing.length) {
      return {
        status: 'verification', title: 'Verification required: identity cannot be confirmed',
        reasons: missing.concat(['Missing evidence is insufficient, not proof of a mismatch. Similar names, addresses, or parent organizations cannot confirm identity. Hold the record for verification.']),
        warnings: [], submittable: false
      };
    }

    var warnings = [];
    if (addresses.length > 1) {
      warnings.push('Addresses differ (' + list(addresses) + '). Decide which is the operating address and which is the billing address in the golden record.');
    }
    return {
      status: 'eligible', title: 'Eligible to propose for governance review',
      reasons: ['Tax identifier and legal name are present and match in every record.'],
      warnings: warnings, submittable: true
    };
  }

  A.rules.identity = { evaluateGroup: evaluateGroup };
})(window.Aperion);
