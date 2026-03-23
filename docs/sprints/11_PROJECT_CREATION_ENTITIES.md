# Sprint 11: AI Project & Habit Creation

**Status:** `Draft`
**Date Proposed:** 2026-03-23
**Objective:** Empower the AI Router to understand natural language project and habit creation, specifically incorporating "target hours" (measured effort). Simultaneously upgrade the underlying CLI creation commands.

## 🎯 Goals
- Allow users to seamlessly create Projects (with target metrics) and Habits straight via free-form text.
- Overhaul manual CLI tools to support the target hours attribute properly.

## 📋 Tasks
### Technical Debt & Housekeeping
- [ ] Check for any pending items from Sprint 10 closure.

### 1. Database & Enum Adjustments
- [ ] Add `CREATE_PROJECT` and `CREATE_HABIT` to `IntentType` enum in `src/core/constants.py` (if not already acting under unknown/chat intents).
- [ ] Ensure `Project` ORM model `target_minutes` parsing is smooth and robust.

### 2. Manual CLI Tooling
- [ ] Update `/new_project` in `src/bot/handlers/projects_habits.py` to parse `<name> | <target_hours>` or `<name>, <target_hours>`.

### 3. AI Pipeline Upgrade
- [ ] Expand `INTENT_ROUTER_SYSTEM_PROMPT` inside `src/core/prompts.py` (or where defined) to teach the router about `CREATE_PROJECT` and `CREATE_HABIT` intents.
- [ ] Define Pydantic extraction schema in `src/ai/providers.py` (`CreateProjectParams`, `CreateHabitParams`).
- [ ] Modify `extract_*` functions in `src/ai/router.py`.

### 4. Router Wiring
- [ ] Bind the new intents in `src/bot/handlers/ai_router.py` handle functions.
- [ ] Translate extracted project `target_hours` or `minutes` into the database and save via `SessionLocal`.

## 🔒 Security & Architecture Notes
- Only parse `float` or `int` safely to avoid payload crashes when users pass string text for time.
- Fallback logic should create the project with `0` target time if the AI fails to glean a specific metric.

## 🏁 Completion Criteria
- User can successfully issue natural language commands like "создай проект под названием Видео по статье 'Наука без чисел' с целью 10 часов и создай привычку Balance".
- Bot creates both the Project and Habit correctly in the database, assigning target effort accurately.
