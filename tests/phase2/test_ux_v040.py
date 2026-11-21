"""v0.4.0 UX and responsive behavior (Step 6).

Covers: visible filter labels, checkbox focus (D7), briefing audio status (D11), contextual
stakeholders (D8), and the compact Next Step bar for constrained viewports (decision P2-5),
emulating Microsoft Edge at 200% zoom: a 1366x768 window minus browser chrome gives about
683x330 CSS pixels at a device scale factor of 2. Edge itself is not available in this
environment; Edge uses the same Chromium engine. Manual verification in Edge is still required.
"""
import pytest

from conftest import SPEECH_MOCK, TARGET_FILES, App
from flow_helpers import KEY_DECISIONS, Flow, flow  # noqa: F401

EDGE_200 = {"width": 683, "height": 330}


def compact(browser, target, size=EDGE_200, scale=2):
    if not TARGET_FILES[target].exists():
        pytest.skip("not built yet")
    ctx = browser.new_context(viewport=size, device_scale_factor=scale, reduced_motion="reduce")
    ctx.add_init_script(SPEECH_MOCK)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(TARGET_FILES[target].as_uri())
    page.wait_for_timeout(350)
    return ctx, page, errors


def rect(page, sel):
    return page.evaluate(f"()=>{{const r=document.querySelector('{sel}').getBoundingClientRect();return {{top:r.top,bottom:r.bottom,height:r.height,width:r.width}}}}")


# ---- labels, focus, status, stakeholders ---------------------------------------------------

def test_U1_filter_controls_have_visible_labels(open_app):
    app = open_app()
    app.nav("work")
    labels = app.page.evaluate("""()=>['search','system','status'].map(id=>{const l=document.querySelector('label[for="'+id+'"]');
        const r=l.getBoundingClientRect();return [l.innerText, r.width>0&&r.height>0, document.getElementById(id).getAttribute('aria-label')]})""")
    assert labels == [["Search records", True, None], ["Source system", True, None], ["Record status", True, None]]


def test_U2_checkbox_keeps_keyboard_focus(open_app):
    """D7 fixed."""
    app = open_app()
    app.nav("work")
    app.page.focus('#rows input[data-id="CRM-10452"]')
    app.page.keyboard.press("Space")
    assert app.page.is_checked('#rows input[data-id="CRM-10452"]')
    assert app.focused()["data"].get("id") == "CRM-10452"
    app.page.keyboard.press("Tab")
    assert app.focused()["data"].get("open") == "CRM-10452", "focus continues from the checkbox"


def test_U3_briefing_shows_its_own_audio_status(open_app):
    """D11 fixed: status messages are visible on Mission Briefing."""
    app = open_app(speech="mock-novoices")
    app.page.click('.audio-toggle[data-source="brief-text"]')
    assert app.page.inner_text(".brief-audio-status") == "No suitable Maya voice selected. Audio not started; use the transcript."
    assert app.visible(".brief-audio-status")
    assert app.page.get_attribute(".brief-audio-status", "role") == "status"


@pytest.mark.parametrize("page_key,name", [("work", "Daniel Brooks"), ("compare", "Maya Chen")])
def test_U4_contextual_stakeholders(open_app, page_key, name):
    """D8: full gallery only on the briefing; one relevant stakeholder per activity, as text."""
    app = open_app()
    assert app.visible("#cast") and not app.visible("#stakeholder-prompt")
    app.nav(page_key)
    assert not app.visible("#cast")
    assert name in app.text("#stakeholder-prompt .sp-name")
    assert app.page.get_attribute("#stakeholder-prompt", "aria-label").startswith("Guidance from " + name)
    assert app.page.evaluate("()=>{const i=document.querySelector('#stakeholder-prompt img');return i.complete&&i.naturalWidth===256&&i.alt===''}")


def test_U5_stakeholder_prompts_for_later_activities(flow):
    f = flow()
    f.to_golden_with_proposals(("A",))
    assert "Priya Shah" in f.page.inner_text("#stakeholder-prompt")
    f.app.nav("validation")
    assert "Marcus Reed" in f.page.inner_text("#stakeholder-prompt")


# ---- compact Next Step bar (Edge 200% emulation) --------------------------------------------

def test_Z1_compact_bar_is_small_and_complete(browser, target):
    ctx, page, errors = compact(browser, target)
    page.click("#nav-work")
    page.mouse.wheel(0, 400)
    page.wait_for_timeout(400)
    bar = rect(page, "#next-step-bar")
    assert bar["height"] <= 70, f"bar is {bar['height']}px tall at 200% zoom (was 145px in v0.3.3)"
    assert bar["bottom"] <= 330.5 and bar["top"] >= 330 - 71, "bar stays at the bottom of the viewport while scrolling"
    for sel in ("#nsb-menu", "#nsb-why", "#next-step-button", "#next-step-heading"):
        assert page.is_visible(sel), sel
    assert page.inner_text("#next-step-button") == "Next Step: Compare selected records (0) →"
    ctx.close()
    assert errors == []


