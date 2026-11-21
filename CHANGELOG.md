# Changelog

## v0.4.0 — release candidate 2 (tag `v0.4.0-rc2`; awaiting acceptance)

### Release candidate 2: D12 correction (decision P2-16)

- Focus outlines and control borders meet WCAG 2.1 SC 1.4.11 (at least 3:1) using the approved palette:
  Cobalt focus outlines on light surfaces, amber kept on the Midnight sidebar, Steel Gray borders on fields
  and secondary buttons. CSS only: `base.css`, `components.css`, `next-step.css`, `compact-nav.css`.
- New `tests/phase2/test_contrast_v040.py` with an in-page audit (`contrast_audit.js`) of every enabled
  control in every learner state, at desktop size and at emulated Edge 200% (including the Menu and Why?
  panels), and a control test showing the same audit reports D12 in v0.3.3-rc1.
- `test_D12_contrast_baseline` (which recorded the defective colors) no longer runs on v0.4.0; it still runs on
  the frozen v0.3.x targets. The region comparison with v0.3.3-rc1 (`test_E1`) normalizes the approved border
  color, as it already does for the version label.
- No functional, content, or layout changes.

## v0.4.0 — release candidate 1 (Phase 2, branch `phase-2`, tag `v0.4.0-rc1`)

### Release candidate 1: Steps 4–7

- **Step 4, Validation:** new activity. Per proposal: identity evidence, written rationale (at least 12
  words), automatic governance checklist, advisory evidence-consistency findings, "Submitted for Governance
  Review" status (never approval), revalidation after changes, submission history. Records not proposed:
  reason for each; follow-up for the held record. Finish case (decision P2-11).
- **Step 5, Debrief and scoring:** `rules/scoring.js`, 23 points in four competencies, levels, decision-specific
  feedback, "How scoring works", decision review, submission history, read-only review, retry with attempt
  history (P2-12, P2-13).
- **Step 6, UX:** compact Next Step bar with Menu and Why? for narrow and short viewports, including Edge at
  200% (Z1, P2-10); visible filter labels; checkbox keeps focus (D7); briefing audio status (D11); contextual
  stakeholder prompts (D8); Next Step guides through Validation and Debrief.
- **Step 7, hardening:** new tests (`test_validation_debrief.py`, `test_ux_v040.py`), full regression on all
  targets, documentation, standalone `dist/aperion-v0.4.0-standalone.html`, release copy in
  `release/v0.4.0-rc1/`.
  Found and fixed during hardening: on short viewports (Edge 200% on a laptop) the Menu panel cut off the
  sixth activity (Debrief) behind a scroll; items are now compact enough that all six show, with a test
  (`test_Z2`). Added `test_E5` (legal-name variants and the correct Group A and B records, P2-14).
- New files: `rules/golden.js`, `rules/scoring.js`, `views/validation.js`, `views/debrief.js`,
  `views/stakeholders.js`, `views/nextbar.js`, `css/compact-nav.css`. `REGRESSION-CHECKLIST.md` is now the v0.4.0
  checklist; the v0.3.3 one is `REGRESSION-CHECKLIST-v0.3.3.md`.

### Checkpoint 1: Steps 1–3

- **Baseline:** v0.3.3-rc1 frozen in `baseline/v0.3.3-rc1/` with checksums (decision P2-8). Phase 1 tests
  moved to `tests/phase1` and still compare v0.3.2 with the frozen rc1.
- **Step 1, identity rules:** `rules/identity.js` replaces `rules/governance.js`. Eligibility requires a present,
  matching tax ID and legal name in every record; contradictions block; missing evidence requires verification;
  single records need no merge. `rules/matching.js` reports conflicts and missing values together, value sets,
  and context rows. Answer key and golden-record design in `data/case.js`. Record notes rewritten as neutral
  investigative information. Fixes D1, D2, D3, D4, D9.
- **Step 2, progress model:** `state.js` keeps identity decisions (group, Keep separate, Hold for verification),
  the last check and whether it is out of date, proposal revisions, golden-record drafts and revisions, and an
  event log. Identical resubmissions refused. Next Step works out the learner's actual next action and moves
  focus there; both comparison buttons share wording, count, and enabled state; `aria-current` on the sidebar.
  Fixes D5, D6.
- **Step 3, Golden Record:** new activity and sidebar item. One golden record per current proposal; six
  attributes (legal name, tax ID, operating address, billing address, parent, primary contact); values only
  from the group's records; each needs an evidence reason; save creates revisions; unchanged saves refused.
