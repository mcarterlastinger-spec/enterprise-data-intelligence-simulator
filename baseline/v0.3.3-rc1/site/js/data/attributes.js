/* Attributes shown in the comparison matrix, and the identity-group choices (unchanged from v0.3.2). */
(function (A) {
  'use strict';
  A.registerModule('data/attributes', ['namespace']);

  /** [label shown to learners, record field] in display order. */
  A.data.attrs = [
    ['Legal name', 'legal'],
    ['Tax identifier', 'tax'],
    ['Business address', 'address'],
    ['Parent organization', 'parent'],
    ['Source system', 'system'],
    ['Last verified', 'verified']
  ];

  /** Identity group letters offered to learners (v0.3.2 fixed set of six). */
  A.data.groupLetters = ['A', 'B', 'C', 'D', 'E', 'F'];
})(window.Aperion);
