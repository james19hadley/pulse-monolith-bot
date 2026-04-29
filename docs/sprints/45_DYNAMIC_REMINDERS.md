# Sprint 45: Dynamic Reminders & Task Watchdog

**Status:** `Draft`
**Date Proposed:** 2026-04-29
**Objective:** Replace vague textual time periods for tasks with exact temporal reminders, and implement a Celery Watchdog to proactively ping the user at the specified time.

## 🎯 Goals
- Transition `Task` entities from generic strings ("morning") to precise exact times (e.g., `14:30`).
- Build a generic Celery Watchdog that runs frequently (every 5-10 minutes) to check for pending reminders and dispatch them.
- Improve AI extraction so it naturally parses "Remind me in 2 hours to call Bob" into the exact datetime.

## 📋 Tasks

### [Database & Models]
- [ ] Drop or migrate `target_time_period` (String) in `Task` model.
- [ ] Add `reminder_time` (DateTime, timezone-aware) to the `Task` model.
- [ ] Add `is_reminder_sent` (Boolean, default False) to the `Task` model to prevent double-pinging.

### [AI & Prompts]
- [ ] Update `AddTasksParams` in `src/ai/providers.py` to extract `reminder_time` as a specific ISO-8601 datetime or relative time offset.
- [ ] Ensure the prompt knows the user's current local time to correctly calculate relative times ("in 2 hours").

### [Celery Scheduler]
- [ ] Create `job_task_reminders` in `src/scheduler/jobs.py` that runs every 5 minutes (using Celery Beat).
- [ ] Logic: Query all `Task` records where `status == 'pending'`, `reminder_time <= NOW()`, and `is_reminder_sent == False`.
- [ ] Send a Telegram message to the user: "⏰ <b>Напоминание:</b> [Task Title]", then set `is_reminder_sent = True`.

### [Reporting Integration]
- [ ] Update `cmd_tasks` or daily report generation to display the scheduled time next to the task.

## 🔒 Security & Architecture Notes
- Celery ETA tasks (`apply_async(eta=...)`) are vulnerable to being lost if Redis restarts/flushes. Therefore, we will use a **Database-Polling Watchdog** (a periodic task that checks the DB state). This is much safer for a persistent monolith.
- We must ensure we compare timezone-aware datetimes correctly (`user_tz` vs `UTC`).

## 🏁 Completion Criteria
- User says "Напомни в 14:15 позвонить Джону", a task is created, and exactly at 14:15 local time the bot sends a push notification.