"""Retained learner decisions (approved behaviors A2 and G5).

Filtering changes visibility, not selection. Deselecting a record keeps its group
assignment, but inactive (deselected) records must not affect validation or proposals.
These tests confirm that filtering and deselection never silently alter retained decisions.
"""
ASSIGN = {"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "A",
          "CRM-10489": "B", "ERP-77902": "B", "CRM-10814": "C"}


def _groups(app):
    return app.page.evaluate("()=>Object.fromEntries([...document.querySelectorAll('select[data-group]')].map(s=>[s.dataset.group,s.value]))")


def _checked(app):
    return app.page.evaluate("()=>[...document.querySelectorAll('#rows input:checked')].map(i=>i.dataset.id)")


def test_T1_filtering_keeps_selection_and_groups(open_app):
    app = open_app()
    app.nav("work")
    app.click_button("Select all records")
    app.nav("compare")
    app.assign(ASSIGN)
    app.nav("work")
    # Apply every kind of filter; none may change selection.
    app.search("medical")
    app.page.select_option("#system", "ERP")
    app.page.select_option("#status", "Active")
    assert app.text("#compare-btn") == "Evaluate selected records (6)"
    app.click_button("Reset")
    assert _checked(app) == list(ASSIGN)
    app.nav("compare")
    assert _groups(app) == ASSIGN


def test_T2_deselected_records_keep_groups_but_do_not_count(open_app):
    app = open_app()
    app.nav("work")
    app.click_button("Select all records")
    app.nav("compare")
    app.assign(ASSIGN)
    app.nav("work")
    # Deselect one record from Group A while a filter hides other records.
    app.page.select_option("#system", "Rebates")
    app.page.uncheck('#rows input[data-id="REB-33907"]')
    app.page.select_option("#system", "")
    app.nav("compare")
    assert "REB-33907" not in _groups(app), "deselected record is not shown in grouping"
    app.validate()
    verdicts = {g["heading"]: g for g in app.governance()}
    assert verdicts["Group A · 2 record(s)"]["records"] == "CRM-10452, ERP-77831"
    assert verdicts["Group A · 2 record(s)"]["verdict"] == "ELIGIBLE FOR GOVERNANCE REVIEW (not approved)", \
        "inactive REB-33907 (missing identifiers) must not influence Group A's verdict"
    app.page.click('[data-propose="A"]')
    assert app.text("#audit").endswith("1 proposal(s) recorded this session.")
    # Reselect: the retained assignment comes back unchanged.
    app.nav("work")
    app.page.check('#rows input[data-id="REB-33907"]')
    app.nav("compare")
    assert _groups(app) == ASSIGN


def test_T3_clear_groups_affects_only_selected_records(open_app):
    app = open_app()
    app.nav("work")
    app.click_button("Select all records")
    app.nav("compare")
    app.assign(ASSIGN)
    app.nav("work")
    app.page.uncheck('#rows input[data-id="CRM-10814"]')
    app.nav("compare")
    app.click_button("Clear groups")
    assert set(_groups(app).values()) == {""}
    app.nav("work")
    app.page.check('#rows input[data-id="CRM-10814"]')
    app.nav("compare")
    assert _groups(app)["CRM-10814"] == "C", "the inactive record's retained assignment survives Clear groups"
