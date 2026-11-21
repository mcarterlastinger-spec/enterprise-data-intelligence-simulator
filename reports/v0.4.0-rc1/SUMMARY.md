# v0.4.0-rc1 test results (2026-11-11, Chromium via Google Chrome, Linux)

The Phase 1 suite ran before the final menu-spacing fix; that fix touches only `site/` CSS, which the Phase 1
suite does not test (it tests the frozen v0.3.2 and v0.3.3-rc1 files). Phase 2 was re-run twice after the fix.

| Suite | Targets | Runs | Failures | Errors | Skipped |
| --- | --- | --- | --- | --- | --- |
| Phase 1 + baseline integrity | baseline v0.3.2, v0.3.3-rc1, v0.3.3-rc1 standalone | 386 | 0 | 0 | 38 |
| Phase 2 + baseline integrity, run 1 | v0.4.0 site, v0.4.0 standalone | 260 | 0 | 0 | 7 |
| Phase 2 + baseline integrity, run 2 (repeat, flakiness check) | v0.4.0 site, v0.4.0 standalone | 260 | 0 | 0 | 7 |

Skips are by design: target-specific checks (standalone-only or modular-only), screenshot regions compared
as markup at some widths (`test_E2`), and axe-core scans (package installs blocked here; they run in CI).

Standalone: `dist/aperion-v0.4.0-standalone.html`, SHA-256
`b1b71788208edc3c28abde4382a188bf5d699da9682d0654da6947654ceeb6ee`.

Not run here: real Microsoft Edge, Firefox, Safari, screen readers, real voices, axe-core, GitHub Actions.
