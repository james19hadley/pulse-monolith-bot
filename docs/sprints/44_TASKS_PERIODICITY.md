# Sprint 44: Tasks, Periodicity, & Memory Space

**Status:** `Draft`
**Date Proposed:** 2026-04-29
**Objective:** Move from simple time-tracking and project trees to complete Day-Level Task Management, Custom Targets (Weekly/Monthly), and persistent User Memory extraction.

## 🎯 Goals
- Implement a dedicated "Memory Space" (KV store/JSON) for user preferences like "Lunch is at 13:00".
- Support new `target_period_type` on projects ("weekly", "monthly", "custom") while preserving the AI's NLP intelligence ("Balance 9 hours total, 3 mins daily").
- Integrate Inbox processing into the evening reflection, converting raw thoughts into actionable Tasks for tomorrow.
- Implement explicit "Task" entities bound to specific time periods (`morning`, `afternoon`).

## 📋 Tasks

### [The User Memory Context]
- [ ] Add a `user_memory` JSON field to the `User` model.
- [ ] Enable the bot to cleanly overwrite and append to `user_memory` via natural language if the intent matches `UPDATE_MEMORY` or `SYSTEM_CONFIG`.

### [Prompt Centralization & Persona Architecture]
- [ ] Move all scattered LLM system prompts (from `jobs.py`, `providers.py`, `router.py`) into one centralized repository file: `src/core/prompts.py`.
- [ ] Build a capability injector: dynamically generate a list of the Bot's capabilities directly from the `IntentType` enum descriptions and feed it to the Chat Fallback prompt.
- [ ] Ensure the prompt simply states "Here are your capabilities: [List]" and lets the Persona decide how to respond if the user asks for something impossible, avoiding rigid "Say you don't know" instructions.
- [ ] Inject the `user_memory` JSON directly into the base Chat and Intent Router prompts.

### [Custom Target Periodicity]
- [ ] Add `target_period` (Enum: `daily`, `weekly`, `monthly`) to the `Project` model schema and database.
- [ ] Adjust `CREATE_ENTITIES` AI prompt to extract these specific `target_period` variants.
- [ ] Adjust the cron script (`src/scheduler/jobs.py`) so that progress and streaks reset only on the correct interval (e.g. Sunday night for Weekly targets).

### [Task Engine & Inbox Converter]
- [ ] Create a robust Inbox command `/inbox` for ad-hoc clearing or management.
- [ ] In the evening `Daily Reflection`, ask the user if today's Inbox items should be deleted or converted to actionable `Tasks`.
- [ ] Add `target_time_period` to `Task` entities for granular day planning ("до обеда", "после обеда").

## 🔒 Security & Architecture Notes
- Prompt Injection is a risk when appending arbitrary user JSON objects to the system prompt; however, the user provides their own API key, so the risk is contained to their own quota. Still, we must isolate it properly inside markdown JSON blocks.
- The Periodicity change requires a DB migration step but must be strictly backward compatible with existing `daily_target_value`.

## 🏁 Completion Criteria
- User can define "Read 50 pages a week" via NLP and the bot schedules it.
- The Bot knows "Lunch is at 13:00" from User Memory.
- Inbox items can be converted to Tasks with a selected time of day.
