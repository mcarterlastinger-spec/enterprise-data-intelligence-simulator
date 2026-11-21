"""Regression protection for v0.4.0: what did not change must still behave like v0.3.3-rc1.

Phase 1 tests whose expectations are still valid are re-run here against the v0.4.0 targets
(site, standalone) by importing them. Tests whose expectations changed on purpose (approved
Phase 2 corrections) are not imported; their replacements live in the other phase2 files.
"""
import io

import pytest
from PIL import Image, ImageChops
import numpy as np

from conftest import FREEZE_CSS, NORMALIZE_VERSION, SPEECH_MOCK, TARGET_FILES

# Still-valid Phase 1 tests (unchanged behavior). Importing them runs them on v0.4.0.
from browser.test_audio import (  # noqa: F401
    test_A1_voice_list_offers_only_feminine_english_voices, test_A2_play_pause_resume_cycle,
    test_A3_replay_is_separate, test_A4_briefing_narration, test_A5_navigation_stops_audio,
    test_A6_starting_other_narration_replaces_current, test_A7_no_suitable_voice_falls_back_to_transcript,
    test_A8_speech_error_resets_controls)
# test_D11 (status hidden on the briefing) is replaced by test_U3 in test_ux_v040.py: fixed in v0.4.0.
from browser.test_records_and_navigation import (  # noqa: F401
    test_R1_record_inventory, test_R2_search, test_R3_filters_and_reset, test_N3_in_page_links)
# test_C9 is replaced by test_P10 (same behavior, approved new button wording).
from browser.test_load_and_identity import (  # noqa: F401
    test_L1_loads_without_errors_from_file, test_L1b_loads_without_errors_over_http, test_L2_initial_state,
    test_L3_visual_identity_tokens, test_L4_avatars_present_and_unchanged, test_V1_version_labels)
from browser.test_structure import (  # noqa: F401
    test_M2_only_one_application_global, test_M4_wrong_script_order_fails_loudly,
    test_M5_no_inline_handlers, test_M7_standalone_matches_current_sources)
from browser.test_keyboard import test_K4_audio_toggle_by_keyboard  # noqa: F401
# test_D12_contrast_baseline recorded the defective colors on purpose. D12 is fixed in v0.4.0-rc2, so it
# runs only on the frozen v0.3.x targets (tests/phase1); test_contrast_v040.py checks the fix.

MODULES_V040 = ["namespace", "util", "data/records", "data/attributes", "data/case", "state", "rules/matching",
                "rules/identity", "rules/golden", "rules/scoring", "audio", "navigation", "views/records",
                "views/compare", "views/golden", "views/validation", "views/debrief", "views/stakeholders",
                "views/nextbar", "bindings", "main"]


def test_M1_v040_modules_load_in_documented_order(open_app):
    app = open_app()
    assert app.page.evaluate("()=>Aperion.loadedModules()") == MODULES_V040


def test_M6_v040_standalone_is_self_contained(browser, target):
    if target != "standalone":
        pytest.skip("standalone build only")
    f = TARGET_FILES[target]
    if not f.exists():
        pytest.skip("standalone not built yet")
    ctx = browser.new_context()
    ctx.add_init_script(SPEECH_MOCK)
    requests = []

    def guard(route):
        requests.append(route.request.url)
        route.continue_() if route.request.url == f.as_uri() else route.abort()
    ctx.route("**/*", guard)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f.as_uri())
    page.wait_for_timeout(350)
    ok = page.evaluate("()=>[...document.images].every(i=>i.complete&&i.naturalWidth===256)")
    n = page.evaluate("()=>Aperion.loadedModules().length")
    ctx.close()
    assert requests == [f.as_uri()] and errors == [] and ok and n == len(MODULES_V040)


def test_R4_details_panel_shows_neutral_notes(open_app):
    app = open_app()
    app.nav("work")
    app.page.click('[data-open="REB-33907"]')
    fields = app.page.evaluate("()=>[...document.querySelectorAll('#details-fields .field')].map(f=>[f.querySelector('b').innerText.trim(),f.lastChild.textContent])")
    assert fields[:7] == [
        ["CUSTOMER", "Northbridge Healthcare"], ["LEGAL NAME", "Not provided"], ["TAX IDENTIFIER", "Missing"],
        ["BUSINESS ADDRESS", "100 Medical Pkwy, Seattle, WA"], ["PARENT ORGANIZATION", "Northbridge Holdings"],
        ["CONTACT EMAIL", "rebates@northbridge.example"], ["LAST VERIFIED", "2026-09-02"]]
    assert fields[7] == ["SOURCE NOTE", "Rebate enrollment submitted without a W-9. Tax identifier and legal name not yet provided."]


