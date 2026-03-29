# Sprint 26: Project Zero, Sticky Menus & NLP Editing

**Status:** `Draft`
**Date Proposed:** March 29, 2026
**Objective:** Eliminate friction for floating time logs (Project 0), centralize the Undo logic, fix sticky menus in Telegram, and allow NLP entity editing.

## 🎯 Goals
1. Make "15 минут" automatically fall back to "Project 0" instead of demanding a new project creation.
2. Remove annoying inline `[Undo]` buttons and rely on the main Reply Menu for undo operations.
3. Fix the "disappearing main menu" bug so the reply keyboard stays active (`is_persistent=True` or forced re-sends).
4. Teach the AI to edit entities (renaming, changing targets) via text.

## 📋 Tasks

### 1. Project Zero & Floating Time
- [x] Ensure "Project 0: Operations" is automatically seeded for all users.
- [x] Update `intent_log_work.py` and Prompts: if the user specifies pure time/progress without a distinct project, assign it to Project 0 instead of prompting to create "New Project".

### 2. UI: Sticky Menus & Undo Centralization
- [x] Remove `InlineKeyboardMarkup` undo buttons from `intent_log_work.py` and others.
- [x] Update the `ReplyKeyboardMarkup` initialization to use `is_persistent=True` (or similar Telegram API flag) so the menu stays visible after sending a text message or interacting with inline prompts.
- [x] Ensure the main menu has a universal "Undo" option.

### 3. NLP Entity Editing Intent
- [x] Create a new intent `EDIT_ENTITIES`.
- [x] Implement AI extraction (entity type, target name, new name/value).
- [x] Route properly and respond gracefully if the user asks for something unsupported.

## 🔒 Security & Architecture Notes
- Entity editing must restrict queries using `user_id`.

## 🏁 Completion Criteria
- User typing "15 минут" silently logs to Project 0.
- Main menu never hides after chatting.
- I can rename an entity seamlessly.
