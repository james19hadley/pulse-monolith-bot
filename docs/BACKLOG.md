# Product Backlog & Icebox

This document stores brilliant ideas, architectural improvements, and "nice-to-have" features that are not yet scheduled for a specific sprint. It prevents scope creep while guaranteeing good ideas are not forgotten.

## 📌 Features & Improvements

### 1. [Moved to Sprint 07] View Layer / Persona Engine Engine
**Issue:** Hardcoded strings in `handlers.py` (e.g., `message.answer(f"✅ Created project:")`) contradict the overall psychology of the bot and reduce maintainability.
**Solution:** 
- Extract all text responses into `views.py`.
- Create a "Bot Style" / "Persona" configuration (e.g., `StyleEnum.EMOJI`, `StyleEnum.TERSE`, `StyleEnum.TARS`).
- Long-term: Allow the user to define their own string templates in the database to completely customize how the bot responds to success/failure states.

### 2. [Moved to Sprint 07] Token Accounting (FinOps)
**Issue:** AI calls cost money, but there's currently no visibility into how many tokens are burned per session/intent.
**Solution:**
- Gemini (and other providers) return total tokens consumed in their response payloads.
- Create a `TokenUsage` table or add columns to `ActionLog`.
- Goal: Create a command `/stats` or send weekly reports showing estimated USD cost and token burn.

### 3. Conversational AI Toggle (`chatty_mode`)
**Issue:** Currently, if the Intent Router evaluates a message as `CHAT_OR_UNKNOWN`, the bot either fails silently or returns a generic native string, breaking the illusion of an intelligent assistant.
**Solution:** 
- Add a user setting `chatty_mode` (boolean).
- If `True`, send the `CHAT_OR_UNKNOWN` text back to the AI Provider, asking it to respond conversationally inside the constraints of the user's `persona_type`.
- If `False`, retain the current strict, fast mapping (or just ignore/reject).
### 4. Deep Analytics & Visualizations (Graphics)
**Issue:** Text-based reports are great for daily accountability, but long-term trends are hard to spot.
**Solution:**
- Generate graphs using matplotlib/plotly showing "The Void" vs. "Focused Time" over weeks or months.
- Goal: Visually map a user's life hours, showing exactly where time was lost and where progress was made. Currently low priority.
