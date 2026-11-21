"""v0.4.0 Validation, scoring, and Debrief (Steps 4 and 5).

Validation: automatic checklist, identity evidence, rationale, "Submitted for Governance Review"
(never approval), revalidation and revision history after changes.
Scoring: 23 points, one decision per point, transparent criteria, levels at 85% / 50%.
Debrief: decision-specific feedback, locked review after finishing, retry as a new attempt.
"""
import pytest

from flow_helpers import GOLDEN_A, KEY_DECISIONS, flow  # noqa: F401

KA, KB = "CRM-10452|ERP-77831", "CRM-10489|ERP-77902"
SA, SB = "CRM-10452-ERP-77831", "CRM-10489-ERP-77902"
GOLDEN_B = {"legalName": ("Northbridge Medical Group LLC", "agree"), "taxId": ("91-7728041", "agree"),
            "operatingAddress": ("20 Clinic Way, Tacoma, WA", "agree"), "billingAddress": ("20 Clinic Way, Tacoma, WA", "billing-source"),
            "parent": ("Northbridge Holdings", "agree"), "primaryContact": ("office@nbmedical.example", "crm-operating")}
RATIONALE = "Both records carry the same tax identifier and the same legal name in CRM and ERP, so they describe one legal entity."


def to_validation(f, golden_a=GOLDEN_A, golden_b=GOLDEN_B):
    f.to_golden_with_proposals()
    f.fill_golden(KA, golden_a)
    f.save(KA)
    f.fill_golden(KB, golden_b)
    f.save(KB)
    f.app.nav("validation")


def complete_validation(f, basis=("tax", "legal"), rationale=RATIONALE, np=None, follow="request"):
    for s in (SA, SB):
        for b in basis:
            f.page.check(f"#vb-{s}-{b}")
        f.page.fill(f"#vr-{s}", rationale)
        f.page.click(f'[data-submit-review="{KA if s == SA else KB}"]')
    np = np or {"CRM-10814": "conflict-identity", "REB-33907": "missing-identity"}
    for rid, reason in np.items():
        f.page.select_option(f"#np-{rid}", reason)
    if follow:
        f.page.select_option("#nf-REB-33907", follow)


def checklist(f, s):
    return f.page.evaluate(f"()=>[...document.querySelectorAll('#vc-{s} .checklist li')].map(li=>[li.className, li.lastChild.textContent.trim()])")


def finish(f):
    f.page.click("#finish-case")


def debrief(f):
    return f.page.evaluate("""()=>({total:document.getElementById('debrief-h').innerText,
        comps:[...document.querySelectorAll('.competency')].filter(s=>s.querySelector('.comp-score')).map(s=>({name:s.querySelector('h3').innerText,
            score:s.querySelector('.comp-score strong').innerText, level:s.querySelector('.comp-score .level').innerText,
            criteria:[...s.querySelectorAll('.criteria li')].map(li=>({met:li.classList.contains('met'), text:li.querySelector('.crit-title').innerText, feedback:li.querySelector('.crit-feedback').innerText}))}))})""")


# ---- Validation -----------------------------------------------------------------------------

def test_V1_checklist_blocks_submission_until_complete(flow):
    f = flow()
    to_validation(f)
    items = checklist(f, SA)
    assert [c[0] for c in items] == ["pass", "pass", "pass", "fail", "fail"]
    assert items[3][1] == "Identity evidence selected"
    assert f.page.is_disabled(f'[data-submit-review="{KA}"]')
    f.page.check(f"#vb-{SA}-tax")
    f.page.fill(f"#vr-{SA}", "Too short to count.")
    assert checklist(f, SA)[4] == ["fail", "Governance rationale written (4 of at least 12 words)"]
    f.page.fill(f"#vr-{SA}", RATIONALE)
    assert all(c[0] == "pass" for c in checklist(f, SA))
    assert not f.page.is_disabled(f'[data-submit-review="{KA}"]')


def test_V2_submission_is_review_not_approval(flow):
    f = flow()
    to_validation(f)
    f.page.check(f"#vb-{SA}-tax")
    f.page.check(f"#vb-{SA}-legal")
    f.page.fill(f"#vr-{SA}", RATIONALE)
    f.page.click(f'[data-submit-review="{KA}"]')
    status = f.page.inner_text(f"#vs-{SA}")
    assert status.startswith("Submitted for Governance Review (revision 1")
    assert "No merge or approval has occurred." in status
    assert "approved" not in status.lower().replace("no merge or approval", "")
    btn = f.page.locator(f'[data-submit-review="{KA}"]')
    assert btn.inner_text() == "Submitted for Governance Review" and btn.is_disabled()


