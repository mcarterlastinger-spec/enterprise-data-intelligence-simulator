"""D12 correction: WCAG 2.1 SC 1.4.11 Non-text Contrast for focus outlines and control borders.

An in-page audit (`contrast_audit.js`) checks every visible, enabled control in every learner state,
at desktop size and at emulated Edge 200% zoom, including the Menu and Why? panels:
  - the keyboard focus outline contrasts at least 3:1 with the colors next to it;
  - each form field and bordered button has an edge (fill or border) of at least 3:1.
Exemptions follow WCAG: disabled controls; borderless text buttons; native checkbox and radio
boundaries (drawn by the browser). See the audit file's header.
"""
from pathlib import Path

import pytest

from flow_helpers import Flow, flow  # noqa: F401
from test_ux_v040 import compact
from test_validation_debrief import complete_validation, finish, to_validation

AUDIT = (Path(__file__).parent / "contrast_audit.js").read_text()


def audit(page):
    page.keyboard.press("Shift")  # a keyboard interaction, so focus is shown as keyboard focus
    page.evaluate(AUDIT)
    return page.evaluate("()=>window.__contrastAudit()")


def assert_clean(results):
    problems = [f"{state}: {f['el']} [{f['check']}] {f['detail']}" for state, r in results.items() for f in r["failures"]]
    assert not problems, "Non-text contrast below 3:1:\n" + "\n".join(problems)
    assert all(r["checked"]["focus"] > 0 for r in results.values())


def walk_states(f, results):
    """Drive the whole case, auditing each learner state."""
    page, app = f.page, f.app
    results["brief"] = audit(page)
    app.nav("work")
    results["records"] = audit(page)
    f.select_all_and_compare()
    results["compare"] = audit(page)
    f.decide({"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "hold",
              "CRM-10489": "B", "ERP-77902": "B", "CRM-10814": "separate"})
    f.check()
    results["compare-checked"] = audit(page)
    app.nav("work")
    app.nav("brief")
    to_validation(f)
    app.nav("golden")
    results["golden"] = audit(page)
    app.nav("validation")
    results["validation"] = audit(page)
    complete_validation(f)
    results["validation-submitted"] = audit(page)
    finish(f)
    page.wait_for_timeout(200)
    page.click("text=How scoring works")
    results["debrief"] = audit(page)


def test_C1_desktop_every_state(flow):
    f = flow(width=1366, height=900)
    results = {}
    walk_states(f, results)
    assert_clean(results)


def test_C2_edge_200_every_state(browser, target):
    ctx, page, errors = compact(browser, target)
    import conftest
    f = Flow(conftest.App(page, target))
    results = {}
    walk_states(f, results)
    page.focus("#nsb-menu")
    page.keyboard.press("Enter")
    results["menu-open"] = audit(page)
    page.keyboard.press("Escape")
    page.click("#nsb-why")
    results["why-open"] = audit(page)
    ctx.close()
    assert_clean(results)
    assert errors == []


def test_C3_palette_and_values(open_app):
    """The fix uses the approved palette: Cobalt focus outlines on light surfaces, the existing amber
    outline on the Midnight sidebar, and Steel Gray borders on fields and secondary buttons."""
    app = open_app()
    app.nav("work")
    page = app.page
    page.evaluate(AUDIT)
    page.keyboard.press("Shift")
    got = page.evaluate("""()=>{const o=s=>{const e=document.querySelector(s);e.focus();const c=getComputedStyle(e);return c.outlineColor+' '+c.outlineWidth};
        const b=s=>getComputedStyle(document.querySelector(s)).borderTopColor;
        return {search:o('#search'), secondary:o('button.secondary'), nav:o('#nav-brief'),
                searchBorder:b('#search'), secondaryBorder:b('button.secondary'), systemBorder:b('#system')}}""")
    cobalt, amber, steel = "rgb(36, 87, 184)", "rgb(241, 167, 60)", "rgb(113, 131, 157)"
    assert got["search"] == got["secondary"] == cobalt + " 3px"
    app.nav("brief")  # Next Step is enabled here
    page.keyboard.press("Shift")
    nxt = page.evaluate("()=>{const e=document.querySelector('#next-step-button');e.focus();const c=getComputedStyle(e);return [document.activeElement===e, c.outlineColor+' '+c.outlineWidth]}")
    assert nxt == [True, cobalt + " 3px"]
    assert got["nav"] == amber + " 3px"
    assert got["searchBorder"] == got["secondaryBorder"] == got["systemBorder"] == steel
    r = page.evaluate("""()=>[__contrastRatio('rgb(36,87,184)','rgb(255,255,255)'), __contrastRatio('rgb(36,87,184)','rgb(248,246,240)'),
        __contrastRatio('rgb(241,167,60)','rgb(16,29,53)'), __contrastRatio('rgb(113,131,157)','rgb(255,255,255)'),
        __contrastRatio('rgb(113,131,157)','rgb(248,246,240)')]""")
    assert all(x >= 3 for x in r), r


def test_C0_audit_detects_d12_in_v033(browser, target):
    """Control: the same audit run on the frozen v0.3.3-rc1 reports the original D12 failures,
    so a clean result on v0.4.0 means the defect is fixed, not that the audit misses it."""
    if target != "site":
        pytest.skip("runs once")
    import conftest
    ctx = browser.new_context(viewport={"width": 1366, "height": 900})
    ctx.add_init_script(conftest.SPEECH_MOCK)
    page = ctx.new_page()
    page.goto(conftest.TARGET_FILES["rc1"].as_uri())
    page.wait_for_timeout(350)
    page.click("#nav-work")
    r = audit(page)
    ctx.close()
    details = {(f["check"], f["detail"].split(" (")[0]) for f in r["failures"]}
    assert ("focus", "outline #f1a73c on #ffffff 2.03:1") in details
    assert ("boundary", "border #a9b6c8 2.06:1") in details
    assert ("boundary", "border #aab7c9 2.03:1") in details
