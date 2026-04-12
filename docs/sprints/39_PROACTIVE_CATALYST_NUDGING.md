# Sprint 39: Proactive Catalyst Nudges & Evening Reflection

**Status:** `Completed`
**Date Proposed:** April 12, 2026
**Objective:** Add proactive reminders (Soft Ping) when sessions go idle, and add a smart, non-intrusive "Evening Reflection" conversational nudge that helps the user log unlogged progress and plan for tomorrow without manually typing commands.

## 🎯 Goals
1. Add a periodic Celery mechanism (`every 30 mins` or `1 hour`) to track inactivity during open sessions.
2. Provide a toggle inside `/settings` so users can customize or disable the proactive nudges.
3. Implement Smart Ping Replacement so unread nudges are deleted before sending new ones, keeping the chat clean.
4. Pass the nudge context to the AI Persona to generate natural, conversational gentle reminders.
5. Create an "Evening Reflection" trigger X minutes before the End of Day cutoff. The bot will proactively reach out ("How did you do on X today? What's your plan for tomorrow?"). If the user ignores it, it safely expires. If they reply, the AI auto-logs their answers.

## 📋 Tasks
### [Bug Fix Priorities]
- [x] Fix `NameError: name 'get_control_panel_data'` when untying the Target Channel.

### [Scheduler & Celery]
- [x] Create `job_catalyst_ping` in `jobs.py` to check for active sessions where the user hasn't messaged within the $CatalystLimit$ window.
- [x] Create `job_evening_reflection` designed to run X minutes before the user's `day_cutoff_time`.

### [Settings & Configuration]
- [x] Ensure `catalyst_limit` logic functions properly in the UI (`system_configs.py`).
- [x] Allow users to completely disable the ping. (Set to 0)
- [x] Add a configuration for "Reflection Time" (Implicitly 30 mins before customizable cutoff) (e.g., 30 mins before cutoff).

### [AI Nudge Generation & UX]
- [x] Implement deleting the prior sent nudge (requires holding `last_ping_message_id` in User or Session context).
- [x] Implement Evening Reflection logic to handle user goals and progress naturally inside `ai_router.py`. (Standard NLP implicitly handles it)

## 🔒 Security & Architecture Notes
- Must ensure that Celery checking does not spam Google API keys if thousands of users are idle at the same time. AI generation should only happen when a ping *needs* to be sent right now.
- If deleting the previous message fails (e.g. older than 48h limit in some Telegram versions), gracefully catch `TelegramBadRequest` and ignore.
- The Reflection should just use standard NLP routing. It prompts the user, the user responds freely, and the NLP extracts LOG_HABIT or LOG_TIME.

## 🏁 Completion Criteria
- A user can be idle for 1 hour, receive a nudge, stay idle for another hour, and find the first nudge naturally replaced with a new one.
- Before sleep, the bot asks "How went the day and what's next?", the user replies "I read 5 pages, plan to sleep", and the bot silently auto-logs 5 pages and schedules tomorrow's thought.
