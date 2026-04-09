# Project Architecture & Nesting Logic

This document describes the structure of Projects in Pulse, how parent-child relationships work, and the proposed logic for "Boolean Composite Habits" (aka Master Quests).

## Current Structure

`Project` is the core entity representing both actionable habits and organizational folders.

- **`id`**: Unique identifier.
- **`title`**: Name of the project or habit.
- **`parent_id`**: Forms hierarchical nesting (`Project.id` -> `Project.id`). Allows unlimited depth (e.g., _Life > Health > Sport > Pushups_).
- **`target_value`**: Daily/weekly target amount (e.g., 3600 seconds or 10 pages).

### AI Routing Integration
The AI context injection pipeline (via `Gemini`) automatically passes all active projects strings (like `[14] Sport`) inside system prompts. This teaches the AI to intuitively extract `parent_project_id` and `new_parent_project_id` natively from unstructured text (e.g., "Add pushups under Sport").


## 1. Dual-Metric Tracking: Time vs. Custom Units

In Pulse, a single `Project` can simultaneously track both **time spent** (minutes/hours) and **absolute units** (pages, points, reps). This requires strict isolation in how metrics are updated to prevent data corruption.

### The Ledger (`TimeLog` Table)
Every time a user logs an entry (e.g., `+40m xv6` or `read 5 pages xv6 for 40m`), a new atomic row is created in the `TimeLog` table:
- `duration_minutes`: **Always** records the time spent (e.g., `40`).
- `progress_amount`: Records the custom unit amount (e.g., `5`). If no custom unit was provided (only time), this is safely `None`.
- `progress_unit`: The unit string (e.g., `pages`).

### The Cache (`Project` Table)
The `Project` model holds a cached state called `current_value`. 
- If a project uses a **time-based** unit (minutes/hours), logging time directly increments `Project.current_value`.
- If a project uses a **custom unit** (pages), only the `progress_amount` from the log increments `current_value`. If a user logs *only time* (`+40m xv6`), the `TimeLog` captures the 40 minutes, but `Project.current_value` completely ignores it. This ensures "pages" are isolated from "minutes".

---

## 2. Parent-Child Relationships & Aggregation

When calculating stats for a project (e.g., inside the Telegram UI `actions.py`), Pulse uses two distinct query patterns to respect the Dual-Metric system across hierarchies:

### Global Aggregation (Time Bubbles Up)
`Total Tracked Hours` is a dynamically calculated, recursively aggregated metric.
The system fetches the `Project.id` and recursively queries for all nested child `id`s down the tree. It then runs a query on the `TimeLog` table (`tree_logs`) matching *any* of those IDs.
- **Result:** Time spent on a child (e.g., "xv6 book") automatically bubbles up to the parent (e.g., "getting mid at cpp"), ensuring parent projects always reflect total time spent across all sub-tasks.

### Local Isolation (Units Stay Scoped)
Custom units and target progress (`pages`, `current_value`) are strictly localized. 
The system runs a separate query (`direct_logs`) strictly matching the exact `Project.id` in focus. 
- **Result:** Reading "5 pages" of "xv6 book" only updates the progress bar of the book itself. It does not artificially leak "5 pages" into the parent's metrics.

---

## Proposed Composite Habit Feature (Boolean Aggregation)

To fix the issue where completing nested items (_Pushups_, _Running_) should automatically check off a parent item without logging manual "duration" data to the parent:

We introduce `aggregation_type` on the `Project` model.

### 1. `aggregation_type = "sum"` (Default)

The parent is a standard folder. If you track 10 minutes on a child task, the AI / Dashboard will sum up total time:
`Parent Progress = Sum of Sub-Projects Progress + Any direct progress`

### 2. `aggregation_type = "boolean_all"` (Composite Requirement)

Ideal for "daily routine" parent items.
Example: **"Morning Routine"**
- Sub-task: Drink 1L Water
- Sub-task: 10 Pushups
- Sub-task: Read 5 pages

Here, "Morning Routine" does not have its own target_value in minutes. Rather, its completion is `True` ONLY if all active child projects have reached `progress >= target_value` on that day.
When the AI or UI evaluates today's progress, if `boolean_all` is met, a virtual "1 session" entry is automatically credited to the parent.

### 3. Execution Pipeline (Next Steps)

1. Add `aggregation_type = Column(String, default="sum")` to `src/db/models.py:Project`.
2. Update the `DailySummary` views to dynamically check children before marking a parent complete.
3. Expose this toggle in the `/edit` UI or let AI infer it when the user says "Create a composite project..."