# Sprint 24: Frictionless Open Sessions & Save-State Rest Mode

**Status:** `Draft`
**Date Proposed:** March 27, 2026
**Objective:** Replace rigid realtime timer constraints with intention-based open sessions, retroactive "Check-out" negotiations, and contextual "Save-State" rests to completely eliminate tracking friction.

## 🎯 Goals
1. Allow users to start open-ended tracking without rigid pre-commitments (e.g., "Started working on Project 1").
2. Implement retroactive "Split the bill" (Check-out negotiation) to account for natural distractions without causing guilt.
3. Introduce "Save-State" rest mode to offload mental context during breaks.
4. Issue immediate "Dopamine Receipts" acknowledging earned progress before breaks.
5. Create contextual Guardrail Pings to rescue forgotten sessions.

## 📋 Tasks

### 1. Open-Ended Sessions & Split-The-Bill Negotiation
- **Start Concept**: User types *"Sat down to code"*. Bot starts session, remains silent.
- **Finish Concept**: User types *"Finished"*. Bot evaluates total elapsed time (e.g., 2h 40m).
- **The Negotiation**: Bot asks: *"Total time was 2h 40m. How much of this was pure Deep Work, and how much do we write off to The Void?"*
- **Psychology**: Validates the fact that humans get distracted. Allows user to honestly retroactively split the pie post-factum without scrambling to hit a "Pause" button during the actual work.

### 2. "Save-State" Rest Mode ⏸️ & Dopamine Receipts
- **Concept**: User says *"Taking a break, stopped at fixing the SQL query"*.
- **Dopamine Receipt**: Bot immediately rewards the preceding effort: *"Acknowledged. Locked in 1h 20m of Deep Work. You've invested 3.5h total today. Go breathe."* This makes notifying the bot a rewarding act, not a chore.
- **Save-State Storage**: The exact phrase ("stopped at fixing SQL query") is saved to the active session state.

### 3. Contextual Rest Nudges (Guardrails)
- If the user is in "Rest Mode" for too long (e.g., >30 mins), the bot pings them, quoting their mental Save-State to reduce the friction of re-entry.
- **Example Ping**: *"Alarm, the break is dragging on. You stepped away 30 minutes ago. Your Save-State: «fixing the SQL query». Are we sitting down to finish, or punching out for the day?"*

### 4. Mid-Session Guardrails
- If a session runs for >2 hours with ZERO communication, bot softly checks in: *"You've been in the Project 1 context for 2 hours. Still in flow, or drifted away? Let's close the session if you are done."*

## 🔒 Security & Architecture Notes
- This overhauls the current `stale_session_killer` logic.
- Requires robust NLP state parsing in `ai_router` to handle "negotiation" turns where the LLM parses the user's split (e.g., "I worked 2 hours, 40 mins was void").

## 🏁 Completion Criteria
- User can start and end sessions purely conversationally.
- The bot successfully asks the user to retroactively split long sessions into Focus and Void.
- The bot can accept a textual "Save-State" and playback the context in a delayed reminder.
