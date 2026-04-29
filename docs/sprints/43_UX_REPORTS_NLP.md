# Sprint 43: UX, Daily Reports, & NLP Enhancements

**Status:** `Active`
**Date Proposed:** 2026-04-29
**Objective:** Polish the core user experience by improving daily report readability, ensuring proper NLP behavior for "done", implementing smart UI for immediate intention feedback (Undo buttons), and adding context memory for the LLM.

## 🎯 Goals
- Make the daily report mathematically strict on parent vs self time.
- Visually protect the mobile Telegram layout by putting progress bars on new lines.
- Fix the "done" regression caused by the Habits -> Projects migration.
- Empower the AI with persistent user context (lunch times, preferences) directly in prompts.
- Ensure only today's inbox items are counted in the evening report.

## 📋 Tasks

### 1. Daily Report Formatting (Completed ✅)
- [x] Restructure parent project time representation to `(Total: Xh Ym)`.
- [x] Push progress bars to a new line with an indent to prevent mobile text-wrapping bugs.

### 2. Inbox Temporal Isolation
- [ ] Update `generate_daily_report_text` to count only `Inbox` items created on the *current day* (post last cutoff).

### 3. Transparent Undo UI
- [ ] When an action is performed, reply with what was explicitly done (e.g. "⏪ Action performed: Moved project A to B").
- [ ] Attach inline buttons to the confirmation message: `✅` and `❌`.
- [ ] Pressing `✅` removes the buttons and solidifies the message.
- [ ] Pressing `❌` invokes the `UNDO` logic, reversing the changes and updating the message to state it was cancelled.

### 4. NLP Fixes ("Done" Regression)
- [ ] Update the `LOG_WORK` system prompt to recognize "done", "finished", "сделал" when applied to projects with `daily_target_value`.
- [ ] Teach the extractor to calculate the remaining amount to reach the daily target and submit it as the logged amount.

### 5. Session Context Prompts
- [ ] Modify `cmd_start_session` or the `SESSION_CONTROL` logic to ask "Над чем работаем?" with inline options representing active projects.

### 6. AI Prompt Memory (Context Injection)
- [ ] Add a `context_memory` string field to the `User` model.
- [ ] Inject this field into the `LOG_WORK`, `ADD_TASKS`, and `SESSION_CONTROL` extraction prompts so the AI inherently knows user schedules (e.g., "Lunch is at 13:00").

## 🔒 Security & Architecture Notes
- The Undo implementation should use the existing `ActionLog` table. Ensure `ActionLog` serializes changes bidirectionally for clean rollbacks.

## 🏁 Completion Criteria
- User can say "typing done" and it logs the exact remaining target minutes.
- The Undo button explicitly tells the user what happened and gives clear emoji-only buttons for feedback.
- Inbox daily counts are accurate.
