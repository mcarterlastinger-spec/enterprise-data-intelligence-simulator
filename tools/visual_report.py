"""Builds a visual-difference report comparing v0.3.2 with the restructured site.

Usage:  python3 tools/visual_report.py [output_dir]   (default: reports/visual)

For every learner state and width used by the screenshot tests, it captures v0.3.2 and the
target in the same browser, counts differing pixels, and writes:
  summary.md      table of all comparisons with pixel counts and pass/fail against 0.1%
  index.html      side-by-side gallery (JPEG previews, for viewing only)
  diff-*.png      full-resolution difference masks, only where any pixel differs
Pixel comparison is always done on the full-resolution PNG captures, never on the previews.
"""
import io
import os
import pathlib
import sys

import numpy as np
from PIL import Image, ImageChops

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "phase1"))

from playwright.sync_api import sync_playwright  # noqa: E402

from conftest import TARGET_FILES  # noqa: E402
from browser.test_equivalence import MAX_DIFF, STATES, WIDTHS, open_state  # noqa: E402

LABELS = {
    "brief": "Mission Briefing", "work": "Customer Records", "work-details": "Records: details open",
    "work-filtered": "Records: filtered", "work-selected": "Records: 2 selected",
    "compare-empty": "Compare: nothing selected", "compare-all": "Compare: all 6 records",
    "compare-validated": "Compare: validated", "compare-proposed": "Compare: proposal submitted",
}


def preview(img, path, max_w=700):
    w, h = img.size
    scale = min(1.0, max_w / w)
    img.resize((int(w * scale), int(h * scale)), Image.LANCZOS).save(path, "JPEG", quality=82)


def main():
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "reports" / "visual"
    target = os.environ.get("APERION_REPORT_TARGET", "site")
    out.mkdir(parents=True, exist_ok=True)
    chrome = "/usr/bin/google-chrome" if pathlib.Path("/usr/bin/google-chrome").exists() else None
    rows = []
    with sync_playwright() as p:
        kw = {"args": ["--no-sandbox", "--font-render-hinting=none", "--force-color-profile=srgb"]}
        if chrome:
            kw["executable_path"] = chrome
        browser = p.chromium.launch(**kw)
        version = browser.version
        for state in STATES:
            for width in WIDTHS:
                shots = []
                for f in (TARGET_FILES["baseline"], TARGET_FILES[target]):
                    ctx, page = open_state(browser, f, state, width)
                    shots.append(Image.open(io.BytesIO(page.screenshot(full_page=True))).convert("RGB"))
                    ctx.close()
                base, got = shots
                same_size = base.size == got.size
                changed = int(np.asarray(ImageChops.difference(base, got)).any(axis=2).sum()) if same_size else -1
                ratio = changed / (base.size[0] * base.size[1]) if same_size else 1.0
                stem = f"{state}-{width}"
                preview(base, out / f"{stem}-v032.jpg")
                preview(got, out / f"{stem}-v033.jpg")
                if changed:
                    ImageChops.difference(base, got).point(lambda v: 255 if v else 0).save(out / f"diff-{stem}.png")
                rows.append((state, width, base.size, got.size, changed, ratio, ratio <= MAX_DIFF and same_size))
        browser.close()

    lines = [f"# Visual comparison: v0.3.2 vs restructured ({target})", "",
             f"Browser: Chromium {version}. Tolerance: {MAX_DIFF:.1%} of pixels (decision 4).", "",
             'Version labels are masked as "V0.3.x" in both captures (the approved v0.3.3 label change is checked separately by test_V1).', "",
             "| State | Width | v0.3.2 size | v0.3.3 size | Differing pixels | Share | Result |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for state, width, bs, gs, changed, ratio, ok in rows:
        lines.append(f"| {LABELS[state]} | {width} px | {bs[0]}×{bs[1]} | {gs[0]}×{gs[1]} | {changed} | "
                     f"{ratio:.4%} | {'Pass' if ok else 'FAIL'} |")
    total_fail = sum(1 for r in rows if not r[6])
    lines += ["", f"{len(rows)} comparisons, {total_fail} over tolerance, "
                  f"{sum(1 for r in rows if r[4])} with any differing pixels."]
    (out / "summary.md").write_text("\n".join(lines) + "\n")

    cards = []
    for state, width, bs, gs, changed, ratio, ok in rows:
        stem = f"{state}-{width}"
        diff = f'<a href="diff-{stem}.png">difference mask</a>' if changed else "no differing pixels"
        cards.append(f"""<section><h2>{LABELS[state]} · {width} px</h2>
<p class="{'ok' if ok else 'bad'}">{'Pass' if ok else 'Over tolerance'}: {changed} differing pixels ({ratio:.4%}); {diff}</p>
<div class="pair"><figure><figcaption>v0.3.2 (original)</figcaption><img src="{stem}-v032.jpg" alt="v0.3.2 {LABELS[state]} at {width} px"></figure>
<figure><figcaption>v0.3.3 (restructured)</figcaption><img src="{stem}-v033.jpg" alt="v0.3.3 {LABELS[state]} at {width} px"></figure></div></section>""")
    (out / "index.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Aperion visual comparison</title>
<style>body{{font:15px/1.5 system-ui,sans-serif;margin:24px;background:#f8f6f0;color:#101d35}}
section{{background:#fff;border:1px solid #d8dce5;border-radius:10px;padding:16px;margin:0 0 18px}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start}}figure{{margin:0}}
img{{width:100%;border:1px solid #d8dce5}}figcaption{{font-weight:700;margin-bottom:6px}}
.ok{{color:#1d6b35}}.bad{{color:#a11b1b;font-weight:700}}</style></head><body>
<h1>Visual comparison: v0.3.2 vs v0.3.3 (restructured)</h1>
<p>Previews are reduced JPEGs for viewing. Pass/fail is computed on full-resolution captures. See summary.md.
Version labels are masked as "V0.3.x" in both captures; the approved v0.3.3 label is checked separately.</p>
{''.join(cards)}</body></html>""")
    print((out / "summary.md").read_text())


if __name__ == "__main__":
    main()
