# Rollback procedure

The original v0.3.2 application is preserved unchanged at `baseline/v0.3.2/index.html`
(SHA-256 `9d7698340682c7df823345a19a524a24c7330ca3467b7e03c554a6124c7bb530`), with the original ZIP.
It is complete on its own and never depends on anything else in this repository. Every test run
verifies its checksums (`tests/test_baseline_integrity.py`).

## Where things stand

| Branch or tag | Contains |
| --- | --- |
| `v0.3.2-baseline` (tag) | Original v0.3.2 only |
| `main` (branch) | Checkpoint A revision 1: v0.3.2 site plus tests and documentation |
| `phase-1-modularize` (branch) | All Phase 1 restructuring work |
| `phase1-checkpoint-a`, `phase1-checkpoint-a-r1`, `phase1-checkpoint-b` (tags) | Review checkpoints |
| `v0.3.3-rc1` (tag) | Release candidate 1 |

Nothing has been pushed to GitHub or published.

## 1. Check the baseline is intact

```sh
cd baseline/v0.3.2 && sha256sum -c CHECKSUMS.txt
```

Both lines must say `OK`.

## 2. Before release (now): reject or pause the release candidate

- **Keep using v0.3.2:** open `baseline/v0.3.2/index.html`, or `git switch main` (its `site/` is v0.3.2).
- **Return to Checkpoint B** (restructure without the version label, standalone build, or RC documentation):
  ```sh
  git switch -c rework phase1-checkpoint-b
  ```
- **Discard Phase 1 restructuring entirely:**
  ```sh
  git switch main
  git branch -D phase-1-modularize      # tags still keep every checkpoint recoverable
  ```
- **Undo one step:** each step is its own commit. `git log --oneline`, then `git revert <commit>`.

## 3. After release to GitHub Pages: restore v0.3.2 on the live site

**Recommended (no code change, about 2 minutes):**

1. GitHub > **Actions** > **Rollback Pages to v0.3.2** > **Run workflow**.
2. Type `ROLLBACK` in the confirmation box and run it.

The workflow verifies the baseline checksum and publishes only `baseline/v0.3.2/index.html`. It does not
run the regression tests (v0.3.2 is their reference) and does not change any branch. Afterwards, set
`PAGES_DEPLOY_ENABLED` to `false` so the next push to `main` does not redeploy v0.3.3.

**Other options:**

- **Re-deploy an earlier good version:** Actions > Test and deploy > open the last good run > Re-run all jobs.
- **Stop all deployments:** set the repository variable `PAGES_DEPLOY_ENABLED` to `false`.
- **Take the site offline:** Settings > Pages > Unpublish site.

To return to v0.3.3 later, set `PAGES_DEPLOY_ENABLED` to `true` and re-run the latest Test and deploy run on `main`.

## 4. Without GitHub

`baseline/v0.3.2/index.html` and `dist/aperion-v0.3.3-standalone.html` are each complete single files.
Either can be opened directly in a browser or hosted anywhere as one file.
