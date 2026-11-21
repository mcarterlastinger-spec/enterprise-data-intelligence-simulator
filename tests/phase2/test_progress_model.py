"""v0.4.0 learner progress model, proposals, and Next Step (Step 2).

Covers: decisions and feedback survive navigation (D6), duplicate submissions refused with
revision history kept (D5), inactive records ignored but their decisions retained (G5), Clear
groups affects only selected records (B2), synchronized comparison buttons, and a Next Step
that always names the learner's actual next action.
"""
from flow_helpers import KEY_DECISIONS, flow  # noqa: F401


def test_P1_check_results_reflect_identity_rules(flow):
    f = flow()
    f.select_all_and_compare()
    f.decide(KEY_DECISIONS)
    f.check()
    assert f.results() == [
        {"heading": "Group A · 2 record(s)", "verdict": "Eligible to propose for governance review",
         "button": "Submit merge proposal for Group A", "enabled": True},
        {"heading": "Group B · 2 record(s)", "verdict": "Eligible to propose for governance review",
         "button": "Submit merge proposal for Group B", "enabled": True}]
    text = f.page.inner_text("#governance-output")
    assert "Held for verification: REB-33907" in text and "Kept separate: CRM-10814" in text


def test_P2_unrelated_entities_cannot_be_submitted(flow):
    """D1 fixed: v0.3.2 offered a Submit button for REB-33907 + CRM-10814."""
    f = flow()
    f.select_all_and_compare()
    f.decide({"REB-33907": "D", "CRM-10814": "D"})
    f.check()
    r = f.results()[0]
    assert r["verdict"] == "Blocked: the evidence shows different entities" and r["button"] is None


