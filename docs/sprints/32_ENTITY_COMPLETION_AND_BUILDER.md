# Sprint 32: Entity Completion & Dynamic Report Builder

**Status:** `Completed`
**Date Proposed:** April 8, 2026
**Objective:** Finalize the half-finished "Tasks" implementation and provide a dynamic, LLM-guided interface for customizing the Evening Report.

## 🎯 Goals
- **Full Task Lifecycle:** The `Task` table exists, but UI integration stopped midway. We need CRUD ops exclusively for tasks via Telegram Inlines and AI parsing.
- **Connect Tasks to Strategy:** Morning Planner should pull from these specific Tasks to suggest "Today's Focus".
- **Dynamic Report Builder:** Users should be able to toggle what stats appear in their nightly report (e.g., hiding 0-minute projects, toggling progress bars, showing/hiding absolute hours).

## 🧠 UX Psychology & Philosophy (Tasks vs Projects)
**CRITICAL CONTEXT FOR DEVELOPMENT:**
We are **NOT** building a Jira backlog or a GTD to-do list. Standard to-do lists cause cognitive overload and anxiety. 
- **Projects** track metrics, time, and progress ("How much have I invested?").
- **Tasks** act as the "Next Physical Action". They exist purely to reduce friction when starting a session. 
- **The "Spoon-feeding" Mechanic:** The bot must act as a gentle nanny. Instead of dumping 50 pending tasks on the user, the Morning Planner (or proactive ping) should look at the database and elegantly extract just 1-3. "Good morning. The next step for Project X is Y. Should we tackle that?"
- **Single-tasking Focus:** The goal is to hold only 1 task in the user's active attention window. Do not build UI that encourages hoarding hundreds of tasks.

## 📋 Tasks

### 1. Task Management UI
- [x] Add explicit "📋 Tasks" button handling in `projects.py` to open a list of pending tasks for a project.
- [x] Implement Add/Complete/Delete inline buttons for individual tasks.
- [x] Teach the AI Intent Router to extract task creation (e.g., "Add buy milk to Project X tasks").

### 2. Morning Planner Integration
- [x] Refactor `job_morning_planner` to grab 1-3 pending Tasks from the DB and pass them to the LLM for a curated morning message.

### 3. Dynamic Report Builder
- [x] Add `📊 Report Format` button to master settings.
- [x] Create an interactive toggler keyboard (e.g., `[x] Show zeros`, `[x] Hide exact hours`, `[x] Show Sub-tasks`).
- [x] Update `views.py` `build_daily_report` to conditionally render text blocks based on the `user.report_config` JSON.

## 🔒 Security & Architecture Notes
- `report_config` should be validated as a Pydantic model before saving into the JSONB DB column to prevent rendering crashes.

## 🏁 Completion Criteria
- User can add a task, see it in the project UI, and mark it complete.
- User can toggle off "Show Zeros" and the evening report immediately reflects the change.