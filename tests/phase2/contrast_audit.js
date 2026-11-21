/* WCAG 2.1 SC 1.4.11 (Non-text Contrast) audit for Aperion, run inside the page by tests.
 *
 * For every visible, enabled, focusable control it checks:
 *   focus    - the keyboard focus outline contrasts at least 3:1 with the colors next to it
 *              (the surface behind the control for outlines drawn outside it; the control's own
 *              fill for outlines drawn inside it with a negative offset).
 *   boundary - for form fields and bordered buttons, the control's edge is identifiable: either its
 *              fill contrasts at least 3:1 with the surface behind it, or its border does (against
 *              both the surface behind it and its own fill).
 * Exempt, as WCAG allows: disabled (inactive) controls; buttons with no border and no distinct fill,
 * which are identified by their text; native checkboxes and radio buttons, which the browser draws
 * (boundary only; their focus outline is still checked).
 * Colors are composited through semi-transparent backgrounds and ancestor opacity.
 */
(function () {
  function parse(c) {
    var m = /rgba?\(([^)]+)\)/.exec(c || '');
    if (!m) return null;
    var p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  }
  function lin(v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
  function lum(c) { return 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b); }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function over(top, bottom) {
    var a = top.a;
    return { r: top.r * a + bottom.r * (1 - a), g: top.g * a + bottom.g * (1 - a), b: top.b * a + bottom.b * (1 - a), a: 1 };
  }
  function hex(c) { return '#' + [c.r, c.g, c.b].map(function (v) { return Math.round(v).toString(16).padStart(2, '0'); }).join(''); }
  function opacityOf(el) {
    var o = 1;
    for (var e = el; e; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity);
    return o;
  }
  /** Background behind `el`'s content, including `el`'s own fill. */
  function surface(el) {
    var layers = [];
    for (var e = el; e; e = e.parentElement) {
      var c = parse(getComputedStyle(e).backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    var col = { r: 255, g: 255, b: 255, a: 1 };
    for (var i = layers.length - 1; i >= 0; i--) col = over(layers[i], col);
    return col;
  }
  function visible(el) {
    if (!el.getClientRects().length) return false;
    var s = getComputedStyle(el);
    if (s.visibility === 'hidden' || s.display === 'none') return false;
    if (el.closest('[hidden],[inert],[aria-hidden="true"]')) return false;
    return true;
  }
  function label(el) {
    var t = el.id ? '#' + el.id : el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '');
    var text = (el.getAttribute('aria-label') || el.textContent || el.value || '').replace(/\s+/g, ' ').trim().slice(0, 40);
    return t + (text ? ' "' + text + '"' : '');
  }

  window.__contrastAudit = function () {
    var sel = 'button, input:not([type=hidden]), select, textarea, summary, a[href], [tabindex]:not([tabindex="-1"])';
    var els = Array.prototype.filter.call(document.querySelectorAll(sel), function (el) { return visible(el) && !el.disabled; });
    var before = document.activeElement;
    var failures = [], checked = { focus: 0, boundary: 0 };
    els.forEach(function (el) {
      var s = getComputedStyle(el);
      var behind = surface(el.parentElement);
      var op = opacityOf(el);
      var fill = parse(s.backgroundColor) || { r: 0, g: 0, b: 0, a: 0 };
      var ownFill = over({ r: fill.r, g: fill.g, b: fill.b, a: fill.a * op }, behind);
      var native = el.matches('input[type=checkbox], input[type=radio]');

      // Boundary
      var bw = parseFloat(s.borderTopWidth), bs = s.borderTopStyle;
      var hasBorder = bw > 0 && bs !== 'none' && bs !== 'hidden';
      var isField = el.matches('input:not([type=checkbox]):not([type=radio]):not([type=button]):not([type=submit]), select, textarea');
      if (!native && (isField || hasBorder)) {
        checked.boundary++;
        var fillRatio = ratio(ownFill, behind);
        if (fillRatio < 3) {
          if (!hasBorder) failures.push({ el: label(el), check: 'boundary', detail: 'no border and fill ' + fillRatio.toFixed(2) + ':1' });
          else {
            var bc = parse(s.borderTopColor);
            var border = over({ r: bc.r, g: bc.g, b: bc.b, a: bc.a * op }, behind);
            var r = Math.min(ratio(border, behind), ratio(border, ownFill));
            if (r < 3) failures.push({ el: label(el), check: 'boundary', detail: 'border ' + hex(border) + ' ' + r.toFixed(2) + ':1 (needs 3:1)' });
          }
        }
      }

      // Focus outline
      checked.focus++;
      el.focus({ preventScroll: true });
      var f = getComputedStyle(el);
      if (document.activeElement !== el) return;
      if (f.outlineStyle === 'none' || parseFloat(f.outlineWidth) === 0) {
        failures.push({ el: label(el), check: 'focus', detail: 'no focus outline' });
      } else if (f.outlineStyle !== 'auto') {
        var oc = parse(f.outlineColor);
        var offset = parseFloat(f.outlineOffset) || 0;
        var adj = offset < 0 ? ownFill : behind;
        var outline = over({ r: oc.r, g: oc.g, b: oc.b, a: oc.a * op }, adj);
        var fr = ratio(outline, adj);
        if (fr < 3) failures.push({ el: label(el), check: 'focus', detail: 'outline ' + hex(outline) + ' on ' + hex(adj) + ' ' + fr.toFixed(2) + ':1 (needs 3:1)' });
      }
    });
    if (before && before.focus) before.focus({ preventScroll: true }); else document.activeElement.blur();
    return { failures: failures, checked: checked, controls: els.length };
  };
  window.__contrastRatio = function (a, b) { return ratio(parse(a), parse(b)); };
})();
