/**
 * NPTEL Psychology of Learning - MCQ Mastery Platform
 * Main Application Logic
 */

class QuizApp {
  constructor() {
    this.questions = window.NPTEL_QUESTIONS || [];
    this.topics = window.WEEK_TOPICS || {};
    
    // Config state
    this.selectedYears = new Set(['2026', '2025', '2024', '2023']);
    this.selectedWeeks = new Set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
    this.quizMode = 'practice'; // 'practice' or 'exam'
    this.questionCount = 30; // 10, 20, 30, 50, 100, or 'all'
    this.shuffleQuestions = true;
    this.shuffleOptions = true;
    this.examDurationMinutes = 30;
    
    // Active Test State
    this.activeTest = null;
    this.timerInterval = null;
    
    // LocalStorage Persistent Stores
    this.bookmarks = new Set(JSON.parse(localStorage.getItem('psych_bookmarks') || '[]'));
    this.mistakes = JSON.parse(localStorage.getItem('psych_mistakes') || '{}');
    this.history = JSON.parse(localStorage.getItem('psych_history') || '[]');
    
    // Flashcard state
    this.fcIndex = 0;
    this.fcQuestions = [];
    this.fcFlipped = false;
    
    // Explorer state
    this.reviewFilter = 'all';
    this.currentView = 'builder';
  }

