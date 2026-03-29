# Sprint 27: The Great Migration (Habits → Projects Unification)

**Status:** `Draft`
**Date Proposed:** March 29, 2026
**Objective:** Deprecate `Habit` as a standalone DB entity and abstract concept. Unify everything into a single, highly flexible `Project` schema. This resolves the cognitive burden of "infinite routines" and creates a seamless unified data layer for tracking bounds, daily quotas, life-time progress, and granular logging.

## 🧠 Philosophy Shift
- **Anti-Infinity:** "Infinite habits" create subconscious pressure and a lack of completion dopamine. Everything is now a bounded project ("Learn Portuguese: 100 hours" or "Run 50 days").
- **Daily Quotas vs Total Goals:** A `Project` can now track its progression via _Total Value_ (e.g., Target: 100 hours) while concurrently holding a _Daily Target_ (e.g., Code 1 hour a day) to automatically measure streaks.
- **Ledger Unification:** By merging into `Project`, previous actions (which were silently dropped beyond their daily bump) are written into the immutable `TimeLog`. Every minute logged beyond a "quota" mathematically counts toward your grand life total.

## 📋 The Migration Plan

### Phase 1: Database Redesign & Data Migration
- [ ] **1. Schema Updates (`src/db/models.py`)**:
    - Add to `Project`:
        - `daily_target_value: Mapped[Optional[int]]`
        - `current_streak: Mapped[int] = mapped_column(Integer, default=0)`
        - `last_completed_date: Mapped[Optional[date]]`
        - `total_completions: Mapped[int] = mapped_column(Integer, default=0)`
- [ ] **2. Write SQLite Data Migration Script (`mig_s27.py`)**:
    - Read all existing `Habit` records.
    - Convert them into new `Project` rows (Target: habit target, Unit: habit unit).
    - Port `current_streak`, `last_completed_date`, `total_completions` directly into the `Project`.
    - Change old references so we don't drop data.
    - **CRITICAL:** Map the newly created `Project.id` to previous dependencies or safely archive old habits.

### Phase 2: Engine & AI Overhaul
- [ ] **1. Update AI Schemas (`src/ai/providers.py`)**:
    - Remove `CREATE_HABIT` intent and `LOG_HABIT` intent classes.
    - Expand `Project` creation parsing so the AI can extract both "global target" and "daily target".
    - Update `EditEntitiesParam` to rip out `entity_type="habit"`.
- [ ] **2. Deprecate Intents & Core Handlers**:
    - **Delete:** `intent_log_habit.py`, `src/bot/handlers/entities/habits.py`.
    - Modify `intent_log_work.py` to seamlessly handle inputs that _feel_ like habits but are routed to the Project ledger.
    - Clean up `router.py`, `ai_router.py`, `prompts.py`, `constants.py` to scrub references to `IntentType.LOG_HABIT`.

### Phase 3: Schedulers & Evening Reports
- [ ] **1. Overhaul `jobs.py` (Cron Scheduler)**:
    - Update the daily midnight cron. Instead of resetting `Habit.current_value`, it should reset the "daily progress" on `Projects` that have a `daily_target_value`.
    - If a user failed to meet the `daily_target_value`, drop the `current_streak` to 0.
- [ ] **2. Rewrite UI Lists & Menus (`views.py`, `keyboards.py`)**:
    - Remove the "🎯 Habits" button from keyboards.
    - Update the Evening Report to loop through `Projects` that had daily quotas and show the 🔥 Streaks natively next to them.

## 🏁 Completion Criteria
- Word `habit` is functionally eradicated from user-facing prompts, bot outputs, and DB constraints.
- Existing user habits are preserved, successfully converting into `Projects` in the DB.
- Typing "Сделал 20 отжиманий" automatically routes to the "Отжимания" Project, writes to the `TimeLog`, increments the daily quota, and registers the 1-day 🔥 streak.

