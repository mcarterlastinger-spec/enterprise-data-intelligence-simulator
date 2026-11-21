/*
 * Golden Record (v0.4.0, decision P2-2).
 *
 * For every current merge proposal, the learner builds one golden record. For each attribute they
 * choose a value that exists in the group's own source records AND the evidence that justifies
 * it. There is no automatic source precedence; operating and billing addresses are separate
 * attributes. Choices are kept in the state store (survive navigation). Saving creates a revision;
 * saving an unchanged record is refused, so the history only holds meaningful changes.
 * Choices update the state without re-rendering the form, so keyboard focus is never lost.
 */
(function (A) {
  'use strict';
  A.registerModule('views/golden', ['util', 'data/records', 'data/case', 'state']);

  var $ = A.$;
  var esc = A.escapeHTML;
  var S = A.state;

  function recordById(id) {
    return A.data.records.find(function (r) { return r.id === id; });
  }

  function timeLabel(ms) {
    return new Date(ms).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }

  function slug(s) {
    return String(s).replace(/[^A-Za-z0-9]+/g, '-');
  }

  /** Distinct exact values for an attribute among the group's records, with their sources. */
  function candidates(members, field) {
    var out = [];
    members.forEach(function (id) {
      var r = recordById(id);
      var v = r[field];
      if (!v) return;
      var c = out.find(function (x) { return x.value === v; });
      if (c) c.sources.push(id); else out.push({ value: v, sources: [id] });
    });
    return out;
  }

  function missingIn(members, field) {
    return members.filter(function (id) { return !recordById(id)[field]; });
  }

  /** Attributes that still need a value or a reason. */
  function incomplete(key) {
    var draft = S.goldenDraft(key);
    return A.data.goldenAttributes.filter(function (a) {
      var c = draft[a.key];
      return !c || !c.value || !c.reason;
    }).map(function (a) { return a.key; });
  }

  function sourceLabel(id) {
    var r = recordById(id);
    return `${id} (${r.system}, verified ${r.verified})`;
  }

  function attributeHTML(p, attr) {
    var base = 'g-' + slug(p.key) + '-' + attr.key;
    var draft = S.goldenDraft(p.key)[attr.key] || {};
    var opts = candidates(p.members, attr.field);
    var miss = missingIn(p.members, attr.field);
    var radios = opts.map(function (o, i) {
      var id = base + '-v' + i;
      return `<div class="choice"><input type="radio" id="${id}" name="${base}" value="${esc(o.value)}" data-sources="${o.sources.join(',')}" ${draft.value === o.value ? 'checked' : ''}><label for="${id}"><span class="choice-value">${esc(o.value)}</span><span class="small muted">from ${o.sources.map(sourceLabel).join(' and ')}</span></label></div>`;
    }).join('');
    var reasons = '<option value="">Choose the evidence…</option>' + A.data.goldenReasons.map(function (r) {
      return `<option value="${r.id}" ${draft.reason === r.id ? 'selected' : ''}>${esc(r.label)}</option>`;
    }).join('');
    return `<fieldset class="golden-attr" data-key="${p.key}" data-attr="${attr.key}"><legend>${esc(attr.label)} <span class="small muted">${esc(attr.prompt)}</span></legend>${radios}${miss.length ? `<p class="small muted">No value in ${miss.join(', ')}.</p>` : ''}<div class="reason-row"><label for="${base}-reason">Evidence for this choice</label><select id="${base}-reason" data-reason>${reasons}</select></div><div class="reason-row"><label for="${base}-note">Note <span class="muted">(optional)</span></label><input type="text" id="${base}-note" data-note value="${esc(draft.note || '')}" maxlength="200"></div></fieldset>`;
  }

  function evidenceTable(members) {
    return `<div class="tablewrap"><table class="evidence"><caption class="sr-only">Source records in this group</caption><thead><tr><th scope="col">Record</th><th scope="col">System</th><th scope="col">Last verified</th><th scope="col">Address</th><th scope="col">Contact</th><th scope="col">Source note</th></tr></thead><tbody>${members.map(function (id) {
      var r = recordById(id);
      return `<tr><th scope="row">${esc(r.id)}</th><td>${esc(r.system)}</td><td>${esc(r.verified)}</td><td>${esc(r.address)}</td><td>${esc(r.contact)}</td><td>${esc(r.note)}</td></tr>`;
    }).join('')}</tbody></table></div>`;
  }

  function statusText(p) {
    var left = incomplete(p.key).length;
    var latest = S.latestGolden(p.key);
    if (left) return `${left} of ${A.data.goldenAttributes.length} attributes still need a value and evidence.` + (latest ? ` Last saved: revision ${latest.rev}.` : '');
    if (!latest) return 'All attributes complete. Not saved yet.';
    if (S.goldenHasUnsavedChanges(p.key)) return `Changes since revision ${latest.rev} are not saved.`;
    return `Saved as revision ${latest.rev} at ${timeLabel(latest.at)}.`;
  }

  function savedSummary(p) {
    var latest = S.latestGolden(p.key);
    if (!latest) return '';
    var reasonLabel = function (id) { var r = A.data.goldenReasons.find(function (x) { return x.id === id; }); return r ? r.label : ''; };
    return `<h4>Saved golden record (revision ${latest.rev})</h4><div class="tablewrap"><table class="golden-summary"><thead><tr><th scope="col">Attribute</th><th scope="col">Value</th><th scope="col">Source</th><th scope="col">Evidence</th></tr></thead><tbody>${A.data.goldenAttributes.map(function (a) {
      var c = latest.choices[a.key] || {};
      return `<tr><th scope="row">${esc(a.label)}</th><td>${esc(c.value || '')}</td><td>${esc((c.sources || []).join(', '))}</td><td>${esc(reasonLabel(c.reason))}${c.note ? '<div class="small muted">' + esc(c.note) + '</div>' : ''}</td></tr>`;
    }).join('')}</tbody></table></div>`;
  }

  function groupHTML(p) {
    var name = slug(p.key);
    return `<section class="golden-group" aria-labelledby="gh-${name}"><h3 id="gh-${name}" tabindex="-1">Group ${p.letter} · ${p.members.join(' + ')} <span class="small muted">(proposal revision ${p.rev})</span></h3>${evidenceTable(p.members)}<div class="golden-form">${A.data.goldenAttributes.map(function (a) { return attributeHTML(p, a); }).join('')}</div><div class="controls"><button class="primary" data-save-golden="${p.key}" data-rev="${p.rev}">Save golden record for Group ${p.letter}</button></div><p class="golden-status" id="gs-${name}" aria-live="polite">${esc(statusText(p))}</p><div class="golden-saved" id="gsum-${name}">${savedSummary(p)}</div></section>`;
  }

  function renderGolden() {
    var props = S.currentProposals();
    var el = $('golden-content');
    if (!props.length) {
      el.innerHTML = '<div class="notice">No current merge proposals. Submit at least one eligible group on Match &amp; Compare first.</div><button class="primary" data-action="showPage:compare">Go to Match &amp; Compare</button>';
      return;
    }
    el.innerHTML = props.map(groupHTML).join('');
    el.querySelectorAll('fieldset.golden-attr').forEach(function (fs) {
      var key = fs.dataset.key, attr = fs.dataset.attr;
      var p = props.find(function (x) { return x.key === key; });
      fs.addEventListener('change', function (e) {
        var t = e.target;
        if (t.type === 'radio') S.setGoldenChoice(key, attr, { value: t.value, sources: t.dataset.sources.split(',') });
        else if (t.hasAttribute('data-reason')) S.setGoldenChoice(key, attr, { reason: t.value });
        else if (t.hasAttribute('data-note')) S.setGoldenChoice(key, attr, { note: t.value.trim() });
        updateStatus(p);
      });
    });
    el.querySelectorAll('[data-save-golden]').forEach(function (b) {
      b.addEventListener('click', function () {
        var p = props.find(function (x) { return x.key === b.dataset.saveGolden; });
        var left = incomplete(p.key);
        var status = $('gs-' + slug(p.key));
        if (left.length) {
          status.textContent = 'Not saved: ' + left.length + ' attribute(s) still need a value and evidence. ' + statusText(p);
          focusFirstIncomplete(p.key);
          return;
        }
        var rev = S.saveGolden(p.key, p.rev);
        status.textContent = rev ? `Saved as revision ${rev.rev} at ${timeLabel(rev.at)}.` : 'No changes since the last saved revision.';
        $('gsum-' + slug(p.key)).innerHTML = savedSummary(p);
        A.navigation.refresh();
      });
    });
  }

  function updateStatus(p) {
    var s = $('gs-' + slug(p.key));
    if (s) s.textContent = statusText(p);
    A.navigation.refresh();
  }

  function focusFirstIncomplete(key) {
    var left = incomplete(key);
    if (!left.length) return false;
    var fs = document.querySelector(`fieldset.golden-attr[data-key="${key}"][data-attr="${left[0]}"]`);
    if (!fs) return false;
    var draft = S.goldenDraft(key)[left[0]] || {};
    var target = draft.value ? fs.querySelector('[data-reason]') : fs.querySelector('input[type=radio]');
    fs.scrollIntoView({ block: 'center' });
    target.focus();
    return true;
  }

  /** Progress across all current proposals, for the Next Step bar. */
  function progress() {
    var props = S.currentProposals();
    for (var i = 0; i < props.length; i++) {
      var p = props[i];
      var left = incomplete(p.key).length;
      if (left) return { state: 'incomplete', proposal: p, left: left };
      if (!S.latestGolden(p.key) || S.goldenHasUnsavedChanges(p.key) || S.latestGolden(p.key).proposalRev !== p.rev) return { state: 'unsaved', proposal: p };
    }
    return { state: props.length ? 'done' : 'none', count: props.length };
  }

  function focusSave(key) {
    var b = document.querySelector(`[data-save-golden="${key}"]`);
    if (b) { b.scrollIntoView({ block: 'center' }); b.focus(); }
  }

  A.views.golden = {
    renderGolden: renderGolden,
    progress: progress,
    incomplete: incomplete,
    candidates: candidates,
    focusFirstIncomplete: focusFirstIncomplete,
    focusSave: focusSave
  };
})(window.Aperion);
