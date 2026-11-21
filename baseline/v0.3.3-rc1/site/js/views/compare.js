/*
 * Match & Compare: comparison matrix, identity grouping, governance validation, proposals.
 * Markup and behavior unchanged from v0.3.2. Rules live in js/rules/ and keep their known
 * defects (D1, D2, D3, D4, D5, D6) until Phase 2 — see KNOWN-DEFECTS.md.
 * Approved behavior G5: group choices are kept for deselected records, but only currently
 * selected records are shown, validated, or included in proposals.
 */
(function (A) {
  'use strict';
  A.registerModule('views/compare', ['util', 'data/records', 'data/attributes', 'state', 'rules/matching', 'rules/governance']);

  var $ = A.$;
  var escapeHTML = A.escapeHTML;
  var S = A.state;
  var records = A.data.records;
  var attrs = A.data.attrs;
  var groupLetters = A.data.groupLetters;
  var matching = A.rules.matching;
  var governance = A.rules.governance;

  function selectedRecords() {
    return Array.from(S.selected).map(function (id) { return records.find(function (r) { return r.id === id; }); });
  }

  function renderCompare() {
    var arr = selectedRecords().filter(Boolean);
    if (arr.length < 2) {
      $('compare-content').innerHTML = '<div class="notice">Select at least two records. You can evaluate the entire dataset simultaneously.</div><button class="primary" data-action="showPage:work">Select records</button>';
      return;
    }
    var cells = attrs.map(function (pair) {
      var label = pair[0], key = pair[1];
      var result = matching.attributeState(arr, key);
      return `<tr><th scope="row">${label}<div class="small muted">${result.state}</div></th>${arr.map(function (r) {
        return `<td class="${matching.cellClass(r, key, result.distinctCount)}">${escapeHTML(r[key] || 'Missing')}</td>`;
      }).join('')}</tr>`;
    }).join('');
    $('compare-content').innerHTML = `<div class="notice">All ${arr.length} selected records are evaluated together. Differences are not automatically identity conflicts. Grouping does not merge records.</div><div class="tablewrap"><table class="matrix"><thead><tr><th scope="col">Attribute</th>${arr.map(function (r) {
      return `<th scope="col">${escapeHTML(r.id)}<div class="small">${escapeHTML(r.name)}</div></th>`;
    }).join('')}</tr></thead><tbody>${cells}</tbody></table></div><h2 style="margin-top:26px">Proposed identity groups</h2><p class="muted">Assign each record to an identity group or leave it unassigned. Changes are reversible. The governance review evaluates each group separately.</p><div class="tablewrap"><table><thead><tr><th>Record</th><th>Tax identifier</th><th>Proposed group</th></tr></thead><tbody>${arr.map(function (r) {
      return `<tr><td>${escapeHTML(r.id)} · ${escapeHTML(r.name)}</td><td>${escapeHTML(r.tax || 'Missing')}</td><td><select aria-label="Identity group for ${escapeHTML(r.id)}" data-group="${r.id}"><option value="">Unassigned</option>${groupLetters.map(function (g) {
        return `<option value="${g}" ${S.groupAssignments[r.id] === g ? 'selected' : ''}>Group ${g}</option>`;
      }).join('')}</select></td></tr>`;
    }).join('')}</tbody></table></div><div class="controls" style="margin-top:15px"><button class="primary" id="review-groups">Validate proposed groups</button><button class="secondary" id="clear-groups">Clear groups</button></div><div id="governance-output" aria-live="polite"></div>`;
    document.querySelectorAll('[data-group]').forEach(function (el) {
      el.addEventListener('change', function () {
        S.setGroup(el.dataset.group, el.value);
        $('governance-output').innerHTML = '<div class="notice">Groups changed. Run validation again before review.</div>';
      });
    });
    $('review-groups').addEventListener('click', validateGroups);
    $('clear-groups').addEventListener('click', function () {
      S.clearGroups(arr.map(function (r) { return r.id; }));
      renderCompare();
    });
  }

  function validateGroups() {
    var arr = selectedRecords();
    var groups = groupLetters.map(function (g) {
      return { g: g, items: arr.filter(function (r) { return S.groupAssignments[r.id] === g; }) };
    }).filter(function (x) { return x.items.length; });
    var out = groups.map(function (grp) {
      var g = grp.g, items = grp.items;
      var verdict = governance.groupVerdict(items);
      return `<section class="groupresult"><strong>Group ${g} · ${items.length} record(s)</strong><p>${verdict.message}</p><p class="small muted">${items.map(function (r) { return r.id; }).join(', ')}</p>${items.length > 1 && !verdict.blocking ? `<button class="secondary" data-propose="${g}">Submit merge proposal for review</button>` : ''}</section>`;
    }).join('');
    $('governance-output').innerHTML = `<h2 style="margin-top:20px">Governance validation</h2>${out || '<div class="notice">Assign records to proposed groups before validating.</div>'}<p class="small muted">This prototype records merge proposals only. No source data is changed, merged, or published. Additional evidence and approval are required.</p><div id="audit" aria-live="polite"></div>`;
    document.querySelectorAll('[data-propose]').forEach(function (b) {
      b.addEventListener('click', function () {
        var g = b.dataset.propose;
        S.addProposal({ group: g, records: arr.filter(function (r) { return S.groupAssignments[r.id] === g; }).map(function (r) { return r.id; }) });
        $('audit').innerHTML = `<div class="feedback">Group ${g} proposal logged for governance review. No merge has occurred. ${S.mergeAudit.length} proposal(s) recorded this session.</div>`;
      });
    });
  }

  A.views.compare = { renderCompare: renderCompare, validateGroups: validateGroups };
})(window.Aperion);
