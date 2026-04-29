# Sprint 43: NLP Polishing, Reporting & Undo UX

**Status:** `Completed`
**Date Proposed:** 2026-04-29
**Objective:** Focuses on improving daily interaction friction points, including formatting Daily Reports, handling NLP habit completions correctly, transparent Undo mechanics, and context-aware focus sessions.

## 🎯 Goals
- Improve visual UX on mobile by properly indenting parent "Total" times and progress bars.
- Fix NLP intent routing for habit completion (e.g. "typing done").
- Add precise UI feedback for the Undo feature (✅ / ❌ emojis).
- Add "Current Focus" questioning at the beginning of a timer session.
- Track Daily Inbox counts correctly without including stale entries in the daily report.

## 📋 Tasks

### [Daily Reporting & UI]
- [x] Change parent project aggregations to display `Total: Xh Ym` and keep self-logged time explicit.
- [x] Unbreak mobile progress bars by rendering them on a fresh indented line.
- [x] Add `🔥 Streak: N` display to the Evening Report next to completed targets.
- [x] Make Inbox count in the Daily Report *strictly* show only items captured today.

### [NLP & Intent Resolution]
- [x] Inject Project Units and Targets into `active_projects_text`.
- [x] Update `extract_log_work` prompt so that if a user says "done", the AI uses the remaining daily target to log the correct duration automatically.
- [x] Audit `EDIT_ENTITIES` vs `LOG_WORK` to ensure "I did my planch" goes to time logging instead of task toggling.

### [Undo Transparency]
- [x] Modify `intent_undo.py` to fetch exactly what action was undone.
- [x] Reply with context (e.g., "⏪ Отменено: Изменение проекта X") and provide inline `✅` and `❌` emoji buttons for feedback.

### [Session Context]
- [x] When starting a session via `/session`, send a prompt asking "Над чем работаем?" with inline buttons for the top active projects.
- [x] Associate the initiated session with the selected project before the timer ends.

## 🔒 Security & Architecture Notes
- The Undo prompt UI must remain mostly emoji-based or strictly minimal to support future i18n properly.
- All modifications to AI prompts (`src/core/prompts.py` or Extraction params) must preserve the existing JSON Schema validation.

## 🏁 Completion Criteria
- User can say "typing done" and 10 minutes are properly logged.
- The Daily Report cleanly lays out projects, correctly counts Streaks, and only counts today's Inbox entries.
- The Undo action returns a context-aware inline string with emoji buttons.
