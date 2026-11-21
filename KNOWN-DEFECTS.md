# Known defects

## Status in v0.4.0-rc2 (branch `phase-2`)

| ID | v0.4.0 status | Evidence |
| --- | --- | --- |
| D1 | **Fixed** — only matching, present tax ID and legal name make a group eligible | `tests/phase2/test_case_data.py::test_I1`, `test_I2`; `test_progress_model.py::test_P2` |
| D2 | **Fixed** — matrix reports conflicts and missing values together, with value sets | `test_case_data.py::test_E1`, `test_E2` |
| D3 | **Fixed** — source system and last verified shown as context | `test_case_data.py::test_E1`, `test_E3` |
| D4 | **Fixed** — one-record group: "No merge needed" | `test_progress_model.py::test_P4` |
| D5 | **Fixed** — identical resubmission refused; revisions kept | `test_progress_model.py::test_P7`, `test_P13` |
| D6 | **Fixed** — check results and decisions survive navigation | `test_progress_model.py::test_P5` |
| D7 | **Fixed** — ticking a checkbox keeps keyboard focus on it | `tests/phase2/test_ux_v040.py::test_U2` |
| D8 | **Fixed** — gallery on the briefing only; one relevant stakeholder prompt per activity | `test_ux_v040.py::test_U4`, `test_U5` |
| D9 | **Fixed** — one normalization per attribute type | `test_case_data.py::test_E4` |
| D11 | **Fixed** — briefing shows its own audio status (live region) | `test_ux_v040.py::test_U3` |
| D12 | **Fixed in rc2** (approved 2026-11-11) — focus outlines Cobalt on light surfaces (6.7:1 on white, 6.2:1 on Warm Ivory), original amber kept on the Midnight sidebar (8.3:1), white inner ring on the Cobalt-filled current Menu item; field and secondary-button borders Steel Gray (3.9:1 on white, 3.6:1 on Warm Ivory) | `tests/phase2/test_contrast_v040.py` C0–C3 (every control, every state, desktop and Edge 200%) |
| Z1 | **Fixed in Chromium emulation** — compact 58 px bar (was 145 px of 330 px) with Menu and Why?; needs confirmation in real Edge at 100% and 200% | `test_ux_v040.py::test_Z1`–`test_Z8`; manual checklist section E |

### Limitations of v0.4.0-rc1 (not defects; documented for acceptance)

| ID | Limitation |
| --- | --- |
| L-1 | Progress is kept in memory only; reloading the page starts a new session (unchanged from v0.3.x). |
| L-2 | The Governance Judgment rationale criterion (GJ2) checks that the rationale names the identity evidence (tax ID or legal name). It is a keyword rule and cannot judge the quality of the writing. |
| L-3 | At very short viewports (under 300 px high, e.g. 400% zoom) the Next Step bar joins the page flow instead of staying fixed, so it never covers content; the learner scrolls to reach it. |
| L-4 | Retry keeps earlier attempts' scores but not their full answers; the debrief shows the latest attempt in detail. |
| L-5 | Stakeholder prompts are text; recorded narration for them is outside v0.4.0 (provider not selected). |
| L-6 | Edge, Firefox, Safari, screen readers, real voices, and axe-core scans have not been run in this workspace (see `TESTING.md`). |
| L-7 | Native checkboxes and radio buttons are drawn by the browser; their outlines (about 4.5:1 in Chromium) are not styled by Aperion. Their focus outlines are checked. Forced-colors (Windows high-contrast) mode uses system colors and needs manual confirmation. |

The sections below describe the defects as they exist in v0.3.2 and v0.3.3-rc1, which are preserved
unchanged and still tested by `tests/phase1`.

These defects exist in v0.3.2 and are **deliberately preserved** in v0.3.3 (Phase 1), because Phase 1 changes no behavior. The automated tests record them so that any change to them is visible and intentional.

**Nothing in this list is approved behavior.** A passing test that records one of these defects means "the defect is still present, as expected," not "this is correct."

## Instructional-integrity defects — must be fixed in Phase 2

### D1 — Invalid merge eligibility (High)

