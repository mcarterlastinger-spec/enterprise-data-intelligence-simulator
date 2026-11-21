"""Side-by-side equivalence with the untouched v0.3.2 baseline.

Each test drives the baseline and the target into the same state in the same browser,
then compares what a learner (or assistive technology) would get:
  - DOM structure, IDs, classes, ARIA attributes, and visible text
  - the accessibility tree (roles, names, states) as screen readers receive it
  - full-page screenshots at desktop, tablet, and phone widths (<= 0.1% pixel difference)
When the target IS the baseline, these tests also confirm the comparison is deterministic.
The approved version-label change (V0.3.2 -> V0.3.3) is masked in both pages before comparing;
test_V1 in test_load_and_identity.py checks the labels themselves.
"""
import io
import json
import pathlib

import numpy as np
import pytest
from PIL import Image, ImageChops

from conftest import FREEZE_CSS, NORMALIZE_VERSION, SPEECH_MOCK, TARGET_FILES

OUT = pathlib.Path(__file__).resolve().parent.parent / "output"
CORRECT_GROUPING = {"CRM-10452": "A", "ERP-77831": "A", "REB-33907": "A",
                    "CRM-10489": "B", "ERP-77902": "B", "CRM-10814": "C"}
STATES = ["brief", "work", "work-details", "work-filtered", "work-selected", "compare-empty",
          "compare-all", "compare-validated", "compare-proposed"]
WIDTHS = [1366, 768, 375]
MAX_DIFF = 0.001  # 0.1% of pixels (approved tolerance, decision 4)


def drive(page, state):
    """Puts a freshly loaded page into a named learner state using normal UI actions."""
    nav = lambda k: page.click({"work": "#nav-work", "compare": "#nav-compare", "brief": "#nav-brief"}[k])
    btn = lambda n: page.get_by_role("button", name=n, exact=True).click()
    if state == "brief":
        settle(page)
        page.mouse.move(0, 0)
        return
    nav("work")
    if state == "work-details":
        page.click('[data-open="REB-33907"]')
    elif state == "work-filtered":
        page.fill("#search", "medical"); page.select_option("#system", "ERP")
    elif state == "work-selected":
        page.check('#rows input[data-id="CRM-10489"]'); page.check('#rows input[data-id="ERP-77902"]')
    elif state == "compare-empty":
        nav("compare")
    elif state.startswith("compare-"):
        btn("Select all records"); nav("compare")
        if state in ("compare-validated", "compare-proposed"):
            for rid, g in CORRECT_GROUPING.items():
                page.select_option(f'select[data-group="{rid}"]', g)
            page.click("#review-groups")
        if state == "compare-proposed":
            page.click('[data-propose="B"]')
    settle(page)
    page.evaluate("()=>{document.activeElement&&document.activeElement.blur()}")
    page.mouse.move(0, 0)


def settle(page):
    """Waits until any smooth scrolling (e.g. scrollIntoView in record details) has finished,
    then returns to the top and waits two frames. Without this, the sticky Next Step bar can be
    captured mid-scroll and screenshots of the same page differ (seen once in Checkpoint A r1)."""
    page.evaluate("""()=>new Promise(res=>{let last=-1,same=0;const tick=()=>{const y=scrollY;
        same=(y===last)?same+1:0;last=y;if(same>=5)return res();requestAnimationFrame(tick)};tick()})""")
    page.evaluate("()=>window.scrollTo({top:0,left:0,behavior:'instant'})")
    page.wait_for_function("()=>scrollY===0")
    # Images loaded from files decode asynchronously; wait so portraits are fully rasterized
    # (otherwise a few edge pixels of the 55 px stakeholder portraits can differ run to run).
    page.evaluate("()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>null)))")
    page.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")


