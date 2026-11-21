# Accessibility status — v0.4.0 release candidate 2

Target: WCAG 2.1 AA.

## Changes in v0.4.0

| Item | WCAG | Status | Evidence |
| --- | --- | --- | --- |
| D7 checkbox focus | 2.4.3 | Fixed | `test_ux_v040.py::test_U2` |
| D11 briefing audio status | 4.1.3 | Fixed | `test_U3` |
| Filters have visible labels | 3.3.2, 2.5.3 | Done | `test_U1` |
| Current sidebar item marked with `aria-current` | 4.1.2 | Done | `test_progress_model.py` |
| Next Step names the actual next action, moves focus there, and explains when unavailable | 2.4.3, 3.3.2 | Done | `test_progress_model.py` N1–N5 |
| Edge 200%: compact bar, keyboard Menu, Why? for screen readers, focused controls not hidden | 1.4.10, 2.4.7, 2.4.11 | Done in emulation; confirm in real Edge | `test_ux_v040.py` Z1–Z8 |
| 320 px reflow | 1.4.10 | Done | `test_Z7` |
| New screens: labelled controls, live status messages, keyboard reachable, visible focus | 1.3.1, 4.1.2, 4.1.3, 2.1.1, 2.4.7 | Done | `test_accessibility_v040.py` X1–X5 |
| Scores shown with text, not only symbols or color (✓/✗ have text equivalents) | 1.1.1, 1.4.1 | Done | `test_validation_debrief.py` |
| D12 focus outline and control-border contrast | 1.4.11 | Fixed in rc2 | `test_contrast_v040.py` C0–C3 |

The sections below are the v0.3.3 assessment, kept for reference. Items fixed above are no longer open.

## v0.3.3 assessment (reference)

Target: WCAG 2.1 AA. v0.3.3 changes no accessibility behavior; every item below is also true of
v0.3.2. Fixes are Phase 2 or later and need approval.

## Confirmed accessibility defects (in `KNOWN-DEFECTS.md`)

| ID | WCAG | Issue | Evidence |
| --- | --- | --- | --- |
| D7 | 2.4.3 Focus Order | Ticking a record checkbox rebuilds the table; keyboard focus jumps to the page body | `test_C8_D7_checkbox_focus_lost` |
| D11 | 4.1.3 Status Messages | On Mission Briefing, audio status messages go to an element on the hidden Records page | `test_D11_briefing_status_target_hidden` |
| D12 | 1.4.11 Non-text Contrast | Focus outline (#F1A73C) about 2.0:1 on white and ivory; input and secondary-button borders about 2.0:1 | `test_D12_contrast_baseline` |

## Further findings from the v0.3.2 technical assessment (not yet in the defect register)

Recorded here so they are not lost. Confidence: **Code** = clear from the code; **Test** = needs
manual or assistive-technology testing to confirm.

| Issue | WCAG | Confidence |
| --- | --- | --- |
| Page changes do not move focus or announce the new page title | 2.4.3, 4.1.3 | Code |
| Current sidebar item not marked with `aria-current` | 4.1.2 (best practice) | Code |
| A disabled Next Step button cannot receive focus, so its reason may be missed by keyboard and screen-reader users | 3.3.2 / usability | Code |
| No skip link to main content | 2.4.1 | Code |
| Group-table header cells lack `scope` | 1.3.1 | Code |
| Unicode symbols used as navigation icons may be read aloud | 1.1.1 | Test |
| Sticky Next Step bar may cover focused controls at high zoom or on phones | 2.4.7 / 2.4.11 (2.2) | Test |
| Speech synthesis may talk over a screen reader | Usability | Test |
| Smooth scrolling ignores the reduced-motion preference | 2.3.3 (AAA) | Code |
| Record details "source notes" reveal answers (instructional design, not WCAG) | — | Code |

## Accessibility tests still outstanding

| Test | Status | How it will run |
| --- | --- | --- |
| axe-core WCAG 2.1 A/AA scan, 9 learner states × 3 targets | Prepared; cannot run in the development workspace (package installs blocked) | GitHub Actions, first run after the repository is created |
| Screen readers: NVDA, JAWS, VoiceOver (macOS and iOS), TalkBack | Not run | Manual checklist D3–D4 |
| 200% and 400% zoom, 320 px reflow, text spacing | Not run | Manual checklist E1–E4, E6 |
| Windows high-contrast (forced colors) mode | Not run | Manual checklist E5 |
| Responsive resizing and orientation | Not run | Manual checklist E7–E8 |
| Keyboard-only path in real browsers other than Chromium | Not run | Manual checklist D1–D2 |

## What is covered automatically (every run, all targets)

- Accessibility tree (roles, names, states) identical to v0.3.2 in 9 learner states.
- Built-in audit in 9 states: control names, form labels, image alt text, duplicate IDs, text contrast (1.4.3).
- Full Tab order on three pages identical to v0.3.2; keyboard-only core path; audio toggle by keyboard.
- `aria-pressed` and `aria-label` states of audio controls.

Automated checks find only part of real accessibility problems. Manual and assistive-technology
testing is required before release.
