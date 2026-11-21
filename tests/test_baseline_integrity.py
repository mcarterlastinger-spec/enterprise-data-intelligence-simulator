"""Static check (no browser): the preserved v0.3.2 baseline must never change."""
import hashlib

from conftest import ROOT

BASELINE = ROOT / "baseline" / "v0.3.2"


def test_S1_baseline_checksums_unchanged():
    lines = (BASELINE / "CHECKSUMS.txt").read_text().split("\n")
    expected = dict(reversed(l.split("  ", 1)) for l in lines if l.strip())
    assert set(expected) == {"index.html", "Enterprise_Data_Intelligence_Prototype_v0.3.2.zip"}
    for name, digest in expected.items():
        got = hashlib.sha256((BASELINE / name).read_bytes()).hexdigest()
        assert got == digest, f"baseline file {name} has changed (expected {digest}, got {got})"
    # Guard against the checksum file itself being edited to match a changed baseline.
    assert expected["index.html"] == "9d7698340682c7df823345a19a524a24c7330ca3467b7e03c554a6124c7bb530"


def test_S2_v033_rc1_baseline_unchanged():
    """The accepted Phase 2 starting point (v0.3.3-rc1) is frozen in baseline/v0.3.3-rc1/."""
    rc1 = ROOT / "baseline" / "v0.3.3-rc1"
    lines = [l for l in (rc1 / "CHECKSUMS.txt").read_text().split("\n") if l.strip()]
    assert len(lines) == 24
    for line in lines:
        digest, name = line.split("  ", 1)
        got = hashlib.sha256((rc1 / name).read_bytes()).hexdigest()
        assert got == digest, f"v0.3.3-rc1 file {name} has changed"
    standalone = [l for l in lines if l.endswith("aperion-v0.3.3-standalone.html")][0]
    assert standalone.startswith("a9817d5971e862cce97ad2ce25532b24a8091978e38f67637a46a54c52301642")
