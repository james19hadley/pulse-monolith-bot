# Sprint 44: Task Management & Weekly/Monthly Periodicity

**Status:** `Draft`
**Date Proposed:** 2026-04-29
**Objective:** Evolve the Bot into an Active Planner by introducing complex Target periodicities, explicit Task assignments with Estimated Time, and a Daily Review reflection.

## 🎯 Goals
- Implement temporal constraints on Target Goals (Daily, Weekly, Monthly).
- Expand current Inbox functionality into a structured "Inbox Review" flow during Evening Check-ins.
- Enable Advanced Task properties: estimated time, specific deadlines (before/after lunch, via AI Memory).

## 📋 Tasks

### 1. Goal Periodicity Migration
- [ ] Add `target_period_type` column (String, default `daily` or `None`) to `projects` table (using `target_period_type` ENUM: daily, weekly, monthly).
- [ ] Update `scheduler/jobs.py` to reset `current_value` / `daily_progress` based on the *correct* periodicity, taking into account `user.timezone`.
- [ ] Update UI to reflect "Weekly Target: X" instead of "Daily Targets:".

### 2. Task Architecture Expansion
- [ ] Add `estimated_minutes` (Int) and `time_period` (String) to the `tasks` table.

### 3. Evening Reflection / Morning Briefing
- [ ] Create an Interactive Report Flow trigger (`/review`).
- [ ] Extract today's Inbox items and ask: "Keep, Task, or Archive?".
- [ ] Allow user to type tomorrow's plan in raw text, parse it with LLM into distinct Task entities with `estimated_minutes`.
- [ ] Morning cronjob: send "Plan for the day" with a "Start Session" button on the first task.

## 🔒 Security & Architecture Notes
- Modifying the `projects` table requires careful tracking as existing records expect `daily_target_value` to clear at midnight. Weekly targets must clear at midnight Sunday (in local user time). Monthly targets clear on the 1st.

## 🏁 Completion Criteria
- User can create a project with a 10h/week target that doesn't reset on Tuesday.
- Inbox automatically empties nightly via an interactive review session.
- User can free-type a "Tomorrow's agenda" and get an organized actionable plan back in the morning.
