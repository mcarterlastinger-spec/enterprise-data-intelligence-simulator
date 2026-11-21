/*
 * Matching rules used by the comparison matrix. Pure functions: records in, results out.
 * Logic is unchanged from v0.3.2, INCLUDING known defects (see KNOWN-DEFECTS.md):
 *   D2  A missing value makes the whole row "Missing evidence", hiding real conflicts.
 *   D3  Source system and Last verified are compared like identity attributes.
 *   D9  Addresses are not normalized; the validator does not use norm() for legal names.
 * Do not correct these in Phase 1. They are scheduled for Phase 2.
 */
(function (A) {
  'use strict';
  A.registerModule('rules/matching', ['namespace']);

  /** Legal-name normalization from v0.3.2: lowercases, drops inc/llc/healthcare words and punctuation. */
  function norm(s) {
    return s.toLowerCase().replace(/\b(incorporated|inc|llc|healthcare)\b/g, '').replace(/[^a-z0-9]/g, '');
  }

  /**
   * Evaluates one attribute across the selected records.
   * Returns { state, distinctCount } where state is the row label shown to learners.
   */
  function attributeState(records, key) {
    var values = records.map(function (r) { return r[key] || ''; });
    var known = values.filter(Boolean);
    var distinct = new Set(known.map(function (v) { return key === 'legal' ? norm(v) : v.toLowerCase(); }));
    var state = known.length !== values.length ? 'Missing evidence'
      : distinct.size > 1 ? 'Conflict / difference'
      : 'Consistent';
    return { state: state, distinctCount: distinct.size };
  }

  /** CSS class for one record's cell in an attribute row. */
  function cellClass(record, key, distinctCount) {
    return !record[key] ? 'missing' : distinctCount > 1 ? 'conflict' : 'consistent';
  }

  A.rules.matching = { norm: norm, attributeState: attributeState, cellClass: cellClass };
})(window.Aperion);
