# Sprint 34: AI Agnosticism & Multiple Providers

**Status:** `Completed`
**Date Proposed:** April 8, 2026
**Objective:** Decouple the bot from Google Gemini and allow seamless swapping of LLM providers dynamically (from the DB), ensuring fallback and customized experiences.

## 🎯 Goals
- **Abstract LLM Implementation:** We need a solid `BaseLLMProvider` interface to accommodate OpenAI, Anthropic, or Local models.
- **Provider Switching Interface:** A clean `⚙️ Settings -> 🤖 AI Model` interface to toggle the engine.
- **OpenAI Integration:** Implement `gpt-4o` or `gpt-4o-mini` as an alternative capable model for the complex intent schemas.

## 📋 Tasks

### 1. The `BaseLLMProvider` Abstract
[x] Create an abstract base class `src/ai/base_provider.py` with standard `generate_text()`, and `extract_intent()` async methods.
[x] Refactor the current `GoogleProvider` to implement this abstract interface properly.

### 2. OpenAI Integration
[x] Implement `src/ai/openai_provider.py` parsing OpenAI's tool-calling definitions instead of Gemini's.
[x] Handle `OPENAI_API_KEY` encryption securely similar to `GOOGLE_API_KEY`.
[x] Test the accuracy of `gpt-4o-mini` vs Gemini on our strict Pydantic parsing goals.

### 3. UI to Swap Engine
[x] Update `src/bot/handlers/settings/general.py` and keyboards.
[x] Add the field `llm_provider` validation into DB interactions to properly instantiate the required provider on the fly.

## 🔒 Security & Architecture Notes
- The API keys need to continue using symmetric encryption before DB storage.
- The `ai` factory should fail gracefully to a fallback text if an API key is busted.

## 🏁 Completion Criteria
- User can go into settings, switch from Gemini to OpenAI.
- Logging work using OpenAI succeeds.
- Switch back to Gemini succeeds.