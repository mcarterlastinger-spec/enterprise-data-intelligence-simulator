/*
 * Aperion Enterprise Data Intelligence Simulator — application namespace.
 *
 * The simulator uses ordinary <script> files (not JavaScript modules) so it works when
 * index.html is opened directly from disk, on GitHub Pages, and as a single standalone file.
 * Everything the application defines lives under ONE global: window.Aperion.
 *
 * SCRIPT LOAD ORDER (index.html must list the files in exactly this order):
 *   1. js/namespace.js          creates window.Aperion and the load-order check
 *   2. js/util.js               $, escapeHTML                         (needs: namespace)
 *   3. js/data/records.js       the six fictional source records      (needs: namespace)
 *   4. js/data/attributes.js    compared attributes, group letters    (needs: namespace)
 *   5. js/state.js              learner state store                   (needs: namespace)
 *   6. js/rules/matching.js     name normalization, attribute states  (needs: namespace)
 *   7. js/rules/governance.js   group verdicts                        (needs: namespace)
 *   8. js/audio.js              Maya narration (speech synthesis)     (needs: util)
 *   9. js/navigation.js         pages and Next Step bar               (needs: util, state, audio)
 *  10. js/views/records.js      Customer Records workspace            (needs: util, data, state, navigation)
 *  11. js/views/compare.js      Match & Compare                       (needs: util, data, state, rules)
 *  12. js/bindings.js           connects buttons to actions           (needs: views, navigation, audio)
 *  13. js/main.js               startup, in the same order as v0.3.2  (needs: everything)
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
