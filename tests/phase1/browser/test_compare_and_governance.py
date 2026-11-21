"""Match & Compare: comparison matrix, identity grouping, governance validation.

Tests marked known_defect record v0.3.2 behavior that is WRONG and scheduled for
correction (see KNOWN-DEFECTS.md). They exist so the defect cannot change silently,
and so Phase 2 can flip them deliberately.
"""
import pytest

ALL_IDS = ["CRM-10452", "ERP-77831", "REB-33907", "CRM-10489", "ERP-77902", "CRM-10814"]
CORRECT_GROUPING = {"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "A",
                    "CRM-10489": "B", "ERP-77902": "B", "CRM-10814": "C"}


def _compare(open_app, ids=None, **kw):
    app = open_app(**kw)
    app.nav("work")
    if ids is None:
        app.click_button("Select all records")
    else:
        app.select_ids(ids)
    app.nav("compare")
    return app


def test_CMP1_matrix_all_records(open_app):
    app = _compare(open_app)
    m = app.matrix()
    assert m["columns"] == ["CRM-10452 Northbridge Health", "ERP-77831 Northbridge Health Inc.",
                            "REB-33907 Northbridge Healthcare", "CRM-10489 Northbridge Medical Group",
                            "ERP-77902 Northbridge Medical Group LLC", "CRM-10814 Northbridge Health Partners"]
    assert [(r["label"], r["state"]) for r in m["rows"]] == [
        ("Legal name", "Missing evidence"), ("Tax identifier", "Missing evidence"),
        ("Business address", "Conflict / difference"), ("Parent organization", "Conflict / difference"),
        ("Source system", "Conflict / difference"), ("Last verified", "Conflict / difference")]
    legal = m["rows"][0]["cells"]
    assert [c["text"] for c in legal] == ["Northbridge Health Inc.", "Northbridge Health Inc.", "Missing",
                                          "Northbridge Medical Group LLC", "Northbridge Medical Group LLC",
                                          "Northbridge Health Partners LLC"]
    assert [c["cls"] for c in legal] == ["conflict", "conflict", "missing", "conflict", "conflict", "conflict"]
    notice = app.text("#compare-content .notice")
    assert notice == ("All 6 selected records are evaluated together. Differences are not automatically "
                      "identity conflicts. Grouping does not merge records.")


def test_CMP2_matrix_consistent_pair(open_app):
    app = _compare(open_app, ["CRM-10489", "ERP-77902"])
    m = app.matrix()
    assert [(r["label"], r["state"]) for r in m["rows"]] == [
        ("Legal name", "Consistent"), ("Tax identifier", "Consistent"), ("Business address", "Consistent"),
        ("Parent organization", "Consistent"), ("Source system", "Conflict / difference"),
        ("Last verified", "Conflict / difference")]
    assert {c["cls"] for c in m["rows"][0]["cells"]} == {"consistent"}


def test_CMP3_fewer_than_two_selected(open_app):
    app = _compare(open_app, ["CRM-10452"])
    assert app.matrix() is None
    assert app.text("#compare-content .notice") == ("Select at least two records. You can evaluate the "
                                                    "entire dataset simultaneously.")


@pytest.mark.known_defect("D2")
def test_C4_D2_missing_hides_conflict(open_app):
    """KNOWN DEFECT D2 — INSTRUCTIONAL INTEGRITY — NOT APPROVED BEHAVIOR.
    Legal name and Tax identifier each hold 3 contradictory values, but because one
    record is missing a value, the row is labelled only 'Missing evidence'.
    Approved requirement: missing values must never conceal contradictory evidence."""
    app = _compare(open_app)
    rows = {r["label"]: r for r in app.matrix()["rows"]}
    for label in ["Legal name", "Tax identifier"]:
        present = {c["text"] for c in rows[label]["cells"] if c["text"] != "Missing"}
        assert len(present) == 3, "the evidence really does conflict"
        assert rows[label]["state"] == "Missing evidence", "defect D2 still present (expected until Phase 2)"


@pytest.mark.known_defect("D3")
def test_C5_D3_metadata_rows_flagged_as_conflict(open_app):
    """KNOWN DEFECT D3 — NOT APPROVED BEHAVIOR: source system and verification date are expected to differ."""
    app = _compare(open_app, ["CRM-10489", "ERP-77902"])
    rows = {r["label"]: r["state"] for r in app.matrix()["rows"]}
    assert rows["Source system"] == "Conflict / difference"
    assert rows["Last verified"] == "Conflict / difference"


def test_G1_group_table_and_options(open_app):
    app = _compare(open_app)
    rows = app.page.evaluate("""()=>[...document.querySelectorAll('#compare-content table:not(.matrix) tbody tr')]
        .map(tr=>[tr.cells[0].innerText.trim(),tr.cells[1].innerText.trim()])""")
    assert rows == [["CRM-10452 · Northbridge Health", "91-4826103"], ["ERP-77831 · Northbridge Health Inc.", "91-4826103"],
                    ["REB-33907 · Northbridge Healthcare", "Missing"], ["CRM-10489 · Northbridge Medical Group", "91-7728041"],
                    ["ERP-77902 · Northbridge Medical Group LLC", "91-7728041"],
                    ["CRM-10814 · Northbridge Health Partners", "91-9346180"]]
    options = app.page.evaluate("()=>[...document.querySelectorAll('select[data-group=\"CRM-10452\"] option')].map(o=>[o.value,o.text])")
    assert options == [["", "Unassigned"]] + [[g, f"Group {g}"] for g in "ABCDEF"]


def test_G2_validate_without_assignments(open_app):
    app = _compare(open_app)
    app.validate()
    assert "Assign records to proposed groups before validating." in app.text("#governance-output")


