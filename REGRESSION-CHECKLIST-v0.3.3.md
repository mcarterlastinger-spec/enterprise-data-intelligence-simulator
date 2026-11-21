# Manual acceptance checklist — v0.3.3 release candidate

Automated tests do not replace this checklist (decision, 2026-11-05). Phase 1 is not complete until
the project owner has run it and approved the release.

## How to use this checklist

1. Open the **original** `baseline/v0.3.2/index.html` and the **release candidate** side by side in
   the same browser. Unless a step says otherwise, the release candidate must behave exactly like
   v0.3.2. The **only** intended visible difference is the version label (V0.3.3 instead of V0.3.2).
2. Test the release candidate in two forms:
   - **Modular:** `site/index.html` from `aperion-v0.3.3-rc1-modular.zip` (unzip first; keep the folder together).
   - **Standalone:** `aperion-v0.3.3-standalone.html` (one file).
3. For each item, record **Same**, **Different** (describe it), or **Not tested**, with the browser and device.
4. Known defects (see `KNOWN-DEFECTS.md`) are **expected to still occur** in v0.3.3. Record them as
   Same if they behave as in v0.3.2. They are not approved behavior.

| Record per session | |
| --- | --- |
| Tester | |
| Date | |
| Browser and version | |
| Operating system and device | |
| Form tested | Modular / Standalone |

---

## A. Opening the release candidate

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| A1 | Double-click `aperion-v0.3.3-standalone.html` (or right-click > Open with > **Microsoft Edge**). | Mission Briefing opens. No blank page, no broken images. | |
| A2 | Disconnect from the internet (or turn on airplane mode), then reload the standalone file. | Everything still works. The file needs no network. | |
| A3 | Unzip the modular package and double-click `site/index.html`. | Same as A1. | |
| A4 | In a terminal: `cd site` then `python3 -m http.server 8000`; open `http://localhost:8000`. | Same as A1. (This is how GitHub Pages serves it.) | |
| A5 | Check the header pill and footer. | Pill reads **FUNCTIONAL PROTOTYPE · V0.3.3**; footer reads **Prototype v0.3.3**. The baseline still reads V0.3.2. | |

## B. Learner experience (Edge, Chrome, and Safari on desktop)

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| B1 | Compare Mission Briefing with v0.3.2. | Same portrait, transcript, four stakeholder cards, colors (Midnight, Cobalt, Steel Gray, Warm Ivory), spacing, and fonts. | |
| B2 | Scroll each page. | Next Step bar text, color, and position match; it stays visible while scrolling. | |
| B3 | Select **Next Step: Explore Customer Records**. | Customer Record Workspace opens with six records. | |
| B4 | Search "medical", then filter System = ERP, then Status = Active, then **Reset**. | Results, counts, and empty-result message match v0.3.2 at each step. | |
| B5 | Open record **REB-33907**, then **Close details**. | Same eight fields and the same scroll behavior. | |
| B6 | **Select all visible** (with a filter on), **Select all records**, **Clear selection**. | The Evaluate button count matches v0.3.2 at each step. | |
| B7 | With all six selected, filter to ERP. | "Showing 2 of 6 records." and "Evaluate selected records (6)": hidden records stay selected (approved behavior). | |
| B8 | Open **Match & Compare** with all six records. | Matrix labels, colors, and horizontal scrolling match. **Known defect D2:** Legal name and Tax identifier show only "Missing evidence". | |
| B9 | Assign A: CRM-10452, ERP-77831, REB-33907; B: CRM-10489, ERP-77902; C: CRM-10814. **Validate proposed groups**. | A: Review required; B: Eligible; C: Eligible (**known defect D4**). | |
| B10 | Assign REB-33907 and CRM-10814 to Group D only; validate. | **Known defect D1:** "Review required" with a Submit button. | |
| B11 | Submit a proposal twice. | Count increases to 2 (**known defect D5**). | |
| B12 | Change a group after validating. | "Groups changed. Run validation again before review." | |
| B13 | Go to Records and back to Compare. | Group choices kept; validation results gone (**known defect D6**). | |
| B14 | Deselect CRM-10814, return to Compare, **Clear groups**, reselect CRM-10814, return to Compare. | Only selected records were cleared; CRM-10814 still shows its earlier group (approved behavior). | |
| B15 | Next Step on each page. | Briefing → Records → (2+ selected) Compare → back to Records. Disabled with a count message when fewer than 2 are selected. | |
| B16 | Sidebar: Golden Record and Validation. | Disabled, "(next)", tooltip "Planned for next milestone". | |

