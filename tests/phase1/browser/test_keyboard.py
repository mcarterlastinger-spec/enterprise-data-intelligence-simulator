"""Keyboard operation and focus behavior."""
import pytest


def test_K1_briefing_tab_order(open_app):
    """Explicit Tab order on Mission Briefing (the first screen a learner sees)."""
    app = open_app()
    app.page.evaluate("()=>document.activeElement&&document.activeElement.blur()")
    seq = []
    for _ in range(7):
        app.page.keyboard.press("Tab")
        f = app.focused()
        seq.append(f["id"] or f["text"])
    assert seq == ["nav-work", "nav-compare", "nav-brief", "▶ Play", "↺ Replay",
                   "Open records workspace", "next-step-button"]


@pytest.mark.parametrize("page_key", ["brief", "work", "compare"])
def test_K2_tab_order_matches_baseline(open_app, browser, page_key, target):
    """The full Tab order on each page must match v0.3.2 exactly."""
    from conftest import TARGET_FILES, SPEECH_MOCK
    def order(file):
        ctx = browser.new_context(viewport={"width": 1366, "height": 900})
        ctx.add_init_script(SPEECH_MOCK)
        p = ctx.new_page(); p.goto(file.as_uri()); p.wait_for_timeout(350)
        p.click({"work": "#nav-work", "compare": "#nav-compare", "brief": "#nav-brief"}[page_key])
        if page_key == "compare":
            p.click("#nav-work"); p.get_by_role("button", name="Select all records", exact=True).click(); p.click("#nav-compare")
        p.evaluate("()=>{document.activeElement&&document.activeElement.blur();window.scrollTo(0,0)}")
        p.click(".brand")  # clicking non-interactive text sets the Tab starting point to the top of the page
        seen = []
        # One full pass through the page. Stop when focus leaves the last control: what happens
        # after that (browser toolbar or wrap to the top) depends on the browser, not the page.
        for _ in range(80):
            p.keyboard.press("Tab")
            item = p.evaluate("""()=>{const e=document.activeElement;
                return [e.tagName,e.id,e.getAttribute('aria-label')||'',(e.innerText||'').trim().slice(0,40),
                        e.dataset.id||e.dataset.open||e.dataset.group||e.dataset.source||''].join('|')}""")
            if item.startswith("BODY|") or (seen and item == seen[0]):
                break
            seen.append(item)
        ctx.close()
        return seen
    base = order(TARGET_FILES["baseline"])
    assert len(base) > 5, "tab order unexpectedly short"
    assert order(TARGET_FILES[target]) == base


def test_K3_keyboard_completes_core_path(open_app):
    """Brief -> Records -> select two records -> Compare using only the keyboard."""
    app = open_app()
    app.page.focus("#next-step-button")
    app.page.keyboard.press("Enter")
    assert app.title() == "Customer Record Workspace"
    app.page.focus('#rows input[data-id="CRM-10489"]')
    app.page.keyboard.press("Space")
    app.page.focus('#rows input[data-id="ERP-77902"]')
    app.page.keyboard.press("Space")
    app.page.focus("#next-step-button")
    app.page.keyboard.press("Enter")
    assert app.title() == "Match & Compare"
    app.page.focus('select[data-group="CRM-10489"]')
    app.page.select_option('select[data-group="CRM-10489"]', "B")
    app.page.select_option('select[data-group="ERP-77902"]', "B")
    app.page.focus("#review-groups")
    app.page.keyboard.press("Enter")
    assert app.governance()[0]["verdict"] == "ELIGIBLE FOR GOVERNANCE REVIEW (not approved)"


def test_K4_audio_toggle_by_keyboard(open_app):
    app = open_app()
    app.page.focus('.audio-toggle[data-source="brief-text"]')
    app.page.keyboard.press("Enter")
    assert app.text('.audio-toggle[data-source="brief-text"]') == "Ⅱ Pause"
    app.page.keyboard.press("Space")
    assert app.text('.audio-toggle[data-source="brief-text"]') == "▶ Resume"
    assert app.focused()["data"].get("source") == "brief-text", "focus stays on the toggle"


@pytest.mark.known_defect("D7")
def test_C8_D7_checkbox_focus_lost(open_app):
    """KNOWN DEFECT D7 — NOT APPROVED BEHAVIOR: toggling a checkbox rebuilds the table and drops focus."""
    app = open_app()
    app.nav("work")
    app.page.focus('#rows input[data-id="CRM-10452"]')
    app.page.keyboard.press("Space")
    assert app.page.is_checked('#rows input[data-id="CRM-10452"]')
    assert app.focused()["tag"] == "BODY"