- Version label V0.4.0; standalone build `dist/aperion-v0.4.0-standalone.html`.
- Tests: `tests/phase2` (rules, data, progress, Next Step, golden record, accessibility of new screens, and
  still-valid Phase 1 tests re-run on v0.4.0, plus region screenshots vs v0.3.3-rc1).

## v0.3.3 — release candidate 1 (Phase 1; awaiting acceptance)

Behavior-preserving restructure and test foundation. The only learner-visible change is the version label.

### Release candidate 1 (tag `v0.3.3-rc1`)

- Version label in the header pill and footer changed from V0.3.2 to V0.3.3 (decision B3). Baseline unchanged.
- Added `tools/build_standalone.py` and the standalone distribution `dist/aperion-v0.3.3-standalone.html`
  (deterministic; lists the SHA-256 of every inlined source file).
- Tests now run against three targets: baseline, modular site, and standalone. Added version-label,
  self-contained (all other requests blocked), and standalone-up-to-date tests. Side-by-side comparisons
  mask only the approved version label.
- CI builds the standalone file and tests all three targets.
- Added a manual-only GitHub workflow, "Rollback Pages to v0.3.2", that republishes the preserved
  baseline file after verifying its checksum.
- Test-harness fixes found while preparing RC1 (no application changes):
  - The version-label mask did not apply (a regular-expression escape was lost), so screenshots of the
    release candidate failed. Fixed, and each comparison now asserts the mask took effect.
  - The full Tab-order comparison could differ after focus left the page (browser-dependent wrap).
    It now records exactly one pass, starting from the top of the page.
  - The "no inline handlers" check matched the word `onclick` inside a code comment in the standalone
    file. It now checks markup only.
- Documented UX-2 (explicit "Clear groups" label) and decisions B1–B7.
- Added `DEPLOYMENT.md`, `ACCESSIBILITY-STATUS.md`, and `RELEASE-NOTES-v0.3.3.md`; rewrote the manual
  checklist as a step-by-step acceptance checklist; updated `README.md`, `TESTING.md`, and `ROLLBACK.md`.

### Checkpoint B — restructured application (branch `phase-1-modularize`)

No learner-facing changes. Version label in the interface still reads V0.3.2 until release approval.

- Step 3: portraits moved to `site/assets/avatars/` (4 files, byte-identical; Maya was embedded 3 times).
- Step 4: stylesheet split into five files in original cascade order; CSS verified token-for-token identical.
- Steps 5–7: JavaScript moved into 13 ordinary script files under `window.Aperion`; learner state
  centralized in `state.js`; matching and governance rules extracted as pure functions (known defects
  preserved); inline `onclick` replaced by `data-action` attributes and one document listener.
- `index.html` formatted for readability (line breaks only before block-level tags).
- Tests: retained-decision tests (filtering, deselection, Clear groups), structure tests (load order,
  single global, data identity, wrong-order failure); DOM comparison maps `onclick` to `data-action`.
- Manual checklist: 200% and 400% zoom, 320 px reflow, Windows high contrast, text spacing,
  responsive resizing, and orientation. Added `TESTING.md` (including tests that cannot run here).
- Page weight (HTML + CSS + JS + images): 665 KB → 346 KB (images 292 KB, code and markup 54 KB).

### Checkpoint A revision 1 — after review

- Reclassified former D10 as approved behavior (selection persists through filtering); added UX-1 to document the needed visible-vs-selected clarity improvement. No behavior change.
- Added a static baseline-integrity test that verifies the v0.3.2 checksums on every run.
- Recorded Checkpoint A review decisions in `DECISIONS.md`.

### Checkpoint A — baseline and characterization tests

- Added the untouched v0.3.2 application and original ZIP under `baseline/v0.3.2/` with checksums.
- `site/index.html` is currently a byte-identical copy of v0.3.2 (restructuring has not started).
- Added characterization tests that record v0.3.2 behavior, including known defects (see `KNOWN-DEFECTS.md`).
- Added `DECISIONS.md`, `KNOWN-DEFECTS.md`, `README.md`, and `ROLLBACK.md`.
- Prepared a GitHub Actions workflow (not yet connected to any repository).

## v0.3.2 — baseline

Original functional prototype as supplied. Preserved unchanged in `baseline/v0.3.2/`.
