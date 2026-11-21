# Testing

## How to run

```sh
python3 -m pip install -r requirements-test.txt
python3 -m playwright install chromium        # not needed if Google Chrome is installed
python3 tools/build_standalone.py             # build the standalone file first
python3 -m pytest                             # everything
python3 -m pytest tests/phase2                # v0.4.0 tests only
APERION_P2_TARGETS=site python3 -m pytest tests/phase2   # only the modular site
```

Failures name the test and the expected and actual values; screenshot failures save images to
`tests/output/`. Dependencies (developer-only, never shipped): Python 3.10+, pytest, Playwright for Python,
Pillow, NumPy, and a Chromium browser.

## Layout and targets

| Suite | Purpose | Targets (environment variable) |
| --- | --- | --- |
| `tests/test_baseline_integrity.py` | Checksums of the frozen v0.3.2 and v0.3.3-rc1 baselines | — |
| `tests/phase1/` | The accepted Phase 1 suite: v0.3.3-rc1 still behaves exactly like v0.3.2 | `baseline`, `rc1`, `rc1-standalone` (`APERION_TARGETS`) |
| `tests/phase2/` | v0.4.0: case data and rules, progress model, Golden Record, Validation, scoring, Debrief, UX and compact navigation, accessibility of new screens, still-valid Phase 1 tests re-run on v0.4.0, and region screenshots of unchanged areas against v0.3.3-rc1 | `site`, `standalone` (`APERION_P2_TARGETS`) |

| Target | File |
| --- | --- |
| `baseline` | `baseline/v0.3.2/index.html` (never edited) |
| `rc1`, `rc1-standalone` | `baseline/v0.3.3-rc1/` (frozen; never edited) |
| `site` | `site/index.html` (v0.4.0 modular source) |
| `standalone` | `dist/aperion-v0.4.0-standalone.html` |

Non-text contrast (WCAG 1.4.11, D12) is checked by `tests/phase2/test_contrast_v040.py`, which runs an in-page
audit (`contrast_audit.js`) on every enabled control in every learner state at desktop size and at emulated
Edge 200%, plus a control run against v0.3.3-rc1 that must report the original defect.

Edge at 200% zoom is emulated as a 683 × 330 CSS-pixel viewport at device scale factor 2 (a 1366 × 660
browser area at 200%), in Chromium, the engine Edge uses.

## Test labels

- Ordinary tests describe **approved** behavior.
- Tests marked `known_defect` record **defective** v0.3.2 behavior so it cannot change silently.
  Their docstrings start with "KNOWN DEFECT … NOT APPROVED BEHAVIOR". A pass means the defect is
  still present as expected in Phase 1, not that it is acceptable. See `KNOWN-DEFECTS.md`.

## Tests that cannot run in the current development environment

| Test or check | Why not | Where it runs |
| --- | --- | --- |
| axe-core WCAG 2.1 A/AA scans (`test_X2_*`, 9 states × 2 targets) | Package installs are blocked in the development workspace | GitHub Actions (prepared, not yet run: repository not created) |
| GitHub Actions workflow itself | Repository not created (awaiting approval) | GitHub |
| Firefox and WebKit (Safari engine) automated runs | Only Chromium is installed | Manual checklist; can be added to CI later |
| Real speech synthesis, voice availability, and sound | Test browsers have no voices; tests use a simulated speech engine | Manual checklist section 2 |
| Screen reader output (NVDA, JAWS, VoiceOver, TalkBack) | Requires assistive technology and a person | Manual checklist section 3 |
| Real 200% and 400% browser zoom, text spacing | Emulated by viewport size and scale factor (`test_ux_v040.py` Z1–Z8); real zoom not automated | Manual checklist section E |
| Windows high-contrast (forced colors) mode | Requires Windows | Manual checklist section 4 |
| Live window resizing and orientation changes | Automated tests use fixed viewport sizes | Manual checklist section 4 |
| Touch input on phones and tablets | No device available | Manual checklist section 5 |
| GitHub Pages hosting | Not authorized to publish | After release approval (`DEPLOYMENT.md`) |
| Microsoft Edge specifically | Edge is not installed; Edge uses the same Chromium engine as the test browser | Manual checklist sections A and E (Edge at 100% and 200%) |

## Test-harness corrections made during Phase 1

| When | Issue | Fix |
| --- | --- | --- |
| Checkpoint A r1 | Screenshot taken during a smooth scroll (baseline vs itself differed) | Wait for scrolling to settle |
| v0.3.3-rc1 | Version-label mask silently not applied | Fixed escape; each comparison asserts the mask worked |
| v0.3.3-rc1 | Tab-order comparison affected by browser focus wrap | Record one pass from the top of the page |
| v0.3.3-rc1 | Inline-handler check matched a code comment | Check markup only |
| v0.3.3-rc1 | Mission Briefing screenshots skipped the "settle" step, so image decoding varied run to run | Settle (scroll, image decode, two frames) applies to every state |

## Known rendering differences (reviewed, within tolerance)

- **Modular site, Mission Briefing at 1366 px: 325 pixels (0.026%).** Edge pixels of the four 55 px
  stakeholder portraits differ by an average of 4 color levels (maximum 44 of 255). The images are
  byte-identical; Chromium resamples images loaded from files slightly differently from images embedded
  as data (the standalone file, like v0.3.2, embeds them and shows 0 differing pixels). Reviewed at 8×
  magnification: no visible difference (`reports/v0.3.3-rc1/portrait-rendering-brief-1366-8x.png`).
- Full-page screenshots occasionally differ by about 10 pixels (0.001%) at the rounded corner of the
Next Step button at 375 px. This occurs when comparing v0.3.2 with itself, so it comes from the
browser's anti-aliasing, not from code. It is well inside the approved 0.1% tolerance.
