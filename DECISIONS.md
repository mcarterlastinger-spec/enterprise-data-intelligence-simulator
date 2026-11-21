# Decisions log

Approved decisions for the Aperion Enterprise Data Intelligence Simulator. Newest first.

## 2026-11-11 — D12 correction authorized (v0.4.0-rc2)

| # | Decision | Implementation |
| --- | --- | --- |
| P2-16 | Correct D12: focus outlines and control borders meet WCAG 2.1 AA non-text contrast (1.4.11), preserving the visual identity, functionality, and the rc1 baseline; deliver as a separate candidate | Approved palette only. Focus outline: Cobalt `#2457B8` on light surfaces (was amber `#F1A73C`, 2.03:1; Next Step button `#F0B34A`, 1.87:1); amber kept on the Midnight sidebar, where it passes and Cobalt would not; white inner ring on the Cobalt-filled current Menu item. Borders of search, filters, identity-decision selects, and secondary buttons: Steel Gray `#71839D` (was `#A9B6C8`/`#AAB7C9`, about 2.05:1). Textareas, summaries, and links now share the same focus outline. rc1 stays tagged `v0.4.0-rc1`; rc2 is tagged `v0.4.0-rc2`. |

## 2026-11-11 — Steps 4–7 approved (v0.4.0 release candidate)

Owner's refinements, and how they were implemented.

| # | Decision | Implementation |
| --- | --- | --- |
| P2-10 | Edge 200% navigation: compact Next Step bar (about 60 px); Menu shows navigation visibly and by keyboard; Next Step visible, context-aware, and operable; Why? available to keyboard and screen readers; bar never hides content, drop-downs, or validation feedback | `css/compact-nav.css`, `views/nextbar.js`. Compact layout when the viewport is under 981 px wide or 601 px high; measured 58 px at Edge-200 emulation. Menu opens a visible activity list (`nav#nsb-menu-panel`) and focuses its first item; Why? toggles the description (`aria-expanded`, `aria-describedby`); Escape closes either; `scroll-padding-bottom` keeps focused controls above the bar. Under 300 px high the bar joins the page flow (L-3). |
| P2-11 | Validation: automatic governance checklist, required written rationale, revision tracking; success reads "Submitted for Governance Review" and implies no merge or approval; changes after submission require revalidation and keep history | `views/validation.js`, `state.js`. Checklist items: identity check eligible, golden record saved, golden record current, identity evidence selected, rationale of at least 12 words. Submission fingerprint (proposal revision, golden revision, evidence, rationale) detects changes. |
| P2-12 | Scoring: four competencies, 23 points; no duplicate credit; Evidence Analysis measures interpretation, not clicks; earned points, levels, and decision-specific feedback; thresholds Proficient ≥85%, Developing ≥50%, Needs Practice <50%; criteria explained to the learner | `rules/scoring.js` (pure function of the finished snapshot). Evidence Analysis 4 (identity evidence for each group; why each unproposed record was not proposed); Identity Resolution 4 (each group and each unproposed record decided correctly); Data Reconciliation 12 (value and an acceptable reason for each attribute, per group); Governance Judgment 3 (all proposals submitted and current; rationale names the identity evidence; correct follow-up for the held record). Each decision is scored in exactly one criterion. |
| P2-13 | Validation and Debrief are functional activities: review decisions, understand errors, retry without compromising assessment integrity | Finishing takes a snapshot that is scored once and locks every activity (read-only review). "Try the case again" clears the work and starts a new attempt; earlier attempts' scores are kept. |
| P2-14 | Identity rules: legal-name normalization verified against the case data; valid Group A and B matches must not be rejected by overly strict comparison | Verified variants: "NORTHBRIDGE HEALTH, INC.", "Northbridge Health Incorporated", "Northbridge Medical Group, L.L.C.", and others (`test_case_data.py::test_E4`). Addresses are supporting evidence and never block a group. |
| P2-15 | Unchanged during Steps 4–7 | "Reset" button label, v0.3.3-rc1 baseline, Checkpoint 1 behavior, approved palette. D12 not changed (needs visual approval). |

## 2026-11-11 — Phase 2 plan approval (v0.4.0)

Goal: portfolio-ready end-to-end demonstration for an interview on 2026-11-12 at 1:00 PM PST.
Feature freeze 9:00 AM PST. Authorized: Steps 1–3 (identity rules, progress model, Golden Record),
then a checkpoint before Steps 4–7.

| # | Decision | Detail |
| --- | --- | --- |
| P2-1 | Identity rules and answer key | Group A CRM-10452 + ERP-77831; Group B CRM-10489 + ERP-77902; CRM-10814 keep separate; REB-33907 hold for verification. Missing tax ID = insufficient evidence, not a mismatch. Similar names, addresses, and parents alone never establish eligibility. Validate actual fields and values. |
| P2-2 | Golden Record | ERP preferred for legal identity where the evidence supports it; CRM for operating information where appropriate. No unconditional source precedence: learners choose and justify each attribute. Billing vs operating addresses distinguished. Every value must exist in the dataset. |
| P2-3 | Competencies | Evidence Analysis, Identity Resolution, Data Reconciliation, Governance Judgment; Proficient / Developing / Needs Practice; transparent numeric score only where criteria support it; decision-specific feedback; no arbitrary percentages. |
| P2-4 | Narration | Keep Maya's narration. Text prompts for Priya, Daniel, and Marcus if reliable gender-appropriate narration would risk delivery. No mismatched voices. |
| P2-5 | Edge 200% zoom | Next Step panel takes excessive space and obscures content; left navigation not visible. Fix must keep navigation and next-step guidance reachable while scrolling. Test 100% and 200% in Edge, keyboard, reflow, no obstruction. |
| P2-6 | Record notes | Replace answer-revealing notes with neutral investigative information without removing needed evidence. |
| P2-7 | Release format | v0.4.0 development version; standalone offline HTML for Edge; keep modular source. No GitHub deployment without explicit approval. |
| P2-8 | Baseline | v0.3.3-rc1 is the accepted Phase 2 baseline (not a public release); preserved unchanged; v0.4.0 developed on branch `phase-2`. |
| P2-9 | Further requirements | Synchronized comparison buttons; persistent, context-aware Next Step; visible filter labels; no duplicate submissions with meaningful revision history; decisions and feedback survive navigation; inactive records never influence validation; functional Golden Record, Validation, and Debrief; keyboard access and visible focus; passing regression tests. |

