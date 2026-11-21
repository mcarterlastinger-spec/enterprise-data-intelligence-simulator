"""Shared test setup for the Aperion characterization suite.

Every browser test runs once per *target*:
  baseline       -> baseline/v0.3.2/index.html            (the untouched original)
  rc1            -> baseline/v0.3.3-rc1/site/index.html  (frozen Phase 2 starting point)
  rc1-standalone -> baseline/v0.3.3-rc1/aperion-v0.3.3-standalone.html
  site           -> site/index.html                       (v0.4.0, under development)
  standalone -> dist/aperion-standalone.html (added once the standalone build exists)

Phase 1 tests (tests/phase1) use APERION_TARGETS (default baseline,rc1,rc1-standalone).
Phase 2 tests (tests/phase2) use APERION_P2_TARGETS (default site,standalone).
Tests interact through the user interface (clicks, keys, visible text) rather than
internal function names, so they keep working while the code is restructured.
"""
import functools
import http.server
import os
import pathlib
import shutil
import socketserver
import threading

import pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET_FILES = {
    "baseline": ROOT / "baseline" / "v0.3.2" / "index.html",
    "rc1": ROOT / "baseline" / "v0.3.3-rc1" / "site" / "index.html",
    "rc1-standalone": ROOT / "baseline" / "v0.3.3-rc1" / "aperion-v0.3.3-standalone.html",
    "site": ROOT / "site" / "index.html",
    "standalone": ROOT / "dist" / "aperion-v0.4.0-standalone.html",
}

# The only approved visible difference between v0.3.2 and the v0.3.3 release candidate
# (decision B3, 2026-11-07): the two version labels. test_V1 checks them explicitly; the
# side-by-side comparisons mask them with NORMALIZE_VERSION so everything else must still match.
VERSION_LABELS = {
    "baseline": ("FUNCTIONAL PROTOTYPE · V0.3.2", "Prototype v0.3.2"),
    "rc1": ("FUNCTIONAL PROTOTYPE · V0.3.3", "Prototype v0.3.3"),
    "rc1-standalone": ("FUNCTIONAL PROTOTYPE · V0.3.3", "Prototype v0.3.3"),
    "site": ("FUNCTIONAL PROTOTYPE · V0.4.0", "Prototype v0.4.0"),
    "standalone": ("FUNCTIONAL PROTOTYPE · V0.4.0", "Prototype v0.4.0"),
}
NORMALIZE_VERSION = r"""()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
  while((n=w.nextNode())){const t=n.textContent.replace(/V0\.(3\.[23]|4\.\d)\b/g,'V0.x.x').replace(/v0\.(3\.[23]|4\.\d)\b/g,'v0.x.x');
  if(t!==n.textContent)n.textContent=t}}"""
SPEECH_MOCK = (pathlib.Path(__file__).parent / "phase1" / "browser" / "speech_mock.js").read_text()
AXE_PATH = ROOT / "vendor" / "axe.min.js"

# Removes motion so screenshots are deterministic. Applied identically to every target.
FREEZE_CSS = "*,*::before,*::after{transition:none!important;animation:none!important;caret-color:transparent!important;scroll-behavior:auto!important}"


def _targets(phase=1):
    """Phase 1 suite: v0.3.2 baseline vs the frozen v0.3.3-rc1 (modular and standalone).
    Phase 2 suite: the v0.4.0 development build (modular and standalone)."""
    if phase == 2:
        raw = os.environ.get("APERION_P2_TARGETS", "site,standalone")
    else:
        raw = os.environ.get("APERION_TARGETS", "baseline,rc1,rc1-standalone")
    names = [t.strip() for t in raw.split(",") if t.strip()]
    for n in names:
        if n not in TARGET_FILES:
            raise ValueError(f"Unknown target {n!r}; choose from {sorted(TARGET_FILES)}")
    return names


def pytest_generate_tests(metafunc):
    if "target" in metafunc.fixturenames:
        phase = 2 if "phase2" in str(metafunc.definition.fspath) else 1
        metafunc.parametrize("target", _targets(phase), scope="session")


def pytest_configure(config):
    config.addinivalue_line("markers", "known_defect(id): records a known v0.3.2 defect that is NOT approved behavior")
    config.addinivalue_line("markers", "needs_axe: requires vendor/axe.min.js (installed in CI)")


@pytest.fixture(scope="session")
def browser():
    chrome = os.environ.get("CHROME_PATH") or ("/usr/bin/google-chrome" if shutil.which("google-chrome") else None)
    with sync_playwright() as p:
        kwargs = {"args": ["--no-sandbox", "--font-render-hinting=none", "--force-color-profile=srgb"]}
        if chrome:
            kwargs["executable_path"] = chrome
        b = p.chromium.launch(**kwargs)
        yield b
        b.close()


