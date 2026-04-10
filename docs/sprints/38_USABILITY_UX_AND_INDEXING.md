# Sprint 38: Usability, UX, and Active Indexing

**Status:** `Completed`
**Date Proposed:** April 9, 2026
**Objective:** Resolve immediate usability annoyances, prevent UI buttons from triggering false NLP intents, surface tasks to the top level, and implement dynamic short IDs for active projects.

## 🎯 Goals
1. Intercept UI buttons (like `📥 Inbox`) so they trigger their native handlers rather than being fed to the AI as text input.
2. Teach the AI to properly respond to queries about the user's project status (e.g., "какая ситуация с проектами") with actual data rather than generic filler.
3. Bring Task Management out of the deep project menus and expose it on the Main Menu.
4. Ensure the proactive "ping" heartbeat is actually firing during working hours when the user has no tasks.
5. Create a dynamic "Short ID" mapping for active projects so users don't have to type 3-digit global database IDs (e.g., mapping Active DB_ID 19 to Local_ID 1).

## 📋 Tasks

### 1. Keyboard Interceptors & False Positives
- [ ] Add explicit text matchers (or a pre-router filter) in `ai_router.py` or `views.py` to catch `📥 Inbox`, `📊 Stats`, `🎯 Projects` and route them to their respective visual handlers rather than `get_intent`.

### 2. Conversational Status Awareness
- [ ] Add an intent `GET_STATUS` or expand the system prompt/routing so that statements like "какая ситуация с проектами" trigger a comprehensive project summary/daily report rather than a generic `CHAT_OR_UNKNOWN` response.
- [ ] Alternatively, provide the `CHAT_OR_UNKNOWN` prompt with the actual list and status of projects so the persona can answer naturally.

### 3. Surface Tasks UI
- [ ] Add a `📋 Tasks` button to the main `ReplyKeyboardMarkup`.
- [ ] Implement a handler that shows a global overview of active tasks across all projects, or tasks without projects.

### 4. Dynamic Short IDs (Local Indexing)
- [ ] In `ai/providers.py` and across UI rendering, implement a mapping function for active projects (e.g., sort by ID, assign 1 to N).
- [ ] When showing projects to the user, display the Short ID (e.g., "• 1. Computer Systems").
- [ ] When sending context to the LLM, pass the mapping so the LLM knows that "Project 1" refers to database ID 19.

### 5. Proactive Nudging Audit
- [ ] Review `job_catalyst_heartbeat` in `src/scheduler/jobs.py`.
- [ ] Ensure that working hours (start/end) are validating correctly against the user's configured timezone.
- [ ] Fix the logic so it actively prompts the user to add tasks if their task list is entirely empty during the active workday.

## 🏁 Completion Criteria
- Tapping `📥 Inbox` opens the inbox rather than saving the word "Inbox".
- Asking "какая ситуация с проектами" shows a report with 0-progress projects.
- Active projects have IDs like 1, 2, 3 instead of 19, 21.
- Global tasks are accessible from the main menu.
- Heartbeat successfully nags the user if no tasks exist during working hours.

### 6. Fix `/stats` Silent Failure
- [x] Investigate why the `/stats` command (or the `📊 Stats` button) returns nothing and fails silently.
- [x] Fix the handler to ensure it properly generates and sends the statistics report.

### 7. Timezone & Delayed Execution Bug
- [x] Investigate the scheduler/Celery jobs (`src/scheduler/jobs.py` or similar) where the channel posting time is calculated.
- [x] Fix the timezone discrepancy that causes posts to occur a couple of hours later than configured, ensuring timezone-aware math is used correctly.

### 8. End of Day & Statistics Reset Alignment
- [x] Audit `midnight_reset_job` and `daily_accountability_job` in `src/scheduler/jobs.py` to ensure the daily progress reset happens correctly and explicitly AT the configured `day_cutoff_time` (even if it's after midnight).
- [x] Ensure race conditions don't occur where stats are wiped before the daily report is generated.

### 9. Report Formatting & Structure Configuration
- [x] Implement UI or NLP settings to change the format/style of the daily report (e.g., Emoji vs Strict, selecting specific blocks like focus/projects/inbox).
- [x] Audit the report generation code to ensure it's flexible and actually respects the user's `report_config` setting, and make it interactive/configurable via the bot (perhaps via `/settings` or `/report_config`).
