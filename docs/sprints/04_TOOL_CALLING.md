# Sprint 04: AI Tool Calling & DB Operations

**Status:** 🟢 Completed

## 🎯 Goal
Bridge the AI Intent Router with actionable Database updates, giving the LLM the ability to write to SQLite. Establish strict rules for Entity Resolution to prevent database fragmentation.

## 📝 Tasks
- [x] Refactor: Replace `CHAT_OR_UNKNOWN` magic string with `pydantic.Enum` of `IntentType`.
- [x] Strategy *(Added during sprint)*: Define Entity Resolution philosophy (Strict ID Matching instead of Hallucinated Strings) in `03_MEMORY_AND_AI_PIPELINE.md`.
- [x] Tool Calling: Implement `LogWorkParams` via Pydantic to strictly extract `duration_minutes` and `project_id`.
- [x] Setup *(Added during sprint)*: Add temporary `/new_project` command for end-to-end testing constraints.
- [x] Connect `IntentType.LOG_WORK` to create a `TimeLog` entry in the database.
- [x] Allow the AI to return dynamic string responses based on the database success.
- [x] Manual testing of logging specific durations to a structured project.

## 🏁 Completion Criteria
- User can send natural language ("coded 1.5 hours on project 1") and the database reflects exactly `90 minutes` tied to the correct `project_id`. **(ACHIEVED)**
