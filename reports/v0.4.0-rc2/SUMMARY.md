# v0.4.0-rc2 test results (2026-11-11, Chromium via Google Chrome, Linux)

rc2 = rc1 plus the D12 non-text contrast fix (CSS only).

| Suite | Targets | Runs | Failures | Errors | Skipped |
| --- | --- | --- | --- | --- | --- |
| Phase 1 + baseline integrity | v0.3.2, v0.3.3-rc1, v0.3.3-rc1 standalone | 386 | 0 | 0 | 38 |
| Phase 2 + baseline integrity, run 1 | v0.4.0 site, v0.4.0 standalone | 266 | 0 | 0 | 8 |
| Phase 2 + baseline integrity, run 2 | v0.4.0 site, v0.4.0 standalone | 266 | 0 | 0 | 8 |

Contrast audit (`test_contrast_v040.py`): every enabled control in 9 learner states at 1366 px and 11 states at
emulated Edge 200% (including the Menu and Why? panels), on both builds: 0 failures. Control run on v0.3.3-rc1
reports the original D12 failures (amber outline 2.03:1; borders 2.03:1 and 2.06:1).

Standalone SHA-256: `02af3dbb8dc829ba9136f37e048efc5e4148f8a9730b8e598fe24a184890e17c`.
