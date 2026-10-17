// Test Auto-Advance on Correct Answer, Stay on Wrong, and Latency Benchmark
const fs = require('fs');

// Mock browser environment
const localStorageMock = (function() {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

global.localStorage = localStorageMock;
global.window = {
  NPTEL_QUESTIONS: [
    { id: '2026-w01-q01', year: '2026', week: 1, type: 'MCQ', question: 'Q1', answer: ['A'], options: [{ key: 'A', text: 'Option A' }, { key: 'B', text: 'Option B' }] },
    { id: '2026-w01-q02', year: '2026', week: 1, type: 'MCQ', question: 'Q2', answer: ['B'], options: [{ key: 'A', text: 'Option A' }, { key: 'B', text: 'Option B' }] },
    { id: '2026-w01-q03', year: '2026', week: 1, type: 'MCQ', question: 'Q3', answer: ['A'], options: [{ key: 'A', text: 'Option A' }, { key: 'B', text: 'Option B' }] }
  ],
  WEEK_TOPICS: { 1: { title: 'Concept of Learning' } },
  matchMedia: () => ({ matches: false }),
  addEventListener: () => {},
  scrollTo: () => {},
  requestAnimationFrame: (cb) => cb(),
  innerWidth: 1024
};

// DOM mock
const elements = {};
function getMockElement(id) {
  if (!elements[id]) {
    elements[id] = {
      id,
      className: '',
      classList: {
        add: function(...cls) { this.classes.push(...cls); },
        remove: function(...cls) { this.classes = this.classes.filter(c => !cls.includes(c)); },
        toggle: function(c, force) {
          if (force === undefined) {
            if (this.contains(c)) this.remove(c); else this.add(c);
          } else if (force) this.add(c); else this.remove(c);
        },
        contains: function(c) { return this.classes.includes(c); },
        classes: []
      },
      style: {},
      textContent: '',
      innerHTML: '',
      querySelectorAll: (sel) => [],
      querySelector: (sel) => null,
      appendChild: () => {},
      disabled: false
    };
  }
  return elements[id];
}

global.document = {
  documentElement: { classList: { add: () => {}, remove: () => {}, toggle: () => {} } },
  getElementById: (id) => getMockElement(id),
  createElement: () => ({
    className: '',
    classList: { add: () => {}, remove: () => {} },
    style: {},
    appendChild: () => {},
    querySelector: () => ({ innerHTML: '', className: '' }),
    querySelectorAll: () => []
  }),
  querySelectorAll: () => [],
  querySelector: () => null,
  addEventListener: (event, cb) => {
    if (event === 'DOMContentLoaded') cb();
  }
};
global.lucide = { createIcons: () => {} };

// Load app.js
const appCode = fs.readFileSync('app.js', 'utf8');
(1, eval)(appCode);

const app = global.window.app;

async function runTests() {
  console.log("--- TEST 1: Practice mode correct answer auto-advances ---");
  app.startTest(window.NPTEL_QUESTIONS);
  console.assert(app.activeTest.currentIndex === 0, "Starts on Q1 (index 0)");
  
  // Q1 correct answer is 'A'
  app.selectOption('A');
  console.assert(app.autoAdvanceTimer !== null, "Auto-advance timer should be active after correct answer");
  
  // Wait for auto-advance timer (350ms)
  await new Promise(r => setTimeout(r, 380));
  console.assert(app.activeTest.currentIndex === 1, `Auto-advanced to Q2 (index 1). Current: ${app.activeTest.currentIndex}`);
  console.log("Test 1 passed!");

  console.log("--- TEST 2: Wrong answer stays on current question ---");
  // Q2 correct answer is 'B'. Selecting 'A' is wrong!
  app.selectOption('A');
  console.assert(app.autoAdvanceTimer === null, "Auto-advance timer MUST be null for wrong answer");
  
  await new Promise(r => setTimeout(r, 400));
  console.assert(app.activeTest.currentIndex === 1, `Must stay on Q2. Current: ${app.activeTest.currentIndex}`);
  console.log("Test 2 passed!");

  console.log("--- TEST 3: Navigating manually clears autoAdvanceTimer ---");
  // On Q2, now select 'B' (correct)
  app.selectOption('B');
  console.assert(app.autoAdvanceTimer !== null, "Timer running for correct answer");
  // Immediately user hits Previous
  app.prevQuestion();
  console.assert(app.autoAdvanceTimer === null, "Timer must be cleared when manually navigating");
  console.assert(app.activeTest.currentIndex === 0, "Went back to Q1");
  console.log("Test 3 passed!");

  console.log("--- TEST 4: Performance & Latency Benchmark ---");
  const iterations = 500;
  const start = performance.now();
  for (let i = 0; i < iterations; i++) {
    app.selectOption('A');
  }
  const totalMs = performance.now() - start;
  const avgMs = totalMs / iterations;
  console.log(`Ran ${iterations} selectOption calls in ${totalMs.toFixed(2)}ms (Average: ${avgMs.toFixed(3)}ms per call)`);
  console.assert(avgMs < 2, `Expected average latency < 2ms, got ${avgMs.toFixed(3)}ms`);
  console.log("Test 4 passed!");

  console.log("\nALL AUTO-ADVANCE & SPEED TESTS PASSED!");
}

runTests().catch(err => {
  console.error("Test error:", err);
  process.exit(1);
});
