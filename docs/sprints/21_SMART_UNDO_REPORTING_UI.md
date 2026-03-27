# Sprint 21: Smart Undo & Reporting Redesign

**Status:** `Completed`
**Date Proposed:** March 26, 2026
**Objective:** Replace the localized inline button undo with a centralized ActionLog-based Smart Undo system, fix UI state bugs, and redesign the daily accountability report for a cleaner aesthetic.

## 🎯 Goals
1. Implement a single global `/undo` and text `↩️ Undo` function via `ActionLog` DB table.
2. Remove cluttered inline undo buttons from project/habit intents.
3. Fix AI comment HTML formatting bug causing parsing errors in Telegram.
4. Overhaul the Daily Report UI structure to make it more compact and informative (replace dashes with modern indents, etc.).
5. Restore missing callback handlers (`ui_entities_menu` and "typing" status in `/test_report`).
6. Fix cron boundary bug that led to empty reports immediately after midnight.

## 📋 Tasks
### Architecture & Core
- [x] Create `ActionLog` table in `src/db/models.py`.
- [x] Update `cmd_undo` in `src/bot/handlers/core.py` to revert state globally.
- [x] Remove inline keyboard append logic for undo in entity and tracker handlers.

### UI & UX Polish
- [x] Restore `cb_entities_menu` to handle the "Back" button correctly in project submenus.
- [x] Fix `html.escape` issue for strings returned by AI comment generation in `src/bot/views.py`.
- [x] Redesign `build_daily_report` visually formatting (change "Deep Work" to "Focus", use `└` for indent).
- [x] Inject `send_chat_action("typing")` into `cq_test_report`.

### Scheduler
- [x] Adjust `start_bound` and `end_bound` in `generate_daily_report_text` so that trailing midnight jobs grab the previous 24 hours properly, preventing zero-data gaps.

## 🔒 Security & Architecture Notes
- Only escape raw database strings (Project names, Habit titles). Do NOT strictly escape LLM responses that return deliberate bold/italic syntax (like `<b>`), simply avoid Markdown markdown (`**`) by explicit prompting.

## 🏁 Completion Criteria
- `/undo` reverts any tracked value accurately without inline buttons.
- Test Reports format nicely without `parse_mode` errors.
- Cron reports fire correctly with all accumulated context for the day.