def _shot(browser, file, width, selector, before=None):
    ctx = browser.new_context(viewport={"width": width, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(SPEECH_MOCK)
    page = ctx.new_page()
    page.goto(file.as_uri())
    page.add_style_tag(content=FREEZE_CSS)
    # The sticky Next Step bar overlaps regions depending on scroll position; its wording changed
    # on purpose (tested in test_progress_model.py), so it is hidden for region comparisons.
    page.add_style_tag(content=".next-step-bar{visibility:hidden!important}")
    page.wait_for_timeout(350)
    if before:
        before(page)
    page.evaluate(NORMALIZE_VERSION)
    # The 4th sidebar item changed from "Golden Record (next)" to "Golden Record" (approved). On narrow
    # layouts the sidebar sits above the content, so give both versions the same label for comparison.
    page.evaluate("()=>{document.querySelectorAll('aside nav button')[3].textContent='Golden Record'}")
    # v0.4.0 shows Mission Briefing audio status on the briefing itself (D11 fix, approved Step 6);
    # rc1 has no such element. Blank it so the rest of the briefing is still compared.
    page.evaluate("()=>document.querySelectorAll('.brief-audio-status').forEach(e=>e.textContent='')")
    # D12 fix (approved 2026-11-11): field and secondary-button borders changed to Steel Gray in v0.4.0-rc2.
    # Give both versions the same border color so everything else in the region is still compared;
    # test_contrast_v040.py checks the new colors.
    page.add_style_tag(content=".secondary,.toolbar input,.toolbar select,select[data-group]{border-color:#71839d!important}")
    page.evaluate("()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>null)))")
    img = Image.open(io.BytesIO(page.locator(selector).screenshot())).convert("RGB")
    ctx.close()
    return img


@pytest.mark.parametrize("width", [1366, 768, 375])
@pytest.mark.parametrize("region", ["brief", "records-table", "header"])
def test_E1_unchanged_regions_match_v033(browser, target, width, region):
    """Regions Phase 2 did not change must look the same as the accepted v0.3.3-rc1 (<= 0.1%).
    The record table sits below the new visible filter labels and stakeholder guidance (approved
    changes), so on narrow layouts it starts at a different sub-pixel offset and anti-aliasing
    differs across the whole table. It is compared as pixels at 1366 px and as markup at all widths
    (test_E2)."""
    if not TARGET_FILES[target].exists():
        pytest.skip("not built yet")
    if region == "records-table" and width != 1366:
        pytest.skip("compared as markup at this width (test_E2)")
    spec = {
        "brief": ("#page-brief", None),
        "records-table": ("#page-work .tablewrap", lambda p: p.click("#nav-work")),
        "header": (".top", None),
    }[region]
    base = _shot(browser, TARGET_FILES["rc1"], width, spec[0], spec[1])
    got = _shot(browser, TARGET_FILES[target], width, spec[0], spec[1])
    # The sidebar's Golden Record button text changed (approved), which can move later content by a
    # sub-pixel amount and round an element's height by 1 px. Allow 1 px; anything more is a change.
    assert abs(got.size[0] - base.size[0]) <= 1 and abs(got.size[1] - base.size[1]) <= 1, \
        f"{region} size changed {base.size} -> {got.size}"
    w, h = min(base.size[0], got.size[0]), min(base.size[1], got.size[1])
    base, got = base.crop((0, 0, w, h)), got.crop((0, 0, w, h))
    changed = int(np.asarray(ImageChops.difference(base, got)).any(axis=2).sum())
    assert changed / (base.size[0] * base.size[1]) <= 0.001, f"{changed} pixels differ in {region} at {width}px"


@pytest.mark.parametrize("width", [1366, 768, 375])
def test_E2_record_table_markup_matches_v033(browser, target, width):
    rows = []
    for t in ("rc1", target):
        ctx = browser.new_context(viewport={"width": width, "height": 900})
        ctx.add_init_script(SPEECH_MOCK)
        page = ctx.new_page()
        page.goto(TARGET_FILES[t].as_uri())
        page.wait_for_timeout(300)
        page.click("#nav-work")
        rows.append(page.evaluate("()=>document.querySelector('#page-work .tablewrap').outerHTML"))
        ctx.close()
    assert rows[1] == rows[0]
