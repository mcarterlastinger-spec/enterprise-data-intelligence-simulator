/*
 * Maya narration using the browser's speech synthesis. Behavior unchanged from v0.3.2:
 *   - Only English voices whose names match a list of feminine voice names are offered.
 *   - One toggle button per transcript: Play -> Pause -> Resume. Replay is separate.
 *   - Changing pages stops narration (called from navigation.js).
 * Known defect D11: status messages are written to #audio-status, which is on the Records
 * page, so Mission Briefing learners do not see them. Not corrected in Phase 1.
 * Playback state is kept here (not in the learner state store) because it is not learner work.
 */
(function (A) {
  'use strict';
  A.registerModule('audio', ['util']);

  var $ = A.$;
  var escapeHTML = A.escapeHTML;

  var currentUtterance = null;
  var lastAudio = null; // eslint-disable-line no-unused-vars -- kept from v0.3.2 (written, never read)
  var audioState = 'idle';
  var audioSource = null;
  var replayHighlighted = false;

  var voiceNamesFemale = ['zira', 'aria', 'jenny', 'samantha', 'victoria', 'karen', 'moira', 'susan',
    'hazel', 'female', 'ava', 'allison', 'serena', 'siri'];

  function voices() {
    return 'speechSynthesis' in window
      ? window.speechSynthesis.getVoices().filter(function (v) { return /^en[-_]/i.test(v.lang); })
      : [];
  }

  function voiceIsPreferred(v) {
    return voiceNamesFemale.some(function (n) { return v.name.toLowerCase().includes(n); });
  }

  function updateAudioStatus(msg) {
    document.querySelectorAll('#audio-status,.brief-audio-status').forEach(function (el) { el.textContent = msg; });
  }

  function sourceName(b) {
    return b.dataset.source === 'brief-text' ? 'mission briefing' : 'Maya message';
  }

  function refreshAudioButtons() {
    document.querySelectorAll('.audio-toggle').forEach(function (b) {
      var active = b.dataset.source === audioSource;
      var playing = active && audioState === 'playing';
      var paused = active && audioState === 'paused';
      b.textContent = playing ? 'Ⅱ Pause' : paused ? '▶ Resume' : '▶ Play';
      b.classList.toggle('is-active', playing);
      b.classList.toggle('is-paused', paused);
      b.setAttribute('aria-pressed', String(playing || paused));
      b.setAttribute('aria-label', playing ? 'Pause ' + sourceName(b) : paused ? 'Resume ' + sourceName(b) : 'Play ' + sourceName(b));
    });
    document.querySelectorAll('.audio-replay').forEach(function (b) {
      var active = b.dataset.source === audioSource && replayHighlighted && audioState === 'playing';
      b.classList.toggle('is-active', active);
      b.setAttribute('aria-pressed', String(active));
    });
  }

  function populateVoices() {
    var el = $('voice-choice');
    if (!el) return;
    var vs = voices();
    var prior = el.value;
    var candidates = vs.filter(voiceIsPreferred);
    el.innerHTML = '<option value="">' + (candidates.length ? 'Select a Maya voice' : 'No known feminine voice available') + '</option>' +
      candidates.map(function (v) {
        return '<option value="' + escapeHTML(v.voiceURI) + '">' + escapeHTML(v.name) + ' (' + escapeHTML(v.lang) + ')</option>';
      }).join('');
    if (candidates.length) {
      el.value = candidates.some(function (v) { return v.voiceURI === prior; }) ? prior : candidates[0].voiceURI;
    }
    el.disabled = !candidates.length;
    updateAudioStatus(candidates.length
      ? 'Voice candidate selected. Play to confirm it sounds appropriate for Maya.'
      : 'No known feminine-sounding voice detected. Audio disabled; transcript remains available.');
  }

  function playAudio(t, character, source, isReplay) {
    if (character === undefined) character = 'Maya';
    if (source === undefined) source = 'maya-message';
    if (isReplay === undefined) isReplay = false;
    if (!('speechSynthesis' in window)) {
      updateAudioStatus('Audio unavailable; transcript remains visible.');
      return;
    }
    var select = $('voice-choice');
    var choice = select ? select.value : undefined;
    var voice = voices().find(function (v) { return v.voiceURI === choice && voiceIsPreferred(v); });
    if (!voice) {
      updateAudioStatus('No suitable Maya voice selected. Audio not started; use the transcript.');
      return;
    }
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(t);
    u.voice = voice;
    u.lang = voice.lang;
    u.rate = 0.94;
    currentUtterance = u;
    lastAudio = { t: t, character: character, source: source };
    audioState = 'playing';
    audioSource = source;
    replayHighlighted = isReplay;
    u.onend = function () {
      if (currentUtterance === u) {
        audioState = 'idle';
        replayHighlighted = false;
        refreshAudioButtons();
        updateAudioStatus('Audio finished. Transcript available.');
      }
    };
    u.onerror = function (e) {
      if (currentUtterance === u && e.error !== 'canceled' && e.error !== 'interrupted') {
        audioState = 'idle';
        replayHighlighted = false;
        refreshAudioButtons();
        updateAudioStatus('Audio unavailable. Transcript available.');
      }
    };
    window.speechSynthesis.speak(u);
    refreshAudioButtons();
    updateAudioStatus((isReplay ? 'Replaying' : 'Playing') + ' Maya with ' + voice.name);
  }

  function toggleAudio(source) {
    if (audioSource === source && audioState === 'playing') {
      window.speechSynthesis.pause();
      audioState = 'paused';
      replayHighlighted = false;
      refreshAudioButtons();
      updateAudioStatus('Paused. Select Resume to continue.');
      return;
    }
    if (audioSource === source && audioState === 'paused') {
      window.speechSynthesis.resume();
      audioState = 'playing';
      replayHighlighted = false;
      refreshAudioButtons();
      updateAudioStatus('Resumed playback.');
      return;
    }
    var el = $(source);
    if (el) playAudio(el.textContent, 'Maya', source);
  }

  function replayAudio(source) {
    var el = $(source || audioSource || 'maya-message');
    if (el) playAudio(el.textContent, 'Maya', el.id, true);
  }

  function pauseAudio() { if (audioState === 'playing') toggleAudio(audioSource); }
  function resumeAudio() { if (audioState === 'paused') toggleAudio(audioSource); }

  function stopAudio() {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    currentUtterance = null;
    audioState = 'idle';
    replayHighlighted = false;
    refreshAudioButtons();
    updateAudioStatus('Stopped.');
  }

  // Unused in v0.3.2's interface; kept for compatibility.
  function speakMaya() { playAudio($('maya-message').textContent, 'Maya', 'maya-message'); }
  function speakText(t) { playAudio(t, 'Maya', 'maya-message'); }

  /** Startup, identical to v0.3.2: load voices after 200 ms and whenever the browser updates them. */
  function init() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = populateVoices;
      setTimeout(populateVoices, 200);
    } else {
      updateAudioStatus('Audio not supported; transcript available.');
    }
    refreshAudioButtons();
  }

  A.audio = {
    init: init,
    state: function () { return audioState; },
    toggleAudio: toggleAudio,
    replayAudio: replayAudio,
    pauseAudio: pauseAudio,
    resumeAudio: resumeAudio,
    stopAudio: stopAudio,
    speakMaya: speakMaya,
    speakText: speakText
  };
})(window.Aperion);