The governance validator only blocks a group when tax identifiers conflict. It ignores legal name, parent organization, and address as blocking evidence.

- **Reproduce:** Match & Compare with all records selected. Assign REB-33907 (Northbridge Healthcare, no tax ID) and CRM-10814 (Northbridge Health Partners, parent "Independent", Everett address) to the same group. Validate.
- **Current result:** "REVIEW REQUIRED: incomplete or differing identity evidence" and a **Submit merge proposal for review** button. The learner can submit a merge of two unrelated legal entities.
- **Required result (approved requirement):** a merge must not be accepted simply because records share similar names or organizational relationships.
- **Test:** `test_C3_D1_unrelated_entities_can_be_submitted` (flagged `known_defect`).

### D2 — Missing values hide conflicts (High)

The comparison matrix reports one state per attribute. If any value is missing, the row is labelled "Missing evidence" even when the present values contradict each other.

- **Reproduce:** select all 6 records and open Match & Compare.
- **Current result:** Legal name shows 3 distinct values and Tax identifier shows 3 distinct values, but both rows are labelled only "Missing evidence".
- **Required result (approved requirement):** missing attribute values must never conceal contradictory evidence.
- **Test:** `test_C4_D2_missing_hides_conflict` (flagged `known_defect`).

## Other defects — scheduled for Phase 2 or later

| ID | Severity | Defect | Test |
| --- | --- | --- | --- |
| D3 | Medium | Source system and Last verified rows labelled "Conflict / difference" although they are expected to differ | `test_C5_D3_metadata_rows_flagged_as_conflict` |
| D4 | Medium | A one-record group is labelled "ELIGIBLE FOR GOVERNANCE REVIEW" | `test_C1_correct_grouping_verdicts` |
| D5 | Medium | The same proposal can be submitted repeatedly | `test_C6_D5_duplicate_proposals_counted` |
| D6 | Medium | Validation results disappear after leaving and returning to Match & Compare | `test_C7_D6_validation_results_lost_on_return` |
| D7 | Medium | Ticking a record checkbox moves keyboard focus to the page body | `test_C8_D7_checkbox_focus_lost` |
| D8 | Medium | Case stakeholders panel appears on every page (approved Phase 2 change: contextual stakeholders) | `test_C11_D8_stakeholders_on_every_page` |
| D9 | Low | Addresses not normalized; legal-name normalization differs between matrix and validator | `test_rule_norm_characterization` |
| D11 | Low | Mission Briefing audio status messages go to an element on the hidden Records page | `test_D11_briefing_status_target_hidden` |
| D12 | Low | Focus outline and form-control borders below 3:1 contrast (WCAG 1.4.11) | `test_D12_contrast_baseline` |

Defect IDs match the v0.3.2 technical assessment. D10 has been reclassified (see below); its ID is retired and not reused.

## Reclassified as approved behavior

### Former D10 — Selection persists through filtering (approved 2026-11-05)

Filtering affects which records are **visible**, not which are **selected**. Records hidden by a search or filter remain selected and are included in "Evaluate selected records (n)" and in Match & Compare. This is intended.

- **Test:** `test_C9_selection_persists_through_filtering` (an approved-behavior test, not a known-defect test).

## Documented UX improvements (not defects; not scheduled for Phase 1)

### UX-1 — Distinguish visible records from total selected records

With a filter active, the table can show "Showing 2 of 6 records." while the button says "Evaluate selected records (6)". Learners may not realize hidden records are still selected.

- **Improvement needed:** make the difference explicit, for example "6 selected (4 hidden by filters)", and make it reachable to screen readers.
- **Constraint:** must not change selection behavior. Requires design approval before implementation.

### UX-2 — Make the "Clear groups" action explicit

"Clear groups" clears group assignments only for records that are currently selected. Assignments
for deselected records are kept and return when those records are reselected (approved behavior,
decision B2; test `test_T3_clear_groups_affects_only_selected_records`).

- **Improvement needed:** a label or confirmation that states the scope, for example
  "Clear groups for selected records", so learners do not assume every assignment was removed.
- **Constraint:** must not change the clearing behavior. Requires design approval before implementation.
