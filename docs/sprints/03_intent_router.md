# Sprint 03: AI Pipeline - The Intent Router

**Status:** `Active`
**Date Proposed:** March 23, 2026
**Objective:** Implement the first step of the two-step AI pipeline: the lightweight Intent Router. This system will analyze natural language input and classify it into strict operational categories without modifying data yet.

## 🎯 Goals
- Implement the `BaseLLMProvider` interface to ensure provider-agnostic AI capabilities.
- Create a fast, cheap classification prompt that enforces strict JSON output.
- Intercept all free-form text messages in Telegram and echo back the detected intent for debugging.

## 📋 Tasks

### Dependencies & Setup
- [x] Add AI provider library to `requirements.txt` (e.g., `google-genai` or `openai`) and install it.
- [x] Add BYOK security (Fernet encryption) to securely store users' keys rather than hardcoding.

### AI Provider Architecture (`src/ai/providers.py`)
- [x] Define `BaseLLMProvider` abstract class.
- [x] Implement `DefaultProvider` (e.g., a lightweight Google/OpenAI model wrap) structured for JSON structure enforcement.

### Routing Logic (`src/core/prompts.py` & `src/ai/router.py`)
- [x] Create `prompts.py` and write the system prompt for the Intent Router. Available intents: `LOG_WORK`, `LOG_HABIT`, `ADD_INBOX`, `SESSION_CONTROL`, `SYSTEM_CONFIG` (for persona changes), `UNDO`, `CHAT_OR_UNKNOWN`.
- [x] Implement `classify_intent(text: str)` in `router.py` to call the LLM and safely parse the JSON response.

### Bot Integration (`src/bot/handlers.py`)
- [x] Add a catch-all message handler for plain text.
- [x] Hook the message text into `classify_intent`.
- [x] Reply to the user in Telegram with the raw detected intent (temporary debugging behavior).

## 🔒 Security & Architecture Notes
- The router must *never* execute database changes. It acts strictly as a traffic controller to prevent prompt injection and context poisoning.
- The use of structured outputs (JSON schema) is mandatory to prevent parsing errors.

## 🏁 Completion Criteria
- [x] User can type conversational text (e.g., "I worked for 40 mins" or "Switch to TARS") in Telegram, and the bot replies with the correctly mapped JSON intent (e.g., `{"intent": "LOG_WORK"}` or `{"intent": "SYSTEM_CONFIG"}`).