## 2026-11-07 — Checkpoint B review (conditional authorization)

| # | Decision | Detail |
| --- | --- | --- |
| B1 | Modular application | Provisionally accepted, subject to manual testing and review. |
| B2 | Clear groups | Preserve current behavior: only currently selected records have their group assignments cleared. Document a future UX enhancement for a more explicit label (UX-2). |
| B3 | Version | v0.3.3 is the final Phase 1 release version. Visible labels change only in the release candidate, never in the preserved v0.3.2 baseline. |
| B4 | Standalone build | Authorized: a self-contained HTML distribution. |
| B5 | Source of truth | The modular application (`site/`) remains the primary maintainable source; the standalone file is generated from it. |
| B6 | Preservation | Maintain the visual identity, learner interactions, and functionality. |
| B7 | Scope | No Phase 2 defect corrections and no new learner-facing features. |

Phase 1 is **not complete** until the release candidate has been reviewed, tested manually by the
project owner, and explicitly approved for release. No publication or deployment before then.
Phase 2 must not begin.

## 2026-11-05 — Checkpoint B authorization

Python with Playwright confirmed; D10 approved behavior (UX-1 future); G5 approved behavior (inactive
records must not affect validation, scoring, or publishing); baseline behaviors are observations, not
endorsements. Add 200%/400% zoom, 320 px reflow, Windows high contrast, and resizing to the manual checklist.

## 2026-11-05 — Checkpoint A review (preliminary)

| # | Decision | Detail |
| --- | --- | --- |
| A1 | Python test framework | Approved, provided tests are reproducible in GitHub Actions, dependencies are documented (`requirements-test.txt`, README), and failures are reported clearly. |
| A2 | Former D10 reclassified | Selection persisting through filtering is **expected behavior**: filtering affects visibility, not selection. Documented UX improvement UX-1 (distinguish visible from total selected). No behavior change in Phase 1. |
| A3 | Known defects | Continue documenting confirmed defects separately from approved requirements. Passing baseline tests must not imply defective behavior is acceptable. |
| A4 | Regression protection | Preserve v0.3.2, maintain checksums, retain the rollback procedure. |

Phase 1 remains at Checkpoint A; steps 3–9 are not yet authorized.

## 2026-11-05 — Phase 1 authorization

| # | Decision | Detail |
| --- | --- | --- |
| 1 | Module format | Ordinary JavaScript files under one controlled application namespace. Must keep working when `index.html` is opened directly from disk (`file://`) and on GitHub Pages. Script-loading order is documented; no unnecessary global variables. |
| 2 | Phase 1 scope | Behavior-preserving restructure and test foundation only. D1 and D2 stay for Phase 2. No business-rule corrections, no stakeholder presentation changes, and no new learner-facing functionality. |
| 3 | Repository | One dedicated public repository, `mcarterlastinger-spec/enterprise-data-intelligence-simulator`, separate from Sales Intelligence Lab and the portfolio site. Structure and deployment configuration may be prepared; creating, publishing, or deploying requires separate explicit approval. |
| 4 | Visual regression tolerance | Visual equivalence with v0.3.2, allowing up to 0.1% differing pixels attributable to rendering or anti-aliasing. Any material layout, typography, spacing, color, image, or interaction difference requires review and approval. |
| 5 | Versioning | Phase 1 releases as **v0.3.3**. v0.4.0 is reserved for a future functional release. |

### Additional requirements (same date)

1. Preserve the original v0.3.2 application unchanged (`baseline/v0.3.2/`).
2. Preserve all working navigation, comparison, grouping, avatar, audio, and Next Step functionality.
3. Maintain the Midnight, Cobalt, Steel Gray, and Warm Ivory visual identity.
4. Do not silently correct or alter instructional content or business rules.
5. Preserve learner state and existing behavior during navigation.
6. Establish automated tests using available tools.
7. Prepare browser and accessibility tests for GitHub Actions if local dependencies are unavailable.
8. Automated tests do not replace manual learner-experience testing.
9. Document all changed files, test results, limitations, and known defects.
10. Provide clear rollback instructions.

## 2026-11-05 — Direction approved after technical assessment

1. Modularize into maintainable files, preserving functionality and visual design.
2. Support GitHub Pages and a documented local workflow; investigate a self-contained build.
3. Stakeholder appearances become contextual (full gallery on Mission Briefing only). **Phase 2.**
4. Prioritize the two instructional-integrity defects (D1, D2). **Phase 2.**
5. Automated regression and accessibility tests before major functionality.
6. Keep evaluating prerecorded character narration; no provider selected until pricing, licensing, and voice quality are verified.

Requirements: a merge must not be accepted because records share similar names or organizational relationships; missing values must never conceal contradictory evidence; learners can investigate, revise, and correct decisions without losing work.

## Approved visual identity

| Name | Hex |
| --- | --- |
| Midnight | `#101D35` |
| Cobalt | `#2457B8` |
| Steel Gray | `#71839D` |
| Warm Ivory | `#F8F6F0` |
