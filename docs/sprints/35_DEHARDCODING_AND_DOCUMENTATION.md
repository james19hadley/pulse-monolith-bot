# Sprint 35: De-hardcoding, Texts, & Documentation

**Status:** `Active`
**Date Proposed:** April 9, 2026
**Objective:** Eliminate hardcoded plain-text from core logic/schedulers, centralize all bot strings into `texts.py` / `views.py`, and fix the "nagging" UX where AI becomes too verbose or pings too frequently.

## 🎯 Goals
- [ ] Centralize all static messages (e.g., Nudge/Ping messages from `scheduler/jobs.py`) into our localization registry (`src/bot/texts.py` or similar).
- [ ] Implement a **"Nudge Acknowledgement"** mechanism to reset the nagging timer and prevent the LLM from writing verbose paragraphs when the user just says "I'm still working".
- [ ] Add systemic prompt constraints so the AI defaults to brief reactions (like ✅) when the user confirms their state without providing new data.

## 📋 Tasks

### 1. Unified Texts Registry
- [ ] Audit `src/scheduler/jobs.py` and `src/bot/` for stray hardcoded Russian text.
- [ ] Move these strings into `src/bot/texts.py` (e.g., `NUDGE_ACTIVE_SESSION`, `NUDGE_REST_SESSION`).
- [ ] Update `views.py` to consume these variables cleanly.

### 2. The "Nagging" Fix (UX Improvement)
- [ ] Add inline buttons to the nudge message (e.g., `["Я работаю 🧘‍♂️", "Завершить 🛑"]`).
- [ ] Create a handler for "I'm still working" that silences the nudge for a longer period (e.g., 1 hour snoozing) without bothering the LLM pipeline, sending just a quick `✅`.
- [ ] Review `interval_minutes` vs `threshold_minutes` logic in `jobs.py` to ensure ping frequency scales gracefully instead of bombarding the user.

### 3. LLM Prompt Tuning
- [ ] Edit `src/core/prompts.py` (Persona / System Prompts) to include a rule: "If the user is just checking in or confirming they are fine, respond mathematically brief or use a single emoji. Do not generate fake encouragement paragraphs."

## 🔒 Security & Architecture Notes
- Must adhere to the new `BaseLLMProvider` structure when tuning generated text.
- No new tables required, unless we decide to save "snooze_until" timestamp in the user `users` settings table.

## 🏁 Completion Criteria
- [ ] The bot stops sending walls of text for simple check-ins.
- [ ] Nudges happen smartly and provide a 1-click "Snooze/Still working" button.
- [ ] Hardcoded strings in `jobs.py` are fully eliminated.
