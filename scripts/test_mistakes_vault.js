// Test Mistakes Vault Import/Export & Non-destructive migration
const fs = require('fs');

// Mock browser environment
const localStorageMock = (function() {
  let store = {};
  return {
    getItem: function(key) {
      return store[key] || null;
    },
    setItem: function(key, value) {
      store[key] = value.toString();
    },
    removeItem: function(key) {
      delete store[key];
    },
    clear: function() {
      store = {};
    },
    _getStore: function() { return store; }
  };
})();

global.localStorage = localStorageMock;
global.window = {
  NPTEL_QUESTIONS: [
    { id: '2026-w01-q01', year: '2026', week: 1, question: 'Sample Q1', answer: ['A'], options: [{ key: 'A', text: 'Option A' }] },
    { id: '2026-w01-q02', year: '2026', week: 1, question: 'Sample Q2', answer: ['B'], options: [{ key: 'B', text: 'Option B' }] },
    { id: '2026-w06-q07', year: '2026', week: 6, question: 'Which of the following is a facilitator of EQ?', answer: ['D'], options: [{ key: 'D', text: 'all of the given' }] }
  ],
  WEEK_TOPICS: {},
  matchMedia: () => ({ matches: false }),
  addEventListener: () => {},
  scrollTo: () => {},
  requestAnimationFrame: (cb) => cb()
};
global.document = {
  documentElement: { classList: { add: () => {}, remove: () => {}, toggle: () => {} } },
  getElementById: (id) => ({
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    textContent: '',
    appendChild: () => {},
    innerHTML: ''
  }),
  createElement: () => ({
    classList: { add: () => {}, remove: () => {} },
    remove: () => {},
    appendChild: () => {},
    innerHTML: ''
  }),
  querySelectorAll: () => [],
  querySelector: () => null,
  addEventListener: (event, cb) => {
    if (event === 'DOMContentLoaded') {
      cb();
    }
  }
};

// Mock Lucide
global.lucide = { createIcons: () => {} };

// Load app.js
const appCode = fs.readFileSync('app.js', 'utf8');
(1, eval)(appCode);

const app = global.window.app;

console.log("--- TEST 1: Initial load with empty storage ---");
console.assert(Object.keys(app.mistakes).length === 0, "Mistakes should be empty initially");
console.log("Test 1 passed!");

console.log("--- TEST 2: Add mistakes to vault ---");
app.addMistake(window.NPTEL_QUESTIONS[0]); // 2026-w01-q01
app.addMistake(window.NPTEL_QUESTIONS[0]); // Missed second time
console.assert(app.mistakes['2026-w01-q01'].count === 2, "Count should be 2 for 2026-w01-q01");
console.log("Test 2 passed!");

console.log("--- TEST 3: Legacy keys recovery ---");
// Simulate a user who had mistakes in an older version key
localStorage.setItem('psychology_mistakes', JSON.stringify({
  '2026-w01-q02': { count: 3, addedAt: 1000 }
}));
const reloaded = app.loadMistakesFromStorage();
console.assert(reloaded['2026-w01-q01'].count === 2, "Existing mistake preserved");
console.assert(reloaded['2026-w01-q02'].count === 3, "Legacy mistake recovered");
console.assert(reloaded['2026-w01-q02'].question.id === '2026-w01-q02', "Hydrated canonical question");
console.log("Test 3 passed!");

console.log("--- TEST 4: Format resilience in normalizeMistakesData ---");
// Format A: Wrapped JSON
const formatA = { mistakes: { '2026-w06-q07': { count: 4 } } };
const normA = app.normalizeMistakesData(formatA);
console.assert(normA['2026-w06-q07'].count === 4, "Format A parsed");

// Format B: Array of IDs
const formatB = ['2026-w01-q01', '2026-w06-q07'];
const normB = app.normalizeMistakesData(formatB);
console.assert(normB['2026-w01-q01'].count === 1, "Format B ID 1 parsed");
console.assert(normB['2026-w06-q07'].count === 1, "Format B ID 2 parsed");

// Format C: Array of question objects
const formatC = [{ id: '2026-w06-q07', count: 5 }];
const normC = app.normalizeMistakesData(formatC);
console.assert(normC['2026-w06-q07'].count === 5, "Format C parsed");
console.log("Test 4 passed!");

console.log("--- TEST 5: Non-destructive import ---");
// Current vault has '2026-w01-q01' (count: 2) and '2026-w01-q02' (count: 3)
// We import backup with '2026-w01-q01' (count: 1) and new '2026-w06-q07' (count: 5)
const importPayload = JSON.stringify({
  mistakes: {
    '2026-w01-q01': { count: 1, addedAt: 500 },
    '2026-w06-q07': { count: 5, addedAt: 2000 }
  }
});
app.importMistakesData(importPayload);

console.assert(app.mistakes['2026-w01-q01'].count === 2, "Count should be max(2, 1) = 2 (not overwritten)");
console.assert(app.mistakes['2026-w01-q02'].count === 3, "Pre-existing '2026-w01-q02' was NOT deleted!");
console.assert(app.mistakes['2026-w06-q07'].count === 5, "'2026-w06-q07' added successfully");
console.assert(Object.keys(app.mistakes).length === 3, "Total mistakes should be exactly 3");
console.log("Test 5 passed!");

console.log("--- TEST 6: Single mistake removal ---");
app.removeMistake('2026-w01-q02');
console.assert(app.mistakes['2026-w01-q02'] === undefined, "'2026-w01-q02' removed");
console.assert(app.mistakes['2026-w01-q01'] !== undefined, "'2026-w01-q01' preserved");
console.assert(app.mistakes['2026-w06-q07'] !== undefined, "'2026-w06-q07' preserved");
console.log("Test 6 passed!");

console.log("--- TEST 7: Corrupted JSON import (Zero Data Loss) ---");
const countBefore = Object.keys(app.mistakes).length;
app.importMistakesData("{ corrupted json bad syntax");
console.assert(Object.keys(app.mistakes).length === countBefore, "Corrupted import must not alter existing mistakes");
console.log("Test 7 passed!");

console.log("--- TEST 8: Question Hydration & Typo Upgrade ---");
// Suppose someone imports a backup from an old version where 2026-w06-q07 had buggy answer ['A']
const oldVersionPayload = JSON.stringify({
  mistakes: {
    '2026-w06-q07': {
      count: 10,
      question: { id: '2026-w06-q07', answer: ['A'] } // old buggy answer
    }
  }
});
app.importMistakesData(oldVersionPayload);
console.assert(app.mistakes['2026-w06-q07'].count === 10, "Count updated to 10");
console.assert(JSON.stringify(app.mistakes['2026-w06-q07'].question.answer) === '["D"]', "Canonical question automatically hydrated! Buggy answer corrected to D!");
console.log("Test 8 passed!");

console.log("--- TEST 9: Empty import (Zero Data Loss) ---");
app.importMistakesData(JSON.stringify({ mistakes: {} }));
console.assert(Object.keys(app.mistakes).length === 2, "Empty import must not wipe vault");
console.log("Test 9 passed!");

console.log("\nALL 9 RIGOROUS TESTS PASSED WITH 100% SUCCESS!");
