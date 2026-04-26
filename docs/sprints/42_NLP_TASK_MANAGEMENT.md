# Sprint 42: NLP Task Management, Smart Nudges & Context Injection

**Status:** `Completed`
**Date Proposed:** 2026-04-26
**Objective:** Enable the AI to fluidly converse about and manipulate the user's pending tasks. Revamp the Catalyst Nudge system to use "Smart Chunking" — requiring a meaningful natural language justification from the user to log elapsed time.

## 🎯 Goals
- Give the AI constant awareness of the user's active projects and pending tasks during normal chat.
- Support NLP-based completion, deletion, and editing of tasks via simple ordinal numbers (1, 2, 3...).
- Implement "Smart Nudge": Nudges will ask "What did you accomplish?". If the user replies with a meaningful update, the AI logs a TimeLog chunk and keeps the session running.
- Provide "Smart End" fallback buttons on the Nudge (e.g., "End Now", "Ended 1h ago").

## 📋 Tasks

### [AI Integration & Tasks]
- [ ] Inject `tasks` and `projects` (with DB IDs) into `_handle_chat`'s system context so the AI can answer "what are my tasks?".
- [ ] Update `EditEntitiesParam` in `src/ai/providers.py` to allow `entity_type: 'task'` and add `new_status` field.
- [ ] Update `_handle_edit_entities` in `intent_entities.py` to process `task` entities (completing, cancelling, deleting).

### [Smart Nudge Mechanics]
- [ ] Modify `job_catalyst_heartbeat` to send a prompt requiring text input rather than just a "I'm working" button.
- [ ] Implement NLP interception: When the user replies to a nudge with their progress, parse the time elapsed since the last log, create a `TimeLog` chunk with their description, and continue the session.
- [ ] Add explicit "End Session Now" and "Ended 1 hour ago" buttons to the nudge for retroactive session correction.

### [UI / Output]
- [ ] Update `/tasks` command UI (`src/bot/handlers/core.py`) to use ordinal numbers (1, 2, 3) instead of bullet points, making them easy to reference.

## 🔒 Security & Architecture Notes
- The AI must return the `DB_ID` of the task when editing, not the ordinal number. We will provide the mapping in the prompt.
- Nudge chunks should use the elapsed time from either `session.start_time` or the latest `TimeLog.created_at`.

## 🏁 Completion Criteria
- User can say "Complete task 1" and the AI correctly updates the DB.
- Nudges successfully force the user to type what they did, which converts into a discrete `TimeLog` chunk inside the running session.
