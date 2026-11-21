"""Checks specific to the restructured application (decision 1: ordinary scripts, one namespace).

These run only against the restructured targets; the v0.3.2 baseline has no modules.
"""
import pathlib
import re

import pytest

from conftest import ROOT, SPEECH_MOCK, TARGET_FILES

MODULE_ORDER = ["namespace", "util", "data/records", "data/attributes", "state", "rules/matching",
                "rules/governance", "audio", "navigation", "views/records", "views/compare", "bindings", "main"]


def _skip_baseline(target):
    if target == "baseline":
        pytest.skip("structure checks apply to the restructured application only")


def test_M1_all_modules_load_in_documented_order(open_app, target):
    _skip_baseline(target)
    app = open_app()
    assert app.page.evaluate("()=>Aperion.loadedModules()") == MODULE_ORDER


def test_M2_only_one_application_global(browser, target, tmp_path):
    """The restructured app adds exactly one global (Aperion); v0.3.2 added many."""
    _skip_baseline(target)
    ctx = browser.new_context()
    ctx.add_init_script(SPEECH_MOCK)
    blank = ctx.new_page()
    empty = tmp_path / "empty.html"
    empty.write_text("<!doctype html><title>empty</title>")
    blank.goto(empty.as_uri())  # same file:// origin type as the app, so the same built-in globals
    builtin = set(blank.evaluate("()=>Object.getOwnPropertyNames(window)"))
    page = ctx.new_page()
    page.goto(TARGET_FILES[target].as_uri())
    page.wait_for_timeout(350)
    added = sorted(set(page.evaluate("()=>Object.getOwnPropertyNames(window)")) - builtin)
    ctx.close()
    assert added == ["Aperion"]


def test_M3_data_identical_to_baseline(browser, target):
    _skip_baseline(target)
    ctx = browser.new_context()
    ctx.add_init_script(SPEECH_MOCK)
    p = ctx.new_page()
    p.goto(TARGET_FILES["baseline"].as_uri())
    base = p.evaluate("()=>JSON.stringify({records, attrs})")  # v0.3.2 script-level constants
    p.goto(TARGET_FILES[target].as_uri())
    got = p.evaluate("()=>JSON.stringify({records:Aperion.data.records, attrs:Aperion.data.attrs})")
    ctx.close()
    assert got == base


def test_M4_wrong_script_order_fails_loudly(browser, target, tmp_path):
    """If index.html lists scripts out of order, startup stops with a clear console error."""
    _skip_baseline(target)
    if target not in ("site", "rc1"):
        pytest.skip("load order is checked on the multi-file site")
    site_dir = TARGET_FILES[target].parent
    html = (site_dir / "index.html").read_text()
    js_dir = site_dir.as_uri()
    html = html.replace('<script src="js/util.js"></script>\n', '')
    html = html.replace('<script src="js/main.js"></script>',
                        '<script src="js/main.js"></script>\n<script src="js/util.js"></script>')
    html = re.sub(r'(src|href)="(js|css|assets)/', lambda m: f'{m.group(1)}="{js_dir}/{m.group(2)}/', html)
    page_file = tmp_path / "wrong-order.html"
    page_file.write_text(html)
    ctx = browser.new_context()
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(page_file.as_uri())
    page.wait_for_timeout(200)
    ctx.close()
    assert any('needs "util", which has not loaded yet' in e for e in errors), errors


def test_M5_no_inline_handlers(target):
    _skip_baseline(target)
    if not TARGET_FILES[target].exists():
        pytest.skip(f"target {target} not built yet")
    html = TARGET_FILES[target].read_text()
    markup = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S)  # ignore code comments in inlined scripts
    assert not re.search(r"<[^>]+\son\w+=", markup), "inline event-handler attributes remain"
    if target in ("site", "rc1"):
        assert "<style>" not in html
        assert not re.search(r"<script>(?!\s*</script>)", html), "no inline application script"


def test_M6_standalone_is_self_contained(browser, target):
    """The standalone file must work with every other request blocked (no files, no network)."""
    if target not in ("standalone", "rc1-standalone"):
        pytest.skip("applies to the standalone build only")
    f = TARGET_FILES[target]
    if not f.exists():
        pytest.skip("standalone not built yet")
    html = f.read_text()
    assert not re.search(r'(?:src|href)="(?!data:|#|https?:)[^"]+"', html), "local file references remain"
    assert not re.search(r'(?:src|href)="https?:', html), "network references present"
    ctx = browser.new_context()
    ctx.add_init_script(SPEECH_MOCK)
    requests = []

    def guard(route):
        requests.append(route.request.url)
        if route.request.url == f.as_uri():
            route.continue_()
        else:
            route.abort()
    ctx.route("**/*", guard)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f.as_uri())
    page.wait_for_timeout(350)
    loaded = page.evaluate("()=>[...document.images].every(i=>i.complete&&i.naturalWidth===256)")
    modules = page.evaluate("()=>Aperion.loadedModules().length")
    ctx.close()
    assert requests == [f.as_uri()], f"unexpected requests: {requests}"
    assert errors == [] and loaded and modules == len(MODULE_ORDER)


def test_M7_standalone_matches_current_sources(target):
    """dist/ must be rebuilt whenever site/ changes; a stale standalone file fails here."""
    if target != "standalone":
        pytest.skip("applies to the standalone build only")
    import subprocess
    import sys
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "build_standalone.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
