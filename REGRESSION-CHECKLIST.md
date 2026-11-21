# Manual acceptance checklist — v0.4.0 release candidate 2

Automated tests do not replace this checklist. v0.4.0 is not released until the project owner has run
it and approved the release. The v0.3.3 checklist is kept in `REGRESSION-CHECKLIST-v0.3.3.md`.

## How to use this checklist

1. Test both forms:
   - **Standalone:** `aperion-v0.4.0-rc2-standalone.html` (one file; open directly in Edge).
   - **Modular:** `site/index.html` from `aperion-v0.4.0-rc2-modular.zip` (unzip; keep the folder together).
2. Microsoft Edge on Windows is the priority browser, at **100% and 200% zoom**.
3. Record **Pass**, **Fail** (describe it), or **Not tested** for each item, with browser and device.
4. The correct answers are in section H, for the tester only.

| Record per session | |
| --- | --- |
| Tester | |
| Date | |
| Browser and version | |
| Operating system and device | |
| Form tested | Standalone / Modular |
| Zoom | 100% / 200% |

---

## A. Opening

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| A1 | Double-click the standalone file | Opens with no network connection; header reads V0.4.0; four portraits shown | |
| A2 | Open the modular `site/index.html` from disk | Identical to A1 | |
| A3 | Turn off Wi-Fi and reload | Still works fully | |

## B. Records and Match & Compare (preserved v0.3.3 behavior plus fixes)

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| B1 | Search, Source system, and Record status filters | Each has a visible label; filtering works as in v0.3.3 | |
| B2 | Tick a record checkbox with the keyboard (Space) | Focus stays on that checkbox (D7 fixed) | |
| B3 | Select records, filter some out, compare | Hidden selections are kept (as in v0.3.3) | |
| B4 | Compare all six records | Each identity row shows conflicts **and** missing values together; Source system and Last verified are labelled as context, not conflicts | |
| B5 | Put CRM-10814 and REB-33907 in one group and check | Group is blocked or needs verification; it cannot be proposed | |
| B6 | Put one record alone in a group | "No merge needed: a single record" | |
| B7 | Propose Group A, go to Records, come back | Decisions, check result, and proposal are still there | |
| B8 | Submit the same proposal again | Refused ("already under review"); changing members creates a revision | |
| B9 | Clear groups | Clears decisions only for the selected records (as in v0.3.3) | |

## C. Golden Record

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| C1 | Open Golden Record after proposing groups | One section per proposed group; six attributes | |
| C2 | Choose values and reasons; save | "Saved as revision 1"; saving again without changes creates no new revision | |
| C3 | Choose a value with a reason that does not fit (e.g. CRM reason for an ERP value) | An advisory message explains the mismatch | |

## D. Validation (new)

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| D1 | Open Validation | Checklist per group updates automatically as items are completed | |
| D2 | Try to submit with an incomplete checklist | Submission not available; the missing items are named | |
| D3 | Write a rationale under 12 words | Checklist shows the word count and stays incomplete | |
| D4 | Complete and submit | "Submitted for Governance Review … No merge or approval has occurred." Nothing says merged or approved | |
| D5 | Change the golden record or rationale after submitting | Status changes to "Changed since submission"; resubmission creates revision 2; history keeps revision 1 | |
| D6 | Answer "Records not proposed" and the held-record follow-up | Finish case becomes available only when everything is complete; the reason is shown while it is not | |

## E. Next Step bar and navigation — Edge at 100% and 200%

At 200% zoom on a typical laptop, Edge shows a narrow, short page; the compact bar should appear.

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| E1 | 100%: look at the Next Step bar on every page | Full bar, as in v0.3.3, with the correct next action | |
| E2 | 200%: look at the bar | One slim row (about 60 px): Menu, short next-step text, Why?, Next Step button | |
| E3 | 200%: press Tab to Menu, press Enter | A visible list of activities opens above the bar with focus on the first item; Tab moves through it; Enter opens an activity; Escape closes it and returns focus to Menu | |
| E4 | 200%: Tab to Why?, press Enter | The explanation appears; a screen reader announces it; Escape closes it | |
| E5 | 200%: Tab through the page, especially the Compare decisions table and Validation form | The focused control is never hidden behind the bar | |
| E6 | 200%: open a drop-down near the bottom of the page | The list is not covered by the bar | |
| E7 | 200%: submit for governance review | The status message is visible above the bar | |
| E8 | 200%: press the Next Step button on each activity | It performs the action it names | |
| E9 | Resize the window from wide to narrow and back during the case | No work is lost; the layout adapts | |
| E10 | 400% zoom | The bar becomes part of the page (scroll to reach it); nothing is covered | |
| E11 | Windows high-contrast (forced colors) mode | All controls, the bar, and focus outlines visible | |
| E12 | Tab through every activity at 100% and 200% | Every focused control has a clearly visible outline: blue on light areas, amber in the dark sidebar, a white ring on the highlighted Menu item; search, filter, and decision fields and outlined buttons have clearly visible edges (D12) | |

## F. Debrief and retry (new)

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| F1 | Finish with the correct answers (section H) | 23 of 23; all four competencies Proficient | |
| F2 | Retry, and make deliberate mistakes | Lower score; each missed criterion has feedback that names the specific decision | |
| F3 | Open "How scoring works" | Explains 23 points, the four competencies, the thresholds (85% / 50%), and that no decision is counted twice | |
| F4 | "Review your work (read-only)" | Earlier activities shown but locked; Next Step returns to the debrief | |
| F5 | "Try the case again" | New attempt starts from the briefing; the debrief lists the earlier attempt's score | |

## G. Audio, screen readers, and devices

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| G1 | Play Maya's briefing; pause, resume, replay | Works as in v0.3.3; status shown on the briefing page (D11 fixed) | |
| G2 | Leave the briefing while speaking | Speech stops | |
| G3 | Stakeholder prompts on each activity | One relevant stakeholder per activity (Daniel, Maya, Priya, Marcus, Maya); full gallery only on the briefing | |
| G4 | NVDA or Narrator with Edge: complete Validation and read the Debrief | Labels, checklist, status messages, and scores are announced | |
| G5 | Phone or tablet (portrait) | Compact bar shown; all activities usable | |

## H. Correct answers (tester only)

- **Group A:** CRM-10452 and ERP-77831 (Northbridge Health Inc.).
- **Group B:** CRM-10489 and ERP-77902 (Northbridge Medical Group LLC).
- **CRM-10814:** Keep separate (identity evidence conflicts). **REB-33907:** Hold for verification (identity evidence missing); follow-up: request the W-9.
- **Identity evidence** for both groups: tax identifier and legal name only.
- **Golden Record, Group A:** operating address from CRM (100 Medical Parkway); billing address from ERP
  (400 Billing Plaza); primary contact from CRM; legal name, tax ID, and parent agree.
- **Rationale:** at least 12 words naming the matching tax identifier and legal name.

## I. Release decision

| Decision | Owner | Result |
| --- | --- | --- |
| Accept v0.4.0-rc2 (or rc1) for the interview demo | Carter Lastinger | |
| D12 fix appearance acceptable (item E12) | Carter Lastinger | |
| Authorize repository creation and GitHub Pages deployment | Carter Lastinger | Not authorized |
