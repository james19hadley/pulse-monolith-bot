# Sprint 23: Proactive Nudging and Spoon-fed Tasks

**Status:** `Draft`
**Date Proposed:** March 27, 2026
**Objective:** Transform the bot from a passive tracker into an active "nanny" that proactively suggests predefined project tasks to the user to reduce task-switching friction.

## 🎯 Goals
1. Implement a system to store actionable step-by-step plans or tasks within a Project.
2. Create a proactive scheduled "Nudge" system that initiates conversation based on inactivity.
3. Design a conversational flow: Warm greet -> Offer options -> Spoon-feed specific next steps.
4. Sub-goal: Emulate "online status" awareness by tracking the user's last interaction with the bot.

## 📋 Tasks
### Core & Database
- [ ] Design and implement a `ProjectTask` or `NextSteps` schema to store actionable items linked to a `Project`.
- [ ] Create UI/Commands for the user to pre-load these tasks into their projects (user specifies the plan, bot just stores it).
- [ ] Add a `last_interacted_at` timestamp to the `User` model to track activity since Telegram Bot API cannot fetch user online status.

### Scheduler & Nudging Logic
- [ ] Create a Celery task that evaluates inactivity thresholds against the user's last interaction or active focus sessions.
- [ ] Integrate LLM to generate "warm" and highly personalized check-in messages (e.g., "Hey slacker, doing nothing?").
- [ ] Build the interactive custom keyboard flow: "Yes, what should I do?" -> Present suggested project -> Present specific predefined tasks.

## 🔒 Security & Architecture Notes
- Avoid spamming the user. Implement strict frequency capping for nudges (e.g., max 1-2 per day) and respect "Silence" / "Sleep" periods.
- Tasks are strictly parsed from the user's predefined list to prevent AI hallucination—the bot is a conduit for the user's own planning, not a manager inventing work.

## 🏁 Completion Criteria
- User can attach specific small tasks/milestones to a project.
- Bot triggers a spontaneous message after prolonged user inactivity.
- Bot successfully navigates the user through a flow that presents exact predefined tasks, successfully reducing "what do I do now" friction.
