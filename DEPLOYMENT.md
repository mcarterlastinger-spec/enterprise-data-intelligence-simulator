# Local testing and GitHub Pages deployment

**Nothing in this guide has been carried out.** Creating the repository, pushing, and enabling Pages
each require explicit approval from the project owner. Phase 1 is not released until approved.

## 1. Local testing

### The modular application (primary source)

The `site/` folder must stay together: `index.html` with `css/`, `js/`, and `assets/`.

- **Quickest:** double-click `site/index.html`. Works in Edge, Chrome, Firefox, and Safari.
- **Same as GitHub Pages:**
  ```sh
  cd site
  python3 -m http.server 8000
  ```
  Then open <http://localhost:8000>. Stop the server with Ctrl+C.
  (Windows without Python: install it from python.org, or use `npx serve site` if Node.js is installed.)

### The standalone file

`dist/aperion-v0.3.3-standalone.html` contains everything in one file. Open it directly in Microsoft
Edge (double-click, or right-click > Open with > Microsoft Edge). It needs no other files and no network.

Rebuild it after any change to `site/`:

```sh
python3 tools/build_standalone.py           # write dist/aperion-v0.3.3-standalone.html
python3 tools/build_standalone.py --check   # confirm it matches the current sources
```

### Automated tests

See `TESTING.md`. In short:

```sh
python3 -m pip install -r requirements-test.txt
python3 -m playwright install chromium
python3 tools/build_standalone.py
python3 -m pytest
```

## 2. GitHub Pages deployment (after approval only)

Approved repository: `mcarterlastinger-spec/enterprise-data-intelligence-simulator` (public,
separate from Sales Intelligence Lab and the portfolio site).

### One-time setup

1. On GitHub, create the empty public repository with that name. Do not add a README or license
   (the project already has them).
2. In the project folder:
   ```sh
   git remote add origin https://github.com/mcarterlastinger-spec/enterprise-data-intelligence-simulator.git
   git push -u origin main
   git push origin phase-1-modularize --tags
   ```
3. Open **Actions** and confirm the "Test and deploy" workflow ran and passed (this is the first time
   the axe-core accessibility scans run).
4. **Settings > Pages > Build and deployment > Source: GitHub Actions.**
5. **Settings > Environments > github-pages**: optionally restrict deployments to the `main` branch.
6. Deployment stays **off** until step 7.

### Releasing v0.3.3 (after manual acceptance and release approval)

7. **Settings > Secrets and variables > Actions > Variables > New repository variable:**
   `PAGES_DEPLOY_ENABLED` = `true`.
8. Merge the release candidate into `main` (pull request from `phase-1-modularize`, or
   `git switch main && git merge --ff-only v0.3.3-rc1 && git push`).
9. The workflow runs every test on the baseline, modular site, and standalone file. Only if all pass
   does it publish `site/` to `https://mcarterlastinger-spec.github.io/enterprise-data-intelligence-simulator/`.
10. Tag the release: `git tag -a v0.3.3 -m "Aperion v0.3.3" && git push origin v0.3.3`.
11. Optional: attach `dist/aperion-v0.3.3-standalone.html` to a GitHub Release for v0.3.3.
12. Run checklist section A against the live URL.

### What gets published

Only the contents of `site/`. The baseline, tests, tools, reports, and documentation stay in the
repository and are never served by Pages. The workflow file is `.github/workflows/ci-pages.yml`; the manual emergency rollback is `.github/workflows/rollback-pages.yml`.

### Stopping or undoing a deployment

See `ROLLBACK.md`. To stop all deployments immediately, set `PAGES_DEPLOY_ENABLED` to `false`.
