/*
 * Governance validation rules for a proposed identity group. Pure function.
 * Logic is unchanged from v0.3.2, INCLUDING known defects (see KNOWN-DEFECTS.md):
 *   D1  INSTRUCTIONAL INTEGRITY: only conflicting tax identifiers block a merge. Groups of
 *       unrelated entities (different parent, address, or missing identifiers) are offered
 *       for submission. NOT APPROVED BEHAVIOR. Scheduled for Phase 2.
 *   D4  A one-record group is reported as eligible for governance review.
 */
(function (A) {
  'use strict';
  A.registerModule('rules/governance', ['namespace']);

  /**
   * Returns { blocking, needsReview, message } for the records in one group.
   * `message` is the verdict text shown to learners.
   */
  function groupVerdict(items) {
    var taxes = Array.from(new Set(items.map(function (r) { return r.tax; }).filter(Boolean)));
    var names = Array.from(new Set(items.map(function (r) { return r.legal; }).filter(Boolean)));
    var blocking = taxes.length > 1;
    var needsReview = items.some(function (r) { return !r.tax || !r.legal; }) || names.length > 1;
    var message = blocking ? 'BLOCKED: conflicting tax identifiers'
      : needsReview ? 'REVIEW REQUIRED: incomplete or differing identity evidence'
      : 'ELIGIBLE FOR GOVERNANCE REVIEW (not approved)';
    return { blocking: blocking, needsReview: needsReview, message: message };
  }

  A.rules.governance = { groupVerdict: groupVerdict };
})(window.Aperion);