  init() {
    this.initTheme();
    this.renderWeekSelectors();
    this.populateExplorerWeeks();
    this.updateMatchCount();
    this.updateNavBadges();
    this.initKeyboardShortcuts();
    this.showView('builder');
    
    // Lucide Icons initialization
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  // ==========================================
  // THEME MANAGEMENT
  // ==========================================
  initTheme() {
    const saved = localStorage.getItem('psych_theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (saved === 'dark' || (!saved && prefersDark)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('psych_theme', isDark ? 'dark' : 'light');
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('hidden');
  }

  // ==========================================
  // VIEW NAVIGATION
  // ==========================================
  showView(viewId) {
    this.currentView = viewId;
    const views = ['builder', 'quiz', 'results', 'explorer', 'flashcards', 'mistakes', 'bookmarks'];
    views.forEach(v => {
      const el = document.getElementById(`view-${v}`);
      if (el) {
        if (v === viewId) {
          el.classList.remove('hidden');
        } else {
          el.classList.add('hidden');
        }
      }
      
      const navBtn = document.getElementById(`nav-btn-${v}`);
      if (navBtn) {
        if (v === viewId) {
          navBtn.className = "nav-tab px-3.5 py-2 rounded-lg text-sm font-semibold flex items-center space-x-2 text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/60 transition-all";
        } else {
          navBtn.className = "nav-tab px-3.5 py-2 rounded-lg text-sm font-semibold flex items-center space-x-2 text-slate-600 dark:text-slate-400 hover:text-brand-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all";
        }
      }
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (viewId === 'explorer') {
      this.filterExplorer();
    } else if (viewId === 'flashcards') {
      this.initFlashcards();
    } else if (viewId === 'mistakes') {
      this.renderMistakesView();
    } else if (viewId === 'bookmarks') {
      this.renderBookmarksView();
    }

    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  updateNavBadges() {
    const mCount = Object.keys(this.mistakes).length;
    const bCount = this.bookmarks.size;
    
    const mBadge = document.getElementById('nav-mistakes-badge');
    if (mBadge) {
      if (mCount > 0) {
        mBadge.textContent = mCount;
        mBadge.classList.remove('hidden');
      } else {
        mBadge.classList.add('hidden');
      }
    }

    const bBadge = document.getElementById('nav-bookmarks-badge');
    if (bBadge) {
      if (bCount > 0) {
        bBadge.textContent = bCount;
        bBadge.classList.remove('hidden');
      } else {
        bBadge.classList.add('hidden');
      }
    }
  }

  // ==========================================
  // BUILDER: WEEK SELECTORS RENDERING
  // ==========================================
  renderWeekSelectors() {
    const container = document.getElementById('weeks-selector-grid');
    if (!container) return;

    // Count questions per week
    const weekCounts = {};
    this.questions.forEach(q => {
      weekCounts[q.week] = (weekCounts[q.week] || 0) + 1;
    });

    let html = '';
    for (let w = 0; w <= 12; w++) {
      const topInfo = this.topics[w] || { title: `Week ${w}`, short: `Week ${w}`, concepts: [] };
      const count = weekCounts[w] || 0;
      const isChecked = this.selectedWeeks.has(w);

      html += `
        <label class="week-checkbox-card cursor-pointer p-3 rounded-xl border-2 ${isChecked ? 'border-brand-500 bg-brand-50/40 dark:bg-brand-950/20' : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900'} hover:border-brand-400 transition-all flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-xs font-extrabold text-brand-600 dark:text-brand-400 uppercase tracking-wide">
                ${w === 0 ? 'Intro (Week 0)' : `Week ${w}`}
              </span>
              <input type="checkbox" value="${w}" ${isChecked ? 'checked' : ''} onchange="app.onWeekToggle(${w}, this.checked)" class="rounded text-brand-600 focus:ring-brand-500 w-4 h-4">
            </div>
            <div class="text-xs font-bold text-slate-900 dark:text-slate-100 line-clamp-1" title="${topInfo.title}">
              ${topInfo.title}
            </div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-1 mt-0.5" title="${topInfo.concepts.join(', ')}">
              ${topInfo.concepts.slice(0, 2).join(' • ')}
            </div>
          </div>
          <div class="mt-2.5 pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-[11px]">
            <span class="text-slate-400">Questions</span>
            <span class="font-extrabold text-slate-700 dark:text-slate-300">${count} Qs</span>
          </div>
        </label>
      `;
    }
    container.innerHTML = html;
  }

  onWeekToggle(weekNum, isChecked) {
    if (isChecked) {
      this.selectedWeeks.add(weekNum);
    } else {
      this.selectedWeeks.delete(weekNum);
    }
    this.renderWeekSelectors();
    this.updateMatchCount();
  }

  setWeekFilter(type) {
    if (type === 'all') {
      this.selectedWeeks = new Set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
    } else if (type === 'foundations') {
      this.selectedWeeks = new Set([0, 1, 2, 3, 4]);
    } else if (type === 'cognition') {
      this.selectedWeeks = new Set([5, 6, 7, 8]);
    } else if (type === 'applied') {
      this.selectedWeeks = new Set([9, 10, 11, 12]);
    } else if (type === 'clear') {
      this.selectedWeeks = new Set();
    }
    this.renderWeekSelectors();
    this.updateMatchCount();
  }

  // ==========================================
  // BUILDER: YEAR FILTERS
  // ==========================================
  setYearFilter(type) {
    const checkboxes = document.querySelectorAll('.year-checkbox-card input[type="checkbox"]');
    if (type === 'all') {
      this.selectedYears = new Set(['2026', '2025', '2024', '2023']);
    } else if (type === 'current') {
      this.selectedYears = new Set(['2026']);
    } else if (type === 'pyqs') {
      this.selectedYears = new Set(['2025', '2024', '2023']);
    }

    checkboxes.forEach(cb => {
      cb.checked = this.selectedYears.has(cb.value);
      const card = cb.closest('.year-checkbox-card');
      if (card) {
        if (cb.checked) {
          card.classList.add('border-brand-500', 'bg-brand-50/50', 'dark:bg-brand-950/30');
          card.classList.remove('border-slate-200', 'dark:border-slate-800');
        } else {
          card.classList.remove('border-brand-500', 'bg-brand-50/50', 'dark:bg-brand-950/30');
          card.classList.add('border-slate-200', 'dark:border-slate-800');
        }
      }
    });

    this.updateMatchCount();
  }

  onModeChange(mode) {
    this.quizMode = mode;
    const practiceCard = document.getElementById('mode-card-practice');
    const examCard = document.getElementById('mode-card-exam');
    const timerContainer = document.getElementById('timer-setting-container');
    const startBtnLabel = document.getElementById('start-btn-label');

    if (mode === 'practice') {
      practiceCard.classList.add('border-brand-500', 'bg-brand-50/40', 'dark:bg-brand-950/30');
      practiceCard.classList.remove('border-slate-200', 'dark:border-slate-800');
      practiceCard.querySelector('.mode-check-badge').className = "mode-check-badge w-5 h-5 rounded-full border-2 border-brand-500 bg-brand-500 text-white flex items-center justify-center text-xs";
      practiceCard.querySelector('.mode-check-badge').textContent = '✓';

      examCard.classList.remove('border-brand-500', 'bg-brand-50/40', 'dark:bg-brand-950/30');
      examCard.classList.add('border-slate-200', 'dark:border-slate-800');
      examCard.querySelector('.mode-check-badge').className = "mode-check-badge w-5 h-5 rounded-full border-2 border-slate-300 dark:border-slate-700 flex items-center justify-center text-xs";
      examCard.querySelector('.mode-check-badge').textContent = '';

      timerContainer.classList.add('hidden');
      startBtnLabel.textContent = 'Start Practice Session';
    } else {
      examCard.classList.add('border-brand-500', 'bg-brand-50/40', 'dark:bg-brand-950/30');
      examCard.classList.remove('border-slate-200', 'dark:border-slate-800');
      examCard.querySelector('.mode-check-badge').className = "mode-check-badge w-5 h-5 rounded-full border-2 border-brand-500 bg-brand-500 text-white flex items-center justify-center text-xs";
      examCard.querySelector('.mode-check-badge').textContent = '✓';

      practiceCard.classList.remove('border-brand-500', 'bg-brand-50/40', 'dark:bg-brand-950/30');
      practiceCard.classList.add('border-slate-200', 'dark:border-slate-800');
      practiceCard.querySelector('.mode-check-badge').className = "mode-check-badge w-5 h-5 rounded-full border-2 border-slate-300 dark:border-slate-700 flex items-center justify-center text-xs";
      practiceCard.querySelector('.mode-check-badge').textContent = '';

      timerContainer.classList.remove('hidden');
      startBtnLabel.textContent = 'Begin Timed Exam';
    }
  }

  setQuestionCount(count) {
    this.questionCount = count;
    document.querySelectorAll('.q-count-btn').forEach(btn => {
      const isThis = (count === 'all' && btn.textContent.includes('All')) ||
                     (count !== 'all' && btn.textContent.startsWith(String(count)));
      if (isThis) {
        btn.className = "q-count-btn px-3 py-2 rounded-lg text-xs font-bold border-2 border-brand-500 bg-brand-50 dark:bg-brand-950/50 text-brand-600 dark:text-brand-400 font-bold transition";
      } else {
        btn.className = "q-count-btn px-3 py-2 rounded-lg text-xs font-bold border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 transition text-slate-700 dark:text-slate-300";
      }
    });
    this.updateMatchCount();
  }

  updateMatchCount() {
    // Read year checkboxes
    const yearBoxes = document.querySelectorAll('.year-checkbox-card input[type="checkbox"]');
    this.selectedYears = new Set();
    yearBoxes.forEach(cb => {
      if (cb.checked) this.selectedYears.add(cb.value);
      const card = cb.closest('.year-checkbox-card');
      if (card) {
        if (cb.checked) {
          card.classList.add('border-brand-500', 'bg-brand-50/50', 'dark:bg-brand-950/30');
          card.classList.remove('border-slate-200', 'dark:border-slate-800');
        } else {
          card.classList.remove('border-brand-500', 'bg-brand-50/50', 'dark:bg-brand-950/30');
          card.classList.add('border-slate-200', 'dark:border-slate-800');
        }
      }
    });

    const matching = this.getMatchingPool();
    const countEl = document.getElementById('matching-pool-count');
    const allInd = document.getElementById('all-count-indicator');
    const selectedEl = document.getElementById('selected-test-count');
    const startBtn = document.getElementById('start-test-btn');

    if (countEl) countEl.textContent = matching.length;
    if (allInd) allInd.textContent = matching.length;

    let testSize = this.questionCount === 'all' ? matching.length : Math.min(this.questionCount, matching.length);
    if (selectedEl) selectedEl.textContent = `${testSize} Questions`;

    if (startBtn) {
      if (matching.length === 0) {
        startBtn.disabled = true;
        startBtn.classList.add('opacity-50', 'cursor-not-allowed');
      } else {
        startBtn.disabled = false;
        startBtn.classList.remove('opacity-50', 'cursor-not-allowed');
      }
    }
  }

  getMatchingPool() {
    return this.questions.filter(q => 
      this.selectedYears.has(q.year) && this.selectedWeeks.has(q.week)
    );
  }

  // ==========================================
  // QUIZ ENGINE: START & RUN
  // ==========================================
  startTest(customQuestions = null) {
    let pool = customQuestions || this.getMatchingPool();
    if (pool.length === 0) {
      alert("No questions match your current combination. Please select at least one year and one week!");
      return;
    }

    const shuffleQ = document.getElementById('shuffle-questions-toggle') ? document.getElementById('shuffle-questions-toggle').checked : true;
    const shuffleOpt = document.getElementById('shuffle-options-toggle') ? document.getElementById('shuffle-options-toggle').checked : true;

    // Clone and optionally shuffle
    let chosen = pool.map(q => ({
      ...q,
      options: shuffleOpt ? this.shuffleArray([...q.options]) : [...q.options]
    }));

    if (shuffleQ) {
      chosen = this.shuffleArray(chosen);
    }

    let size = customQuestions ? chosen.length : (this.questionCount === 'all' ? chosen.length : Math.min(this.questionCount, chosen.length));
    chosen = chosen.slice(0, size);

    // Setup active test state
    this.activeTest = {
      questions: chosen,
      currentIndex: 0,
      userAnswers: {}, // id -> ['A'] or ['A', 'C']
      flagged: new Set(),
      revealedPractice: new Set(),
      startTime: Date.now(),
      elapsedSeconds: 0,
      mode: this.quizMode,
      durationMinutes: this.quizMode === 'exam' ? parseInt(document.getElementById('exam-timer-select').value || '30') : 0
    };

    // Setup Timer
    clearInterval(this.timerInterval);
    const timerBadge = document.getElementById('quiz-timer-badge');
    const timerDisplay = document.getElementById('quiz-timer-display');
    
    if (this.activeTest.mode === 'exam' && this.activeTest.durationMinutes > 0) {
      timerBadge.classList.remove('hidden');
      timerBadge.classList.add('flex');
      let remainingSeconds = this.activeTest.durationMinutes * 60;
      
      const updateTimer = () => {
        const mins = Math.floor(remainingSeconds / 60);
        const secs = remainingSeconds % 60;
        timerDisplay.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        
        if (remainingSeconds <= 300) { // 5 min warning
          timerBadge.classList.add('bg-rose-50', 'text-rose-700', 'border-rose-300', 'dark:bg-rose-950', 'dark:text-rose-300');
        }
        
        if (remainingSeconds <= 0) {
          clearInterval(this.timerInterval);
          alert("Time's up! Your exam is being automatically submitted.");
          this.finalizeTestSubmission();
        }
        remainingSeconds--;
        this.activeTest.elapsedSeconds++;
      };
      
      updateTimer();
      this.timerInterval = setInterval(updateTimer, 1000);
    } else {
      timerBadge.classList.add('hidden');
      timerBadge.classList.remove('flex');
      this.timerInterval = setInterval(() => {
        if (this.activeTest) this.activeTest.elapsedSeconds++;
      }, 1000);
    }

    // Set UI mode pill
    const modePill = document.getElementById('quiz-mode-pill');
    if (this.activeTest.mode === 'practice') {
      modePill.textContent = 'Practice Mode';
      modePill.className = 'text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300';
    } else {
      modePill.textContent = 'Exam Mode';
      modePill.className = 'text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-100 text-violet-800 dark:bg-violet-950 dark:text-violet-300';
    }

    this.showView('quiz');
    this.renderQuestion(0);
    this.renderPalette();
  }

  shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }

  // ==========================================
  // QUESTION RENDERING & INTERACTION
  // ==========================================
  renderQuestion(index) {
    if (!this.activeTest) return;
    this.activeTest.currentIndex = index;
    const q = this.activeTest.questions[index];
    const total = this.activeTest.questions.length;

    // Header info
    document.getElementById('quiz-progress-text').textContent = `Question ${index + 1} of ${total}`;
    const pct = ((index + 1) / total) * 100;
    document.getElementById('quiz-progress-bar').style.width = `${pct}%`;
    
    const topic = this.topics[q.week] || { title: `Week ${q.week}` };
    document.getElementById('quiz-current-category').textContent = `${q.week === 0 ? 'Intro' : `Week ${q.week}`}: ${topic.title}`;
    
    // Badges
    document.getElementById('q-year-badge').textContent = q.year === '2026' ? '2026 Current Assignment' : `${q.year} PYQ`;
    document.getElementById('q-week-badge').textContent = q.week === 0 ? 'Week 0 (Intro)' : `Week ${q.week}`;
    document.getElementById('q-type-badge').textContent = q.type === 'MSQ' ? 'Multiple Select (MSQ)' : 'Single Choice (MCQ)';
    document.getElementById('q-id-badge').textContent = `#${q.id}`;

    // Question Text
    document.getElementById('q-text').textContent = q.question;

    // Options List
    const container = document.getElementById('q-options-container');
    container.innerHTML = '';
    const userSelected = this.activeTest.userAnswers[q.id] || [];
    const isPracticeRevealed = this.activeTest.mode === 'practice' && this.activeTest.revealedPractice.has(q.id);

    q.options.forEach(opt => {
      const isSelected = userSelected.includes(opt.key);
      const isCorrect = q.answer.includes(opt.key);

      const card = document.createElement('div');
      let cardClass = "option-card flex items-start space-x-3 p-4 rounded-xl border-2 ";
      let pillClass = "option-pill ";

      if (isPracticeRevealed) {
        cardClass += "locked ";
        if (isCorrect) {
          cardClass += "correct-revealed ";
          pillClass += "bg-emerald-500 text-white";
        } else if (isSelected && !isCorrect) {
          cardClass += "wrong-revealed ";
          pillClass += "bg-rose-500 text-white";
        } else {
          cardClass += "border-slate-200 dark:border-slate-800 opacity-60 ";
          pillClass += "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400";
        }
      } else {
        if (isSelected) {
          cardClass += "border-brand-500 bg-brand-50/60 dark:bg-brand-950/40 text-brand-950 dark:text-brand-100 ";
          pillClass += "bg-brand-600 text-white";
        } else {
          cardClass += "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900 ";
          pillClass += "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300";
        }
      }

      card.className = cardClass;
      card.onclick = () => this.selectOption(opt.key);

      card.innerHTML = `
        <div class="${pillClass}">${opt.key}</div>
        <div class="flex-1 text-sm sm:text-base font-medium leading-relaxed pt-0.5">
          ${opt.text}
        </div>
        ${isPracticeRevealed ? (
          isCorrect ? '<i data-lucide="check" class="w-5 h-5 text-emerald-600 flex-shrink-0"></i>' :
          (isSelected ? '<i data-lucide="x" class="w-5 h-5 text-rose-600 flex-shrink-0"></i>' : '')
        ) : ''}
      `;
      container.appendChild(card);
    });

    // Explanation Box in Practice Mode
    const expBox = document.getElementById('q-explanation-box');
    if (isPracticeRevealed) {
      expBox.classList.remove('hidden');
      document.getElementById('q-explanation-text').textContent = q.explanation || `Correct Answer: Option ${q.answer.join(', ')}`;
      document.getElementById('q-source-text').textContent = `Source: ${q.source || 'NPTEL Course Material'}`;
    } else {
      expBox.classList.add('hidden');
    }

    // Bookmark & Flag buttons state
    const isBookmarked = this.bookmarks.has(q.id);
    const bmBtn = document.getElementById('quiz-bookmark-btn');
    if (isBookmarked) {
      bmBtn.className = "p-2 rounded-lg border border-amber-300 dark:border-amber-800 text-amber-500 bg-amber-50 dark:bg-amber-950/40 transition";
    } else {
      bmBtn.className = "p-2 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-400 hover:text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-950/30 transition";
    }

    const isFlagged = this.activeTest.flagged.has(q.id);
    const flagBtn = document.getElementById('btn-flag-q');
    if (isFlagged) {
      flagBtn.className = "px-3 py-2 rounded-xl border border-amber-400 bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 text-xs font-bold transition flex items-center space-x-1";
    } else {
      flagBtn.className = "px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-amber-50 dark:hover:bg-amber-950/40 hover:text-amber-600 transition flex items-center space-x-1";
    }

    // Prev / Next button state
    document.getElementById('btn-prev-q').disabled = index === 0;
    document.getElementById('btn-prev-q').classList.toggle('opacity-40', index === 0);

    const nextBtn = document.getElementById('btn-next-q');
    if (index === total - 1) {
      nextBtn.innerHTML = `<span>Submit</span> <i data-lucide="check-circle" class="w-4 h-4"></i>`;
    } else {
      nextBtn.innerHTML = `<span>Next</span> <i data-lucide="chevron-right" class="w-4 h-4"></i>`;
    }

    this.renderPalette();
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  selectOption(optKey) {
    if (!this.activeTest) return;
    const q = this.activeTest.questions[this.activeTest.currentIndex];
    let current = this.activeTest.userAnswers[q.id] || [];

    if (q.type === 'MSQ') {
      if (current.includes(optKey)) {
        current = current.filter(k => k !== optKey);
      } else {
        current.push(optKey);
      }
    } else {
      // Single Choice MCQ
      current = [optKey];
    }

    this.activeTest.userAnswers[q.id] = current;

    if (this.activeTest.mode === 'practice') {
      this.activeTest.revealedPractice.add(q.id);
      
      // Check correctness
      const isCorrect = this.isAnswerCorrect(current, q.answer);
      if (!isCorrect) {
        // Add to mistakes vault
        this.addMistake(q);
      } else if (this.mistakes[q.id]) {
        // If answered correctly in practice, remove or decrement
        delete this.mistakes[q.id];
        localStorage.setItem('psych_mistakes', JSON.stringify(this.mistakes));
        this.updateNavBadges();
      }
    }

    this.renderQuestion(this.activeTest.currentIndex);
  }

  clearCurrentResponse() {
    if (!this.activeTest) return;
    const q = this.activeTest.questions[this.activeTest.currentIndex];
    delete this.activeTest.userAnswers[q.id];
    this.activeTest.revealedPractice.delete(q.id);
    this.renderQuestion(this.activeTest.currentIndex);
  }

  toggleCurrentFlag() {
    if (!this.activeTest) return;
    const q = this.activeTest.questions[this.activeTest.currentIndex];
    if (this.activeTest.flagged.has(q.id)) {
      this.activeTest.flagged.delete(q.id);
    } else {
      this.activeTest.flagged.add(q.id);
    }
    this.renderQuestion(this.activeTest.currentIndex);
  }

  toggleCurrentBookmark() {
    if (!this.activeTest) return;
    const q = this.activeTest.questions[this.activeTest.currentIndex];
    this.toggleBookmark(q.id);
    this.renderQuestion(this.activeTest.currentIndex);
  }

  prevQuestion() {
    if (this.activeTest && this.activeTest.currentIndex > 0) {
      this.renderQuestion(this.activeTest.currentIndex - 1);
    }
  }

  nextQuestion() {
    if (!this.activeTest) return;
    if (this.activeTest.currentIndex < this.activeTest.questions.length - 1) {
      this.renderQuestion(this.activeTest.currentIndex + 1);
    } else {
      this.submitTestConfirm();
    }
  }

  // ==========================================
  // QUESTION PALETTE
  // ==========================================
  togglePaletteDrawer() {
    const drawer = document.getElementById('palette-drawer');
    drawer.classList.toggle('hidden');
  }

  renderPalette() {
    if (!this.activeTest) return;
    const grid = document.getElementById('palette-buttons-grid');
    if (!grid) return;

    let html = '';
    let answeredCount = 0;

    this.activeTest.questions.forEach((q, idx) => {
      const isCurrent = idx === this.activeTest.currentIndex;
      const ans = this.activeTest.userAnswers[q.id];
      const isAnswered = ans && ans.length > 0;
      const isFlagged = this.activeTest.flagged.has(q.id);
      const isPracticeRevealed = this.activeTest.mode === 'practice' && this.activeTest.revealedPractice.has(q.id);

      if (isAnswered) answeredCount++;

      let btnClass = "palette-btn ";
      if (isCurrent) btnClass += "current ";

      if (isPracticeRevealed) {
        const correct = this.isAnswerCorrect(ans, q.answer);
        btnClass += correct ? "bg-emerald-500 text-white " : "bg-rose-500 text-white ";
      } else if (isFlagged) {
        btnClass += "bg-amber-500 text-white ";
      } else if (isAnswered) {
        btnClass += "bg-brand-600 text-white ";
      } else {
        btnClass += "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 ";
      }

      html += `
        <button onclick="app.renderQuestion(${idx})" class="${btnClass}" title="Go to Question ${idx + 1}">
          ${idx + 1}
        </button>
      `;
    });

    grid.innerHTML = html;
    document.getElementById('palette-stats-summary').textContent = `${answeredCount} / ${this.activeTest.questions.length} Answered`;
  }

  isAnswerCorrect(userAns, correctAns) {
    if (!userAns || !correctAns || userAns.length !== correctAns.length) return false;
    const sortedUser = [...userAns].sort();
    const sortedCorrect = [...correctAns].sort();
    return sortedUser.every((val, index) => val === sortedCorrect[index]);
  }

  // ==========================================
  // TEST SUBMISSION & SCORECARD EVALUATION
  // ==========================================
  submitTestConfirm() {
    const total = this.activeTest.questions.length;
    const answered = Object.keys(this.activeTest.userAnswers).length;
    const summaryText = document.getElementById('modal-submit-summary-text');
    summaryText.textContent = `You have answered ${answered} of ${total} questions. Are you ready to submit and calculate your detailed results scorecard?`;
    document.getElementById('modal-submit').classList.remove('hidden');
    if (window.lucide) window.lucide.createIcons();
  }

  closeSubmitModal() {
    document.getElementById('modal-submit').classList.add('hidden');
  }

  confirmQuitTest() {
    if (confirm("Are you sure you want to exit the current test? Your progress will be saved in history.")) {
      clearInterval(this.timerInterval);
      this.showView('builder');
    }
  }

  finalizeTestSubmission() {
    this.closeSubmitModal();
    clearInterval(this.timerInterval);

    const questions = this.activeTest.questions;
    let correct = 0;
    let wrong = 0;
    let skipped = 0;

    const weekScores = {}; // weekNum -> { correct, total }

    questions.forEach(q => {
      if (!weekScores[q.week]) {
        weekScores[q.week] = { correct: 0, total: 0 };
      }
      weekScores[q.week].total++;

      const userAns = this.activeTest.userAnswers[q.id];
      if (!userAns || userAns.length === 0) {
        skipped++;
      } else {
        const isRight = this.isAnswerCorrect(userAns, q.answer);
        if (isRight) {
          correct++;
          weekScores[q.week].correct++;
          // remove from mistakes vault if mastered
          if (this.mistakes[q.id]) {
            delete this.mistakes[q.id];
          }
        } else {
          wrong++;
          this.addMistake(q);
        }
      }
    });

    localStorage.setItem('psych_mistakes', JSON.stringify(this.mistakes));
    this.updateNavBadges();

    const total = questions.length;
    const percentage = Math.round((correct / total) * 100);

    // Save history
    this.history.unshift({
      date: new Date().toISOString(),
      score: correct,
      total: total,
      percentage: percentage,
      mode: this.activeTest.mode,
      timeSpent: this.activeTest.elapsedSeconds
    });
    localStorage.setItem('psych_history', JSON.stringify(this.history.slice(0, 30)));

    // Render Results View
    this.renderScorecard({
      correct,
      wrong,
      skipped,
      total,
      percentage,
      weekScores,
      timeSpent: this.activeTest.elapsedSeconds
    });

    this.showView('results');

    // Confetti on good score
    if (percentage >= 70 && window.confetti) {
      window.confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 }
      });
    }
  }

  renderScorecard(data) {
    document.getElementById('score-percentage-text').textContent = `${data.percentage}%`;
    document.getElementById('stat-correct-count').textContent = data.correct;
    document.getElementById('stat-wrong-count').textContent = data.wrong;
    document.getElementById('stat-unanswered-count').textContent = data.skipped;
    
    const mins = Math.floor(data.timeSpent / 60);
    const secs = data.timeSpent % 60;
    document.getElementById('stat-time-spent').textContent = `${mins}m ${secs}s`;

    // Circular gauge animation
    const circle = document.getElementById('score-circle-path');
    setTimeout(() => {
      circle.setAttribute('stroke-dasharray', `${data.percentage}, 100`);
    }, 150);

    // Grade and Title Verdict
    const gradeBadge = document.getElementById('score-grade-badge');
    const titleEl = document.getElementById('score-verdict-title');
    const subEl = document.getElementById('score-verdict-subtitle');

    if (data.percentage >= 90) {
      gradeBadge.textContent = "Elite Distinction";
      gradeBadge.className = "px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300";
      titleEl.textContent = "Mastery Level Reached!";
      subEl.textContent = "Exceptional performance across the tested concepts.";
    } else if (data.percentage >= 75) {
      gradeBadge.textContent = "First Class Pass";
      gradeBadge.className = "px-3 py-1 rounded-full text-xs font-extrabold bg-brand-100 text-brand-800 dark:bg-brand-950 dark:text-brand-300";
      titleEl.textContent = "Strong Understanding!";
      subEl.textContent = "You're well prepared for the NPTEL assignment problems.";
    } else if (data.percentage >= 50) {
      gradeBadge.textContent = "Passing Mark";
      gradeBadge.className = "px-3 py-1 rounded-full text-xs font-extrabold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300";
      titleEl.textContent = "Good Effort!";
      subEl.textContent = "Review the missed concepts below to boost your score.";
    } else {
      gradeBadge.textContent = "Needs Revision";
      gradeBadge.className = "px-3 py-1 rounded-full text-xs font-extrabold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300";
      titleEl.textContent = "More Practice Needed";
      subEl.textContent = "Take time to review the lecture slide references for these weeks.";
    }

    // Retry Missed button count
    const missedCount = data.wrong + data.skipped;
    document.getElementById('retry-missed-count').textContent = missedCount;
    document.getElementById('btn-retry-missed').disabled = missedCount === 0;
    document.getElementById('btn-retry-missed').classList.toggle('opacity-50', missedCount === 0);

    // Week Breakdown
    const weekContainer = document.getElementById('results-week-breakdown');
    let weekHtml = '';
    for (const [wStr, s] of Object.entries(data.weekScores)) {
      const w = parseInt(wStr);
      const topInfo = this.topics[w] || { title: `Week ${w}` };
      const wPct = Math.round((s.correct / s.total) * 100);
      const isWeak = wPct < 60;

      weekHtml += `
        <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-extrabold text-slate-800 dark:text-slate-200">
              ${w === 0 ? 'Intro (Week 0)' : `Week ${w}`}: ${topInfo.title}
            </span>
            <span class="font-bold ${isWeak ? 'text-rose-500' : 'text-emerald-600'}">${s.correct}/${s.total} (${wPct}%)</span>
          </div>
          <div class="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
            <div class="${isWeak ? 'bg-rose-500' : 'bg-emerald-500'} h-2 rounded-full" style="width: ${wPct}%"></div>
          </div>
        </div>
      `;
    }
    weekContainer.innerHTML = weekHtml;

    // Counts for review filter tabs
    document.getElementById('rf-count-all').textContent = data.total;
    document.getElementById('rf-count-wrong').textContent = data.wrong;
    document.getElementById('rf-count-correct').textContent = data.correct;
    document.getElementById('rf-count-skipped').textContent = data.skipped;

    this.setReviewFilter('all');
  }

  setReviewFilter(filter) {
    this.reviewFilter = filter;
    document.querySelectorAll('.rf-btn').forEach(btn => {
      const isThis = btn.id === `rf-${filter}`;
      if (isThis) {
        btn.className = "rf-btn px-3 py-1.5 rounded-lg bg-brand-50 text-brand-700 dark:bg-brand-950/80 dark:text-brand-300 font-bold border border-brand-200 dark:border-brand-800";
      } else {
        btn.className = "rf-btn px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-semibold";
      }
    });

    this.renderReviewList();
  }

  renderReviewList() {
    if (!this.activeTest) return;
    const container = document.getElementById('results-review-list');
    const questions = this.activeTest.questions;

    let filtered = questions.filter(q => {
      const userAns = this.activeTest.userAnswers[q.id];
      const isAnswered = userAns && userAns.length > 0;
      const isRight = isAnswered && this.isAnswerCorrect(userAns, q.answer);

      if (this.reviewFilter === 'wrong') return isAnswered && !isRight;
      if (this.reviewFilter === 'correct') return isRight;
      if (this.reviewFilter === 'skipped') return !isAnswered;
      return true;
    });

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="text-center py-8 text-slate-400 text-sm">
          No questions match the "${this.reviewFilter}" filter.
        </div>
      `;
      return;
    }

    let html = '';
    filtered.forEach((q, idx) => {
      const userAns = this.activeTest.userAnswers[q.id] || [];
      const isAnswered = userAns.length > 0;
      const isRight = isAnswered && this.isAnswerCorrect(userAns, q.answer);
      const isBookmarked = this.bookmarks.has(q.id);

      html += `
        <div class="p-5 rounded-2xl border ${isRight ? 'border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/20 dark:bg-emerald-950/10' : (!isAnswered ? 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900' : 'border-rose-200 dark:border-rose-900/40 bg-rose-50/20 dark:bg-rose-950/10')} space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center space-x-2">
              <span class="px-2.5 py-1 rounded-md text-xs font-bold ${isRight ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' : (!isAnswered ? 'bg-slate-100 text-slate-700 dark:bg-slate-800' : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300')}">
                ${isRight ? '✓ Correct' : (!isAnswered ? '○ Skipped' : '✕ Incorrect')}
              </span>
              <span class="text-xs font-bold text-slate-500">${q.year} PYQ • ${q.week === 0 ? 'Intro' : `Week ${q.week}`}</span>
            </div>
            <button onclick="app.toggleBookmark('${q.id}'); app.renderReviewList();" class="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 ${isBookmarked ? 'text-amber-500 bg-amber-50 dark:bg-amber-950' : 'text-slate-400 hover:text-amber-500'}">
              <i data-lucide="bookmark" class="w-4 h-4"></i>
            </button>
          </div>

          <div class="font-bold text-slate-900 dark:text-slate-100 text-sm sm:text-base leading-relaxed">
            ${q.question}
          </div>

          <div class="space-y-2 pt-1">
            ${q.options.map(opt => {
              const isUserChoice = userAns.includes(opt.key);
              const isCorrectChoice = q.answer.includes(opt.key);
              let optStyle = "p-3 rounded-xl border text-xs sm:text-sm flex items-start space-x-2.5 ";

              if (isCorrectChoice) {
                optStyle += "border-emerald-500 bg-emerald-50 dark:bg-emerald-950/50 text-emerald-900 dark:text-emerald-200 font-semibold";
              } else if (isUserChoice && !isCorrectChoice) {
                optStyle += "border-rose-500 bg-rose-50 dark:bg-rose-950/50 text-rose-900 dark:text-rose-200 line-through opacity-80";
              } else {
                optStyle += "border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-900/60 text-slate-600 dark:text-slate-400";
              }

              return `
                <div class="${optStyle}">
                  <span class="font-bold uppercase w-5 text-center">${opt.key}.</span>
                  <span class="flex-1">${opt.text}</span>
                  ${isCorrectChoice ? '<span class="text-emerald-600 font-extrabold text-xs">✓ Correct</span>' : ''}
                  ${isUserChoice && !isCorrectChoice ? '<span class="text-rose-600 font-extrabold text-xs">Your Choice</span>' : ''}
                </div>
              `;
            }).join('')}
          </div>

          <!-- Explanation box -->
          <div class="p-3.5 rounded-xl bg-slate-100/80 dark:bg-slate-800/80 text-xs space-y-1">
            <span class="font-extrabold text-brand-600 dark:text-brand-400 block">Lecture Slide Reference & Solution:</span>
            <p class="text-slate-700 dark:text-slate-300 leading-relaxed">${q.explanation || `Correct Answer: Option ${q.answer.join(', ')}`}</p>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();
  }

  retryMissedQuestions() {
    if (!this.activeTest) return;
    const missed = this.activeTest.questions.filter(q => {
      const userAns = this.activeTest.userAnswers[q.id];
      return !userAns || !this.isAnswerCorrect(userAns, q.answer);
    });

    if (missed.length === 0) {
      alert("You answered all questions correctly! Great job!");
      return;
    }

    this.startTest(missed);
  }

  retakeSameTest() {
    if (!this.activeTest) return;
    this.startTest(this.activeTest.questions);
  }

  // ==========================================
  // EXPLORER VIEW (QUESTION SEARCH BANK)
  // ==========================================
  populateExplorerWeeks() {
    const sel = document.getElementById('explorer-week-select');
    if (!sel) return;
    let html = '<option value="all">All Weeks (0 to 12)</option>';
    for (let w = 0; w <= 12; w++) {
      const topInfo = this.topics[w] || { title: `Week ${w}` };
      html += `<option value="${w}">${w === 0 ? 'Intro (Week 0)' : `Week ${w}`}: ${topInfo.title}</option>`;
    }
    sel.innerHTML = html;
  }

  filterExplorer() {
    const query = (document.getElementById('explorer-search-input')?.value || '').toLowerCase().trim();
    const year = document.getElementById('explorer-year-select')?.value || 'all';
    const week = document.getElementById('explorer-week-select')?.value || 'all';

    let matches = this.questions.filter(q => {
      if (year !== 'all' && q.year !== year) return false;
      if (week !== 'all' && String(q.week) !== week) return false;
      if (query) {
        const words = query.split(/\s+/).filter(Boolean);
        const fullText = (q.question + ' ' + q.options.map(o => o.text).join(' ') + ' ' + (q.explanation || '')).toLowerCase();
        return words.every(w => fullText.includes(w));
      }
      return true;
    });

    document.getElementById('explorer-match-count').textContent = matches.length;
    const container = document.getElementById('explorer-cards-list');
    if (!container) return;

    if (matches.length === 0) {
      container.innerHTML = `
        <div class="text-center py-12 text-slate-400 text-sm">
          No questions matched your search criteria.
        </div>
      `;
      return;
    }

    // Limit display to 50 for performance
    const displayList = matches.slice(0, 50);

    let html = '';
    displayList.forEach(q => {
      const isBookmarked = this.bookmarks.has(q.id);
      html += `
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center space-x-2">
              <span class="px-2.5 py-1 rounded-md text-xs font-bold bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300">
                ${q.year} • ${q.week === 0 ? 'Intro' : `Week ${q.week}`}
              </span>
              <span class="text-xs text-slate-500 font-semibold">${q.type}</span>
            </div>
            <button onclick="app.toggleBookmark('${q.id}'); app.filterExplorer();" class="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 ${isBookmarked ? 'text-amber-500 bg-amber-50 dark:bg-amber-950' : 'text-slate-400 hover:text-amber-500'}">
              <i data-lucide="bookmark" class="w-4 h-4"></i>
            </button>
          </div>

          <div class="font-bold text-slate-900 dark:text-slate-100 text-sm sm:text-base leading-relaxed">
            ${q.question}
          </div>

          <div class="space-y-2">
            ${q.options.map(opt => `
              <div class="p-2.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 text-xs sm:text-sm flex items-start space-x-2">
                <span class="font-bold uppercase w-5">${opt.key}.</span>
                <span class="flex-1">${opt.text}</span>
              </div>
            `).join('')}
          </div>

          <!-- Collapsible Answer Detail -->
          <details class="cursor-pointer group pt-1">
            <summary class="text-xs font-bold text-brand-600 dark:text-brand-400 hover:underline select-none">
              Reveal Correct Answer & Lecture Reference
            </summary>
            <div class="mt-2 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
              <div class="font-bold text-emerald-600 dark:text-emerald-400">Answer: Option ${q.answer.join(', ')}</div>
              <div class="text-slate-600 dark:text-slate-300">${q.explanation || 'See NPTEL Lecture Slides for reference.'}</div>
            </div>
          </details>
        </div>
      `;
    });

    if (matches.length > 50) {
      html += `
        <div class="text-center py-4 text-xs font-semibold text-slate-500">
          Showing first 50 of ${matches.length} matches. Type in search to narrow down results.
        </div>
      `;
    }

    container.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();
  }

  // ==========================================
  // FLASHCARD RECALL MODE
  // ==========================================
  initFlashcards() {
    this.fcQuestions = this.shuffleArray([...this.getMatchingPool()]);
    this.fcIndex = 0;
    this.fcFlipped = false;
    this.renderFlashcard();
  }

  renderFlashcard() {
    const total = this.fcQuestions.length;
    if (total === 0) {
      document.getElementById('fc-progress-text').textContent = `Card 0 of 0`;
      document.getElementById('fc-category-badge').textContent = `None`;
      document.getElementById('fc-question-text').textContent = 'No questions match your current year and week selection. Please select at least one week in the Test Builder.';
      document.getElementById('fc-answer-text').textContent = 'N/A';
      document.getElementById('fc-explanation-text').textContent = '';
      return;
    }
    const q = this.fcQuestions[this.fcIndex];

    document.getElementById('fc-progress-text').textContent = `Card ${this.fcIndex + 1} of ${total}`;
    document.getElementById('fc-category-badge').textContent = `${q.year} • ${q.week === 0 ? 'Intro' : `Week ${q.week}`}`;
    document.getElementById('fc-question-text').textContent = q.question;

    // Build answer text
    const answerOpts = q.options.filter(o => q.answer.includes(o.key));
    const ansText = answerOpts.map(o => `Option ${o.key}: ${o.text}`).join(' / ');
    document.getElementById('fc-answer-text').textContent = ansText;
    document.getElementById('fc-explanation-text').textContent = q.explanation || 'Refer to NPTEL course slide notes.';

    // Reset flip
    const inner = document.getElementById('flashcard-inner');
    inner.classList.remove('rotate-y-180');
    this.fcFlipped = false;
  }

  flipFlashcard() {
    const inner = document.getElementById('flashcard-inner');
    inner.classList.toggle('rotate-y-180');
    this.fcFlipped = !this.fcFlipped;
  }

  nextFlashcard() {
    if (this.fcQuestions.length === 0) return;
    this.fcIndex = (this.fcIndex + 1) % this.fcQuestions.length;
    this.renderFlashcard();
  }

  prevFlashcard() {
    if (this.fcQuestions.length === 0) return;
    this.fcIndex = (this.fcIndex - 1 + this.fcQuestions.length) % this.fcQuestions.length;
    this.renderFlashcard();
  }

  // ==========================================
  // MISTAKE VAULT & BOOKMARKS
  // ==========================================
  addMistake(question) {
    if (!this.mistakes[question.id]) {
      this.mistakes[question.id] = {
        question: question,
        count: 1,
        addedAt: Date.now()
      };
    } else {
      this.mistakes[question.id].count++;
    }
    localStorage.setItem('psych_mistakes', JSON.stringify(this.mistakes));
    this.updateNavBadges();
  }

  renderMistakesView() {
    const keys = Object.keys(this.mistakes);
    document.getElementById('vault-mistakes-count').textContent = keys.length;
    const btn = document.getElementById('btn-practice-all-mistakes');
    btn.disabled = keys.length === 0;
    btn.classList.toggle('opacity-50', keys.length === 0);

    const container = document.getElementById('mistakes-cards-list');
    if (keys.length === 0) {
      container.innerHTML = `
        <div class="text-center py-12 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 text-slate-400">
          <i data-lucide="check-circle" class="w-8 h-8 mx-auto mb-2 text-emerald-500"></i>
          <p class="font-bold">No recorded mistakes!</p>
          <p class="text-xs mt-1">Questions you answer incorrectly will automatically gather here for focused revision.</p>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    let html = '';
    keys.forEach(k => {
      const item = this.mistakes[k];
      const q = item.question;
      html += `
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-rose-100 dark:border-rose-900/40 shadow-sm space-y-3">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-rose-600 bg-rose-50 dark:bg-rose-950 px-2.5 py-1 rounded-md">
              Missed ${item.count} ${item.count === 1 ? 'time' : 'times'}
            </span>
            <span class="text-slate-500">${q.year} • Week ${q.week}</span>
          </div>
          <div class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">${q.question}</div>
          <div class="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
            Correct Answer: ${q.answer.join(', ')}
          </div>
          <div class="text-xs text-slate-500">${q.explanation || ''}</div>
        </div>
      `;
    });
    container.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();
  }

  practiceMistakes() {
    const list = Object.values(this.mistakes).map(m => m.question);
    if (list.length === 0) return;
    this.startTest(list);
  }

  clearMistakesVault() {
    if (confirm("Are you sure you want to clear all questions from your Mistakes Vault?")) {
      this.mistakes = {};
      localStorage.removeItem('psych_mistakes');
      this.updateNavBadges();
      this.renderMistakesView();
    }
  }

  toggleBookmark(qId) {
    if (this.bookmarks.has(qId)) {
      this.bookmarks.delete(qId);
    } else {
      this.bookmarks.add(qId);
    }
    localStorage.setItem('psych_bookmarks', JSON.stringify([...this.bookmarks]));
    this.updateNavBadges();
  }

  renderBookmarksView() {
    const bArray = [...this.bookmarks];
    document.getElementById('vault-bookmarks-count').textContent = bArray.length;
    const btn = document.getElementById('btn-practice-bookmarks');
    btn.disabled = bArray.length === 0;
    btn.classList.toggle('opacity-50', bArray.length === 0);

    const container = document.getElementById('bookmarks-cards-list');
    if (bArray.length === 0) {
      container.innerHTML = `
        <div class="text-center py-12 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 text-slate-400">
          <i data-lucide="bookmark" class="w-8 h-8 mx-auto mb-2 text-amber-500"></i>
          <p class="font-bold">No bookmarked questions yet!</p>
          <p class="text-xs mt-1">Click the bookmark icon on any question to save it here for targeted revision.</p>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    const bookmarkedQs = this.questions.filter(q => this.bookmarks.has(q.id));
    let html = '';
    bookmarkedQs.forEach(q => {
      html += `
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-amber-100 dark:border-amber-900/40 shadow-sm space-y-3">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-amber-600 bg-amber-50 dark:bg-amber-950 px-2.5 py-1 rounded-md">
              Starred Question
            </span>
            <div class="flex items-center space-x-2">
              <span class="text-slate-500">${q.year} • Week ${q.week}</span>
              <button onclick="app.toggleBookmark('${q.id}'); app.renderBookmarksView();" class="text-rose-500 hover:text-rose-700 text-xs font-semibold">Remove</button>
            </div>
          </div>
          <div class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">${q.question}</div>
          <div class="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
            Correct Answer: ${q.answer.join(', ')}
          </div>
          <div class="text-xs text-slate-500">${q.explanation || ''}</div>
        </div>
      `;
    });
    container.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();
  }

  practiceBookmarks() {
    const list = this.questions.filter(q => this.bookmarks.has(q.id));
    if (list.length === 0) return;
    this.startTest(list);
  }

  clearBookmarksVault() {
    if (confirm("Are you sure you want to clear all bookmarked questions?")) {
      this.bookmarks.clear();
      localStorage.removeItem('psych_bookmarks');
      this.updateNavBadges();
      this.renderBookmarksView();
    }
  }

  initKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      // Don't trigger shortcuts if user is typing in an input, textarea or select
      const tag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
      if (tag === 'input' || tag === 'textarea' || tag === 'select') return;

      const currentView = this.currentView;

      if (currentView === 'quiz' && this.activeTest) {
        const q = this.activeTest.questions[this.activeTest.currentIndex];
        if (!q) return;

        // Keys 1-5 or A-E to select option
        const key = e.key.toUpperCase();
        const digitIndex = parseInt(e.key, 10) - 1;
        
        let matchingOpt = null;
        if (['A', 'B', 'C', 'D', 'E'].includes(key)) {
          matchingOpt = q.options.find(o => o.key === key);
        } else if (!isNaN(digitIndex) && digitIndex >= 0 && digitIndex < q.options.length) {
          matchingOpt = q.options[digitIndex];
        }

        if (matchingOpt) {
          e.preventDefault();
          this.selectOption(matchingOpt.key);
          return;
        }

        if (e.key === 'ArrowRight') {
          e.preventDefault();
          this.nextQuestion();
        } else if (e.key === 'ArrowLeft') {
          e.preventDefault();
          this.prevQuestion();
        } else if (e.key.toLowerCase() === 'f') {
          e.preventDefault();
          this.toggleCurrentFlag();
        }
      } else if (currentView === 'flashcards') {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          this.flipFlashcard();
        } else if (e.key === 'ArrowRight') {
          e.preventDefault();
          this.nextFlashcard();
        } else if (e.key === 'ArrowLeft') {
          e.preventDefault();
          this.prevFlashcard();
        }
      }
    });
  }
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  window.app = new QuizApp();
  window.app.init();
});
