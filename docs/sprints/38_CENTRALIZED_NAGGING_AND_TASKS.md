# Sprint 38: Centralized Nagging & Task Prompts

**Status:** `Active`
**Date Proposed:** April 9, 2026
**Objective:** Replace in-memory nagging limits with a robust, database-backed centralized system to prevent bot spam (delete old nag, send new). Implement a new "zero tasks" nag when a user is idoling out-of-session.

## 🎯 Goals
- [x] Centralize bot message updates/deletions so annoying duplicate messages are removed.
- [x] Implement a "Do a task" prompt when idle for over an hour with 0 tasks.
- [x] Ensure Celery workers don't lose state (migrate `last_ping_message_ids` to the DB).

## 📋 Tasks

### 1. Database Migration
- [x] Add `last_nag_message_id` and `last_nag_timestamp` to `User` model.
- [x] Generate or mock Alembic migration for `User` model.

### 2. Centralized Nagging Logic
- [x] Update `catalyst_heartbeat` in `src/scheduler/jobs.py` to use `User.last_nag...` instead of in-memory dictionaries.
- [x] Add exception handling for `bot.delete_message` to avoid blocking if the message was already deleted by the user.
- [x] Update the db commit after sending the new message.

### 3. "Zero Tasks" Gentle Nudge
- [x] Add logic in `jobs.py` to check users without active sessions.
- [x] Check if their last `TimeLog` is older than 1 hour.
- [x] Check if `db.query(Task).filter_by(user_id=user.id, status='pending').count() == 0`.
- [x] Send new `NUDGE_ZERO_TASKS` prompt.

## 🏁 Completion Criteria
- When an active session pings, the previous ping is deleted.
- Users with 0 tasks who haven't worked in 1hr receive a gentle push to create a task, utilizing the same centralized delete-before-send mechanic.
