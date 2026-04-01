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