@pytest.fixture(scope="session")
def http_root():
    """Serves the repository over http://127.0.0.1 to mirror GitHub Pages."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = functools.partial(Quiet, directory=str(ROOT))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
        httpd.shutdown()


class App:
    """A simulator page plus helpers that act the way a learner would."""

    def __init__(self, page, target):
        self.page = page
        self.target = target
        self.console_errors = []
        page.on("console", lambda m: m.type == "error" and self.console_errors.append(m.text))
        page.on("pageerror", lambda e: self.console_errors.append(str(e)))

    # ---- reading -------------------------------------------------------------
    def text(self, sel):
        return self.page.inner_text(sel).strip()

    def visible(self, sel):
        return self.page.evaluate(
            "s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return r.width>0&&r.height>0}", sel)

    def title(self):
        return self.text("#page-title")

    def table_rows(self):
        return self.page.evaluate(
            "()=>[...document.querySelectorAll('#rows tr')].map(tr=>[...tr.cells].map(td=>td.innerText.trim()))")

    def results(self):
        return self.text("#results")

    def next_step(self):
        return {
            "heading": self.text("#next-step-heading"),
            "description": self.text("#next-step-description"),
            "label": self.text("#next-step-button"),
            "disabled": self.page.is_disabled("#next-step-button"),
        }

    def matrix(self):
        return self.page.evaluate("""()=>{const t=document.querySelector('#compare-content .matrix');if(!t)return null;
          return {columns:[...t.querySelectorAll('thead th')].slice(1).map(th=>th.innerText.trim().replace(/\\s+/g,' ')),
            rows:[...t.querySelectorAll('tbody tr')].map(tr=>{const th=tr.querySelector('th');
              return {label:th.firstChild.textContent.trim(),state:th.querySelector('div').innerText.trim(),
                cells:[...tr.querySelectorAll('td')].map(td=>({text:td.innerText.trim(),cls:td.className}))}})}}""")

    def governance(self):
        return self.page.evaluate("""()=>[...document.querySelectorAll('#governance-output .groupresult')].map(s=>({
            heading:s.querySelector('strong').innerText.trim(),
            verdict:s.querySelectorAll('p')[0].innerText.trim(),
            records:s.querySelectorAll('p')[1].innerText.trim(),
            can_submit:!!s.querySelector('[data-propose]')}))""")

    def focused(self):
        return self.page.evaluate("()=>{const e=document.activeElement;return {tag:e.tagName,id:e.id||null,data:e.dataset?Object.assign({},e.dataset):{},text:(e.innerText||e.value||'').trim().slice(0,60)}}")

    # ---- acting --------------------------------------------------------------
    def nav(self, page_key):
        self.page.click({"work": "#nav-work", "compare": "#nav-compare", "brief": "#nav-brief", "golden": "#nav-golden", "validation": "#nav-validation", "debrief": "#nav-debrief"}[page_key])

    def next(self):
        self.page.click("#next-step-button")

    def search(self, q):
        self.page.fill("#search", q)

    def select_ids(self, ids):
        for i in ids:
            self.page.check(f'#rows input[data-id="{i}"]')

    def click_button(self, text):
        self.page.get_by_role("button", name=text, exact=True).click()

    def assign(self, mapping):
        for rid, g in mapping.items():
            self.page.select_option(f'select[data-group="{rid}"]', g)

    def validate(self):
        self.page.click("#review-groups")

    def speech_log(self):
        return self.page.evaluate("()=>window.__speech?window.__speech.log.slice():null")

    def rule(self, name):
        """Returns a JS expression for an internal rule function, independent of file layout."""
        return {
            "norm": "(window.Aperion&&Aperion.rules&&Aperion.rules.matching&&Aperion.rules.matching.norm)||window.norm",
        }[name]


@pytest.fixture
def open_app(browser, target):
    """open_app(width=1366, speech='mock'|'mock-novoices'|'native', url=None) -> App"""
    pages = []

    def _open(width=1366, height=900, speech="mock", url=None, freeze=True):
        if url is None and not TARGET_FILES[target].exists():
            pytest.skip(f"target {target} not built yet")
        ctx = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
        if speech == "mock":
            ctx.add_init_script(SPEECH_MOCK)
        elif speech == "mock-novoices":
            ctx.add_init_script("window.__speechConfig={voices:[]};" + SPEECH_MOCK)
        # Browsers request /favicon.ico over http; v0.3.2 has none. Answer it so it is not logged as an error.
        ctx.route("**/favicon.ico", lambda r: r.fulfill(status=204, body=""))
        page = ctx.new_page()
        app = App(page, target)
        page.goto(url or TARGET_FILES[target].as_uri())
        if freeze:
            page.add_style_tag(content=FREEZE_CSS)
        page.wait_for_timeout(350)  # v0.3.2 populates voices after a 200 ms timer
        pages.append(ctx)
        return app

    yield _open
    for c in pages:
        c.close()
