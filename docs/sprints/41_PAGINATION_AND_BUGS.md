# Sprint 41: Pagination, Bug Fixes & Timezone Accuracy

**Status:** `Active`
**Date Proposed:** 2026-04-25
**Objective:** Resolve critical UX bugs including pagination for long project lists, timezone conversion logic, daily targets applying to archived projects, and the undo engine breaking on state rollback.

## 🎯 Goals
- Add pagination (Next/Prev) to the `/projects` list menu so all projects are viewable.
- Fix timezone handling so Daily Reports trigger exactly at the user's localized cutoff time (e.g., 23:00 Berlin).
- Ensure daily targets and streaks only apply to `status="active"` projects, ignoring archived/completed ones.
- Debug and fix the `ActionLog` Undo engine so rolling back AI actions doesn't throw exceptions.

## 📋 Tasks

### [Bug Fixes]
- [ ] Fix timezone conversion for Celery accountability jobs.
- [ ] Filter `projects` by `status='active'` when applying daily targets in evening reflection.
- [ ] Investigate `ActionLog` state application bug and add proper error handling/fallback.

### [UI / Keyboards]
- [ ] Refactor `/projects` command to use a paginated Inline Keyboard if project count > 5.

## 🔒 Security & Architecture Notes
- Use `zoneinfo` carefully and ensure `tzdata` is robust.
- When paginating, store the current page in the callback data (e.g., `projects_page_2`).

## 🏁 Completion Criteria
- User can view all projects via Next/Prev buttons.
- Timezone correctly computes Berlin 23:00.
- Undo button correctly restores previous DB state without crashing.
