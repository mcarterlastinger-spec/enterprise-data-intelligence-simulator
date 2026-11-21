/*
 * Aperion Enterprise Data Intelligence Simulator — application namespace.
 *
 * The simulator uses ordinary <script> files (not JavaScript modules) so it works when
 * index.html is opened directly from disk, on GitHub Pages, and as a single standalone file.
 * Everything the application defines lives under ONE global: window.Aperion.
 *
 * SCRIPT LOAD ORDER (index.html must list the files in exactly this order):
 *   1. js/namespace.js           creates window.Aperion and the load-order check
 *   2. js/util.js                $, escapeHTML                          (needs: namespace)
 *   3. js/data/records.js        the six fictional source records       (needs: namespace)
 *   4. js/data/attributes.js     compared attributes, group letters     (needs: namespace)
 *   5. js/data/case.js           answer key, golden record, assessment  (needs: namespace)
 *   6. js/state.js               learner progress model                 (needs: namespace)
 *   7. js/rules/matching.js      normalization, attribute assessment    (needs: namespace)
 *   8. js/rules/identity.js      merge-eligibility rules                (needs: rules/matching)
 *   9. js/rules/golden.js        evidence-consistency checks            (needs: rules/matching)
 *  10. js/rules/scoring.js       competency scoring                     (needs: data/case)
 *  11. js/audio.js               Maya narration (speech synthesis)      (needs: util)
 *  12. js/navigation.js          pages and progress-aware Next Step     (needs: util, state, audio)
 *  13. js/views/records.js       Customer Records workspace             (needs: util, data, state, navigation)
 *  14. js/views/compare.js       Match & Compare                        (needs: util, data, state, rules)
 *  15. js/views/golden.js        Golden Record                          (needs: util, data, state)
 *  16. js/views/validation.js    Validation                             (needs: rules, views/golden)
 *  17. js/views/debrief.js       Debrief and scoring display            (needs: rules/scoring)
 *  18. js/views/stakeholders.js  contextual stakeholder guidance        (needs: util, data/case)
 *  19. js/views/nextbar.js       compact Next Step bar: Menu and Why?   (needs: util)
 *  20. js/bindings.js            connects buttons to actions            (needs: views, navigation, audio)
 *  21. js/main.js                startup                                (needs: everything)
 *
 * Each file calls Aperion.registerModule(name, dependencies). If a file is missing or out of
 * order, startup stops with a clear error in the browser console instead of failing silently.
 */
(function () {
  'use strict';

  if (window.Aperion) {
    throw new Error('Aperion: namespace already defined. Is js/namespace.js loaded twice?');
  }

  var loaded = ['namespace'];

  window.Aperion = {
    data: {},
    rules: {},
    views: {},

    registerModule: function (name, dependencies) {
      (dependencies || []).forEach(function (dep) {
        if (loaded.indexOf(dep) === -1) {
          throw new Error('Aperion: "' + name + '" needs "' + dep + '", which has not loaded yet. ' +
            'Check the script order in index.html (see js/namespace.js).');
        }
      });
      if (loaded.indexOf(name) !== -1) {
        throw new Error('Aperion: "' + name + '" loaded twice.');
      }
      loaded.push(name);
    },

    loadedModules: function () {
      return loaded.slice();
    }
  };
})();
