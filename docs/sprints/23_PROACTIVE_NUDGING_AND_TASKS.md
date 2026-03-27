# Sprint 23: Proactive Nudging and Spoon-fed Tasks

**Status:** `Completed`
**Date Proposed:** March 27, 2026
**Objective:** Transform the bot from a passive tracker into an active "Butler/Nanny" that proactively suggests predefined project tasks to the user to reduce task-switching friction.

## 🎯 Goals
1. Implement a system to store actionable step-by-step plans or tasks within a Project.
2. Create a proactive scheduled "Nudge" system that initiates conversation based on inactivity.
3. Design a conversational flow: Warm greet -> Offer options -> Spoon-feed specific next steps.
4. Implement "Pedagogical Evening Chats" for habit accountability.

## 📋 Tasks

### 1. Database & AI Architecture
- [x] Design and implement a `Task` schema in database that supports both Project-linked and Standalone tasks.
- [x] Create the `IntentType.ADD_TASKS` Pydantic models for Gemini extraction.
- [x] Implement the handler that automatically routes bullet points or NLP strings into individual Task database rows.

### 2. UI/UX Interaction
- [x] Create UI to view the top 5 next active tasks natively inside the Project view.
- [x] Add inline `[📋 Manage Tasks]` button to manage tasks individually (completing or deleting them).
- [x] Fix intent tracker UI logic discrepancy where NLP logs didn't calculate total progress identical to UI queries.

### 3. Stability & Bug Fixes
- [x] Link `TimeLog` manually back to `active_session_id` to repair false positive *The Void Expands* catalyst pings.
- [x] Abandon complex *Emulated Online Status* (last_interacted_at) to avoid over-engineering; rely purely on session heartbeat.

### 4. Daytime Proactive Nudges & Evening Chats
- [x] Integrate LLM into the `catalyst_heartbeat` to generate "warm" check-in messages that extract pending tasks to suggest automatically.
- [x] Add `periodicity_days` and `nudge_threshold_days` to the `Habit` model.
- [x] Update Habit UI to natively allow configuration of periodicity and nudge logic per habit.
- [x] Add Evening Nudge logic to detect unlogged habits and generate coach messages (using custom threshold).

## 🔒 Security & Architecture Notes
- We maintain `Task` as a separate SQL table rather than muddying `Project` or `Habit` schemas (KISS + YAGNI).
- Strict adherence to respectful timezone boundaries is critical for AI-initiated prompts.

## 🏁 Completion Criteria
- User can say "Add tasks: X, Y" and they gracefully link to the project.
- User can resolve tasks via UI.
- Bot proactively interrupts long focus-silences with custom NLP messages citing next tasks.