def test_V3_changes_require_revalidation_and_keep_history(flow):
    f = flow()
    to_validation(f)
    f.page.check(f"#vb-{SA}-tax")
    f.page.check(f"#vb-{SA}-legal")
    f.page.fill(f"#vr-{SA}", RATIONALE)
    f.page.click(f'[data-submit-review="{KA}"]')
    # Change the golden record after submitting.
    f.app.nav("golden")
    f.choose(KA, "primaryContact", "ap@northbridge.example", "billing-source")
    f.save(KA)
    f.app.nav("validation")
    assert f.page.inner_text(f"#vs-{SA}").startswith("Changed since submission.")
    assert f.page.inner_text(f'[data-submit-review="{KA}"]') == "Resubmit Group A (revision 2)"
    f.page.click(f'[data-submit-review="{KA}"]')
    assert "revision 2" in f.page.inner_text(f"#vs-{SA}")
    hist = f.page.evaluate(f"()=>[...document.querySelectorAll('#vhist-{SA} li')].map(li=>li.textContent)")
    assert len(hist) == 2 and "golden record revision 1" in hist[0] and "golden record revision 2" in hist[1]


def test_V4_editing_rationale_after_submission_marks_it_changed(flow):
    f = flow()
    to_validation(f)
    f.page.check(f"#vb-{SA}-tax")
    f.page.fill(f"#vr-{SA}", RATIONALE)
    f.page.click(f'[data-submit-review="{KA}"]')
    f.page.fill(f"#vr-{SA}", RATIONALE + " Verified by the finance team.")
    assert f.page.inner_text(f"#vs-{SA}").startswith("Changed since submission.")


def test_V5_advisory_evidence_consistency(flow):
    f = flow()
    golden = dict(GOLDEN_A, operatingAddress=("400 Billing Plaza, Seattle, WA", "crm-operating"))
    to_validation(f, golden_a=golden)
    adv = f.page.inner_text(f"#vc-{SA}")
    assert "Operating address: You cited the CRM relationship record, but this value does not come from a CRM record." in adv
    assert "(advisory)" in adv


def test_V6_finish_requires_every_item(flow):
    f = flow()
    to_validation(f)
    assert f.page.is_disabled("#finish-case")
    blockers = f.page.inner_text("#finish-why")
    assert "Submit Group A for governance review." in blockers and "Choose a follow-up for REB-33907." in blockers
    complete_validation(f)
    assert not f.page.is_disabled("#finish-case")
    assert f.next_step()["label"] == "Next Step: Finish case and view debrief"


def test_V7_validation_survives_navigation(flow):
    f = flow()
    to_validation(f)
    f.page.check(f"#vb-{SA}-tax")
    f.page.fill(f"#vr-{SA}", RATIONALE)
    f.page.locator(f"#vr-{SA}").blur()
    f.app.nav("work")
    f.app.nav("validation")
    assert f.page.is_checked(f"#vb-{SA}-tax") and f.page.input_value(f"#vr-{SA}") == RATIONALE


# ---- Scoring and Debrief ---------------------------------------------------------------------

def test_S1_perfect_run_scores_23(flow):
    f = flow()
    to_validation(f)
    complete_validation(f)
    finish(f)
    assert f.app.title() == "Debrief"
    d = debrief(f)
    assert d["total"] == "Your result: 23 of 23 points"
    assert [(c["name"], c["score"], c["level"]) for c in d["comps"]] == [
        ("Evidence Analysis", "4 of 4 points", "Proficient"), ("Identity Resolution", "4 of 4 points", "Proficient"),
        ("Data Reconciliation", "12 of 12 points", "Proficient"), ("Governance Judgment", "3 of 3 points", "Proficient")]


def test_S2_mistakes_get_decision_specific_feedback(flow):
    f = flow()
    golden = dict(GOLDEN_A, operatingAddress=("400 Billing Plaza, Seattle, WA", "recent"), primaryContact=("ap@northbridge.example", "crm-operating"))
    to_validation(f, golden_a=golden)
    complete_validation(f, basis=("tax", "legal", "name"), rationale="These records describe the same organization because the names and addresses match closely across systems.",
                        np={"CRM-10814": "name", "REB-33907": "missing-identity"}, follow="merge-now")
    finish(f)
    d = {c["name"]: c for c in debrief(f)["comps"]}
    ea = d["Evidence Analysis"]
    assert ea["score"] == "1 of 4 points" and ea["level"] == "Needs Practice"
    assert "You also cited similar customer names: supporting evidence only" in ea["criteria"][0]["feedback"]
    assert 'You said: "Its customer name is different."' in ea["criteria"][2]["feedback"]
    dr = d["Data Reconciliation"]
    assert dr["score"] == "10 of 12 points" and dr["level"] == "Developing"
    op = [c for c in dr["criteria"] if "Northbridge Health Inc.: Operating address" in c["text"]][0]
    assert 'You chose "400 Billing Plaza, Seattle, WA". Expected "100 Medical Parkway, Seattle, WA".' in op["feedback"]
    gj = d["Governance Judgment"]
    assert gj["score"] == "1 of 3 points"
    assert "Mention the matching tax identifier or legal name" in gj["criteria"][1]["feedback"]
    assert 'You chose: "Merge it into the matching group now' in gj["criteria"][2]["feedback"]
    assert d["Identity Resolution"]["score"] == "4 of 4 points", "identity decisions are scored once, not again elsewhere"


