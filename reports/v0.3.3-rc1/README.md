# v0.3.3-rc1 automated results

All runs: targets baseline (v0.3.2), site (modular RC), standalone (single-file RC); headless Chromium 153 on Linux.
Each run = 128 test cases x 3 targets + 1 baseline checksum test = 385 test runs.

| Run | Failures | Skipped | Notes |
| --- | --- | --- | --- |
| regression-run1 | 0 | 37 | Before the final test-harness change (Mission Briefing screenshots not yet settled) |
| regression-run2 | 0 | 37 | Same as run 1 |
| regression-run3 | 0 | 37 | **Final harness.** Release-candidate result |
| regression-run4 | 0 | 37 | **Final harness.** Repeat for stability |

Skipped (37): 27 axe-core scans (need vendor/axe.min.js; run in GitHub Actions), 10 structure checks
that apply only to some targets (e.g. module checks skip on v0.3.2; standalone-only checks skip elsewhere).

Earlier attempts during RC preparation failed because of test-harness faults, which were fixed
(see TESTING.md, "Test-harness corrections"); no application code changed as a result.

visual-modular/ and visual-standalone/: side-by-side screenshot reports (27 comparisons each).
portrait-rendering-brief-1366-8x.png: 8x magnified v0.3.2 (left) vs modular RC (right) for the
only nonzero comparison (325 px, 0.026%).