def open_state(browser, file, state, width=1366):
    ctx = browser.new_context(viewport={"width": width, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(SPEECH_MOCK)
    page = ctx.new_page()
    page.goto(file.as_uri())
    page.add_style_tag(content=FREEZE_CSS)
    page.wait_for_timeout(350)
    drive(page, state)
    page.evaluate(NORMALIZE_VERSION)  # mask the approved version-label change (checked by test_V1)
    leftover = page.evaluate("()=>/[Vv]0\\.3\\.[23]/.test(document.body.innerText)")
    assert not leftover, "version label was not masked; comparison would be invalid"
    page.wait_for_timeout(50)
    return ctx, page


DOM_SNAPSHOT = """()=>{
  const skip=new Set(['SCRIPT','STYLE','LINK','META','TITLE','HEAD']);
  // src is ignored because images moved to files (bytes are checked by test_L4).
  // v0.3.2 onclick="fn('arg')" and v0.3.3 data-action="fn:arg" are normalized to the same
  // "action=fn:arg" so each button must still trigger exactly the same action.
  const action=a=>{if(a.name==='data-action')return 'action='+a.value;
    const v=a.value, open=v.indexOf('('), name=v.slice(0,open), inner=v.slice(open+1,v.lastIndexOf(')')).split("'").join('');
    return 'action='+(inner?name+':'+inner:name)};
  const out=[];
  (function walk(el,depth){
    if(skip.has(el.tagName))return;
    const attrs=[...el.attributes].filter(a=>a.name!=='src').map(a=>(a.name==='onclick'||a.name==='data-action')?action(a):a.name+'='+a.value).sort();
    const own=[...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('').replace(/\\s+/g,' ').trim();
    const extra=(el.tagName==='INPUT'||el.tagName==='SELECT')?' value='+el.value+(el.type==='checkbox'?' checked='+el.checked:''):'';
    out.push(' '.repeat(depth)+el.tagName+' '+attrs.join(' ')+(own?' "'+own+'"':'')+extra);
    for(const c of el.children)walk(c,depth+1);
  })(document.body,0);
  return out;
}"""


def ax_tree(page):
    cdp = page.context.new_cdp_session(page)
    nodes = cdp.send("Accessibility.getFullAXTree")["nodes"]
    out = []
    for n in nodes:
        if n.get("ignored"):
            continue
        role = n.get("role", {}).get("value", "")
        name = n.get("name", {}).get("value", "")
        if role in ("generic", "none", "InlineTextBox", "LineBreak") and not name:
            continue
        props = {p["name"]: p.get("value", {}).get("value") for p in n.get("properties", [])
                 if p["name"] in ("checked", "disabled", "pressed", "expanded", "focusable", "level", "live", "hidden")}
        out.append(f"{role}|{name}|{json.dumps(props, sort_keys=True)}")
    return out


@pytest.mark.parametrize("state", STATES)
def test_E1_dom_matches_baseline(browser, target, state):
    if not TARGET_FILES[target].exists():
        pytest.skip(f"target {target} not built yet")
    snaps = []
    for f in (TARGET_FILES["baseline"], TARGET_FILES[target]):
        ctx, page = open_state(browser, f, state)
        snaps.append(page.evaluate(DOM_SNAPSHOT))
        ctx.close()
    assert snaps[1] == snaps[0]


@pytest.mark.parametrize("state", STATES)
def test_E2_accessibility_tree_matches_baseline(browser, target, state):
    if not TARGET_FILES[target].exists():
        pytest.skip(f"target {target} not built yet")
    trees = []
    for f in (TARGET_FILES["baseline"], TARGET_FILES[target]):
        ctx, page = open_state(browser, f, state)
        trees.append(ax_tree(page))
        ctx.close()
    assert len(trees[0]) > 50, "accessibility tree unexpectedly small"
    assert trees[1] == trees[0]


@pytest.mark.parametrize("width", WIDTHS)
@pytest.mark.parametrize("state", STATES)
def test_E3_screenshot_matches_baseline(browser, target, state, width):
    if not TARGET_FILES[target].exists():
        pytest.skip(f"target {target} not built yet")
    shots = []
    for f in (TARGET_FILES["baseline"], TARGET_FILES[target]):
        ctx, page = open_state(browser, f, state, width)
        shots.append(Image.open(io.BytesIO(page.screenshot(full_page=True))).convert("RGB"))
        ctx.close()
    base, got = shots
    assert got.size == base.size, f"page size changed: {base.size} -> {got.size}"
    diff = ImageChops.difference(base, got)
    changed = int(np.asarray(diff).any(axis=2).sum())
    ratio = changed / (base.size[0] * base.size[1])
    if changed:
        OUT.mkdir(parents=True, exist_ok=True)
        stem = f"{target}-{state}-{width}"
        base.save(OUT / f"{stem}-baseline.png"); got.save(OUT / f"{stem}-target.png")
        diff.point(lambda v: 255 if v else 0).save(OUT / f"{stem}-diff.png")
    assert ratio <= MAX_DIFF, f"{changed} pixels differ ({ratio:.4%}); see tests/output/{target}-{state}-{width}-*.png"
