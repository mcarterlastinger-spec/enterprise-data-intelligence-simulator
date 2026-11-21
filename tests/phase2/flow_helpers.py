"""Phase 2 helpers: drive the v0.4.0 learner workflow through the interface."""
import pytest

KEY_DECISIONS = {"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "hold",
                 "CRM-10489": "B", "ERP-77902": "B", "CRM-10814": "separate"}

GOLDEN_A = {  # value index chosen by visible text, reason id
    "legalName": ("Northbridge Health Inc.", "erp-legal"),
    "taxId": ("91-4826103", "agree"),
    "operatingAddress": ("100 Medical Parkway, Seattle, WA", "crm-operating"),
    "billingAddress": ("400 Billing Plaza, Seattle, WA", "billing-source"),
    "parent": ("Northbridge Holdings", "agree"),
    "primaryContact": ("operations@northbridge.example", "crm-operating"),
}


class Flow:
    def __init__(self, app):
        self.app = app
        self.page = app.page

    def next_step(self):
        return self.app.next_step()

    def select_all_and_compare(self):
        self.app.nav("work")
        self.app.click_button("Select all records")
        self.app.nav("compare")

    def decide(self, decisions):
        for rid, v in decisions.items():
            self.page.select_option(f'select[data-group="{rid}"]', v)

    def check(self):
        self.page.click("#review-groups")

    def results(self):
        return self.page.evaluate("""()=>[...document.querySelectorAll('#governance-output .groupresult')].map(s=>({
            heading:s.querySelector('strong').innerText.trim(), verdict:s.querySelector('.verdict').innerText.trim(),
            button:(s.querySelector('button')||{}).innerText||null,
            enabled:!!s.querySelector('button:not([disabled])')}))""")

    def submit(self, letter):
        self.page.click(f'[data-propose="{letter}"]')

    def history(self):
        return self.page.evaluate("()=>[...document.querySelectorAll('#audit .history li')].map(li=>li.innerText.replace(/ · submitted [^·]+·/,' ·'))")

    def to_golden_with_proposals(self, letters=("A", "B")):
        self.select_all_and_compare()
        self.decide(KEY_DECISIONS)
        self.check()
        for g in letters:
            self.submit(g)
        self.app.nav("golden")

    def choose(self, key, attr, value_text, reason):
        fs = f'fieldset.golden-attr[data-key="{key}"][data-attr="{attr}"]'
        self.page.locator(f"{fs} .choice").filter(has_text=value_text).locator("input").check()
        self.page.select_option(f"{fs} [data-reason]", reason)

    def fill_golden(self, key, choices):
        for attr, (value, reason) in choices.items():
            self.choose(key, attr, value, reason)

    def save(self, key):
        self.page.click(f'[data-save-golden="{key}"]')

    def status(self, key):
        return self.page.inner_text(f'#gs-{key.replace("|", "-")}')


@pytest.fixture
def flow(open_app):
    def _make(**kw):
        return Flow(open_app(**kw))
    return _make
