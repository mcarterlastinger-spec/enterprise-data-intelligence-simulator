"""v0.4.0 Golden Record activity (Step 3, decision P2-2).

Learners choose, for each attribute, a value that exists in the group's own records and the
evidence that justifies it. Operating and billing addresses are separate decisions. Choices
survive navigation, saving creates revisions, and unchanged saves are refused.
"""
from flow_helpers import GOLDEN_A, KEY_DECISIONS, flow  # noqa: F401

KEY_A = "CRM-10452|ERP-77831"
KEY_B = "CRM-10489|ERP-77902"


def _options(f, key, attr):
    return f.page.evaluate(f"""()=>[...document.querySelectorAll('fieldset.golden-attr[data-key="{key}"][data-attr="{attr}"] .choice')].map(c=>[c.querySelector('.choice-value').innerText, c.querySelector('input').dataset.sources])""")


def test_G1_golden_record_unavailable_until_a_proposal_exists(flow):
    f = flow()
    assert f.page.is_disabled("#nav-golden")
    assert f.page.get_attribute("#nav-golden", "title") == "Submit an eligible merge proposal first"
    f.select_all_and_compare()
    f.decide(KEY_DECISIONS)
    f.check()
    assert f.page.is_disabled("#nav-golden")
    f.submit("A")
    assert not f.page.is_disabled("#nav-golden")


def test_G2_one_golden_record_per_current_proposal(flow):
    f = flow()
    f.to_golden_with_proposals()
    heads = f.page.evaluate("()=>[...document.querySelectorAll('.golden-group h3')].map(h=>h.innerText)")
    assert heads == ["Group A · CRM-10452 + ERP-77831 (proposal revision 1)", "Group B · CRM-10489 + ERP-77902 (proposal revision 1)"]
    assert f.page.evaluate("()=>document.querySelectorAll('fieldset.golden-attr').length") == 12


def test_G3_choices_come_only_from_the_groups_records(flow):
    f = flow()
    f.to_golden_with_proposals()
    assert _options(f, KEY_A, "operatingAddress") == [["100 Medical Parkway, Seattle, WA", "CRM-10452"], ["400 Billing Plaza, Seattle, WA", "ERP-77831"]]
    assert _options(f, KEY_A, "billingAddress") == _options(f, KEY_A, "operatingAddress"), "billing and operating are separate decisions over the same evidence"
    assert _options(f, KEY_A, "legalName") == [["Northbridge Health Inc.", "CRM-10452,ERP-77831"]]
    assert _options(f, KEY_B, "primaryContact") == [["office@nbmedical.example", "CRM-10489"], ["billing@nbmedical.example", "ERP-77902"]]
    text = f.page.inner_text(".golden-group")
    assert "REB-33907" not in text and "CRM-10814" not in text


def test_G4_every_attribute_needs_a_value_and_evidence(flow):
    f = flow()
    f.to_golden_with_proposals(("A",))
    f.choose(KEY_A, "legalName", "Northbridge Health Inc.", "erp-legal")
    f.save(KEY_A)
    assert f.status(KEY_A).startswith("Not saved: 5 attribute(s) still need a value and evidence.")
    assert f.page.evaluate("()=>document.activeElement.closest('fieldset').dataset.attr") == "taxId", "focus moves to the first incomplete attribute"
    # A value without a reason is still incomplete.
    f.page.locator(f'fieldset.golden-attr[data-key="{KEY_A}"][data-attr="taxId"] input').first.check()
    assert "5 of 6 attributes" in f.status(KEY_A)


def test_G5_save_creates_revisions_and_refuses_unchanged(flow):
    f = flow()
    f.to_golden_with_proposals(("A",))
    f.fill_golden(KEY_A, GOLDEN_A)
    assert f.status(KEY_A) == "All attributes complete. Not saved yet."
    f.save(KEY_A)
    assert f.status(KEY_A).startswith("Saved as revision 1")
    f.save(KEY_A)
    assert f.status(KEY_A) == "No changes since the last saved revision."
    f.choose(KEY_A, "primaryContact", "ap@northbridge.example", "billing-source")
    assert f.status(KEY_A) == "Changes since revision 1 are not saved."
    f.save(KEY_A)
    assert f.status(KEY_A).startswith("Saved as revision 2")
    summary = f.page.evaluate("()=>[...document.querySelectorAll('.golden-summary tbody tr')].map(tr=>[...tr.children].map(c=>c.innerText))")
    assert summary[5] == ["Primary business contact", "ap@northbridge.example", "ERP-77831",
                          "Finance record identifies this as the billing / remittance value"]


def test_G6_choices_survive_navigation(flow):
    f = flow()
    f.to_golden_with_proposals(("A",))
    f.choose(KEY_A, "operatingAddress", "100 Medical Parkway", "crm-operating")
    f.app.nav("work")
    f.app.nav("golden")
    fs = f'fieldset.golden-attr[data-key="{KEY_A}"][data-attr="operatingAddress"]'
    assert f.page.locator(f"{fs} input:checked").get_attribute("value") == "100 Medical Parkway, Seattle, WA"
    assert f.page.input_value(f"{fs} [data-reason]") == "crm-operating"


def test_G7_next_step_guides_golden_record(flow):
    f = flow()
    f.to_golden_with_proposals(("A",))
    assert f.next_step()["description"] == "Group A: 6 of 6 attributes still need a value and evidence."
    f.app.next()
    assert f.page.evaluate("()=>document.activeElement.closest('fieldset').dataset.attr") == "legalName"
    f.fill_golden(KEY_A, GOLDEN_A)
    assert f.next_step()["label"] == "Next Step: Go to Save for Group A"
    f.app.next()
    assert f.page.evaluate("()=>document.activeElement.dataset.saveGolden") == KEY_A
    f.save(KEY_A)
    ns = f.next_step()
    assert ns["label"] == "Next Step: Continue to Validation →" and ns["disabled"] is False
    f.app.next()
    assert f.app.title() == "Validation"


def test_G8_keyboard_choice_keeps_focus(flow):
    f = flow()
    f.to_golden_with_proposals(("A",))
    sel = f'fieldset.golden-attr[data-key="{KEY_A}"][data-attr="taxId"] [data-reason]'
    f.page.focus(sel)
    f.page.keyboard.press("ArrowDown")
    assert f.page.evaluate("()=>document.activeElement.hasAttribute('data-reason')")
    radio = f'fieldset.golden-attr[data-key="{KEY_A}"][data-attr="operatingAddress"] input'
    f.page.focus(radio)
    f.page.keyboard.press("Space")
    assert f.page.evaluate("()=>document.activeElement.type") == "radio"


def test_G9_superseded_proposal_drops_its_golden_record(flow):
    """A golden record belongs to a current proposal; changing the group removes it from the activity."""
    f = flow()
    f.to_golden_with_proposals()
    f.app.nav("compare")
    f.decide({"CRM-10489": "separate"})
    f.app.nav("golden")
    heads = f.page.evaluate("()=>[...document.querySelectorAll('.golden-group h3')].map(h=>h.innerText)")
    assert heads == ["Group A · CRM-10452 + ERP-77831 (proposal revision 1)"]
