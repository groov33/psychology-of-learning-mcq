# NPTEL Psychology of Learning - MCQ Mastery Platform

A comprehensive, responsive web application for practicing and testing multiple-choice questions from **NPTEL's "Psychology of Learning"** course (IIT Kharagpur).

Built from the official assignment PDFs in the `Extras/` folder:
- **2026 (Current Course Run)**: All 12 Weekly Assignments (120 Questions)
- **2025 PYQs**: Weeks 1 to 11 Assignments (110 Questions)
- **2024 PYQs**: Weeks 0 to 11 Assignments (119 Questions)
- **2023 PYQs**: Weeks 0 to 12 Assignments (129 Questions)
- **Total**: **478 Questions** with 100% verified answers and lecture slide references!

---

## 🚀 How to Run the Website

### Option 1: One-Click Windows Launch (Recommended)
Double-click **`start.bat`** in this folder, or run:
```powershell
python server.py
```
This automatically starts a local server at `http://localhost:8080` and opens your browser.

### Option 2: Direct Offline Launch (Zero Server Required)
Simply double-click **`index.html`** in any modern web browser (Chrome, Edge, Firefox, Safari). The app is 100% client-side with all question data embedded in `data/questions-data.js`.

---

## ✨ Key Features & Testing Variations

### 1. Flexible Combinations & Custom Testing
- **Any Year Combination**: Test only the current 2026 run, only previous year questions (2023–2025), or mix and match any combination of years.
- **Any Week Combination**: Select individual weeks (0 to 12) or use one-click presets:
  - *Weeks 0–4: Foundations & Cognition*
  - *Weeks 5–8: Motivation, Emotion & Experiential Learning*
  - *Weeks 9–12: E-Learning, Assessment & Sustainable Development*
- **Custom Question Count**: Choose 10, 20, 30, 50, 100, or all matching questions.
- **Randomization**: Toggle question shuffling and option shuffling.

### 2. Modes of Testing
- **⚡ Practice Mode (Instant Feedback)**:
  - Immediate green/red highlight upon selecting an answer.
  - Reveals the exact NPTEL lecture slide reference and solution.
  - Automatically sends missed questions to the **Mistakes Vault**.
- **🏆 Exam Simulation (Timed Test)**:
  - Full exam environment with countdown timer (15, 30, 45, 60 minutes or untimed).
  - Interactive **Question Palette** showing answered, unanswered, and flagged questions.
  - Detailed scorecard, accuracy rating, and grade generated upon submit.
- **🃏 Concept Flashcards**:
  - 3D card-flip mode for active recall of key concepts and answers before exams.

### 3. Comprehensive Analytics & Scorecard
- **Visual Score Gauge & Performance Grade** (Elite Distinction, First Class, Pass).
- **Unit-by-Unit Mastery Breakdown**: Progress bars revealing strong weeks vs weak areas.
- **Retry Missed Questions**: One-click button to immediately practice only the questions you got wrong.
- **Full Review Filter**: Filter results by *All*, *Incorrect Only*, *Correct Only*, or *Skipped*.

### 4. Searchable Question Bank Explorer
- Live search across all 478 questions by concept or psychologist (e.g., *Pavlov, Skinner, Bloom, Maslow, Goleman, Bandura, Kolb*).
- Filter by week or year with expandable solutions.

### 5. Smart Persistence
- **Mistakes Vault**: Keeps track of questions you answered incorrectly across sessions.
- **Bookmarks**: Star tricky questions during practice for later review.
- **Dark Mode / Light Mode**: Seamless theme toggle saved to local storage.

---

## 📁 Project Structure

```
├── index.html            # Main web application interface
├── styles.css            # Custom CSS & animations
├── app.js                # Quiz logic, scorecard engine & state management
├── server.py             # Lightweight local HTTP server
├── start.bat             # One-click Windows launcher
├── build_dataset.py      # Master dataset builder from PDF sources
├── verify_dataset.py     # Integrity validation script (0 errors across 478 Qs)
├── data/
│   ├── questions.json    # Clean JSON questions database
│   ├── questions-data.js # Standalone JS question bank
│   ├── topics.js         # Week titles, concepts & syllabus metadata
│   └── summary.json      # Dataset statistics summary
├── scripts/              # Parsers for each year's PDFs
└── Extras/               # Original NPTEL assignment PDFs
```
