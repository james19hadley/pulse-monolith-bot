# Sprint 09: The CLI Fallback (Zero-AI Mode)

**Status:** `Completed`
**Date Proposed:** March 23, 2026
**Objective:** Add hardcoded, explicit slash commands for core tracking functions (`/log`, `/habit`, `/inbox`) that bypass the AI processor completely. This ensures the bot remains 100% functional even if LLM APIs go down or tokens run out.

## 🎯 Goals
- Implement deterministic command handlers in `handlers.py` that map directly to the database.
- Create user-friendly syntax formats (e.g., `/log 15 Read documentation` or `/habit 1`).
- Ensure these commands work instantly locally, saving API round-trips for routine inputs.

## 📋 Tasks

### 1. The Core Data Entry Rules
- [x] `/log [minutes] [description...]` - Logs time to the Void (no project) or parses a project somehow (simplest MVP = log to Void with description, or select active project).
- [x] `/habit [id/title] [optional: +/- value]` - Increments a habit immediately.
- [x] `/inbox [text...]` - Dumps an idea directly into the inbox list.

### 2. Implementation
- [x] Define the commands in `src/bot/handlers.py` alongside the existing `/end_session` block.
- [x] Wire the logic securely to `repo.py` functions natively without relying on Pydantic `Tool_Caller`.
- [x] Provide clear error messages if parsing fails (no LLM magic here, pure hard syntax).

## 🔒 Security & Architecture Notes
- These commands must bypass the `llm_router`.
- If a user sends pure text instead of a slash-command, it still goes to the LLM. 
- These act strictly as "emergency" or "fast-lane" overrides.

## 🏁 Completion Criteria
- User can log 30 minutes of time and increment a habit simultaneously via slash commands when they don't want to wait 2 seconds for Gemini to respond.