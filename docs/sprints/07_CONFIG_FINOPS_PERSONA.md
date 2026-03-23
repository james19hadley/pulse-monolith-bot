# Sprint 07: Configuration, FinOps & Persona

**Status:** 🟡 Active
**Date Proposed:** March 23, 2026

**Objective:** Give the user deep control over the bot's behavior by moving hardcoded variables to the database, implementing exact Token Usage tracking to measure AI costs, and extracting text templates into a Persona Engine.

## 🎯 Goals
- Make the "Catalyst" heartbeat fully configurable per-user via the Database.
- Implement Token Accounting (FinOps) to track the exact cost of every AI request.
- Centralize hardcoded strings into a View/Persona layer.

## 📋 Tasks

### 1. Database & Schema Expansion (Configs & Setup)
- [ ] Add `catalyst_threshold_minutes` and `catalyst_interval_minutes` to the `User` model.
- [ ] Add a `TokenUsage` table mapping requests to burned tokens.
- [ ] Write logic to alter the database schema safely (or use a simple script for SQLite).

### 2. Catalyst Dynamic Parameters
- [ ] Alter `src/main.py` scheduler to run globally at a short interval (e.g. 5 minutes).
- [ ] Alter `src/scheduler/jobs.py` to evaluate the *per-user* settings (`now - idle_since > user.catalyst_threshold_minutes`).
- [ ] Allow the user to update their Catalyst settings via chat command (e.g. `/settings catalyst 30`).

### 3. Token Accounting (FinOps)
- [ ] Update `src/ai/providers.py` to capture `usage_metadata` (prompt tokens, completion tokens) from Gemini API responses.
- [ ] Log every `LLM` call to the `TokenUsage` database table, linked to the current Session or Intent.
- [ ] Create a `/stats` command to output current token burn and approximate USD cost.

### 4. Persona & View Engine
- [ ] Extract hardcoded strings from `src/bot/handlers.py` and `jobs.py`.
- [ ] Move them to `src/bot/views.py`.
- [ ] (Optional) Add a simple toggle for Persona Styles if requested.

## 🏁 Completion Criteria
- User can configure `The Catalyst` to trigger at 30 minutes instead of 60.
- AI usage logs are successfully pushed to DB, and `/stats` outputs total token spend.
- `handlers.py` logic no longer relies on hardcoded string formatting for UX responses.
