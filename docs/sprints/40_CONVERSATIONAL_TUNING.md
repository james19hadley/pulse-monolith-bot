# Sprint 40: Conversational Tuning & Reflection Settings

**Status:** `Completed`
**Date Proposed:** 2026-04-13
**Objective:** Add a structured UI in the settings menu allowing the user to precisely customize the AI's "talkativeness" and configure the specific topics the AI should ask about during the evening reflection.

## 🎯 Goals
- Give the user granular control over how chatty the AI is (Talkativeness Level).
- Provide toggle-able options for Evening Reflection (what to focus on).
- Establish Day-to-Day Continuity: AI remembers what was planned yesterday evening and reminds the user today morning.
- Fix the silent Proactive Check so the bot nudges the user to start working even if they already have pending tasks.
- Create an intuitive Inline Keyboard UI in the `/settings` pane.

## 📋 Tasks

### [Database & State]
- [ ] Add `talkativeness_level` (String/Enum) to `User` model.
- [ ] Add `reflection_config` (JSON) to `User` model (or expand `report_config`).
  - Expected keys: `focus_wins` (bool), `focus_blockers` (bool), `focus_tomorrow` (bool), `custom_prompt` (string).
- [ ] Add `last_evening_plan` (String) to `User` model to store the continuity context.

### [UI / Keyboards]
- [ ] Add `[🗣 AI Conversation]` button in the main Settings panel (`src/bot/handlers/settings/system_configs.py`).
- [ ] Create a new settings sub-menu `Talkativeness Level` with options:
  - 🧊 Minimal (Facts only)
  - ⚖️ Standard
  - 🧠 Coach (Deep, verbose answers)
- [ ] Create a new settings sub-menu `Evening Reflection` with:
  - 🔘 Toggle: Blockers & Problems
  - 🔘 Toggle: Tomorrow's Plan (Saves Context)
  - 🔘 Toggle: Daily Wins
  - 📝 Set Custom Question (FSM text input)

### [AI Integration & Schedulers]
- [ ] Inject `talkativeness_level` into the global `get_persona_prompt` function.
- [ ] Update `job_evening_reflection` in `src/scheduler/jobs.py` to read `reflection_config` and dynamically build the prompt.
- [ ] Update `job_morning_planner`: Make it fetch `last_evening_plan`. Ask the AI to draft the morning welcome message enforcing continuity ("Remember, you said you'd do X...").
- [ ] Update `job_catalyst_heartbeat` to ALSO nudge users who have `pending_tasks > 0` but haven't logged any time today (proactive push to start working).

## 🔒 Security & Architecture Notes
- Settings should be easily accessible but not clutter the main `/settings` menu. Group them under an "AI & Persona" sub-menu.
- JSON schema for reflection must be validated before writing to the DB.

## 🏁 Completion Criteria
- User can toggle reflection topics on/off.
- User can change talkativeness.
- The AI correctly obeys these constraints in the evening reflection Celery job.
