// Simulated speech engine for automated tests.
// Test browsers have no speech voices, so this replaces window.speechSynthesis
// with a recorder that behaves like the Web Speech API closely enough to exercise
// the simulator's playback state machine. It never produces sound.
// Real voice playback must still be checked by a person (REGRESSION-CHECKLIST.md).
(() => {
  const config = window.__speechConfig || {};
  const voices = (config.voices || [
    { name: 'Samantha', lang: 'en-US', voiceURI: 'Samantha', default: true, localService: true },
    { name: 'Daniel', lang: 'en-GB', voiceURI: 'Daniel', default: false, localService: true },
    { name: 'Anna', lang: 'de-DE', voiceURI: 'Anna', default: false, localService: true }
  ]);
  const log = [];
  let current = null;

  class FakeUtterance {
    constructor(text) {
      this.text = text; this.voice = null; this.lang = ''; this.rate = 1;
      this.onend = null; this.onerror = null;
    }
  }

  const engine = {
    speaking: false, paused: false, pending: false, onvoiceschanged: null,
    getVoices() { return voices.slice(); },
    speak(u) {
      log.push({ op: 'speak', text: u.text, voice: u.voice && u.voice.name, lang: u.lang, rate: u.rate });
      current = u; this.speaking = true; this.paused = false;
    },
    pause() { log.push({ op: 'pause' }); this.paused = true; },
    resume() { log.push({ op: 'resume' }); this.paused = false; },
    cancel() {
      log.push({ op: 'cancel' });
      const u = current; current = null; this.speaking = false; this.paused = false;
      // Real browsers report a cancelled utterance asynchronously.
      if (u && u.onerror) setTimeout(() => u.onerror({ error: 'interrupted' }), 0);
    }
  };

  Object.defineProperty(window, 'speechSynthesis', { value: engine, configurable: true });
  window.SpeechSynthesisUtterance = FakeUtterance;
  window.__speech = {
    log,
    currentText: () => (current ? current.text : null),
    finish() {
      const u = current; current = null; engine.speaking = false;
      if (u && u.onend) u.onend({});
    },
    fail(error) {
      const u = current; current = null; engine.speaking = false;
      if (u && u.onerror) u.onerror({ error: error || 'synthesis-failed' });
    }
  };
})();