## C. Audio (real voices; cannot be automated)

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| C1 | Open Customer Records and look at the voice list. | Same Maya voice candidates as v0.3.2 in the same browser, or the "No known feminine-sounding voice" message. | |
| C2 | Mission Briefing: **Play**. | Maya's briefing plays; button changes to **Pause**. | |
| C3 | **Pause**, then **Resume**. | Audio pauses and resumes by ear; labels change to Resume, then Pause. | |
| C4 | **Replay**. | Restarts from the beginning. | |
| C5 | While Maya is speaking, select **Next Step**. | Audio stops immediately. | |
| C6 | Let the full briefing play. | Plays to the end without being cut off (Chrome on Windows is the most likely to fail; compare with v0.3.2). | |

## D. Keyboard and screen reader

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| D1 | Using only Tab, Shift+Tab, Enter, Space, and arrow keys: Briefing → Records → select 2 records → Compare → assign groups → Validate. | Possible end to end, as in v0.3.2. **Known defect D7:** after ticking a checkbox, focus jumps to the top of the page. | |
| D2 | Tab through each page. | Focus order and visible focus outline match v0.3.2. | |
| D3 | **NVDA** (Windows) or **VoiceOver** (macOS: Cmd+F5): read each page; navigate headings and tables. | Headings, buttons, table headers, and the results count are announced as in v0.3.2. | |
| D4 | Play audio while a screen reader is on. | Note whether speech overlaps the screen reader (same as v0.3.2 expected). | |

## E. Zoom, reflow, contrast modes, and resizing (WCAG 2.1 AA)

Use Edge or Chrome on desktop unless noted. Compare with v0.3.2 in the same browser.

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| E1 | **200% zoom** (Ctrl/Cmd and +) with a 1280 px wide window, every page. | Text and controls readable and usable; nothing clipped or overlapping; no lost content or function (1.4.4). | |
| E2 | **400% zoom** at 1280 px wide (≈ 320 CSS px). | Content reflows to one column; no horizontal scrolling except inside the data tables and matrix (1.4.10). | |
| E3 | **320 px reflow**: narrow the window, or use DevTools device toolbar (F12 > Ctrl+Shift+M) at 320 px. | Same as E2; sidebar and Next Step bar remain usable. | |
| E4 | At 200% and 400%, Tab through each page. | Note whether the sticky Next Step bar covers the focused control, and how much screen it uses. | |
| E5 | **Windows high-contrast mode** (Settings > Accessibility > Contrast themes; then Edge). | Buttons, focus outlines, checkboxes, selects, disabled navigation, matrix states, and audio buttons remain distinguishable. | |
| E6 | **Text spacing** (optional bookmarklet): line height 1.5, letter spacing 0.12 em, word spacing 0.16 em. | No text cut off (1.4.12). | |
| E7 | **Responsive resizing**: slowly drag the window from 1400 px to 320 px and back on each page, with records selected, groups assigned, and record details open. | Layout switches at about 980, 700, and 570 px as in v0.3.2; nothing jumps or disappears; selections, groups, and details are kept. | |
| E8 | **Orientation** (phone or tablet): rotate on each page. | Content and learner choices are kept (1.3.4). | |

## F. Phone and tablet

| ID | Step | Expected result | Result |
| --- | --- | --- | --- |
| F1 | iPhone Safari and Android Chrome: open the release candidate (modular via a local server or GitHub Pages preview later; standalone via Files app). | Layout, sidebar, sticky Next Step bar, and matrix scrolling match v0.3.2. | |
| F2 | Tap through B3–B15. | Same results as desktop. | |

## G. Release decision

| Question | Answer |
| --- | --- |
| Any **Different** results not explained by the version label? | |
| Any known defect behaving differently from v0.3.2? | |
| Outstanding items not tested, and why | |
| Approve v0.3.3 for release? (Yes / No / Yes with conditions) | |
| Approved by, date | |
