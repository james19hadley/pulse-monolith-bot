# Sprint 23: Proactive Nudging and Spoon-fed Tasks

**Status:** `Draft`
**Date Proposed:** March 27, 2026
**Objective:** Transform the bot from a passive tracker into an active "Butler/Nanny" that proactively suggests predefined project tasks to the user to reduce task-switching friction.

## 🎯 Goals
1. Implement a system to store actionable step-by-step plans or tasks within a Project.
2. Create a proactive scheduled "Nudge" system that initiates conversation based on inactivity.
3. Design a conversational flow: Warm greet -> Offer options -> Spoon-feed specific next steps.
4. Emulate "online status" awareness by tracking the user's last interaction with the bot.
5. Implement "Pedagogical Evening Chats" for habit accountability.

## 📋 Tasks
### 1. Spoon-fed Project Tasks
- Design and implement a `ProjectTask` or `NextSteps` schema.
- Create UI/Commands to pre-load plans into projects.
- *Psychology*: The user struggles with "what to do next". The bot removes this friction by spoon-feeding predefined tasks ("Would you like to do X for 40 mins?").

### 2. Emulated Online Status
- Add a `last_interacted_at` timestamp to the `User` model.
- Because Telegram doesn't provide real-time online status, the bot will use recent interactions as a proxy for "the user is awake and active".

### 3. Daytime Proactive Nudges
- Create a Celery task evaluating inactivity against `last_interacted_at`.
- Integrate LLM to generate "warm" check-in messages.
- *Constraint*: Must strictly respect timezone/working hours. No nighttime pings. Frequency capping (max 1-2 per day).

### 4. Pedagogical Evening Chats 🦉
- If a habit hasn't been logged for 2+ days, the bot initiates a coaching conversation in the evening.
- Example: *"You haven't done X, what is blocking you?"*
- Again, strictly isolated to evening hours, respecting sleep schedules.