def test_Z2_menu_shows_navigation_visibly_and_by_keyboard(browser, target):
    ctx, page, _ = compact(browser, target)
    page.focus("#nsb-menu")
    page.keyboard.press("Enter")
    assert page.get_attribute("#nsb-menu", "aria-expanded") == "true"
    panel = rect(page, "#nsb-menu-panel")
    assert page.is_visible("#nsb-menu-panel") and panel["top"] >= 0 and panel["height"] > 100, "the menu is on screen, not off-screen"
    items = page.evaluate("()=>[...document.querySelectorAll('#nsb-menu-panel .nsb-item')].map(b=>[b.textContent.replace(/\\s+/g,' ').trim().slice(2),b.disabled,b.getAttribute('aria-current')])")
    assert [i[0] for i in items] == ["Customer Records", "Match & Compare", "Mission Briefing", "Golden Record (Submit an eligible merge proposal first)", "Validation (Submit an eligible merge proposal first)", "Debrief (Finish the case on Validation first)"]
    assert items[2][2] == "page" and items[3][1] is True
    clipped = page.evaluate("""()=>{const p=document.getElementById('nsb-menu-panel').getBoundingClientRect();
        return [...document.querySelectorAll('#nsb-menu-panel .nsb-item')].filter(b=>{const r=b.getBoundingClientRect();
        return r.top < p.top || r.bottom > p.bottom || r.height < 24;}).map(b=>b.textContent.trim())}""")
    assert clipped == [], f"every activity is visible in the menu without scrolling: {clipped}"
    assert page.evaluate("()=>document.activeElement.classList.contains('nsb-item')"), "focus moves into the menu"
    page.keyboard.press("Escape")
    assert page.evaluate("()=>document.activeElement.id") == "nsb-menu" and not page.is_visible("#nsb-menu-panel")
    page.keyboard.press("Enter")
    page.keyboard.press("Enter")  # activate the first item: Customer Records
    assert page.inner_text("#page-title") == "Customer Record Workspace"
    assert not page.is_visible("#nsb-menu-panel")
    ctx.close()


def test_Z3_why_is_keyboard_and_screen_reader_accessible(browser, target):
    ctx, page, _ = compact(browser, target)
    page.click("#nav-work")
    assert page.get_attribute("#next-step-button", "aria-describedby") == "next-step-description"
    assert page.text_content("#next-step-description") == "Select at least two records to compare (0 selected)."
    assert rect(page, "#next-step-description")["width"] <= 1, "collapsed visually, still in the accessibility tree"
    page.focus("#nsb-why")
    page.keyboard.press("Enter")
    assert page.get_attribute("#nsb-why", "aria-expanded") == "true"
    d = rect(page, "#next-step-description")
    assert d["width"] > 200 and d["top"] >= 0
    page.keyboard.press("Escape")
    assert page.get_attribute("#nsb-why", "aria-expanded") == "false"
    assert page.evaluate("()=>document.activeElement.id") == "nsb-why"
    ctx.close()


def test_Z4_next_step_operable_at_200(browser, target):
    ctx, page, _ = compact(browser, target)
    page.focus("#next-step-button")
    page.keyboard.press("Enter")
    assert page.inner_text("#page-title") == "Customer Record Workspace"
    ctx.close()


def test_Z5_focused_controls_are_not_hidden_by_the_bar(browser, target):
    ctx, page, _ = compact(browser, target)
    app = App(page, target)
    f = Flow(app)
    f.select_all_and_compare()
    page.focus('select[data-group="CRM-10452"]')
    hidden = []
    for _ in range(12):
        page.keyboard.press("Tab")
        info = page.evaluate("""()=>{const e=document.activeElement;const r=e.getBoundingClientRect();
            const bar=document.getElementById('next-step-bar');if(bar.contains(e)||e===document.body)return null;
            const b=bar.getBoundingClientRect();return {id:e.id||e.dataset.group||e.tagName,bottom:r.bottom,barTop:b.top}}""")
        if info and info["bottom"] > info["barTop"] + 1:
            hidden.append(info)
    ctx.close()
    assert hidden == [], f"focused controls under the Next Step bar: {hidden}"


def test_Z6_desktop_bar_unchanged(browser, target):
    ctx, page, _ = compact(browser, target, size={"width": 1366, "height": 900}, scale=1)
    assert not page.is_visible("#nsb-menu") and not page.is_visible("#nsb-why")
    assert page.is_visible("#next-step-description")
    ctx.close()


def test_Z7_320px_reflow(browser, target):
    ctx, page, errors = compact(browser, target, size={"width": 320, "height": 568}, scale=1)
    for key in ["#nav-work", "#nav-compare", "#nav-brief"]:
        page.click(key)
        assert page.evaluate("()=>document.documentElement.scrollWidth") <= 320, f"horizontal scrolling on {key}"
    bar = rect(page, "#next-step-bar")
    assert bar["height"] <= 100 and page.is_visible("#next-step-button") and page.is_visible("#nsb-menu")
    ctx.close()
    assert errors == []


def test_Z8_resizing_keeps_learner_work(browser, target):
    ctx, page, errors = compact(browser, target, size={"width": 1366, "height": 900}, scale=1)
    f = Flow(App(page, target))
    f.select_all_and_compare()
    f.decide(KEY_DECISIONS)
    f.check()
    for size in [EDGE_200, {"width": 980, "height": 700}, {"width": 320, "height": 568}, {"width": 1366, "height": 900}]:
        page.set_viewport_size(size)
        page.wait_for_timeout(100)
        values = page.evaluate("()=>Object.fromEntries([...document.querySelectorAll('select[data-group]')].map(s=>[s.dataset.group,s.value]))")
        assert values == KEY_DECISIONS
        assert "Eligible to propose" in page.inner_text("#governance-output")
    ctx.close()
    assert errors == []
