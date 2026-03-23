# Sprint 06: Autonomy & AI Completeness

**Status:** � Completed
**Date Proposed:** March 23, 2026
**Date Completed:** March 23, 2026
**Objective:** Finalize all remaining natural language intents so the user rarely needs literal commands, and build the "Catalyst" background monitoring system that makes the Monolith truly proactive.

## 🎯 Goals
- Achieve 100% Intent Router coverage for core tracking activities (Habits, Inbox, Session Control).
- Implement the "Undo Engine" leveraging the ActionLog table.
- Build the Background Polling System ("The Soft Ping") that nudges the user to prevent The Void.

## 📋 Tasks

### 1. Intent Expansion (Pydantic & Routing)
- [x] Connect `IntentType.LOG_HABIT` to extract habit data and log it.
- [x] Connect `IntentType.ADD_INBOX` to record pure text notes (Brain Dump) to the `Inbox` table.
- [x] Connect `IntentType.SESSION_CONTROL` to trigger `/start_session` and `/end_session` purely from natural text ("I'm starting a block").

### 2. The Undo Engine
- [x] Ensure that every state-changing intent writes the previous and new state to `ActionLog`.
- [x] Implement `IntentType.UNDO` to read the last ActionLog for the user and safely delete/revert the change in SQLAlchemy.

### 3. The Catalyst (Background Scheduler)
- [x] Add `APScheduler` to `requirements.txt`.
- [x] Create `src/scheduler/jobs.py` with an async job that runs every X minutes.
- [x] Logic: If a session is active and no logs were created in the last 60 minutes, send a "Soft Ping".
- [x] Logic: Remember the last ping message ID and delete it before sending a new one to prevent wall-of-text anxiety.


### 4. Void Fixes & Configuration Refactoring
- [x] Implement Retroactive Close in `stale_session_killer` so we don't track 16 hours of sleep.
- [x] Create `USER_SETTINGS_REGISTRY` in `config.py` for settings structure.
- [x] Refactor `/settings` in `handlers.py` to map from the registry dynamically instead of IF/ELSE chains.
- [x] Use purely English for all config code.


### 4. Void Fixes & Configuration Refactoring
- [x] Implement Retroactive Close in `stale_session_killer` so we don't track 16 hours of sleep.
- [x] Create `USER_SETTINGS_REGISTRY` in `config.py` for settings structure.
- [x] Refactor `/settings` in `handlers.py` to map from the registry dynamically instead of IF/ELSE chains.
- [x] Use purely English for all config code.

## 🏁 Completion Criteria
- User can say "I'm starting" and "save this idea: buy milk" and the bot handles it flawlessly.
- User can say "undo" and the last log is deleted.
- The bot proactively pings an idle active session.
