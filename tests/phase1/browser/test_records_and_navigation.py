"""Customer Records workspace, selection, Next Step, and page navigation."""
import pytest

ALL_ROWS = [
    ["", "CRM-10452", "Northbridge Health", "CRM", "Active", "2026-10-14"],
    ["", "ERP-77831", "Northbridge Health Inc.", "ERP", "Active", "2026-10-22"],
    ["", "REB-33907", "Northbridge Healthcare", "Rebates", "Pending", "2026-09-02"],
    ["", "CRM-10489", "Northbridge Medical Group", "CRM", "Active", "2026-10-18"],
    ["", "ERP-77902", "Northbridge Medical Group LLC", "ERP", "Active", "2026-10-20"],
    ["", "CRM-10814", "Northbridge Health Partners", "CRM", "Active", "2026-10-09"],
]


def _work(open_app, **kw):
    app = open_app(**kw)
    app.nav("work")
    return app


def test_R1_record_inventory(open_app):
    app = _work(open_app)
    assert app.title() == "Customer Record Workspace"
    assert app.table_rows() == ALL_ROWS
    assert app.results() == "Showing 6 of 6 records."
    assert app.text("#stat-all") == "6" and app.text("#stat-visible") == "6"


@pytest.mark.parametrize("query,expected_ids", [
    ("north", ["CRM-10452", "ERP-77831", "REB-33907", "CRM-10489", "ERP-77902", "CRM-10814"]),
    ("NORTHBRIDGE MEDICAL", ["CRM-10489", "ERP-77902"]),
    ("91-7728041", ["CRM-10489", "ERP-77902"]),
    ("100 Medical Pkwy", ["REB-33907"]),          # abbreviations are not normalized
    ("Holdings", ["CRM-10452", "ERP-77831", "REB-33907", "CRM-10489", "ERP-77902"]),
    ("nbpartners", []),                           # contact email is not searched
    ("Tacoma", ["CRM-10489", "ERP-77902"]),
])
def test_R2_search(open_app, query, expected_ids):
    app = _work(open_app)
    app.search(query)
    ids = [r[1] for r in app.table_rows() if len(r) > 1]
    assert ids == expected_ids
    assert app.results() == f"Showing {len(expected_ids)} of 6 records."
    assert app.text("#stat-visible") == str(len(expected_ids))


def test_R3_filters_and_reset(open_app):
    app = _work(open_app)
    p = app.page
    p.select_option("#system", "ERP")
    assert [r[1] for r in app.table_rows()] == ["ERP-77831", "ERP-77902"]
    p.select_option("#system", "Rebates")
    assert [r[1] for r in app.table_rows()] == ["REB-33907"]
    p.select_option("#system", "")
    p.select_option("#status", "Pending")
    assert [r[1] for r in app.table_rows()] == ["REB-33907"]
    p.select_option("#status", "Active")
    p.select_option("#system", "CRM")
    assert [r[1] for r in app.table_rows()] == ["CRM-10452", "CRM-10489", "CRM-10814"]
    app.search("zzz")
    assert app.table_rows() == [["No matching records. Adjust your filters."]]
    assert app.results() == "Showing 0 of 6 records."
    app.click_button("Reset")
    assert app.table_rows() == ALL_ROWS
    assert p.input_value("#search") == "" and p.input_value("#system") == "" and p.input_value("#status") == ""


def test_R4_record_details_panel(open_app):
    app = _work(open_app)
    assert not app.visible("#details")
    app.page.click('[data-open="REB-33907"]')
    assert app.visible("#details")
    assert app.text("#details-title") == "Record details · REB-33907"
    fields = app.page.evaluate("()=>[...document.querySelectorAll('#details-fields .field')].map(f=>[f.querySelector('b').innerText.trim(),f.lastChild.textContent])")
    assert fields == [
        ["CUSTOMER", "Northbridge Healthcare"], ["LEGAL NAME", "Not provided"], ["TAX IDENTIFIER", "Missing"],
        ["BUSINESS ADDRESS", "100 Medical Pkwy, Seattle, WA"], ["PARENT ORGANIZATION", "Northbridge Holdings"],
        ["CONTACT EMAIL", "rebates@northbridge.example"], ["LAST VERIFIED", "2026-09-02"],
        ["SOURCE NOTE", "Incomplete tax identifier; rebate account needs verification."]]
    app.click_button("Close details")
    assert not app.visible("#details")


