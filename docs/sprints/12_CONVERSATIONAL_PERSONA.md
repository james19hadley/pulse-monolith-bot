# Sprint 12: Conversational AI & Persona Engine

**Status:** `Completed`
**Date Proposed:** 2026-03-23
**Objective:** Replace the dry "Intent detected, but no implementation" fallback with a fully conversational AI layer. If the user's message is classified as `CHAT_OR_UNKNOWN`, the bot should reply contextually using the user's configured Persona settings, acting as a coach, butler, or monolith.

## 🎯 Goals
- Implement a chat completion method in the LLM provider interface.
- Bind `CHAT_OR_UNKNOWN` intent to this new conversational endpoint.
- Read the user's `persona_type` (and `custom_persona_prompt` if any) from the DB to wrap the system prompt accordingly.

## 📋 Tasks

### 1. Database & Config Sync
- [x] Verify `persona_type` and `custom_persona_prompt` fields exist and are accessible on the `User` model.
- [x] Define default system prompts for standard personas (e.g., `monolith`, `butler`, `coach`, `sarcastic`).

### 2. Provider Implementation
- [x] Add a `generate_chat_response(text: str, persona_prompt: str) -> str` method to `GoogleProvider` inside `src/ai/providers.py`.
- [x] Pass the appropriate persona-based `system_instruction` configuration to the `genai.Client`.

### 3. Router Wiring
- [x] Update `src/bot/handlers/ai_router.py` to catch `IntentType.CHAT_OR_UNKNOWN`.
- [x] Query the correct persona prompt based on the user's settings.
- [x] Send the message to the new chat generation endpoint and return the answer gracefully to Telegram via Markdown/HTML text.

## 🔒 Security & Architecture Notes
- Keep tokens in mind. Standard chat might consume more tokens since it generates conversational text rather than short JSON boundaries. Ensure token usage is accounted for if possible.
- Wrap output in safe HTML escaping if the LLM decides to use markdown formatting (like `<` or `>`), or ensure the Telegram response safely escapes it to prevent `TelegramBadRequest`.

## 🏁 Completion Criteria
- User can say "Hello!" or "I'm feeling lazy..." and the bot responds continuously within character, without throwing native implementation errors or failing parse mode validations.

### 4. Integration with Report Formatter (Sprint 08)
- [x] Connect the `persona_type` and `custom_persona_prompt` directly to the "Chef's Kiss" commentary generated quietly at the end of the Daily Reports.
- [x] Ensure `CHAT_OR_UNKNOWN` conversational prompts are aware of the user's current `report_config` (style/blocks) so the Persona can references how it formats daily summaries if asked.
