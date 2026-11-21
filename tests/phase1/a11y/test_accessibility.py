"""Accessibility checks.

Phase 1 rule: the target must have NO NEW accessibility issues compared with v0.3.2,
and must not silently change existing ones (fixes belong to Phase 2).

  - test_X1: built-in checks that run anywhere (names, labels, alt text, duplicate IDs,
             text contrast). No extra software needed.
  - test_X2: axe-core scan. Needs vendor/axe.min.js, which GitHub Actions installs.
             Skipped locally when the file is absent.
  - test_D12: records the known non-text contrast failures (KNOWN DEFECT D12).
Automated checks find only part of real accessibility problems; manual screen-reader
testing is still required (REGRESSION-CHECKLIST.md).
"""
import pytest

from conftest import AXE_PATH, TARGET_FILES
from browser.test_equivalence import STATES, open_state

LITE_AUDIT = """()=>{
  const issues=[];
  const visible=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'};
  const desc=e=>e.tagName+(e.id?'#'+e.id:'')+(e.dataset&&e.dataset.id?'[data-id='+e.dataset.id+']':'')+(e.dataset&&e.dataset.group?'[data-group='+e.dataset.group+']':'');
  // 1. Controls need an accessible name
  document.querySelectorAll('button,input,select,textarea,a[href]').forEach(e=>{
    if(!visible(e))return;
    const name=(e.getAttribute('aria-label')||e.innerText||'').trim()||(e.id&&document.querySelector('label[for="'+e.id+'"]')?'label':'')||(e.closest('label')?'label':'');
    if(!name)issues.push('no-name:'+desc(e));
  });
  // 2. Images need alt text
  document.querySelectorAll('img').forEach(e=>{if(!e.hasAttribute('alt'))issues.push('no-alt:'+desc(e))});
  // 3. Duplicate IDs
  const seen={};document.querySelectorAll('[id]').forEach(e=>{seen[e.id]=(seen[e.id]||0)+1});
  Object.entries(seen).filter(([k,v])=>v>1).forEach(([k])=>issues.push('dup-id:'+k));
  // 4. Text contrast (WCAG 1.4.3) for visible elements with their own text
  const parse=c=>{const m=c.match(/[\\d.]+/g);return m?m.map(Number):[0,0,0,0]};
  const lum=([r,g,b])=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(r)+.7152*f(g)+.0722*f(b)};
  const bgOf=e=>{for(let n=e;n;n=n.parentElement){const c=parse(getComputedStyle(n).backgroundColor);if(c.length<4||c[3]>0)return c.slice(0,3)}return [255,255,255]};
  document.querySelectorAll('body *').forEach(e=>{
    if(!visible(e)||e.disabled||e.closest(':disabled'))return;
    const own=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());if(!own)return;
    const cs=getComputedStyle(e);const fg=parse(cs.color).slice(0,3),bg=bgOf(e);
    const a=lum(fg),b=lum(bg);const ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
    const px=parseFloat(cs.fontSize),bold=parseInt(cs.fontWeight)>=700;const large=px>=24||(bold&&px>=18.66);
    if(ratio<(large?3:4.5))issues.push('contrast:'+desc(e)+':'+ratio.toFixed(2));
  });
  return issues;
}"""


@pytest.mark.parametrize("state", STATES)
def test_X1_builtin_accessibility_audit_matches_baseline(browser, target, state):
    if not TARGET_FILES[target].exists():
        pytest.skip(f"target {target} not built yet")
    results = []
    for f in (TARGET_FILES["baseline"], TARGET_FILES[target]):
        ctx, page = open_state(browser, f, state)
        results.append(page.evaluate(LITE_AUDIT))
        ctx.close()
    base, got = results
    new = sorted(set(got) - set(base))
    gone = sorted(set(base) - set(got))
    assert not new, f"new accessibility issues: {new}"
    assert not gone, f"existing issues changed without approval: {gone}"


@pytest.mark.needs_axe
@pytest.mark.parametrize("state", STATES)
def test_X2_axe_no_new_violations(browser, target, state):
    if not AXE_PATH.exists():
        pytest.skip("axe-core not installed locally (vendor/axe.min.js); this test runs in GitHub Actions")
    if not TARGET_FILES[target].exists():
        pytest.skip(f"target {target} not built yet")
    axe = AXE_PATH.read_text()
    results = []
    for f in (TARGET_FILES["baseline"], TARGET_FILES[target]):
        ctx, page = open_state(browser, f, state)
        page.add_script_tag(content=axe)
        res = page.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});
            return r.violations.map(v=>v.id+':'+v.impact+':'+v.nodes.map(n=>n.target.join(' ')).sort().join(','))}""")
        results.append(sorted(res))
        ctx.close()
    base, got = results
    assert sorted(set(got) - set(base)) == [], "new axe violations"
    assert sorted(set(base) - set(got)) == [], "axe results changed without approval"


@pytest.mark.known_defect("D12")
def test_D12_contrast_baseline(open_app):
    """KNOWN DEFECT D12 — NOT APPROVED BEHAVIOR (WCAG 1.4.11): focus outline and control borders are below 3:1."""
    app = open_app()
    app.nav("work")
    styles = app.page.evaluate("""()=>{const s=e=>getComputedStyle(document.querySelector(e));
        const i=document.querySelector('#search');i.focus();
        return {search_border:s('#search').borderTopColor, secondary_border:s('button.secondary').borderTopColor}}""")
    assert styles == {"search_border": "rgb(169, 182, 200)", "secondary_border": "rgb(170, 183, 201)"}
    app.page.keyboard.press("Tab")  # keyboard focus so :focus-visible applies
    outline = app.page.evaluate("()=>{const c=getComputedStyle(document.activeElement);return [c.outlineStyle,c.outlineWidth,c.outlineColor]}")
    assert outline == ["solid", "3px", "rgb(241, 167, 60)"]  # #F1A73C: 2.03:1 on white
