# Sprint 35: De-hardcoding, Texts, & Documentation

**Status:** `Draft`
**Date Proposed:** April 8, 2026
**Objective:** Eliminate hardcoded text in Python files for easier localization/editing and establish a central FAQ/User Guide to lower the cognitive overhead of learning the bot.

## 🎯 Goals
- **Centralize Copywriting:** Provide a single source of truth for all Bot UI and Bot conversational (non-AI) messages.
- **Bot Documentation:** Generate the first `USER_GUIDE.md` detailing every major mechanic of the bot from logging work to using "The Void", Undo, and Archiving.
- **In-App Help:** Create a `/guide` or `/faq` command that maps directly to these concepts so users aren't left guessing what to do next.

## 📋 Tasks

### 1. `src/bot/texts.py` Hub
- [ ] Create a dictionary or Class structure to contain keys like `MSG_PROJECT_CREATED`, `MSG_CANT_UNDERSTAND`.
- [ ] Go through `handlers/entities/`, `handlers/intents/`, and `scheduler/jobs.py` and replace raw strings with imported constants.

### 2. `docs/USER_GUIDE.md`
- [ ] Document: "The Tracker Core" (Absolute vs Relative Tracking).
- [ ] Document: The core philosophy of "Tasks vs Projects" (Nanny spoon-feeding, single-tasking, avoiding GTD burnout).
- [ ] Document: "The Void" concept.
- [ ] Document: The Morning Planner and Evening Accountability Engine.
- [ ] Document: Nudges, habits vs projects, and NLP Edit commands (`Вычти 10 минут`).

### 3. Telegram `/guide` Command
- [ ] Implement an interactive `/help` handler using pagination or inline keyboards to browse the User Guide chapters right in Telegram.

## 🔒 Security & Architecture Notes
- If `texts.py` gets too large, split it by module (`texts/projects.py`, `texts/intents.py`) or consider `yaml`/`json`. Python dictionaries are preferred for simplicity right now.

## 🏁 Completion Criteria
- Developers can update all grammar and wording directly in `texts.py`.
- Typing `/guide` in the bot opens a clickable menu exploring the main concepts.