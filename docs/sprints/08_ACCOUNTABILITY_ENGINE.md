# Sprint 08: Accountability Engine & Daily Reports

**Status:** 🟡 Active
**Date Proposed:** March 23, 2026

**Objective:** Fulfill the final core MVP requirement by enabling the bot to act as a channel admin that automatically aggregates and posts a daily summary of the user's progress.

## 🎯 Goals
- Allow users to bind the bot to a specific Telegram Channel for public/private accountability.
- Build an aggregation engine that collects today's TimeLogs, completed Habits, and Inbox notes.
- Use the AI (Gemini) to format this raw data into a beautiful, persona-driven "Evening Report".
- Automate the posting using the scheduler or allow manual triggers.

## 📋 Tasks

### 1. Channel Binding
- [ ] Add `target_channel_id` (String or Integer) to the `User` DB model.
- [ ] Create a `/bind_channel` command or a natural language intent so the user can register their accountability channel.

### 2. Stats Aggregation
- [ ] Create a database utility function that queries all activity between `start_of_day` and `day_cutoff_time`.
- [ ] Calculate total focused time, list of updated habits, and new inbox items.

### 3. The Daily Report (AI Generation)
- [ ] Create a new prompt in `prompts.py` that instructs the LLM to format the daily stats into a cohesive report.
- [ ] Update `router.py` / `handlers.py` to support generating this report (e.g., via `/report` command).

### 4. Automation (Scheduler)
- [ ] Add a new job in `jobs.py` that runs daily at `user.day_cutoff_time`.
- [ ] Let the bot automatically send the generated report to the designated `target_channel_id`.

## 🏁 Completion Criteria
- User can link a channel.
- User can type `/report` to instantly receive a nice summary of the day.
- Bot automatically posts the report to the channel at the end of the day.
