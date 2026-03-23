# Product Backlog & Icebox

This document stores brilliant ideas, architectural improvements, and "nice-to-have" features that are not yet scheduled for a specific sprint. It prevents scope creep while guaranteeing good ideas are not forgotten.

## 📌 Features & Improvements

### 1. View Layer / Persona Engine Engine
**Issue:** Hardcoded strings in `handlers.py` (e.g., `message.answer(f"✅ Created project:")`) contradict the overall psychology of the bot and reduce maintainability.
**Solution:** 
- Extract all text responses into `views.py`.
- Create a "Bot Style" / "Persona" configuration (e.g., `StyleEnum.EMOJI`, `StyleEnum.TERSE`, `StyleEnum.TARS`).
- Long-term: Allow the user to define their own string templates in the database to completely customize how the bot responds to success/failure states.

### 2. Token Accounting (FinOps)
**Issue:** AI calls cost money, but there's currently no visibility into how many tokens are burned per session/intent.
**Solution:**
- Gemini (and other providers) return total tokens consumed in their response payloads.
- Create a `TokenUsage` table or add columns to `ActionLog`.
- Goal: Create a command `/stats` or send weekly reports showing estimated USD cost and token burn.
