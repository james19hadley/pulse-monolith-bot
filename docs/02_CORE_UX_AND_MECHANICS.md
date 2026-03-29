# `02_CORE_UX_AND_MECHANICS.md`

## 1. The Session-Based Tracking Model
The system MUST NOT track the user's entire 24-hour day. Tracking the whole day includes personal time, breaks, and sleep, which inevitably ruins productivity metrics and induces the "guilt spiral."
Instead, the bot uses **Work Sessions**. The user's life outside a session is completely private and unmonitored.

### 1.1. Starting a Session
*   **Action:** The user explicitly sends a command (e.g., `/start_session` or types "I'm starting a work block").
*   **System Response:** The bot records the exact `start_time` in the database. It replies with a dry confirmation: *"Session initiated. Monitoring active."*
*   **Effect:** The background scheduler (Heartbeat) is activated. The bot will now begin its periodic pinging.

### 1.2. Ending a Session
*   **Action:** The user sends `/end_session` or says "I'm done for now."
*   **System Response:** The bot calculates the total duration of the session. It sums up all the "focused work" logged during this specific window. 
*   **The Math of "The Void":** 
    *   `Total Session Duration` = `end_time` - `start_time`.
    *   `Focused Time` = Sum of all logged micro-reports (e.g., 40 mins on Project A + 20 mins on reading).
    *   `The Void (Lost Time)` = `Total Session Duration` - `Focused Time`.
*   **Output:** The bot replies locally in the chat with a summary of the session: *"Session closed. Total time: 4h. Focused: 2h 30m. The Void: 1h 30m."*

## 2. The Soft Ping (The Catalyst Mechanism)
This is the core pro-active feature of the bot. It is designed to nudge the user without becoming a spammy "graveyard of notifications."

*   **Trigger:** Within an *active session*, if the user has not sent any messages for 1 hour (configurable), the background job triggers a ping.
*   **The Nudge (Next Action):** The ping is NOT a generic "What are you doing?". The bot queries the database for an `active` project and its defined `next_action`. 
    *   *Example Bot Message:* "1 hour has passed. Your next step for [Project: C++ RPG] is[Read chapter on Pointers - 1 hour]. Is this still accurate, or are you doing something else?"
*   **THE KILLER UX FEATURE (Ping Replacement):** 
    *   Before sending a new ping, the bot MUST check if there is an unanswered ping previously sent.
    *   If yes, the bot **DELETES** the old ping from the Telegram chat history before posting the new one. 
    *   *Psychological Reason:* When the user opens Telegram after 3 hours of doomscrolling, they will only see ONE calm message, not a wall of 3 missed alarms. This removes shame and lowers the barrier to reply.

## 3. Micro-Reporting & Free-Form Input
The user interacts via natural language. There are no UI buttons or strict `/log` formats required for daily use.

*   **Input:** User types: *"I coded for 40 minutes and then did 10 pushups."*
*   **Processing:** The bot's AI Router identifies the intents (`LOG_TIME` and `LOG_HABIT`). It silently updates the database via Tool Calling (updating Project time by +40, updating Project counter by +10).
*   **Output:** The bot does not generate conversational fluff (e.g., "Great job! You are doing amazing!"). It responds with a factual confirmation: *"Logged: 40m to C++. Logged: 10 Pushups."* 

## 4. The Evening Report (The "Kompromat" & Channel Publishing)
The ultimate accountability mechanism. The bot summarizes the entire day (all closed sessions) and publishes a standardized report to a designated external Telegram channel.

### 4.1. Publishing Triggers
There are two ways the report is generated:
1.  **Active Trigger:** The user sends `/end_day`.
2.  **Passive Trigger (The Kompromat):** A cron job runs at a user-defined `day_cutoff_time` (e.g., 03:00 AM). If the user fell asleep, got distracted, or is hiding from the bot, the system forcefully closes any open sessions, calculates the stats, and posts the report automatically. *You cannot hide.*

### 4.2. Report Formatting
The report is strictly standardized, markdown-formatted, and completely devoid of LLM hallucinations or emotional commentary. It is constructed via Python logic, not AI generation.

**Structure Example:**
```markdown
# ⬛ Pulse Monolith: Daily Sync [Date]

**Time Metrics:**
* Total Session Time: 6h 00m
* 🟩 Focused Time: 4h 15m
* ⬛ The Void (Lost Time): 1h 45m

**Active Quests (Projects):**
* C++ Text RPG: +2h 00m -> [Total: 8h / 30h] 🟩🟩⬜⬜⬜
* Infrastructure Setup: +2h 15m -> [Total: 5h / 10h] 🟩🟩🟩⬜⬜

**Daily Routine (Projects):**
* Pushups: 10/10 ✅
* Read 10 Pages: 0/10 ❌
```

## 5. Inbox (The Brain Dump)
To prevent the user from context-switching or opening Notion, the bot accepts raw ideas.
*   **Action:** User says *"Idea: add a Stripe payment gateway later."*
*   **Processing:** AI flags intent as `ADD_INBOX` and saves it to the database.
*   **Retrieval:** The user can command `/inbox` to get a simple list of unmanaged thoughts. These do NOT clutter the daily project reports.

## 7. The Persona Engine (System Prompts)
The system does not have a rigidly hardcoded personality. The user needs a safe environment that can adapt to their current state. For some tasks, a dry machine is needed; for others, a sarcastic partner.

*Crucial Rule:* The persona only affects free-form conversations (intent `CHAT_OR_UNKNOWN`) and the styling of the Evening Report. For routine logging (`LOG_WORK`), the bot always replies with 1-2 words to save tokens.

### 7.1. Available Archetypes
When assembling the LLM context, the Python backend injects one of the following System Prompts based on `Users.persona_type`:

1.  **The Monolith (Default):** "You are Monolith Pulse. A dry, impartial system interface. You give no moral judgments. No praise, no scolding. You are a mirror reflecting facts, metrics, and time. Keep answers extremely concise."
2.  **TARS (Interstellar):** "You are TARS, a tactical AI assistant. You speak to the user as a trench partner. Use military/space terminology. You are direct, with a touch of dry machine sarcasm if the user is lazy, but always constructive and mission-focused."
3.  **FRIDAY / JARVIS (Iron Man):** "You are FRIDAY, an advanced analytical AI. Call the user 'Boss'. Focus on system optimization, time calculation, and efficiency. Polite, helpful, using technical language (probabilities, completion stats)."
4.  **Alfred Pennyworth:** "You are Alfred, a loyal British butler. Your goal is the user's well-being. If the user rests, call it 'strategic recovery, sir'. Courteous, aristocratic, always finding ways to boost morale."
5.  **Custom:** Uses the string stored in `Users.custom_persona_prompt`.

### 7.2. Switching Mechanics
Changing persona is handled via Tool Calling, not text generation.
*   **Action:** User says *"Switch to TARS mode."*
*   **Routing:** AI Intent Router classifies as `SYSTEM_CONFIG`.
*   **Execution:** LLM calls `update_persona(persona_type="tars")`. Database is updated, and the bot replies in the new voice.
