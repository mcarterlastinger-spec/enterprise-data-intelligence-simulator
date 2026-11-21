"""Loading, initial state, visual identity, and avatars."""
import base64
import hashlib
import re

from conftest import ROOT, TARGET_FILES, VERSION_LABELS

def _image_bytes(target_file, src):
    if src.startswith("data:"):
        return base64.b64decode(src.split(",", 1)[1])
    return (target_file.parent / src).read_bytes()


def test_L1_loads_without_errors_from_file(open_app):
    app = open_app()
    assert app.console_errors == []


def test_L1b_loads_without_errors_over_http(open_app, http_root, target):
    rel = TARGET_FILES[target].relative_to(ROOT).as_posix()
    app = open_app(url=f"{http_root}/{rel}")
    assert app.title() == "Mission Briefing"
    assert app.console_errors == []


def test_L2_initial_state(open_app):
    app = open_app()
    p = app.page
    assert p.title() == "Aperion | Enterprise Data Intelligence Simulator"
    assert app.title() == "Mission Briefing"
    assert app.visible("#page-brief") and not app.visible("#page-work") and not app.visible("#page-compare")
    assert p.get_attribute("#nav-brief", "class") == "nav active"
    assert app.text(".pill") == VERSION_LABELS[app.target][0]
    assert app.text(".eyebrow") == "CASE EDI-001 · NORTHBRIDGE HEALTH"
    assert app.next_step() == {
        "heading": "Ready to investigate?",
        "description": "You can read the transcript or listen to Maya. Audio completion is not required.",
        "label": "Next Step: Explore Customer Records →",
        "disabled": False,
    }
    assert "No data is transmitted or stored on a server." in app.text(".foot")


def test_L3_visual_identity_tokens(open_app):
    app = open_app()
    tokens = app.page.evaluate("""()=>{const s=getComputedStyle(document.documentElement);
        return ['--navy','--blue','--steel','--ivory'].map(v=>s.getPropertyValue(v).trim().toLowerCase())}""")
    assert tokens == ["#101d35", "#2457b8", "#71839d", "#f8f6f0"]  # Midnight, Cobalt, Steel Gray, Warm Ivory
    colors = app.page.evaluate("""()=>({body:getComputedStyle(document.body).backgroundColor,
        aside:getComputedStyle(document.querySelector('aside')).backgroundColor,
        primary:getComputedStyle(document.querySelector('#next-step-button')).backgroundColor})""")
    assert colors == {"body": "rgb(248, 246, 240)", "aside": "rgb(16, 29, 53)", "primary": "rgb(36, 87, 184)"}


def test_L4_avatars_present_and_unchanged(open_app, target):
    app = open_app()
    imgs = app.page.evaluate("()=>[...document.images].map(i=>({alt:i.alt,src:i.getAttribute('src'),w:i.naturalWidth,h:i.naturalHeight}))")
    assert [i["alt"] for i in imgs] == [
        "Maya Chen avatar portrait", "Maya Chen avatar portrait", "Maya Chen avatar portrait",
        "Priya Shah avatar portrait", "Daniel Brooks avatar portrait", "Marcus Reed avatar portrait"]
    assert all(i["w"] == 256 and i["h"] == 256 for i in imgs), "every portrait must load at 256x256"
    # Compare image bytes with the untouched baseline, by position.
    base_html = TARGET_FILES["baseline"].read_text()
    base_srcs = re.findall(r'<img[^>]*src="([^"]+)"', base_html)
    for img, base_src in zip(imgs, base_srcs):
        got = hashlib.sha256(_image_bytes(TARGET_FILES[target], img["src"])).hexdigest()
        want = hashlib.sha256(_image_bytes(TARGET_FILES["baseline"], base_src)).hexdigest()
        assert got == want, f"{img['alt']} image bytes differ from v0.3.2"


def test_V1_version_labels(open_app, target):
    """Approved difference (decision B3): the release candidate shows v0.3.3; the baseline keeps v0.3.2."""
    app = open_app()
    pill, foot = VERSION_LABELS[target]
    assert app.text(".pill") == pill
    assert foot in app.text(".foot")
    body = app.page.inner_text("body")
    other = "0.3.2" if target != "baseline" else "0.3.3"
    assert other not in body, f"unexpected version text {other} on {target}"
