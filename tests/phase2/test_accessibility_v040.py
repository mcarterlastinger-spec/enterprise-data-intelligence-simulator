"""Accessibility checks for the new v0.4.0 screens (Match & Compare decisions, check results,
proposal history, Golden Record). Uses the built-in audit from Phase 1 (control names, labels,
alt text, duplicate IDs, text contrast) and adds label, keyboard, and focus checks.
axe-core scans of these screens run in GitHub Actions (not available in this workspace).
"""
import pytest

from a11y.test_accessibility import LITE_AUDIT
from flow_helpers import GOLDEN_A, KEY_DECISIONS, flow  # noqa: F401

KEY_A = "CRM-10452|ERP-77831"


def _states(f, state):
    if state == "compare-decided":
        f.select_all_and_compare()
        f.decide(KEY_DECISIONS)
    elif state == "compare-checked":
        f.select_all_and_compare()
        f.decide(KEY_DECISIONS)
        f.check()
        f.submit("A")
    elif state == "golden":
        f.to_golden_with_proposals()
    elif state == "golden-saved":
        f.to_golden_with_proposals(("A",))
        f.fill_golden(KEY_A, GOLDEN_A)
        f.save(KEY_A)


@pytest.mark.parametrize("state", ["compare-decided", "compare-checked", "golden", "golden-saved"])
def test_X1_builtin_audit_clean_on_new_screens(flow, state):
    f = flow()
    _states(f, state)
    assert f.page.evaluate(LITE_AUDIT) == []


def test_X2_every_golden_control_is_labelled(flow):
    f = flow()
    _states(f, "golden")
    unlabelled = f.page.evaluate("""()=>[...document.querySelectorAll('#golden-content input, #golden-content select')]
        .filter(e=>!(e.id && document.querySelector('label[for="'+e.id+'"]'))).map(e=>e.outerHTML.slice(0,80))""")
    assert unlabelled == []
    groups = f.page.evaluate("()=>[...document.querySelectorAll('fieldset.golden-attr')].every(fs=>fs.querySelector('legend').innerText.trim().length>0)")
    assert groups


def test_X3_golden_record_reachable_by_keyboard(flow):
    """Tab reaches every attribute's evidence selector and the Save button, in reading order."""
    f = flow()
    _states(f, "golden")
    f.page.focus(".golden-group h3")
    seen = []
    for _ in range(80):
        f.page.keyboard.press("Tab")
        info = f.page.evaluate("()=>{const e=document.activeElement;return e.hasAttribute('data-reason')?'reason:'+e.closest('fieldset').dataset.attr:(e.dataset.saveGolden?'save':'')}")
        if info:
            seen.append(info)
        if info == "save":
            break
    assert seen == ["reason:legalName", "reason:taxId", "reason:operatingAddress", "reason:billingAddress",
                    "reason:parent", "reason:primaryContact", "save"]


def test_X4_status_messages_are_live_regions(flow):
    f = flow()
    _states(f, "golden")
    assert f.page.get_attribute(f'#gs-{KEY_A.replace("|", "-")}', "aria-live") == "polite"
    f.app.nav("compare")
    assert f.page.get_attribute("#governance-output", "aria-live") == "polite"


def test_X5_focus_visible_on_new_controls(flow):
    f = flow()
    _states(f, "golden")
    f.page.focus("body")
    f.page.keyboard.press("Tab")
    sel = f'fieldset.golden-attr[data-key="{KEY_A}"][data-attr="legalName"] [data-reason]'
    f.page.focus(sel)
    f.page.keyboard.press("Shift+Tab")
    f.page.keyboard.press("Tab")
    style = f.page.evaluate("()=>{const c=getComputedStyle(document.activeElement);return [c.outlineStyle,c.outlineWidth]}")
    assert style[0] != "none" and style[1] != "0px"
