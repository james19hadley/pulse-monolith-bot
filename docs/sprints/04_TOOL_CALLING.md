# Sprint 04: AI Tool Calling & DB Operations

**Status:** 🟡 In Progress

## 🎯 Goal
Bridge the AI Intent Router with actionable Database updates, giving the LLM the ability to write to SQLite.

## 📝 Tasks
- [ ] Refactor: Replace `CHAT_OR_UNKNOWN` magic string with `pydantic.Enum` of `IntentType`.
- [ ] Connect `IntentType.LOG_WORK` to create a `TimeLog` entry in the database.
- [ ] Allow the AI to return dynamic string responses based on the database success.
- [ ] Manual testing of logging 20 minutes to a project.