def test_S3_wrong_identity_decisions(flow):
    f = flow()
    f.select_all_and_compare()
    f.decide({"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "separate", "CRM-10489": "B", "ERP-77902": "B", "CRM-10814": "hold"})
    f.check()
    f.submit("A")
    f.submit("B")
    f.app.nav("golden")
    f.fill_golden(KA, GOLDEN_A)
    f.save(KA)
    f.fill_golden(KB, GOLDEN_B)
    f.save(KB)
    f.app.nav("validation")
    complete_validation(f, np={"CRM-10814": "conflict-identity", "REB-33907": "missing-identity"}, follow=None)
    f.page.select_option("#nf-CRM-10814", "request")  # CRM-10814 was (wrongly) held, so it needs a follow-up
    finish(f)
    ir = {c["name"]: c for c in debrief(f)["comps"]}["Identity Resolution"]
    assert ir["score"] == "2 of 4 points" and ir["level"] == "Developing"
    fb = " ".join(c["feedback"] for c in ir["criteria"])
    assert "CRM-10814 is not unverified" in fb and "REB-33907 cannot be proven to be a different entity" in fb


def test_S4_levels_follow_thresholds(open_app):
    app = open_app()
    got = app.page.evaluate("()=>[[4,4],[3,4],[2,4],[1,4],[11,12],[10,12],[6,12],[5,12],[3,3],[2,3],[1,3]].map(x=>Aperion.rules.scoring.level(x[0],x[1]))")
    assert got == ["Proficient", "Developing", "Developing", "Needs Practice", "Proficient", "Developing", "Developing",
                   "Needs Practice", "Proficient", "Developing", "Needs Practice"]


def test_S5_scoring_explained_to_learner(flow):
    f = flow()
    to_validation(f)
    complete_validation(f)
    finish(f)
    f.page.click(".scoring-help summary")
    help_text = f.page.inner_text(".scoring-help")
    assert "no decision is counted twice" in help_text
    assert "Proficient at 85% or more" in help_text and "Developing at 50% or more" in help_text and "Needs Practice below 50%" in help_text
    assert "%" not in f.page.inner_text("#debrief-h"), "scores are shown as points, not percentages"


def test_S6_finished_case_is_locked_and_reviewable(flow):
    f = flow()
    to_validation(f)
    complete_validation(f)
    finish(f)
    f.app.nav("compare")
    assert "Case finished (attempt 1)." in f.page.inner_text(".locked-notice")
    assert f.page.is_disabled('select[data-group="CRM-10452"]') and f.page.is_disabled("#review-groups")
    f.app.nav("golden")
    assert f.page.locator("#golden-content input").first.is_disabled()
    f.app.nav("validation")
    assert f.page.is_disabled(f"#vr-{SA}")
    f.app.nav("work")
    assert f.page.is_disabled('#rows input[data-id="CRM-10452"]')
    f.page.select_option("#system", "ERP")
    assert f.page.is_disabled('#rows input[data-id="ERP-77831"]'), "still locked after the table re-renders"
    assert f.next_step()["label"] == "Next Step: View your debrief →"


def test_S7_retry_starts_new_attempt_and_keeps_history(flow):
    f = flow()
    to_validation(f)
    complete_validation(f, follow="deactivate")
    finish(f)
    f.page.click("#retry-case")
    assert f.app.title() == "Mission Briefing"
    assert f.page.is_disabled("#nav-debrief") and f.page.is_disabled("#nav-golden")
    to_validation(f)
    complete_validation(f)
    finish(f)
    assert f.page.inner_text("#debrief-h") == "Your result: 23 of 23 points"
    assert "attempt 1: 22 of 23 (Proficient)" in f.page.inner_text(".debrief-summary")


def test_S8_debrief_lists_decisions_and_history(flow):
    f = flow()
    to_validation(f)
    complete_validation(f)
    finish(f)
    rows = f.page.evaluate("()=>[...document.querySelectorAll('.decision-review tbody tr')].map(tr=>[tr.cells[0].innerText.split(' ')[0].split('\\n')[0], tr.cells[1].innerText, tr.cells[2].innerText])")
    assert rows[0] == ["CRM-10452", "Proposed with ERP-77831", "Merge with ERP-77831"]
    assert rows[2] == ["REB-33907", "Hold for verification", "Hold for verification"]
    hist = f.page.inner_text("#hist-h + ol")
    assert "Submitted for Governance Review: CRM-10452 + ERP-77831, revision 1" in hist
