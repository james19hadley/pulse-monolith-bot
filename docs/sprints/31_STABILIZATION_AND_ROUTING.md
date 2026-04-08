# Sprint 31: Stabilization & Routing Fixes

**Status:** `Completed`
**Date Proposed:** April 8, 2026
**Objective:** Resolve high-friction bugs, fix notification routing between DMs and linked channels, and stabilize the core experience before adding new functionality.

## 🎯 Goals
- **Smart Notification Routing:** Bot currently sends everything (reports, morning plans, private nudges) to the linked channel. We need to split this: Public/Accountability to Channel, Private/Nudges to DM.
- **Fix Broken Settings:** Channel unlinking does not properly clear the DB state or UI state.
- **Undo Audit:** Revisit the Undo action log stack to ensure all recent data model changes (like absolute progress vs relative delta) can be safely reverted without mathematical errors.
- **Cron Timing Accuracy:** Verify that scheduled celery tasks actually trigger at the correct local user time without offsetting due to server timezone defaults.

## 📋 Tasks

### 1. Routing & Channels
- [x] Audit `src/scheduler/jobs.py` and replace `target_chat_id = user.target_channel_id or user.telegram_id` with strict logic based on notification type.
- [x] Ensure Morning Planner and Evening Nudge ONLY go to `user.telegram_id`.
- [x] Ensure Daily Accountability Report goes to `user.target_channel_id` (if set), otherwise fallback to DM.
- [x] Review `src/bot/handlers/settings/general.py` and fix the "Unlink Channel" callback to properly nullify the DB value and refresh the session.

### 2. Time & Progress Logic Fixes
- [x] Investigate the exact Celery beat UTC edge cases that caused posts to arrive at the wrong hour. Add comprehensive python-level timezone conversion tests if necessary.
- [x] Audit "Empty Project" rendering. If a project has 0 total progress, does it look buggy? Implement empty state safeguards.

### 3. Smart Undo Audit
- [x] Audit `src/bot/handlers/intents/intent_undo.py` for comprehensive test coverage against the new absolute tracking feature.
- [x] Ensure that undoing a "Target Completion" correctly restores the daily targets and total completion counts (both up and down).

## 🔒 Security & Architecture Notes
- No new tables are needed. Just strict data patching.
- Ensure all datetime references explicitly use `timezone.utc` and convert gracefully using python's `zoneinfo`.

## 🏁 Completion Criteria
- User can link AND unlink a channel seamlessly.
- Bot triggers morning nudge in private messages, and evening report in the public channel.
- Empty progress projects render elegantly without newlines.
- Undo reliably reverses target completions and preserves mathematical consistency.
- User can log work and immediately press "Undo" without breaking constraints.