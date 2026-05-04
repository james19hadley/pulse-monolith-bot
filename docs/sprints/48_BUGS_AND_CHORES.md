# Sprint 48: Bug Fixes & UX Polish

**Status:** `Active`
**Date Proposed:** 2026-05-04
**Objective:** Address critical edge cases in AI intent mapping, task tracking, and session logic that currently degrade the user experience.

## 📋 Tasks

### [Bug 1: Inbox Ghost Items]
- [x] **Issue:** A test string "Inbox" is permanently stuck in the user's Inbox and reported daily.
- [x] **Fix:** Investigate the `Clear inbox` command. Why did it mark tasks as completed instead of clearing the inbox?
- [x] **AI Router Fix:** Update `src/core/prompts.py` to ensure `CLEAR_INBOX` or similar intent exists, and instruct the LLM: *If the user asks to do something not on the intent list (or ambiguous), return `CHAT_OR_UNKNOWN` so the bot can ask for clarification rather than hallucinating an action.*

### [Bug 2: Redo / Undo UI Loop]
- [x] **Issue:** After pressing Undo, the bot sends an inline keyboard with ✅/❌. Pressing ❌ says "Redo is WIP", but pressing the button also triggers a confusing "Меню обновлено" message.
- [x] **Fix:** Audit `cq_undo_bad` and `cq_undo_ok` in `src/bot/handlers/core.py`. Ensure we gracefully handle the inline keyboard removal without throwing arbitrary success messages or leaving dangling state.

### [Bug 3: Missing Context Query on Session Start]
- [x] **Issue:** When the user clicks `▶️ Session` from the main menu, the bot starts a session but *does not* ask "Чем мы занимаемся?" as implemented in Sprint 40.
- [x] **Fix:** Review `cmd_start_session` in `src/bot/handlers/sessions.py`. Ensure the bot follows up with the inline keyboard of active projects or a text prompt (e.g., `EntityState.waiting_for_session_context`) immediately after the timer starts.

### [Bug 4: Telegram Webhook Timeout ("Silent Death")]
- [x] **Issue:** Sending a complex request (e.g., creating 7 tasks) causes the synchronous Google Gemini API to block the `asyncio` event loop for minutes. Telegram sees a timeout (no response within 5 seconds), aborts the connection, and retries the webhook delivery repeatedly, causing duplicated tasks and a frozen bot state for other commands.
- [x] **Fix:** Refactored `src/ai/router.py` to be fully asynchronous. Replaced direct `genai.Client` sync calls with `asyncio.to_thread` workers. Upgraded all AI calls from handlers (`src/bot/handlers/intents/*.py`) to `await` the router layer wrapper.
- [x] **UX Polish:** Created `ProcessingSpinner` (`src/bot/handlers/spinner.py`) to show a non-blocking animated "Typing..." style indicator in Telegram, ensuring the user knows the AI is working natively even if the backend is doing heavy IO for >5 seconds.
