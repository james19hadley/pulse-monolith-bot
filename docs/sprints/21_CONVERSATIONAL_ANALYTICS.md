# Sprint 21: Conversational Analytics Intent

**Status:** `Draft`
**Date Proposed:** March 26, 2026
**Objective:** Save API tokens and improve UX by adding a specific `CHECK_STATS` intent to the AI Router, instead of passing the entire database to the general chat persona.

## 🎯 Goals
1. Add `CHECK_STATS` into `src/core/prompts.py` (Intent Router).
2. Create `_handle_check_stats` in `ai_router.py`.
3. When trigged (e.g. "сколько часов у проекта 1"), the bot queries the actual DB for that specific entity and feeds ONLY that data to the LLM to generate an accurate, persona-styled response.
