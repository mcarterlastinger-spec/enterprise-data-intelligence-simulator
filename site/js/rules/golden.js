/*
 * Golden-record evidence checks (v0.4.0). Pure functions.
 *
 * These are the automatic, rule-based checks a data steward's tooling would run before a
 * governance submission. They test whether the evidence a learner cited is CONSISTENT with the
 * source they chose (e.g. "ERP is the system of record" must cite an ERP value). They do not
 * reveal the answer key: a consistent choice can still be the wrong business decision, which
 * is assessed in the debrief.
 */
(function (A) {
  'use strict';
  A.registerModule('rules/golden', ['rules/matching']);

  var m = A.rules.matching;

  function recordById(id) {
    return A.data.records.find(function (r) { return r.id === id; });
  }

  /**
   * Returns null when the cited reason is consistent with the chosen value's sources,
   * otherwise a short explanation.
   * choice: { value, sources: [ids], reason }, members: [ids], field: record field name.
   */
  function reasonConsistency(choice, members, field) {
    if (!choice || !choice.value || !choice.reason) return null;
    var sources = (choice.sources || []).map(recordById);
    var withValue = members.map(recordById).filter(function (r) { return r[field]; });
    var systems = sources.map(function (r) { return r.system; });
    switch (choice.reason) {
      case 'agree': {
        var distinct = new Set(withValue.map(function (r) { return m.norm(field === 'contact' ? 'contact' : field, r[field]); }));
        return distinct.size > 1 ? 'You cited agreement, but the sources in this group hold different values.' : null;
      }
      case 'erp-legal':
        return systems.indexOf('ERP') === -1 ? 'You cited ERP as the system of record, but this value does not come from an ERP record.' : null;
      case 'crm-operating':
        return systems.indexOf('CRM') === -1 ? 'You cited the CRM relationship record, but this value does not come from a CRM record.' : null;
      case 'billing-source':
        return systems.indexOf('ERP') === -1 ? 'You cited the finance (billing) record, but this value does not come from the ERP finance record.' : null;
      case 'recent': {
        var latest = withValue.slice().sort(function (a, b) { return a.verified < b.verified ? 1 : -1; })[0];
        return latest && (choice.sources || []).indexOf(latest.id) === -1 ? 'You cited the most recently verified source, but ' + latest.id + ' (verified ' + latest.verified + ') is more recent.' : null;
      }
      case 'only':
        return withValue.length > 1 ? 'You cited the only source with a value, but ' + withValue.length + ' records in this group have one.' : null;
      default:
        return null;
    }
  }

  A.rules.golden = { reasonConsistency: reasonConsistency };
})(window.Aperion);
