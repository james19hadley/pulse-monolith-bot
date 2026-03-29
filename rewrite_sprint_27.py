with open("docs/sprints/27_THE_GREAT_MIGRATION.md", "w") as f:
    f.write("""# Sprint 27: The Great Migration (Habits → Projects Unification)

**Status:** `Draft`
**Date Proposed:** March 29, 2026
**Objective:** Deprecate `Habit` as a standalone concept and entity. Unify operations into a highly flexible `Project` schema. This resolves the cognitive burden of "infinite routines" and ensures all tracking writes to a unified, immutable time ledger.

---

## 🧠 Philosophy Shift
1. **Anti-Infinity:** "Infinite habits" create subconscious pressure. Everything must be a bounded project ("Learn Portuguese: 100 hours" or "Read 50 pages").
2. **Daily Quotas vs Total Goals:** A `Project` tracks progression via _Total Value_ (Target: 100 hours) while concurrently supporting a _Daily Target_ (Code 1 hour a day) to measure streaks.
3. **Ledger Unification:** Every minute spent (even on daily quotas) is appended to the `TimeLog`. If a user overperforms their daily quota, the total project accumulates the extra time perfectly.

---

## 🛠️ The Exhaustive File-by-File Migration Checklist
*A total of 35 files contain the word 'habit'. Below is the exact execution plan so no context is lost.*

### 1. DELETION CANDIDATES (Files to remove entirely)
- [ ] `src/bot/handlers/entities/habits.py` - Delete. Move display logic to projects if needed.
- [ ] `src/bot/handlers/intents/intent_log_habit.py` - Delete. NLP parsing now routes completely through `intent_log_work.py`.

### 2. DATABASE & ORM (`src/db/`)
- [ ] `src/db/models.py`: 
  - Delete `Habit` class. 
  - Update `Project` class. Add: `daily_target_value`, `daily_progress`, `current_streak`, `last_completed_date`, `total_completions`.
- [ ] `src/db/repo.py`: Remove all functions like `get_habits`, `create_habit`. Update helper logic to fetch projects by `daily_target_value`.
- [ ] **MIGRATION SCRIPT (`mig_s27.py`)**: 
  - Read all rows from `habits` table.
  - Convert into `projects` table rows where `target_value` becomes `daily_target_value`, mapping old streaks to the properties.
  - Drop the SQLite `habits` table safely.

### 3. CRON JOB SCHEDULER (`src/scheduler/`)
- [ ] `src/scheduler/jobs.py`: 
  - Rewrite `midnight_reset`. 
  - Instead of resetting `habit.current_value`, it must inspect all `Projects` with a `daily_target_value`.
  - Calculate if `daily_progress` >= `daily_target_value`. If yes, bump `total_completions`. If no, break `current_streak = 0`.
  - Finally, reset `project.daily_progress = 0`.

### 4. AI & NLP PIPELINE (`src/ai/`, `src/core/`)
- [ ] `src/ai/providers.py`: Delete `CREATE_HABIT` enum. Tear out `LOG_HABIT` extraction logic. Rewrite `EditEntitiesParam` to reject `entity_type="habit"`.
- [ ] `src/core/prompts.py`: Delete instructions for the LLM to route "habits". Teach it that daily routines belong to `EDIT_ENTITIES` -> `Project`.
- [ ] `src/ai/router.py`: Delete `extract_log_habit`.
- [ ] `src/bot/handlers/ai_router.py`: Remove conditionals pointing to `IntentType.LOG_HABIT` and `CREATE_HABIT`.
- [ ] `src/core/personas.py`: Clean any references matching "AI tracks your habits".
- [ ] `src/core/constants.py`: Remove `IntentType` definitions referencing habits.

### 5. BOT HANDLERS & ROUTERS (`src/bot/handlers/`)
- [ ] `src/bot/handlers/core.py`: Remove `/habits` command block and `undo_habit`.
- [ ] `src/bot/handlers/entities/commands.py`: Remove habit specific router prefixes.
- [ ] `src/bot/handlers/entities/menu.py`: Eradicate habit keyboard callback handlers.
- [ ] `src/bot/handlers/entities/router.py`: Do not include `habits.py`.
- [ ] `src/bot/handlers/entities/projects.py`: Upgrade Project UI. If a Project has a `daily_target_value`, show its 🔥 streak here.
- [ ] `src/bot/handlers/intents/intent_entities.py`: Remove `if entity_type == 'habit':` blocks from creation, edit, and deletion logic.
- [ ] `src/bot/handlers/intents/intent_session.py`: Remove unused SQL habit imports.
- [ ] `src/bot/handlers/intents/intent_log_work.py`: Will now be the ultimate single-source of truth. Must be able to increment `daily_progress` *and* `current_value` on projects simultaneously.
- [ ] `src/bot/handlers/utils.py`: Remove habit fetching queries.
- [ ] `src/bot/handlers/settings/system_configs.py`: Remove textual habit references in config payloads.

### 6. UI, MENUS, & TEXTS (`src/bot/`)
- [ ] `src/bot/views.py`: Heavy rewrite of the Evening Report. Remove `render_active_habits`. Instead, fetch projects possessing daily routines and render them smoothly inside the existing report layout.
- [ ] `src/bot/keyboards.py`: Remove "🎯 Habits" from the Sticky Main Menu `ReplyKeyboardMarkup`.
- [ ] `src/bot/states.py`: Delete `HabitCreationForm` and unused state classes.
- [ ] `src/bot/texts.py`: Clear out bot hardcoded texts mentioning "habits".
- [ ] `src/main.py`: Drop `BotCommand("habits", "Display active habits")` from the config array.

### 7. DOCUMENTATION SCRUBBING (`docs/`)
- [ ] Find and replace architectural mentions in:
    - [ ] `docs/02_CORE_UX_AND_MECHANICS.md`
    - [ ] `docs/03_MEMORY_AND_AI_PIPELINE.md`
    - [ ] `docs/04_DATABASE_AND_STATE.md`
    - [ ] `docs/BACKLOG.md`
    - *(Sprint histories do not need retrospective editing, but live engine docs must reflect the Unification)*

---

## 🏁 Completion Criteria
- Codebase executes without a single instance of `AttributeError` or `SQLAlchemy Error` related to the missing `Habit` table.
- A user can say `"Add daily habit reading 15 mins for project Reading"` and the LLM accurately understands to set a `daily_target_value` on a `Project`.
- A user can log `"Read 25 mins"` and see the Daily Target fulfilled AND their lifetime Ledger update.
""")
