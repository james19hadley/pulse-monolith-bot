# Sprint 39: Proactive Catalyst Nudges

**Status:** `Active`
**Date Proposed:** April 12, 2026
**Objective:** Enhance the background scheduler to identify when the user falls silent and automatically send a contextual nudge (Soft Ping), along with settings to manage the frequency.

## 🎯 Goals
1. Add a periodic Celery mechanism (`every 30 mins` or `1 hour`) to track inactivity during open sessions.
2. Provide a toggle inside `/settings` so users can customize or disable the proactive nudges.
3. Implement Smart Ping Replacement so unread nudges are deleted before sending new ones, keeping the chat clean.
4. Pass the nudge context to the AI Persona to generate natural, conversational gentle reminders.

## 📋 Tasks
### [Bug Fix Priorities]
- [x] Fix `NameError: name 'get_control_panel_data'` when untying the Target Channel.

### [Scheduler & Celery]
- [ ] Create `job_catalyst_ping` in `jobs.py` to check for active sessions where the user hasn't messaged within the $CatalystLimit$ window.

### [Settings & Configuration]
- [ ] Ensure `catalyst_limit` logic functions properly in the UI (`system_configs.py`).
- [ ] Allow users to completely disable the ping.

### [AI Nudge Generation & UX]
- [ ] Implement deleting the prior sent nudge (requires holding `last_nudge_msg_id` in User or Session context).

## 🔒 Security & Architecture Notes
- Must ensure that Celery checking does not spam Google API keys if thousands of users are idle at the same time. AI generation should only happen when a ping *needs* to be sent right now.
- If deleting the previous message fails (e.g. older than 48h limit in some Telegram versions), gracefully catch `TelegramBadRequest` and ignore.

## 🏁 Completion Criteria
- A user can be idle for 1 hour, receive a nudge, stay idle for another hour, and find the first nudge naturally replaced with a new one.
