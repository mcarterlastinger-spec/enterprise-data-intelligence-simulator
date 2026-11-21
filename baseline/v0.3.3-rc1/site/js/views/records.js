/*
 * Customer Records workspace: record table, search and filters, record details, selection.
 * Behavior unchanged from v0.3.2. Approved behavior (decision A2): filters change which
 * records are visible, not which are selected. Known defect D7: ticking a checkbox rebuilds
 * the table, so keyboard focus moves to the page body. Not corrected in Phase 1.
 */
(function (A) {
  'use strict';
  A.registerModule('views/records', ['util', 'data/records', 'state', 'navigation']);

  var $ = A.$;
  var escapeHTML = A.escapeHTML;
  var S = A.state;
  var records = A.data.records;

  function render() {
    var q = $('search').value.trim().toLowerCase();
    var system = $('system').value;
    var status = $('status').value;
    var shown = records.filter(function (r) {
      return (!system || r.system === system) && (!status || r.status === status) &&
        (!q || [r.id, r.name, r.tax, r.address, r.legal, r.parent].some(function (v) { return v.toLowerCase().includes(q); }));
    });
    // Markup is identical to v0.3.2.
    $('rows').innerHTML = shown.map(function (r) {
      return `<tr><td><input type="checkbox" aria-label="Select ${escapeHTML(r.id)} for comparison" data-id="${r.id}" ${S.selected.has(r.id) ? 'checked' : ''}></td><td><button class="record" data-open="${r.id}">${r.id}</button></td><td>${escapeHTML(r.name)}</td><td>${r.system}</td><td><span class="status ${r.status.toLowerCase()}">${r.status}</span></td><td>${r.verified}</td></tr>`;
    }).join('') || '<tr><td colspan="6">No matching records. Adjust your filters.</td></tr>';
    $('stat-visible').textContent = shown.length;
    $('results').textContent = `Showing ${shown.length} of ${records.length} records.`;
    $('compare-btn').disabled = S.selected.size < 2;
    $('compare-btn').textContent = `Evaluate selected records (${S.selected.size})`;
    A.navigation.updateNextStep(S.activeLearningPage);
    document.querySelectorAll('[data-id]').forEach(function (e) {
      e.addEventListener('change', function () {
        if (e.checked) S.select(e.dataset.id); else S.deselect(e.dataset.id);
        render();
      });
    });
    document.querySelectorAll('[data-open]').forEach(function (e) {
      e.addEventListener('click', function () { openRecord(e.dataset.open); });
    });
  }

  function resetFilters() {
    $('search').value = '';
    $('system').value = '';
    $('status').value = '';
    render();
  }

  function openRecord(id) {
    var current = records.find(function (r) { return r.id === id; });
    S.setCurrent(current);
    $('details').classList.remove('hidden');
    $('details-title').textContent = `Record details · ${id}`;
    var fields = {
      'Customer': current.name,
      'Legal name': current.legal || 'Not provided',
      'Tax identifier': current.tax || 'Missing',
      'Business address': current.address,
      'Parent organization': current.parent,
      'Contact email': current.contact,
      'Last verified': current.verified,
      'Source note': current.note
    };
    $('details-fields').innerHTML = Object.entries(fields).map(function (kv) {
      return `<div class="field"><b>${escapeHTML(kv[0])}</b>${escapeHTML(kv[1])}</div>`;
    }).join('');
    $('details').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function closeDetails() {
    $('details').classList.add('hidden');
  }

  function selectAllVisible() {
    document.querySelectorAll('#rows input[data-id]').forEach(function (e) { S.select(e.dataset.id); });
    render();
  }

  function selectAllRecords() {
    records.forEach(function (r) { S.select(r.id); });
    render();
  }

  function clearSelection() {
    S.clearSelection();
    render();
  }

  A.views.records = {
    render: render,
    resetFilters: resetFilters,
    openRecord: openRecord,
    closeDetails: closeDetails,
    selectAllVisible: selectAllVisible,
    selectAllRecords: selectAllRecords,
    clearSelection: clearSelection
  };
})(window.Aperion);