def test_R5_selection_controls(open_app):
    app = _work(open_app)
    btn = "#compare-btn"
    assert app.text(btn) == "Evaluate selected records (0)" and app.page.is_disabled(btn)
    app.select_ids(["CRM-10452"])
    assert app.text(btn) == "Evaluate selected records (1)" and app.page.is_disabled(btn)
    app.select_ids(["ERP-77831"])
    assert app.text(btn) == "Evaluate selected records (2)" and not app.page.is_disabled(btn)
    app.click_button("Clear selection")
    assert app.text(btn) == "Evaluate selected records (0)"
    app.page.select_option("#system", "ERP")
    app.click_button("Select all visible")
    assert app.text(btn) == "Evaluate selected records (2)"
    app.page.select_option("#system", "")
    checked = app.page.evaluate("()=>[...document.querySelectorAll('#rows input:checked')].map(i=>i.dataset.id)")
    assert checked == ["ERP-77831", "ERP-77902"]
    app.click_button("Select all records")
    assert app.text(btn) == "Evaluate selected records (6)"


def test_C9_selection_persists_through_filtering(open_app):
    """APPROVED BEHAVIOR (decision 2026-11-05, formerly D10): filtering changes visibility, not selection.
    Records hidden by a filter stay selected and are counted. A UX improvement to distinguish
    visible from total selected records is documented as UX-1 in KNOWN-DEFECTS.md (not in Phase 1)."""
    app = _work(open_app)
    app.click_button("Select all records")
    app.page.select_option("#system", "ERP")
    assert app.results() == "Showing 2 of 6 records."
    assert app.text("#compare-btn") == "Evaluate selected records (6)"


def test_N1_next_step_full_path(open_app):
    app = open_app()
    app.next()
    assert app.title() == "Customer Record Workspace"
    assert app.next_step() == {"heading": "Ready to compare?",
                               "description": "Select at least two records to compare (0 selected).",
                               "label": "Next Step: Compare Selected Records →", "disabled": True}
    app.select_ids(["CRM-10452"])
    assert app.next_step()["description"] == "Select at least two records to compare (1 selected)."
    assert app.next_step()["disabled"] is True
    app.select_ids(["ERP-77831"])
    assert app.next_step() == {"heading": "Ready to compare?",
                               "description": "Select two or more records to investigate their identity evidence together.",
                               "label": "Next Step: Compare Selected Records →", "disabled": False}
    app.next()
    assert app.title() == "Match & Compare"
    assert app.next_step() == {"heading": "Review or revise your investigation",
                               "description": "Return to the record inventory to inspect evidence and adjust your selection.",
                               "label": "Next Step: Return to Customer Records →", "disabled": False}
    app.next()
    assert app.title() == "Customer Record Workspace"
    checked = app.page.evaluate("()=>[...document.querySelectorAll('#rows input:checked')].map(i=>i.dataset.id)")
    assert checked == ["CRM-10452", "ERP-77831"], "selection must survive navigation"


def test_N2_sidebar_navigation(open_app):
    app = open_app()
    for key, title in [("work", "Customer Record Workspace"), ("compare", "Match & Compare"), ("brief", "Mission Briefing")]:
        app.nav(key)
        assert app.title() == title
        actives = app.page.evaluate("()=>[...document.querySelectorAll('.nav.active')].map(b=>b.id)")
        assert actives == [f"nav-{key}"]
        assert app.page.evaluate("()=>scrollY") == 0
    disabled = app.page.evaluate("()=>[...document.querySelectorAll('.nav:disabled')].map(b=>[b.innerText.trim(),b.title])")
    assert disabled == [["◇ \xa0 Golden Record (next)", "Planned for next milestone"],
                        ["✓ \xa0 Validation (next)", "Planned for next milestone"]]


def test_N3_in_page_links(open_app):
    app = _work(open_app)
    app.click_button("View mission briefing")
    assert app.title() == "Mission Briefing"
    app.click_button("Open records workspace")
    assert app.title() == "Customer Record Workspace"
    app.nav("compare")
    assert "Select at least two records." in app.text("#compare-content")
    app.page.click("#compare-content button")  # "Select records"
    assert app.title() == "Customer Record Workspace"


@pytest.mark.known_defect("D8")
def test_C11_D8_stakeholders_on_every_page(open_app):
    """KNOWN DEFECT D8 — NOT APPROVED BEHAVIOR (Phase 2: contextual stakeholders): gallery shows on every page."""
    app = open_app()
    for key in ["brief", "work", "compare"]:
        app.nav(key)
        assert app.visible(".cast-grid"), key
    names = app.page.evaluate("()=>[...document.querySelectorAll('.cast-member strong')].map(s=>s.innerText)")
    assert names == ["Maya Chen", "Priya Shah", "Daniel Brooks", "Marcus Reed"]
