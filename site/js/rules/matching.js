/*
 * Evidence comparison rules (v0.4.0). Pure functions: records in, results out.
 *
 * Fixes from v0.3.x:
 *   D2  Missing values no longer hide conflicts: a row reports conflicts AND missing values.
 *   D3  Source system and Last verified are context, expected to differ, never "conflicts".
 *   D9  One normalization per attribute type, used by the matrix and the identity rules alike.
 */
(function (A) {
  'use strict';
  A.registerModule('rules/matching', ['namespace']);

  /** Legal names: case, punctuation, and legal-form suffixes do not change the entity. */
  function normLegal(s) {
    return String(s || '').toLowerCase()
      .replace(/&/g, ' and ')
      .replace(/\bl\.\s?l\.\s?c\b\.?/g, ' llc ')
      .replace(/\b(incorporated|inc|llc|corp|corporation|co|company|ltd|limited)\b\.?/g, '')
      .replace(/^\s*the\s+/, '')
      .replace(/[^a-z0-9]/g, '');
  }

  /** Tax identifiers: compare digits only. */
  function normTax(s) {
    return String(s || '').replace(/[^0-9]/g, '');
  }

  var STREET_WORDS = { pkwy: 'parkway', ave: 'avenue', av: 'avenue', st: 'street', rd: 'road', blvd: 'boulevard', dr: 'drive', ste: 'suite', wa: 'wa' };

  /** Addresses: case, punctuation, and common street abbreviations do not change the place. */
  function normAddress(s) {
    return String(s || '').toLowerCase().replace(/[.,#]/g, ' ').split(/\s+/).filter(Boolean)
      .map(function (w) { return STREET_WORDS[w] || w; }).join(' ');
  }

  function normText(s) {
    return String(s || '').trim().toLowerCase();
  }

  /** How each compared attribute is treated. */
  var KIND = {
    legal: { role: 'identity', norm: normLegal },
    tax: { role: 'identity', norm: normTax },
    address: { role: 'supporting', norm: normAddress },
    parent: { role: 'supporting', norm: normText },
    system: { role: 'context', norm: normText },
    verified: { role: 'context', norm: normText }
  };

  function norm(key, value) {
    return (KIND[key] ? KIND[key].norm : normText)(value);
  }

  /**
   * Assesses one attribute across records.
   * Returns { role, state, label, distinct, missing, sets } where `sets` maps each record ID
   * to a 1-based value-set number (records with equal normalized values share a number).
   */
  function attributeAssessment(records, key) {
    var role = KIND[key] ? KIND[key].role : 'supporting';
    var order = [];
    var sets = {};
    var missing = 0;
    records.forEach(function (r) {
      var v = r[key];
      if (!v) { missing += 1; sets[r.id] = 0; return; }
      var n = norm(key, v);
      var i = order.indexOf(n);
      if (i === -1) { order.push(n); i = order.length - 1; }
      sets[r.id] = i + 1;
    });
    var distinct = order.length;
    var state, label;
    if (role === 'context') {
      state = 'context';
      label = 'Context: expected to differ between systems';
    } else if (distinct === 0) {
      state = 'missing';
      label = 'Missing in all selected records';
    } else if (distinct === 1) {
      state = missing ? 'consistent-missing' : 'consistent';
      label = missing ? 'Consistent where present · ' + missing + ' missing' : 'Consistent';
    } else {
      state = missing ? 'conflict-missing' : 'conflict';
      label = 'Conflict: ' + distinct + ' different values' + (missing ? ' · ' + missing + ' missing' : '');
    }
    return { role: role, state: state, label: label, distinct: distinct, missing: missing, sets: sets };
  }

  /** CSS class for one record's cell, given the row assessment. */
  function cellClass(record, key, assessment) {
    if (assessment.role === 'context') return 'context';
    if (!record[key]) return 'missing';
    return assessment.distinct > 1 ? 'conflict' : 'consistent';
  }

  A.rules.matching = {
    norm: norm,
    normLegal: normLegal,
    normTax: normTax,
    normAddress: normAddress,
    attributeAssessment: attributeAssessment,
    cellClass: cellClass
  };
})(window.Aperion);
