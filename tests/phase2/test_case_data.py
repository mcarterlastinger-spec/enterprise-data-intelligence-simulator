"""v0.4.0 case data, answer key, and identity rules (Step 1).

These tests verify the approved answer key against the actual dataset (decision P2-1:
"validate the actual fields and values before finalizing the answer key") and pin the
corrected rules for defects D1, D2, D3, D4, and D9.
"""
import pytest

KEY_A = ["CRM-10452", "ERP-77831"]
KEY_B = ["CRM-10489", "ERP-77902"]


def _eval(app, ids):
    return app.page.evaluate("""ids=>{const r=ids.map(id=>Aperion.data.records.find(x=>x.id===id));
        return Aperion.rules.identity.evaluateGroup(r)}""", ids)


def _synthetic(app, recs):
    return app.page.evaluate("recs=>Aperion.rules.identity.evaluateGroup(recs)", recs)


# ---- dataset and answer key ------------------------------------------------------------------

def test_K1_answer_key_matches_dataset(open_app):
    app = open_app()
    data = app.page.evaluate("()=>({records:Aperion.data.records, key:Aperion.data.answerKey})")
    recs = {r["id"]: r for r in data["records"]}
    key = data["key"]
    assert [g["records"] for g in key["groups"]] == [KEY_A, KEY_B]
    assert key["separate"] == ["CRM-10814"] and key["hold"] == ["REB-33907"]
    # Every record is covered exactly once.
    covered = sum((g["records"] for g in key["groups"]), []) + key["separate"] + key["hold"]
    assert sorted(covered) == sorted(recs)
    # The facts the key relies on are really in the data.
    assert recs["CRM-10452"]["tax"] == recs["ERP-77831"]["tax"] == "91-4826103"
    assert recs["CRM-10452"]["legal"] == recs["ERP-77831"]["legal"] == "Northbridge Health Inc."
    assert recs["CRM-10489"]["tax"] == recs["ERP-77902"]["tax"] == "91-7728041"
    assert recs["CRM-10489"]["legal"] == recs["ERP-77902"]["legal"] == "Northbridge Medical Group LLC"
    assert recs["CRM-10814"]["tax"] == "91-9346180" and recs["CRM-10814"]["parent"] == "Independent"
    assert recs["REB-33907"]["tax"] == "" and recs["REB-33907"]["legal"] == ""


def test_K2_golden_key_values_exist_in_group_records(open_app):
    app = open_app()
    d = app.page.evaluate("()=>({records:Aperion.data.records, attrs:Aperion.data.goldenAttributes, key:Aperion.data.goldenKey, reasons:Aperion.data.goldenReasons.map(r=>r.id)})")
    recs = {r["id"]: r for r in d["records"]}
    assert sorted(d["key"]) == ["CRM-10452|ERP-77831", "CRM-10489|ERP-77902"]
    for group, expected in d["key"].items():
        members = group.split("|")
        for a in d["attrs"]:
            e = expected[a["key"]]
            values = [recs[m][a["field"]] for m in members]
            assert e["value"] in values, f"{group} {a['key']}: {e['value']!r} not in {values}"
            assert e["reasons"] and set(e["reasons"]) <= set(d["reasons"])
            assert e["why"]


def test_K3_billing_and_operating_addresses_are_evidenced(open_app):
    """The golden key's billing/operating split must rest on evidence the learner can see."""
    app = open_app()
    recs = {r["id"]: r for r in app.page.evaluate("()=>Aperion.data.records")}
    assert "remittance address" in recs["ERP-77831"]["note"]
    assert "site visit" in recs["CRM-10452"]["note"]
    assert "billing contact" in recs["ERP-77902"]["note"]


def test_K4_notes_do_not_reveal_answers(open_app):
    """Decision P2-6: neutral investigative notes; v0.3.2's answer-revealing notes are gone."""
    app = open_app()
    notes = " ".join(app.page.evaluate("()=>Aperion.data.records.map(r=>r.note)")).lower()
    for phrase in ["same legal entity", "unrelated legal entity", "separate subsidiary", "similar name"]:
        assert phrase not in notes


# ---- identity rules (D1, D4) -----------------------------------------------------------------

@pytest.mark.parametrize("ids,status", [
    (KEY_A, "eligible"),
    (KEY_B, "eligible"),
    (["CRM-10452", "ERP-77831", "REB-33907"], "verification"),   # missing evidence, not a mismatch
    (["REB-33907", "CRM-10814"], "blocked"),                      # v0.3.2 D1: was submittable
    (["CRM-10452", "CRM-10814"], "blocked"),
    (["CRM-10452", "ERP-77831", "REB-33907", "CRM-10489", "ERP-77902"], "blocked"),
    (["CRM-10814"], "single"),                                    # v0.3.2 D4: was "eligible"
    (KEY_A + KEY_B, "blocked"),
])
def test_I1_identity_verdicts(open_app, ids, status):
    app = open_app()
    v = _eval(app, ids)
    assert v["status"] == status
    assert v["submittable"] is (status == "eligible")


def test_I2_similar_name_address_parent_never_establish_eligibility(open_app):
    """Approved requirement: similar names, addresses, and parents alone never make a group eligible."""
    app = open_app()
    base = {"name": "Acme Health", "legal": "", "tax": "", "address": "1 Main St, Seattle, WA", "parent": "Acme Holdings", "system": "CRM", "verified": "2026-01-01"}
    v = _synthetic(app, [dict(base, id="X-1"), dict(base, id="X-2", system="ERP")])
    assert v["status"] == "verification" and not v["submittable"]
    v = _synthetic(app, [dict(base, id="X-1", tax="11-1111111", legal="Acme Health Inc."),
                         dict(base, id="X-2", tax="22-2222222", legal="Acme Health Inc.")])
    assert v["status"] == "blocked", "matching names and addresses cannot outweigh different tax IDs"


