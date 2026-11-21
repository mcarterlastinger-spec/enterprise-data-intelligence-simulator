/*
 * Learner state store.
 *
 * Holds the same learner state v0.3.2 kept in separate top-level variables, with the same
 * values and lifetimes (everything resets when the page is reloaded, as in v0.3.2):
 *
 *   selected            Set of selected record IDs. Kept when records are filtered out of view
 *                       (approved behavior, decision A2).
 *   current             The record last opened in the details panel.
 *   groupAssignments    Record ID -> group letter ('' when set back to Unassigned). Kept for
 *                       records that are deselected (approved behavior G5); validation only
 *                       considers currently selected records.
 *   mergeAudit          Merge proposals logged this session.
 *   activeLearningPage  The page the Next Step bar describes.
 *
 * All changes go through the functions below, and each change is appended to `events`.
 * The event list is not shown to learners in Phase 1; it exists so later phases can add
 * saving, undo, and decision history without another restructure.
 */
(function (A) {
  'use strict';
  A.registerModule('state', ['namespace']);

  var S = {
    selected: new Set(),
    current: null,
    groupAssignments: {},
    mergeAudit: [],
    activeLearningPage: 'brief',
    events: []
  };

  function record(type, detail) {
    S.events.push({ type: type, detail: detail, at: Date.now() });
  }

  S.select = function (id) {
    S.selected.add(id);
    record('select', { id: id });
  };

  S.deselect = function (id) {
    S.selected.delete(id);
    record('deselect', { id: id });
  };

  S.clearSelection = function () {
    S.selected.clear();
    record('clear-selection', {});
  };

  S.setCurrent = function (rec) {
    S.current = rec;
    record('open-record', { id: rec ? rec.id : null });
  };

  S.setGroup = function (id, group) {
    S.groupAssignments[id] = group;
    record('set-group', { id: id, group: group });
  };

  S.clearGroups = function (ids) {
    ids.forEach(function (id) { delete S.groupAssignments[id]; });
    record('clear-groups', { ids: ids.slice() });
  };

  S.addProposal = function (proposal) {
    S.mergeAudit.push(proposal);
    record('propose-merge', proposal);
  };

  S.setActivePage = function (page) {
    S.activeLearningPage = page;
  };

  A.state = S;
})(window.Aperion);
