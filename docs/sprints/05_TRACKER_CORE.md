# Sprint 05: The Tracker Core & "The Void"

**Status:** 🟡 Active
**Objective:** Replace temporary dev commands with official UX. Implement the core psychological feature of the bot: calculating "The Void" at the end of a session.

## 🎯 Goals
- Give the user the ability to view, create, and manage active Projects.
- Calculate and display "The Void" (Lost time = Total Session Time - Focused Logging Time) upon ending a session.

## 📋 Tasks
- [ ] Add `/projects` command to list all active projects with their IDs and current total time.
- [ ] Upgrade `/new_project` to have proper edge-case handling and integrate its response into `views.py`.
- [ ] Update `cmd_end_session` logic:
  - Calculate `total_session_time`.
  - Query all `TimeLog` entries linked to that `session_id` and sum their `duration_minutes`.
  - Calculate `void_time = total_session_time - active_time`.
  - Display the final mathematical breakdown to the user via a clean view.

## 🏁 Completion Criteria
- User can start a session, log 30 minutes, wait 60 minutes, end the session, and see a summary stating they had 30 mins of Focus and 30 mins of The Void.
