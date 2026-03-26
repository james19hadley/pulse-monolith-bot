# Sprint 18: UI Architecture & Project Progress Unification

**Status:** `Active`
**Date Proposed:** March 26, 2026
**Objective:** Complete the UI refactoring by standardizing all magic strings via a Central Registry (`texts.py`), and redesign the database models for Projects to accurately track generic units (e.g., hours, pages) alongside elapsed session time (for the Void engine).

## 🎯 Goals
1. **UI Standardization:** Integrate `src/bot/texts.py` across all keyboards and handlers to solve routing bugs with "📥 Inbox" and inline buttons.
2. **Unified Project Models:** Rename `target_minutes` to `target_value` and `total_minutes_spent` to `current_value`, adding a `unit` string (default "minutes").
3. **Double-entry Tracking:** Expand logging so we track both `duration_minutes` (for the Session/Void) and `progress_amount` / `progress_unit` (for the specific Project).
4. **Visual Reporting:** Update the Evening Report to aggregate and visually render Project progress (e.g., progress bars based on unit types).

## 📋 Tasks
### Base & UI Refactor
- [ ] Apply `texts.py` cleanly to `keyboards.py` and `handlers/`.
- [ ] Resolve Aiogram text matching overlapping with AI freeform router.

### Database Schema Evolution
- [x] Alter `Project` table: replace minute fields with `target_value`, `current_value`, and `unit`.
- [x] Alter `TimeLog` table: add `progress_amount` and `progress_unit`.
- [x] Implement DB schema changes and ensure backwards compatibility with old records if any.

### Logic & Prompts
- [ ] Update AI functions/Tools to extract both time spent AND progress magnitude from natural language ("I read 50 pages taking 1 hour").
- [ ] Adjust `/projects` list view to render hours if `unit == "minutes"`, otherwise display raw units (e.g., "50/300 pages").
- [ ] Update Evening Report compiler to tally new progress attributes and draw progress bars.

## 🔒 Security & Architecture Notes
- Maintain absolute protection of the Session `duration_minutes`. Changing a project's "pages" should not corrupt the total time tracked for the day's calculation of "The Void". The "Void" math relies ONLY on time.

## 🏁 Completion Criteria
- All UI buttons invoke accurate responses without fallback "Void" processing.
- The user can create a project with unit "pages" or "tasks", log progress naturally via text, and verify that the `/projects` list reflects the accurate unit string and progress bar.
