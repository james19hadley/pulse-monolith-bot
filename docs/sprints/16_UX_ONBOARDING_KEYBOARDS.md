# Sprint 16: UX Overhaul, Onboarding & Keyboards

**Status:** `Active`
**Date Proposed:** 2026-03-24

**Objective:** Transition the bot from a "CLI for developers" to a modern "B2C Product". This involves removing the reliance on slash commands, introducing interactive buttons, creating a warm onboarding sequence, and implementing multi-step conversation flows (FSM) for complex setups like API keys.

## 🎯 Architectural Philosophy (How we build it cleanly)
To avoid cluttering the existing `handlers.py` logic, we will introduce two new patterns to the architecture:
1. **Keyboards Layer (`src/bot/keyboards.py`):** All Telegram inline (under-message) and reply (bottom-bar) keyboards will be generated here. Handlers will simply call `get_main_menu()` or `get_providers_keyboard()`.
2. **FSM - Finite State Machine (`src/bot/states.py`):** We will use `aiogram.fsm` to manage multi-step interactions. Instead of parsing a single `/add_key google 123` string, the bot will remember what step the user is on (e.g., `State: WaitingForProvider`, `State: WaitingForKey`).

## 📋 Tasks

### 1. The Warm Onboarding & Views Refactor
- [ ] Rewrite `welcome_message` in `src/bot/views.py` to be informative and approachable.
- [ ] Add the hardcoded language disclaimer: *"Message me in any natural language, I understand all languages."*
- [ ] Provide clear, hardcoded examples of natural language interaction to save AI tokens (e.g., *"Set time like in Huston and post to channel exactly at midnight"*).

### 2. Main Menu GUI
- [ ] Create `src/bot/keyboards.py`.
- [ ] Implement a persistent Reply Keyboard (bottom menu) that gives quick access to the most used functions (e.g., 🟢 Start Session, 🛑 End Session, 📥 Inbox, ⚙️ Settings).

### 3. Multi-step API Key Setup (FSM)
- [ ] Define FSM states in `src/bot/states.py` (e.g., `AddKeyState`).
- [ ] Refactor the `/add_key` handler.
    - **Step 1:** User clicks "Add Key". Bot replies: "Select Provider" + Inline Keyboard [Google] [OpenAI] [Anthropic].
    - **Step 2:** User clicks Provider. Bot replies: "Please paste your API key."
    - **Step 3:** Bot securely saves it and exits the FSM state.

## 🏁 Completion Criteria
- A new user presses `/start` and receives a beautiful, multi-step welcome message with examples and a bottom-bar menu.
- Adding an API key is a guided click-and-paste process, not a syntax puzzle.
