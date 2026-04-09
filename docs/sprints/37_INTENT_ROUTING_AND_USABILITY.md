# Sprint 37: Intent Routing & Usability Fixes

**Status:** `Draft`
**Date Proposed:** April 9, 2026
**Objective:** Fix critical bugs in the NLP routing and session tracking where the system automatically assigns work to the default project (`Project 0: Operations`) and fails to handle math/transfer operations.

## 🎯 Goals
- [ ] Understand why "Start session" captures the project context visually but track it to Project 0 by default.
- [ ] Ensure start-session intent correctly locks the session to the requested `project_id`.
- [ ] Improve the `LOG_WORK` intent parser to handle multi-project operations smoothly (e.g., subtract 133 mins from X, add 133 to Y).

## 📋 Tasks

### 1. Session Binding Fix
- [ ] Analyze `extract_session_control` parameters in `src/ai/tools.py` and `base_provider.py`. 
- [ ] Ensure `SessionControlParams` can detect and pass `project_id` or string context on start.
- [ ] Update `src/bot/handlers/sessions.py` to save the identified `project_id` directly into the `AgentSession` row during creation.
- [ ] Fix `handle_end_session` so it logs the time to the bound project rather than defaulting to Project 0.

### 2. Complex Time Operations (Add & Subtract)
- [ ] Re-evaluate how the AI generates intents when asked to move time (e.g., "вычти эти 133 минуты из проекта 14 и запиши их на проект 1").
- [ ] Update `LogWorkParams` or provide clearer rules in `src/core/prompts.py` so the NLP knows to generate *two* `LOG_WORK` operations (subtract 133 from 14, and add 133 to 1) instead of just one.
- [ ] Alternatively, handle it as a new intent "TRANSFER_WORK". Let's decide which is simpler during implementation.

## 🏁 Completion Criteria
- When you say "Start working on Pulse Monolith Bot", the tracked time when stopping the session applies correctly to that specific project, not Operations.
- When you tell the bot to "Subtract X from Project Y and add it to Project Z", the system correctly updates both targets simultaneously.