def test_P3_rec_with_group_a_requires_verification(flow):
    f = flow()
    f.select_all_and_compare()
    f.decide({"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "A"})
    f.check()
    r = f.results()[0]
    assert r["verdict"] == "Verification required: identity cannot be confirmed" and r["button"] is None


def test_P4_single_record_group_not_called_eligible(flow):
    """D4 fixed."""
    f = flow()
    f.select_all_and_compare()
    f.decide({"CRM-10814": "C"})
    f.check()
    assert f.results()[0]["verdict"] == "No merge needed: a single record"


def test_P5_decisions_and_results_survive_navigation(flow):
    """D6 fixed: results are kept, not erased, when the learner leaves and returns."""
    f = flow()
    f.select_all_and_compare()
    f.decide(KEY_DECISIONS)
    f.check()
    before = f.results()
    f.app.nav("work")
    f.app.nav("brief")
    f.app.nav("compare")
    assert f.results() == before
    values = f.page.evaluate("()=>Object.fromEntries([...document.querySelectorAll('select[data-group]')].map(s=>[s.dataset.group,s.value]))")
    assert values == KEY_DECISIONS


def test_P6_changing_a_decision_marks_results_out_of_date(flow):
    f = flow()
    f.select_all_and_compare()
    f.decide(KEY_DECISIONS)
    f.check()
    f.decide({"CRM-10814": "B"})
    text = f.page.inner_text("#governance-output")
    assert "Out of date." in text
    assert all(r["button"] is None for r in f.results()), "no submitting from an out-of-date check"
    assert f.next_step()["label"] == "Next Step: Check proposed groups"


def test_P7_duplicate_submission_refused_and_history_kept(flow):
    """D5 fixed: identical resubmission refused; a changed group is a new revision."""
    f = flow()
    f.select_all_and_compare()
    f.decide(KEY_DECISIONS)
    f.check()
    f.submit("B")
    r = [x for x in f.results() if x["heading"].startswith("Group B")][0]
    assert r["button"] == "Submitted" and r["enabled"] is False
    # Relabel the same two records as Group C: still the same proposal.
    f.decide({"CRM-10489": "C", "ERP-77902": "C"})
    f.check()
    r = [x for x in f.results() if x["heading"].startswith("Group C")][0]
    assert r["button"] == "Submitted" and "already under review" in f.page.inner_text("#governance-output")
    assert len(f.history()) == 1


def test_P8_changed_membership_creates_revision(flow):
    f = flow()
    f.select_all_and_compare()
    f.decide({"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "A"})
    f.check()  # verification required: cannot submit
    f.decide({"REB-33907": "hold"})
    f.check()
    f.submit("A")
    f.app.nav("work")
    f.page.uncheck('#rows input[data-id="ERP-77831"]')
    f.page.check('#rows input[data-id="ERP-77831"]')
    f.app.nav("compare")
    assert f.history() == ["Group A, revision 1: CRM-10452, ERP-77831 · Current"]
    # Move ERP-77831 out and back in to a new letter: identical membership under another letter is a duplicate.
    f.decide({"CRM-10452": "D", "ERP-77831": "D"})
    f.check()
    assert [x for x in f.results() if x["heading"].startswith("Group D")][0]["button"] == "Submitted"


def test_P9_inactive_records_keep_decisions_but_do_not_count(flow):
    """G5: deselected records keep their decision; validation ignores them."""
    f = flow()
    f.select_all_and_compare()
    f.decide({"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "A"})
    f.app.nav("work")
    f.page.uncheck('#rows input[data-id="REB-33907"]')
    f.app.nav("compare")
    f.check()
    assert f.results()[0]["verdict"] == "Eligible to propose for governance review"
    f.app.nav("work")
    f.page.check('#rows input[data-id="REB-33907"]')
    f.app.nav("compare")
    assert f.page.input_value('select[data-group="REB-33907"]') == "A"
    assert "Out of date." in f.page.inner_text("#governance-output"), "reactivating a record changes the decisions checked"


def test_P10_filtering_never_changes_decisions(flow):
    f = flow()
    f.select_all_and_compare()
    f.decide(KEY_DECISIONS)
    f.check()
    f.app.nav("work")
    f.app.search("medical")
    f.page.select_option("#system", "ERP")
    f.page.select_option("#status", "Active")
    assert f.page.inner_text("#compare-btn") == "Compare selected records (6)"
    f.app.nav("compare")
    assert f.page.evaluate("()=>document.querySelectorAll('select[data-group]').length") == 6
    assert "Out of date." not in f.page.inner_text("#governance-output")


def test_P11_clear_groups_only_affects_selected_records(flow):
    """B2: approved behavior preserved."""
    f = flow()
    f.select_all_and_compare()
    f.decide(KEY_DECISIONS)
    f.app.nav("work")
    f.page.uncheck('#rows input[data-id="CRM-10814"]')
    f.app.nav("compare")
    f.app.click_button("Clear groups")
    assert set(f.page.evaluate("()=>[...document.querySelectorAll('select[data-group]')].map(s=>s.value)")) == {""}
    f.app.nav("work")
    f.page.check('#rows input[data-id="CRM-10814"]')
    f.app.nav("compare")
    assert f.page.input_value('select[data-group="CRM-10814"]') == "separate"


def test_P12_decision_change_keeps_keyboard_focus(flow):
    f = flow()
    f.select_all_and_compare()
    f.page.focus('select[data-group="CRM-10452"]')
    f.page.select_option('select[data-group="CRM-10452"]', "A")
    assert f.page.evaluate("()=>document.activeElement.dataset.group") == "CRM-10452"


# ---- comparison buttons and Next Step ------------------------------------------------------

def test_N1_comparison_buttons_synchronized(flow):
    f = flow()
    f.app.nav("work")
    for n, ids in [(0, []), (1, ["CRM-10452"]), (2, ["ERP-77831"])]:
        f.app.select_ids(ids)
        ns = f.next_step()
        assert f.page.inner_text("#compare-btn") == f"Compare selected records ({n})"
        assert ns["label"] == f"Next Step: Compare selected records ({n}) →"
        assert ns["disabled"] is f.page.is_disabled("#compare-btn") is (n < 2)
    f.page.click("#compare-btn")
    assert f.app.title() == "Match & Compare"
    f.app.nav("work")
    f.app.next()
    assert f.app.title() == "Match & Compare"


def test_N2_next_step_follows_actual_progress(flow):
    f = flow()
    seen = []
    f.app.next()
    f.app.click_button("Select all records")
    f.app.next()
    seen.append(f.next_step()["label"])
    f.app.next()  # focuses first undecided record
    assert f.page.evaluate("()=>document.activeElement.dataset.group") == "CRM-10452"
    f.decide(KEY_DECISIONS)
    seen.append(f.next_step()["label"])
    f.app.next()  # runs the check
    assert f.results()
    seen.append(f.next_step()["label"])
    f.app.next()
    assert f.page.evaluate("()=>document.activeElement.dataset.propose") == "A"
    f.submit("A")
    seen.append(f.next_step()["label"])
    f.submit("B")
    seen.append(f.next_step()["label"])
    f.app.next()
    assert f.app.title() == "Golden Record"
    seen.append(f.next_step()["label"])
    assert seen == ["Next Step: Go to the next undecided record", "Next Step: Check proposed groups",
                    "Next Step: Go to Group A’s proposal", "Next Step: Go to Group B’s proposal",
                    "Next Step: Build golden records →", "Next Step: Go to the next incomplete attribute"]


def test_N3_disabled_next_step_explains_why(flow):
    f = flow()
    f.app.nav("work")
    assert f.page.get_attribute("#next-step-button", "aria-describedby") == "next-step-description"
    assert f.next_step()["description"] == "Select at least two records to compare (0 selected)."


def test_N4_no_eligible_group_tells_learner_to_revise(flow):
    f = flow()
    f.select_all_and_compare()
    f.decide({"CRM-10452": "A", "CRM-10814": "A", "ERP-77831": "separate", "REB-33907": "hold",
              "CRM-10489": "separate", "ERP-77902": "separate"})
    f.check()
    assert f.next_step()["label"] == "Next Step: Review the check results"


def test_N5_navigation_marks_current_page(flow):
    f = flow()
    f.app.nav("work")
    assert f.page.get_attribute("#nav-work", "aria-current") == "page"
    assert f.page.get_attribute("#nav-brief", "aria-current") is None


def test_P13_revision_history_records_superseded_proposals(flow):
    f = flow()
    f.select_all_and_compare()
    f.decide({"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "hold", "CRM-10814": "separate",
              "CRM-10489": "separate", "ERP-77902": "separate"})
    f.check()
    f.submit("A")
    # The learner reconsiders: Group A should be the Medical Group pair instead.
    f.decide({"CRM-10452": "separate", "ERP-77831": "separate", "CRM-10489": "A", "ERP-77902": "A"})
    f.check()
    assert f.results()[0]["button"] == "Submit revision 2 for Group A"
    f.submit("A")
    assert f.history() == ["Group A, revision 1: CRM-10452, ERP-77831 · Superseded by revision 2",
                           "Group A, revision 2: CRM-10489, ERP-77902 · Current"]
