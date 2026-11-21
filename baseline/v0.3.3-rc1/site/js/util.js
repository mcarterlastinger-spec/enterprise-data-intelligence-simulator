/* Shared helpers (unchanged from v0.3.2). */
(function (A) {
  'use strict';
  A.registerModule('util', ['namespace']);

  /** Returns the element with the given id. */
  A.$ = function (id) {
    return document.getElementById(id);
  };

  /** Escapes text for safe insertion into HTML. */
  A.escapeHTML = function (s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  };
})(window.Aperion);
