// Automated test for Persistent Question Status & Mastery Engine
const fs = require('fs');
const path = require('path');

// Mock browser environment
const localStorageStore = {};
global.localStorage = {
  getItem: (k) => localStorageStore[k] || null,
  setItem: (k, v) => { localStorageStore[k] = String(v); },
  removeItem: (k) => { delete localStorageStore[k]; },
  clear: () => { Object.keys(localStorageStore).forEach(k => delete localStorageStore[k]); }
};

global.window = {
  addEventListener: () => {},
  matchMedia: () => ({ matches: false }),
  scrollTo: () => {}
};

global.document = {
  addEventListener: () => {},
  documentElement: {
    classList: {
      add: () => {},
      remove: () => {},
      toggle: () => {}
    }
  },
  getElementById: (id) => {
    return {
      textContent: '',
      style: {},
      classList: {
        add: () => {},
        remove: () => {},
        toggle: () => {},
        contains: () => false
      },
      innerHTML: '',
      querySelectorAll: () => [],
      appendChild: () => {},
      removeChild: () => {},
      value: 'all'
    };
  },
  querySelectorAll: () => [],
  createElement: () => ({
    appendChild: () => {},
    classList: { add: () => {}, remove: () => {} }
  }),
  body: {
    appendChild: () => {},
    removeChild: () => {}
  }
};

// Load questions data
const dataCode = fs.readFileSync(path.join(__dirname, '../data/questions-data.js'), 'utf8');
eval(dataCode); // populates window.NPTEL_QUESTIONS
const topicsCode = fs.readFileSync(path.join(__dirname, '../data/topics.js'), 'utf8');
eval(topicsCode); // populates window.WEEK_TOPICS

const vm = require('vm');
// Load app.js
const appCode = fs.readFileSync(path.join(__dirname, '../app.js'), 'utf8');
vm.runInThisContext(appCode + '\nglobal.QuizApp = QuizApp;');

console.log("=== RUNNING QUESTION STATUS TESTS ===");

// TEST 1: Initialization & Auto-seeding from existing mistakes
localStorage.clear();
localStorage.setItem('psych_mistakes', JSON.stringify({
  '2026-w01-q01': { id: '2026-w01-q01', count: 2, addedAt: 1000 }
}));

const app = new QuizApp();
const statusMap = app.questionStatus;
if (!statusMap['2026-w01-q01'] || statusMap['2026-w01-q01'].status !== 'wrong') {
  console.error("FAIL: Auto-seeding from mistakes failed", statusMap['2026-w01-q01']);
  process.exit(1);
}
console.log("PASS 1: Existing mistakes automatically seeded into question status:", statusMap['2026-w01-q01']);

// TEST 2: Recording question status & updating on change
app.recordQuestionStatus('2026-w01-q02', ['A'], false);
if (app.questionStatus['2026-w01-q02'].status !== 'wrong' || app.questionStatus['2026-w01-q02'].wrongCount !== 1) {
  console.error("FAIL: Recording wrong answer failed", app.questionStatus['2026-w01-q02']);
  process.exit(1);
}
console.log("PASS 2a: Recorded wrong answer successfully");

// User re-attempts and gets it right: status must update to 'correct'!
app.recordQuestionStatus('2026-w01-q02', ['B'], true);
if (app.questionStatus['2026-w01-q02'].status !== 'correct' || app.questionStatus['2026-w01-q02'].attempts !== 2 || app.questionStatus['2026-w01-q02'].correctCount !== 1) {
  console.error("FAIL: Status did not update properly on answer change", app.questionStatus['2026-w01-q02']);
  process.exit(1);
}
console.log("PASS 2b: Status dynamically updated to correct upon answer change:", app.questionStatus['2026-w01-q02']);

// Flush save to storage and verify persistence
app.flushQuestionStatusSave();
const storedRaw = localStorage.getItem('psych_question_status');
if (!storedRaw) {
  console.error("FAIL: Question status not saved to localStorage");
  process.exit(1);
}
const parsedStored = JSON.parse(storedRaw);
if (parsedStored['2026-w01-q02'].status !== 'correct') {
  console.error("FAIL: Saved status mismatch in localStorage", parsedStored['2026-w01-q02']);
  process.exit(1);
}
console.log("PASS 2c: Persistent storage save and reload verified");

// TEST 3: Matching pool filtering by status
// Mock element builder-status-filter
let mockStatusFilter = 'all';
global.document.getElementById = (id) => {
  if (id === 'builder-status-filter') {
    return { value: mockStatusFilter };
  }
  return {
    textContent: '',
    style: {},
    classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false },
    innerHTML: '',
    querySelectorAll: () => [],
    appendChild: () => {},
    removeChild: () => {},
    value: 'all'
  };
};

mockStatusFilter = 'all';
const poolAll = app.getMatchingPool();

mockStatusFilter = 'unattempted';
const poolUnattempted = app.getMatchingPool();

mockStatusFilter = 'correct';
const poolCorrect = app.getMatchingPool();

mockStatusFilter = 'wrong';
const poolWrong = app.getMatchingPool();

console.log(`Pool stats: All=${poolAll.length}, Unattempted=${poolUnattempted.length}, Correct=${poolCorrect.length}, Wrong=${poolWrong.length}`);

if (poolCorrect.length !== 1 || poolCorrect[0].id !== '2026-w01-q02') {
  console.error("FAIL: Pool correct filter mismatch", poolCorrect.length);
  process.exit(1);
}
if (poolWrong.length !== 1 || poolWrong[0].id !== '2026-w01-q01') {
  console.error("FAIL: Pool wrong filter mismatch", poolWrong.length);
  process.exit(1);
}
if (poolUnattempted.length !== poolAll.length - 2) {
  console.error("FAIL: Pool unattempted filter mismatch", poolUnattempted.length);
  process.exit(1);
}
console.log("PASS 3: Status filtering in Test Builder verified perfectly");

// TEST 4: Export and Import with zero data loss
const exportPayload = {
  schemaVersion: "2.1",
  mistakes: {
    '2026-w01-q03': { id: '2026-w01-q03', count: 5, addedAt: 5000 }
  },
  questionStatus: {
    '2026-w01-q03': { status: 'wrong', attempts: 5, correctCount: 0, wrongCount: 5 }
  }
};

app.importMistakesData(JSON.stringify(exportPayload));
if (!app.mistakes['2026-w01-q01']) {
  console.error("FAIL: Existing mistake 2026-w01-q01 was lost during import!");
  process.exit(1);
}
if (!app.mistakes['2026-w01-q03']) {
  console.error("FAIL: New mistake 2026-w01-q03 was not imported!");
  process.exit(1);
}
if (!app.questionStatus['2026-w01-q03'] || app.questionStatus['2026-w01-q03'].status !== 'wrong') {
  console.error("FAIL: Question status was not imported/merged!");
  process.exit(1);
}
console.log("PASS 4: Backup export/import seamlessly merged with zero data loss");

// TEST 5: Reset Question Status preserves Mistakes Vault
app.resetQuestionStatus();
if (Object.keys(app.questionStatus).length !== 0) {
  console.error("FAIL: Question status not cleared");
  process.exit(1);
}
if (Object.keys(app.mistakes).length === 0) {
  console.error("FAIL: Resetting question status mistakenly cleared mistakes vault!");
  process.exit(1);
}
console.log("PASS 5: Resetting question status kept Mistakes Vault completely safe");

console.log("\nALL 5 AUTOMATED TEST SUITES PASSED SUCCESSFULLY!");
