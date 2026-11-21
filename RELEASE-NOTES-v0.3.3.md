# Aperion v0.3.3 — release notes (release candidate 1)

**Status:** release candidate for manual acceptance testing. Not released, not published.

## Summary

v0.3.3 is a behavior-preserving restructure of v0.3.2 and the foundation for future development.
Learners should notice no difference except the version label.

## What changed

- **Version label:** "V0.3.2" → "V0.3.3" in the header pill and footer (decision B3). This is the only
  intended visible change.
- **Maintainable source:** the single 665 KB file is now a modular application in `site/`:
  `index.html`, 5 stylesheets, 13 script files under one global (`Aperion`), and 4 portrait files.
- **Standalone distribution:** `aperion-v0.3.3-standalone.html`, one self-contained file generated from
  the modular source, for opening directly in Microsoft Edge or sharing.
- **Quality controls:** automated regression tests comparing every release form with v0.3.2,
  a GitHub Actions workflow (deployment off by default), and a manual acceptance checklist.

## What did not change

- Records, instructional text, business rules, scoring (none), navigation, Next Step behavior,
  audio behavior, stakeholder presentation, visual identity, and layout at all tested widths.
- **Known defects are still present**, including the instructional-integrity defects D1 (invalid merge
  eligibility) and D2 (missing values hide conflicts). They are scheduled for Phase 2 and are
  **not approved behavior**. See `KNOWN-DEFECTS.md`.
- Approved behaviors kept: selections survive filtering (A2); group choices are kept for deselected
  records and inactive records do not affect validation (G5); Clear groups affects only selected
  records (B2).

## Known limitations

- Accessibility scans with axe-core and the GitHub workflow have not yet run (repository not created).
- Real voices, screen readers, Safari, Firefox, Edge, phones, zoom, and high-contrast mode require the
  manual checklist. See `ACCESSIBILITY-STATUS.md` and `TESTING.md`.
- The modular application must keep its folder structure; use the standalone file to share one file.

## Files in this release candidate

| File | Purpose |
| --- | --- |
| `aperion-v0.3.3-rc1-modular.zip` | The modular application (`site/`) for review, local testing, and GitHub Pages |
| `aperion-v0.3.3-standalone.html` | Single self-contained file; open directly in Microsoft Edge |
| `aperion-v0.3.3-rc1-repository.zip` | Full repository with Git history, tests, reports, and documentation |
