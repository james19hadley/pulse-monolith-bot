# Sprint 46: Task Durations & UX Optimization

**Status:** `Completed`
**Date Proposed:** 2026-04-29
**Objective:** Add estimated duration support to tasks and improve the UX of the `📋 Tasks` view so it displays durations and formatted reminder times.

## 🎯 Goals
- Allow users to specify expected durations for tasks (e.g., "1.5 hours", "30 mins").
- Modify the DB `Task` schema to store `estimated_minutes`.
- Enhance the UI for the `/tasks` command so the user can easily see estimated load and times.
- Ensure the morning planner pulls task durations to inform the user of the day's total workload.

## 📋 Tasks

### [Database & Models]
- [ ] Add `estimated_minutes` (Integer, nullable) to the `Task` model.
- [ ] Create a patch script `patch_task_duration.py` to alter the database table without a full wipe.

### [AI & Prompts]
- [ ] Update `AddTasksParams` and `TaskParam` in `src/ai/providers.py` to extract `estimated_minutes` from text.

### [UI & Views]
- [ ] Update `cmd_tasks` in `src/bot/handlers/core.py` to cleanly format the tasks list including duration (e.g. "1h 30m") and reminder time if scheduled.
- [ ] Incorporate task durations into `job_morning_planner` to give a summary of the day's load.

## 🔒 Security & Architecture Notes
- The patch script must use `AUTOCOMMIT` as learned in Sprint 44/45 to prevent transaction lock errors.

## 🏁 Completion Criteria
- User says "Добавь задачу 1.5 часа упражнения к книжке", the task is saved with `estimated_minutes=90`.
- The `/tasks` UI cleanly displays the 90 minutes.