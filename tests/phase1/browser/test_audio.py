"""Maya narration controls (browser speech synthesis), using the simulated speech engine.

These tests check the playback state machine, labels, ARIA state, and status messages.
They cannot judge how a real voice sounds; that stays on the manual checklist.
"""
import pytest

MAYA_MSG = ("Welcome to the investigation. Start by searching for Northbridge records. Inspect identifiers "
            "and relationships before deciding which records belong together.")


def _btn(app, kind, source):
    sel = f'.audio-{kind}[data-source="{source}"]'
    return app.page.evaluate("""s=>{const b=document.querySelector(s);return {text:b.innerText.trim(),
        pressed:b.getAttribute('aria-pressed'),label:b.getAttribute('aria-label'),cls:[...b.classList].sort().join(' ')}}""", sel)


def _status(app):
    return app.page.evaluate("()=>document.getElementById('audio-status').textContent")


def test_A1_voice_list_offers_only_feminine_english_voices(open_app):
    app = open_app()
    options = app.page.evaluate("()=>[...document.querySelectorAll('#voice-choice option')].map(o=>[o.value,o.text])")
    assert options == [["", "Select a Maya voice"], ["Samantha", "Samantha (en-US)"]]
    assert app.page.input_value("#voice-choice") == "Samantha"
    assert not app.page.is_disabled("#voice-choice")
    assert _status(app) == "Voice candidate selected. Play to confirm it sounds appropriate for Maya."


def test_A2_play_pause_resume_cycle(open_app):
    app = open_app()
    app.nav("work")
    src = "maya-message"
    assert _btn(app, "toggle", src) == {"text": "▶ Play", "pressed": "false", "label": "Play Maya message",
                                        "cls": "audio-toggle primary"}
    app.page.click(f'.audio-toggle[data-source="{src}"]')
    assert _btn(app, "toggle", src) == {"text": "Ⅱ Pause", "pressed": "true", "label": "Pause Maya message",
                                        "cls": "audio-toggle is-active primary"}
    assert _status(app) == "Playing Maya with Samantha"
    log = app.speech_log()
    assert log[-2:] == [{"op": "cancel"}, {"op": "speak", "text": MAYA_MSG, "voice": "Samantha", "lang": "en-US", "rate": 0.94}]
    app.page.click(f'.audio-toggle[data-source="{src}"]')
    assert _btn(app, "toggle", src) == {"text": "▶ Resume", "pressed": "true", "label": "Resume Maya message",
                                        "cls": "audio-toggle is-paused primary"}
    assert _status(app) == "Paused. Select Resume to continue."
    app.page.click(f'.audio-toggle[data-source="{src}"]')
    assert _btn(app, "toggle", src)["text"] == "Ⅱ Pause"
    assert _status(app) == "Resumed playback."
    assert [e["op"] for e in app.speech_log()[-2:]] == ["pause", "resume"]
    app.page.evaluate("()=>window.__speech.finish()")
    assert _btn(app, "toggle", src) == {"text": "▶ Play", "pressed": "false", "label": "Play Maya message",
                                        "cls": "audio-toggle primary"}
    assert _status(app) == "Audio finished. Transcript available."


def test_A3_replay_is_separate(open_app):
    app = open_app()
    app.nav("work")
    app.page.click('.audio-replay[data-source="maya-message"]')
    assert _status(app) == "Replaying Maya with Samantha"
    assert _btn(app, "replay", "maya-message")["pressed"] == "true"
    assert "is-active" in _btn(app, "replay", "maya-message")["cls"]
    assert _btn(app, "toggle", "maya-message")["text"] == "Ⅱ Pause"
    app.page.click('.audio-toggle[data-source="maya-message"]')  # pause clears the replay highlight
    assert _btn(app, "replay", "maya-message")["pressed"] == "false"
    speaks = [e for e in app.speech_log() if e["op"] == "speak"]
    assert len(speaks) == 1 and speaks[0]["text"] == MAYA_MSG


def test_A4_briefing_narration(open_app):
    app = open_app()
    app.page.click('.audio-toggle[data-source="brief-text"]')
    speak = [e for e in app.speech_log() if e["op"] == "speak"][-1]
    assert speak["text"].startswith("I'm Maya Chen, Director of Data Governance.")
    assert _btn(app, "toggle", "brief-text")["label"] == "Pause mission briefing"


def test_A5_navigation_stops_audio(open_app):
    app = open_app()
    app.page.click('.audio-toggle[data-source="brief-text"]')
    app.next()
    assert app.speech_log()[-1] == {"op": "cancel"}
    assert _btn(app, "toggle", "brief-text")["text"] == "▶ Play"
    assert _status(app) == "Stopped."
    # paused audio is also stopped on navigation
    app.page.click('.audio-toggle[data-source="maya-message"]')
    app.page.click('.audio-toggle[data-source="maya-message"]')
    app.nav("brief")
    assert app.speech_log()[-1] == {"op": "cancel"}
    assert _btn(app, "toggle", "maya-message")["text"] == "▶ Play"


def test_A6_starting_other_narration_replaces_current(open_app):
    app = open_app()
    app.page.click('.audio-toggle[data-source="brief-text"]')
    # The Records-page control is hidden here; activate it programmatically so the page does not change.
    app.page.evaluate("()=>document.querySelector('.audio-toggle[data-source=\\'maya-message\\']').click()")
    assert _btn(app, "toggle", "maya-message")["text"] == "Ⅱ Pause"
    assert _btn(app, "toggle", "brief-text")["text"] == "▶ Play"
    assert [e["op"] for e in app.speech_log()][-2:] == ["cancel", "speak"]


def test_A7_no_suitable_voice_falls_back_to_transcript(open_app):
    app = open_app(speech="mock-novoices")
    options = app.page.evaluate("()=>[...document.querySelectorAll('#voice-choice option')].map(o=>o.text)")
    assert options == ["No known feminine voice available"]
    assert app.page.is_disabled("#voice-choice")
    assert _status(app) == "No known feminine-sounding voice detected. Audio disabled; transcript remains available."
    app.nav("work")
    app.page.click('.audio-toggle[data-source="maya-message"]')
    assert _status(app) == "No suitable Maya voice selected. Audio not started; use the transcript."
    assert _btn(app, "toggle", "maya-message")["text"] == "▶ Play"
    assert app.visible("#maya-message")


@pytest.mark.known_defect("D11")
def test_D11_briefing_status_target_hidden(open_app):
    """KNOWN DEFECT D11 — NOT APPROVED BEHAVIOR: on Mission Briefing, audio status goes to an element on the hidden Records page."""
    app = open_app(speech="mock-novoices")
    app.page.click('.audio-toggle[data-source="brief-text"]')
    assert _status(app) == "No suitable Maya voice selected. Audio not started; use the transcript."
    assert not app.visible("#audio-status")


def test_A8_speech_error_resets_controls(open_app):
    app = open_app()
    app.nav("work")
    app.page.click('.audio-toggle[data-source="maya-message"]')
    app.page.evaluate("()=>window.__speech.fail('synthesis-failed')")
    assert _btn(app, "toggle", "maya-message")["text"] == "▶ Play"
    assert _status(app) == "Audio unavailable. Transcript available."