@pytest.mark.known_defect("D4")
def test_C1_correct_grouping_verdicts(open_app):
    """Correct identity grouping. Also records KNOWN DEFECT D4 — NOT APPROVED BEHAVIOR: a single-record group is called eligible."""
    app = _compare(open_app)
    app.assign(CORRECT_GROUPING)
    app.validate()
    assert app.governance() == [
        {"heading": "Group A · 3 record(s)", "verdict": "REVIEW REQUIRED: incomplete or differing identity evidence",
         "records": "CRM-10452, ERP-77831, REB-33907", "can_submit": True},
        {"heading": "Group B · 2 record(s)", "verdict": "ELIGIBLE FOR GOVERNANCE REVIEW (not approved)",
         "records": "CRM-10489, ERP-77902", "can_submit": True},
        {"heading": "Group C · 1 record(s)", "verdict": "ELIGIBLE FOR GOVERNANCE REVIEW (not approved)",
         "records": "CRM-10814", "can_submit": False}]
    assert "This prototype records merge proposals only." in app.text("#governance-output")


def test_C2_conflicting_tax_ids_blocked(open_app):
    app = _compare(open_app)
    app.assign({i: "A" for i in ALL_IDS[:5]})
    app.validate()
    g = app.governance()[0]
    assert g == {"heading": "Group A · 5 record(s)", "verdict": "BLOCKED: conflicting tax identifiers",
                 "records": "CRM-10452, ERP-77831, REB-33907, CRM-10489, ERP-77902", "can_submit": False}


@pytest.mark.known_defect("D1")
def test_C3_D1_unrelated_entities_can_be_submitted(open_app):
    """KNOWN DEFECT D1 — INSTRUCTIONAL INTEGRITY — NOT APPROVED BEHAVIOR.
    REB-33907 (no tax ID) and CRM-10814 (parent 'Independent', different city) are
    unrelated legal entities, yet the validator offers a merge proposal.
    Approved requirement: a merge must not be accepted simply because records share
    similar names or organizational relationships."""
    app = _compare(open_app)
    app.assign({"REB-33907": "D", "CRM-10814": "D"})
    app.validate()
    assert app.governance() == [
        {"heading": "Group D · 2 record(s)", "verdict": "REVIEW REQUIRED: incomplete or differing identity evidence",
         "records": "REB-33907, CRM-10814", "can_submit": True}]
    app.page.click('[data-propose="D"]')
    assert app.text("#audit") == ("Group D proposal logged for governance review. No merge has occurred. "
                                  "1 proposal(s) recorded this session.")


@pytest.mark.known_defect("D5")
def test_C6_D5_duplicate_proposals_counted(open_app):
    """KNOWN DEFECT D5 — NOT APPROVED BEHAVIOR: the same proposal can be logged repeatedly."""
    app = _compare(open_app)
    app.assign({"CRM-10489": "B", "ERP-77902": "B"})
    app.validate()
    app.page.click('[data-propose="B"]')
    app.page.click('[data-propose="B"]')
    assert app.text("#audit").endswith("2 proposal(s) recorded this session.")


def test_G3_changing_groups_requires_revalidation(open_app):
    app = _compare(open_app)
    app.assign({"CRM-10489": "B", "ERP-77902": "B"})
    app.validate()
    app.page.select_option('select[data-group="CRM-10452"]', "C")
    assert app.text("#governance-output") == "Groups changed. Run validation again before review."


def test_G4_clear_groups(open_app):
    app = _compare(open_app)
    app.assign(CORRECT_GROUPING)
    app.click_button("Clear groups")
    values = app.page.evaluate("()=>[...document.querySelectorAll('select[data-group]')].map(s=>s.value)")
    assert values == [""] * 6
    assert app.text("#governance-output") == ""


@pytest.mark.known_defect("D6")
def test_C7_D6_validation_results_lost_on_return(open_app):
    """Group choices survive navigation (correct; must be preserved). KNOWN DEFECT D6 — NOT APPROVED BEHAVIOR: validation results do not."""
    app = _compare(open_app)
    app.assign(CORRECT_GROUPING)
    app.validate()
    app.nav("work")
    app.nav("compare")
    values = app.page.evaluate("()=>Object.fromEntries([...document.querySelectorAll('select[data-group]')].map(s=>[s.dataset.group,s.value]))")
    assert values == CORRECT_GROUPING
    assert app.text("#governance-output") == ""


def test_G5_deselected_records_excluded_but_remembered(open_app):
    app = _compare(open_app)
    app.assign({"CRM-10489": "B", "ERP-77902": "B", "CRM-10814": "B"})
    app.nav("work")
    app.page.uncheck('#rows input[data-id="CRM-10814"]')
    app.nav("compare")
    app.validate()
    assert app.governance()[0]["records"] == "CRM-10489, ERP-77902"
    app.nav("work")
    app.page.check('#rows input[data-id="CRM-10814"]')
    app.nav("compare")
    assert app.page.input_value('select[data-group="CRM-10814"]') == "B"


def test_rule_norm_characterization(open_app):
    """Records the legal-name normalization exactly as v0.3.2 implements it (see D9)."""
    app = open_app()
    expr = app.rule("norm")
    cases = ["Northbridge Health Inc.", "Northbridge Healthcare", "Northbridge Medical Group LLC",
             "NORTHBRIDGE   health, incorporated", "Acme-Co. LLC", ""]
    got = app.page.evaluate(f"cases=>{{const f={expr};return cases.map(c=>f(c))}}", cases)
    assert got == ["northbridgehealth", "northbridge", "northbridgemedicalgroup", "northbridgehealth", "acmeco", ""]
