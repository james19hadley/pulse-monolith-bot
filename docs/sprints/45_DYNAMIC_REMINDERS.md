# Sprint 45: Dynamic Reminders & Celery ETA

**Status:** `Completed`
**Date Proposed:** 2026-04-29
**Objective:** Replace vague textual time periods for tasks with exact temporal reminders, and implement Redis/Celery ETA scheduling to proactively ping the user at the exact specified time without Database Polling.

## 🎯 Goals
- Transition `Task` entities from generic strings ("morning") to precise exact times (e.g., `14:30`).
- Leverage Redis Message Broker via `apply_async(eta=...)` for exact-second delivery instead of running a minute-by-minute database Watchdog.
- Improve AI extraction so it naturally parses "Remind me in 2 hours to call Bob" into the exact datetime.

## 📋 Tasks

### [Database & Models]
- [x] Drop or migrate `target_time_period` (String) in `Task` model.
- [x] Add `reminder_time` (DateTime, timezone-aware) to the `Task` model.
- [x] Add `is_reminder_sent` (Boolean, default False) to the `Task` model to prevent double-pinging.

### [AI & Prompts]
- [x] Update `AddTasksParams` in `src/ai/providers.py` to extract `reminder_time` as a specific ISO-8601 datetime or relative time offset.
- [x] Ensure the prompt knows the user's current local time to correctly calculate relative times ("in 2 hours").

### [Celery Scheduler (Event-Driven)]
- [x] Create `job_send_task_reminder` in `src/scheduler/jobs.py` that accepts a `task_id` and executes instantly.
- [x] Modify the AI intent handler to immediately dispatch the task to Redis using `job.apply_async(args=[id], eta=reminder_time)`.
- [x] Send a Telegram message to the user: "⏰ <b>Напоминание:</b> [Task Title]", then set `is_reminder_sent = True`.

### [Reporting Integration]
- [x] Update `cmd_tasks` or daily report generation to display the scheduled time next to the task.

## 🔒 Security & Architecture Notes
- We shifted from a **Database-Polling Watchdog** to **Redis ETA Scheduling**. This drastically reduces PostgreSQL queries (avoiding `SELECT * FROM tasks` every minute).
- Redis must be configured with persistence (AOF/RDB) to ensure ETA tasks survive a container restart.
- We must ensure we compare timezone-aware datetimes correctly (`user_tz` vs `UTC`).

## 🏁 Completion Criteria
- User says "Напомни в 14:15 позвонить Джону", a task is created, pushed directly into Redis ETA queue, and exactly at 14:15 local time the bot sends a push notification.