def test_I3_missing_tax_is_insufficient_not_a_mismatch(open_app):
    app = open_app()
    v = _eval(app, ["CRM-10452", "REB-33907"])
    assert v["status"] == "verification"
    assert any("REB-33907 has no tax identifier or legal name" in r for r in v["reasons"])
    assert any("insufficient, not proof of a mismatch" in r for r in v["reasons"])


def test_I4_eligible_group_warns_about_address_roles(open_app):
    app = open_app()
    v = _eval(app, KEY_A)
    assert any("operating address" in w and "billing address" in w for w in v["warnings"])
    assert _eval(app, KEY_B)["warnings"] == []


# ---- evidence matrix (D2, D3, D9) ------------------------------------------------------------

def test_E1_matrix_reports_conflict_and_missing_together(open_app):
    app = open_app()
    app.nav("work")
    app.click_button("Select all records")
    app.nav("compare")
    rows = app.page.evaluate("""()=>[...document.querySelectorAll('.matrix tbody tr')].map(tr=>[
        tr.querySelector('th').firstChild.textContent, tr.querySelector('.role-tag').innerText, tr.querySelector('.state-label').innerText])""")
    assert rows == [
        ["Legal name", "IDENTITY EVIDENCE", "Conflict: 3 different values · 1 missing"],
        ["Tax identifier", "IDENTITY EVIDENCE", "Conflict: 3 different values · 1 missing"],
        ["Business address", "SUPPORTING EVIDENCE", "Conflict: 4 different values"],
        ["Parent organization", "SUPPORTING EVIDENCE", "Conflict: 2 different values"],
        ["Source system", "CONTEXT", "Context: expected to differ between systems"],
        ["Last verified", "CONTEXT", "Context: expected to differ between systems"]]


def test_E2_value_sets_show_which_records_agree(open_app):
    app = open_app()
    app.nav("work")
    app.click_button("Select all records")
    app.nav("compare")
    tax = app.page.evaluate("""()=>[...document.querySelectorAll('.matrix tbody tr')[1].querySelectorAll('td')].map(td=>[td.className, (td.querySelector('.valueset')||{}).innerText||''])""")
    assert tax == [["conflict", "Set 1"], ["conflict", "Set 1"], ["missing", ""], ["conflict", "Set 2"], ["conflict", "Set 2"], ["conflict", "Set 3"]]
    addr = app.page.evaluate("""()=>[...document.querySelectorAll('.matrix tbody tr')[2].querySelectorAll('.valueset')].map(s=>s.innerText)""")
    assert addr[0] == addr[2] == "Set 1", "'100 Medical Pkwy' and '100 Medical Parkway' are the same address"


def test_E3_consistent_pair_with_context_rows(open_app):
    app = open_app()
    app.nav("work")
    app.select_ids(KEY_B)
    app.nav("compare")
    states = app.page.evaluate("()=>[...document.querySelectorAll('.matrix .state-label')].map(s=>s.innerText)")
    assert states == ["Consistent"] * 4 + ["Context: expected to differ between systems"] * 2
    assert app.page.evaluate("()=>document.querySelectorAll('.matrix td.conflict').length") == 0


def test_E4_normalization_rules(open_app):
    app = open_app()
    got = app.page.evaluate("""()=>{const m=Aperion.rules.matching;return [
        m.normLegal('Northbridge Health Inc.'), m.normLegal('NORTHBRIDGE HEALTH, INCORPORATED'),
        m.normLegal('Northbridge Healthcare'), m.normLegal('Northbridge Health Partners LLC'),
        m.normTax('91-4826103'), m.normAddress('100 Medical Pkwy, Seattle, WA'), m.normAddress('100 Medical Parkway, Seattle, WA')]}""")
    assert got[0] == got[1] == "northbridgehealth"
    assert got[2] == "northbridgehealthcare", "v0.3.2 dropped the word 'healthcare' (D9)"
    assert got[3] != got[0]
    assert got[4] == "914826103"
    assert got[5] == got[6]


def test_E5_legal_name_variants_and_case_groups(open_app):
    """Decision P2-14: legal-name normalization accepts ordinary formatting variants, and the
    correct Group A and B records are eligible (not rejected by overly strict comparison)."""
    app = open_app()
    got = app.page.evaluate("""()=>{const m=Aperion.rules.matching, id=Aperion.rules.identity, R=Aperion.data.records;
      const v=['Northbridge Health Inc.','NORTHBRIDGE HEALTH, INC.','Northbridge Health Incorporated','northbridge health inc',
               'Northbridge Medical Group LLC','Northbridge Medical Group, L.L.C.','NORTHBRIDGE MEDICAL GROUP, LLC'].map(m.normLegal);
      const g=ids=>id.evaluateGroup(ids.map(x=>R.find(r=>r.id===x))).status;
      return {v, a:g(['CRM-10452','ERP-77831']), b:g(['CRM-10489','ERP-77902']),
              ab:g(['CRM-10452','CRM-10489']), hp:g(['CRM-10452','CRM-10814']), reb:g(['CRM-10452','REB-33907'])};}""")
    v = got["v"]
    assert v[0] == v[1] == v[2] == v[3] == "northbridgehealth"
    assert v[4] == v[5] == v[6] == "northbridgemedicalgroup"
    assert got["a"] == "eligible" and got["b"] == "eligible"
    assert got["ab"] == "blocked" and got["hp"] == "blocked"
    assert got["reb"] == "verification"
