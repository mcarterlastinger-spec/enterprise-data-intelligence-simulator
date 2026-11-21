# Aperion Enterprise Data Intelligence Simulator

A performance-based enterprise data training experience. Learners investigate customer records
across CRM, ERP, and rebate-management systems, evaluate potential duplicates, reconcile
conflicting attributes, and propose governed merges. All records, organizations, and values are fictional.

**Status:** **v0.4.0 release candidate 2** (tag `v0.4.0-rc2`, branch `phase-2`; rc2 adds the D12 contrast fix to rc1), awaiting manual
acceptance testing. Adds the complete case: identity rules, a progress model, Golden Record, Validation,
and a scored Debrief. Not published, not merged. Release notes: `RELEASE-NOTES-v0.4.0.md`.
The v0.3.3-rc1 release candidate is frozen in `baseline/v0.3.3-rc1/`.

## Repository layout

| Path | Purpose |
| --- | --- |
| `site/index.html` | Page markup. |
| `site/css/` | Styles in seven files, in cascade order: tokens, base, responsive, components, next-step, workflow, compact-nav. |
| `site/js/` | Twenty-one ordinary script files under one global, `window.Aperion`. **Load order matters**: see the header of `site/js/namespace.js`. |
| `site/assets/avatars/` | The four stakeholder portraits, byte-identical to v0.3.2. |
| `baseline/v0.3.2/` | The original v0.3.2 file and ZIP. Never edited. |
| `baseline/v0.3.3-rc1/` | The v0.3.3 release candidate, frozen with checksums. Never edited. |
| `release/` | Checksummed copies of each release candidate's standalone file. |
| `tests/` | Automated tests (see below). |
| `.github/workflows/ci-pages.yml` | Runs tests on GitHub; deploys to Pages only when enabled. |
| `DECISIONS.md` | Approved decisions. |
| `KNOWN-DEFECTS.md` | Defect status in v0.4.0, limitations, and the defects preserved in v0.3.x. |
| `REGRESSION-CHECKLIST.md` | Manual acceptance checklist for v0.4.0 (Edge at 100% and 200%). The v0.3.3 checklist is `REGRESSION-CHECKLIST-v0.3.3.md`. |
| `TESTING.md` | How tests run, labels, and which tests cannot run in the development environment. |
| `DEPLOYMENT.md` | Local testing and GitHub Pages deployment instructions (not yet carried out). |
| `ACCESSIBILITY-STATUS.md` | Known accessibility defects, further findings, and outstanding accessibility tests. |
| `RELEASE-NOTES-v0.4.0.md`, `RELEASE-NOTES-v0.3.3.md` | What changed in each release and what did not. |
| `tools/build_standalone.py` | Builds the standalone single-file distribution from `site/`. |
| `ROLLBACK.md` | How to undo a step or restore v0.3.2. |

## Two forms of the application

| Form | Where | Use |
| --- | --- | --- |
| Modular (primary source) | `site/` | Editing, GitHub Pages, review of individual files |
| Standalone single file | `dist/aperion-v0.4.0-standalone.html` | Opening directly in Microsoft Edge or any browser, sharing as one file, offline use. Generated from `site/` by `tools/build_standalone.py`; never edit it by hand |

## Preview locally

Either double-click `site/index.html`, or, to match GitHub Pages exactly:

```sh
cd site
python3 -m http.server 8000
# open http://localhost:8000
```

## Run the tests

Requires Python 3.10 or later and Google Chrome or Playwright's Chromium.

```sh
python3 -m pip install -r requirements-test.txt
python3 -m playwright install chromium     # skip if Google Chrome is installed
python3 tools/build_standalone.py          # build the standalone file so it is tested too
python3 -m pytest
```

`tests/phase1` keeps proving that v0.3.3-rc1 matches v0.3.2; `tests/phase2` tests v0.4.0 (modular site and
standalone). Full details, targets, and the tests that cannot run here: `TESTING.md`.

## Script loading

`index.html` loads the scripts at the end of `<body>`, in this order: namespace, util, data/records,
data/attributes, data/case, state, rules/matching, rules/identity, rules/golden, rules/scoring, audio,
navigation, views/records, views/compare, views/golden, views/validation, views/debrief,
views/stakeholders, views/nextbar, bindings, main. Each file declares what it needs; if the order is wrong,
the page stops with a console error naming the missing file. The application creates no globals other
than `Aperion`. Buttons use `data-action="name"` or `data-action="name:argument"` (see `js/bindings.js`)
instead of inline `onclick`. Rules (`js/rules/`) are pure functions with no access to the page.

## Deployment

Not yet authorized. See `DEPLOYMENT.md`. Nothing deploys until the repository owner sets the Actions
variable `PAGES_DEPLOY_ENABLED=true`; after that, pushes to `main` publish `site/` to GitHub Pages only
when every test passes.
