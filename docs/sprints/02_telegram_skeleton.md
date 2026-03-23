# Sprint 02: Telegram Skeleton & CLI Commands

**Status:** `Completed`
**Date Proposed:** March 23, 2026
**Objective:** Build the foundational Telegram bot layer using `aiogram` and implement the basic AI-less commands (CLI Fallback) for starting and ending work sessions.

## 🎯 Goals
- Set up the main bot execution loop (Long Polling).
- Implement automatic user registration in the database upon user's first interaction.
- Build exact CLI equivalents for session management (`/start_session` and `/end_session`).

## 📋 Tasks
### Core Configuration & Setup
- [x] Create `src/core/config.py` to load and validate environment variables (e.g., bot tokens).
- [x] Create `src/main.py` as the main entry point for the long polling bot loop.

### Bot Handlers (`src/bot/handlers.py`)
- [x] Implement `/start` — welcome the user and register them in the `users` table if they do not exist.
- [x] Implement `/start_session` — open a new `Session` record in the database for the user.
- [x] Implement `/end_session` — forcefully close the active session and print the time spent.

### Presentation Layer (`src/bot/views.py`)
- [x] Create a views module to store the Monolith's dry and factual response texts so they don't clutter the routing logic.

## 🔒 Security & Architecture Notes
- The bot logic at this stage must remain intentionally "dumb" and strictly tied direct SQL(Alchemy) interactions. This implements our fail-safe CLI fallback (Zero-AI Mode).
- Must enforce strict isolation by passing the Telegram `user_id` when making any requests to the database to fetch active sessions.

## 🏁 Completion Criteria
- Running `python src/main.py` starts the bot without throwing an error.
- Sending `/start`, `/start_session`, and `/end_session` via Telegram accurately alters state in `db.sqlite3` and returns the expected text response.
