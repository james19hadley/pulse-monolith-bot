# Sprint 29: Project Hierarchies (Main Quests & Sub-quests)

**Status:** `Draft / Architecture Approved`
**Date Proposed:** March 29, 2026

## 🎯 Motivation: Why do we need this?
Currently, all projects exist as a flat list. If a user wants to achieve a massive goal like "Learn Data Science (120 hours)", they have to either log everything into a single giant project (which makes it hard to track what *exactly* was done today, e.g., "Pandas" vs "Math") OR create many small isolated projects, which clutters the UI and lacks a sense of "Global Completion". 

**Gamification relies on "Epic Quests".** By allowing sub-projects to feed into a Master Project, the user can see daily granular work (like reading a specific book) naturally filling up a massive life goal.

## ✨ Features Unlocked
1. **Master-Quest Progress:** Logging 2 hours to a sub-project automatically bubbles up, showing the Master Project is now 2 hours closer to its 120h goal.
2. **Beautiful Grouped Reports:** Evening reports will render a nested tree structure (e.g., Main Project at the top, indented sub-projects below it), making the report infinitely more readable than a random flat list.
3. **Clean UI:** Sub-projects can be filtered or "folded" under their Master Project in menus to unclutter the main "Projects" list.

## 🗂️ Nesting Level Support
- **Database Schema:** Infinite. The schema uses a standard self-referential `parent_id` design.
- **UI/UX Level (Restriction):** Up to **2 levels of nesting** (Epic -> Main Quest -> Sub-quest).

### 📱 Telegram UI Organization (Breadcrumb Navigation)
To handle 2 levels of nesting without overwhelming the user, the inline menu will act like a file explorer:
1. **Main Projects List:** Shows ONLY "Root" projects (where `parent_id` is Null).
2. **Project View:** Inside a Root project's settings, we add a `📂 Sub-projects (3)` button.
3. **Breadcrumbs:** Clicking into a child project changes the back button logic to walk up the tree: `🔙 Back to [Parent Name]`.
4. **Creation:** When creating a new project, you can create it globally or click `➕ Add Sub-project` right from inside an existing project's menu.

## 🏛️ Architecture & Data Storage

### 1. The Relation (How they depend on each other)
Sub-projects are linked to their parent via a standard Foreign Key.
- `parent_id: INTEGER REFERENCES projects(id) ON DELETE SET NULL`
If a Master Quest is deleted, its sub-quests don't disappear, they just become unbound root projects (or we can prompt the user to archive them).

### 2. "Compute, Don't Store" (The Single Source of Truth)
We have selected **Variant 1**. The Parent Project never physically stores the sum of its children's hours in the database.
- **Why:** To guarantee mathematical purity and 0 bugs. If a user edits or deletes an old time log from a sub-project, the parent project's total is immediately and automatically correct without requiring complex cascading updates, CRON recalculations, or rollback logic.
- **How it works:** When generating a report or menu, the system runs a single optimized SQL query: `SUM(duration_minutes) FROM time_logs WHERE project_id IN (self_id, child_1_id, child_2_id)`. For personal workloads (<100,000 logs), this execution time is ~1 millisecond.

### 3. Mixed Units Fallback
If a Master Project tracks hours, but a Sub-Project tracks "pages", the Master Project simply sums the `duration_minutes` attached to the Sub-Project's TimeLogs. Pages remain isolated logically to the Sub-Project.

## 📋 Implementation Steps
- [ ] **DB:** Add `parent_id` to `Project` model and generate Alembic migration.
- [ ] **Engine:** Write `get_project_tree()` query aggregator.
- [ ] **UI:** Add `🔗 Link to Master Project` button in Project Settings.
- [ ] **UI:** Update `generate_daily_report_text` in `utils.py` to draw tree nodes (`├─` and `└─`).
