# Aperion v0.4.0 — release notes (release candidate 2)

**Status:** release candidate for acceptance testing. Not released, not merged, not deployed.
Built on the v0.3.3-rc1 release candidate, which is preserved unchanged in `baseline/v0.3.3-rc1/`.

## The learner experience, end to end

1. **Mission Briefing** — Maya's assignment (transcript and optional narration) and the full stakeholder gallery.
2. **Customer Records** — six records from CRM, ERP, and Rebates; labelled search and filters; record details.
3. **Match & Compare** — evidence matrix (conflicts and missing values shown together, value sets, context rows);
   a decision for each record: identity group, Keep separate, or Hold for verification; governance identity
   check; merge proposals with revision history.
4. **Golden Record** — for each proposal, choose each attribute's value from the group's own records and the
   evidence that justifies it; operating and billing addresses decided separately; saved revisions.
5. **Validation** — identity evidence, written rationale, automatic governance checklist, advisory evidence
   checks, "Submitted for Governance Review" (never an approval), explanations for records not proposed, and a
   follow-up for the held record. Finish the case.
6. **Debrief** — 23-point competency assessment (Evidence Analysis 4, Identity Resolution 4, Data
   Reconciliation 12, Governance Judgment 3), Proficient / Developing / Needs Practice per competency,
   decision-specific feedback, decision review, submission history, and "Try the case again".

## Changes from v0.3.3

| Area | Change | Defects fixed |
| --- | --- | --- |
| Identity rules | Eligibility only from present, matching tax ID and legal name; contradictions block; missing evidence requires verification; single records need no merge; legal-name variants (Inc./Incorporated, LLC/L.L.C., punctuation, case) match | D1, D4, D9 |
| Evidence matrix | Conflicts and missing values reported together; value sets; source system and verification date shown as context | D2, D3 |
| Progress model | Decisions, check results, proposals, golden records, and validation survive navigation; out-of-date results flagged | D6 |
| Proposals | Identical resubmissions refused; changes become revisions with history | D5 |
| New activities | Golden Record, Validation, Debrief | — |
| Next Step | Always names the learner's actual next action and moves focus there; explains when disabled | — |
| Comparison buttons | Same wording, count, enabled state, and action | — |
| Filters | Visible labels: Search records, Source system, Record status | — |
| Records | Ticking a checkbox keeps keyboard focus | D7 |
| Briefing audio | Status messages shown on the briefing itself | D11 |
| Stakeholders | Gallery on the briefing only; one relevant stakeholder's guidance per activity, as text | D8 |
| Constrained screens | Compact 58 px Next Step bar with Menu (visible activity navigation) and Why? (explanation) for narrow or short viewports, including Edge at 200% zoom | Z1 |
| Record notes | Rewritten as neutral investigative information; no answers revealed | — |
| Focus and borders | Focus outlines and control borders at least 3:1 (Cobalt focus outlines; amber kept on the sidebar; Steel Gray borders). Added in rc2 | D12 |
| Version label | V0.4.0 | — |

## Not changed

Maya's narration (browser speech synthesis), the visual identity (Midnight, Cobalt, Steel Gray, Warm Ivory),
the six records and their values, search and filter behavior, selection persistence through filtering (A2),
retained decisions for deselected records (G5), and Clear groups affecting only selected records (B2).

## Known limitations

See `KNOWN-DEFECTS.md` and `ACCESSIBILITY-STATUS.md`. In short: Edge, Safari, Firefox, screen readers, and real voices need manual testing; axe-core scans run
only in GitHub Actions; progress resets on page reload.
