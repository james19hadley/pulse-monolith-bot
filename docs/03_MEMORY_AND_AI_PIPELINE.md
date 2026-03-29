# `03_MEMORY_AND_AI_PIPELINE.md`

## 1. The Two-Step AI Pipeline (Routing & Execution)
To optimize API costs, latency, and accuracy, the system does NOT send every user message to a heavy, expensive LLM. We utilize a two-step pipeline.

### Step 1: The Intent Router (Fast & Cheap)
Every incoming message first hits a lightweight model (e.g., Gemini Flash-Lite or GPT-4o-mini).
*   **Goal:** Determine what the user wants to do. No text generation allowed.
*   **Output:** A strict JSON string categorizing the intent.
*   **Categories:** `LOG_WORK`, `LOG_HABIT`, `ADD_INBOX`, `SESSION_CONTROL`, `UNDO`, `CHAT_OR_UNKNOWN`.
*   *Why this matters:* If the intent is `CHAT_OR_UNKNOWN` (the user is talking about the weather or asking the bot to be a secretary), the system bypasses the database completely, preventing accidental data corruption.

### Step 2: Tool Calling / Execution
If the intent requires a database change (e.g., `LOG_WORK`), the system passes the message and the current Context to the main model (e.g., Gemini 1.5 Flash or Pro) with a strict set of available **Tools (Functions)**.
*   **The Golden Rule:** The LLM MUST NOT write or update text states manually. It must invoke Python functions.
*   *Example:* User says: *"Spent 40 mins on C++ RPG."*
*   *LLM Output:* `{"function_call": {"name": "add_project_time", "args": {"project_id": 12, "minutes": 40}}}`
*   *Python Action:* The Python backend catches this JSON, runs the SQL query, and formats the dry, factual response for Telegram.

## 2. Context & Memory Management (Preventing Context Overflow)
If we send the user's entire history to the LLM, the token count will explode, causing slow responses and high costs. We use a **Block-Based Memory Architecture**. The Python backend dynamically assembles a lightweight Markdown string before sending it to the LLM.

**The Context Payload contains:**
1.  **Block A: System Persona:** "You are the Pulse Monolith. You are dry, factual, and strictly map user input to tools."
2.  **Block B: Active Quests (Projects):** ONLY projects with `status='active'`. Completed or paused projects are excluded to save tokens.
    *   *Format:* `[Project ID: 12] C++ Text RPG | Next Action: Pointers (60m)`
3.  **Block C: Daily Projects:** Today's routine and current counters.
    *   *Format:* `[Project ID: 5] Pushups | Current: 0/10`
4.  **Block D: Short-Term Working Memory:** The last 3 to 5 interactions in the current session. This allows the user to say *"I coded for 40 mins"* and then follow up with *"and 20 more just now"* without losing context.
5.  **Block E: Temporal Awareness:** Injected strictly by Python.
    *   *Format:* `Current Time: Monday, 15:30 (Europe/Berlin). Session is ACTIVE.`

## 3. Concurrency & Race Conditions (The FIFO Queue)
A standard bot breaks when a user sends 3 messages in 2 seconds while walking down the street. The LLM processes them in parallel, reading the same outdated database state, and overwriting each other.

**The Solution: User-Level Locking and Queueing**
*   **Mechanism:** When Message 1 arrives, the Python backend sets a lock (`is_processing = True`) for that specific `user_id`.
*   **Queue:** Messages 2 and 3 are pushed to a FIFO (First-In-First-Out) queue.
*   **UX:** The bot immediately triggers Telegram's `send_chat_action(action='typing')` to signal that the Monolith has received the data and is thinking. Do NOT reply with "I am busy."
*   **Execution:** Once Message 1's database transaction is complete, the lock is released, the Context is refreshed, and Message 2 is processed with the new state. This guarantees 100% data integrity without frustrating the user.

## 4. Provider-Agnostic Architecture (Multi-LLM Routing)
This system is designed as a robust SaaS, not a fragile script tied to one corporation. It must survive API outages.

*   **Abstraction Layer:** The code must implement a `BaseLLMProvider` interface.
*   **Implementations:** `GoogleProvider`, `OpenAIProvider`, `AnthropicProvider`.
*   **Bring Your Own Key (BYOK):** The database (`Users` table) stores the user's preferred provider and API key. The system decrypts and uses it on the fly.
*   **Automatic Fallback:** If the primary provider (e.g., Google) returns a 500 Error or times out, the `LLMRouter` catches the exception and silently retries the request using a fallback provider (e.g., OpenAI).
*   **Absolute Failure (CLI Mode):** If all AI APIs are down, the bot does not die. It switches to rigid CLI commands (e.g., `/log 12 40` -> Log 40 mins to Project ID 12).

## 5. The "Time Blindness" Rule
Large Language Models are notoriously bad at math, time zones, and calculating relative dates (e.g., daylight saving time).
*   **Rule:** The LLM is **NEVER** allowed to calculate absolute timestamps.
*   **Handling Time:** If the bot needs to schedule a ping or log a specific duration, the LLM must only extract the raw intent (e.g., `duration_minutes: 40`, `delay_minutes: 60`).
*   **Python's Job:** The Python backend takes those raw integers, applies the user's timezone (stored in the DB, e.g., `Europe/Berlin`), and uses Python's `datetime` or `APScheduler` to handle the actual math.

## 3. Entity Resolution & Data Integrity (Design Choice)

To prevent database fragmentation (e.g., creating duplicate projects for "coding", "programming", "coded"), the system strictly adheres to the following principles:

### 3.1 Strict Mapping (No Hallucinated Entities)
The LLM cannot create `Projects` or `Projects` on the fly as a side effect of logging time. 
*   Before parsing a `LOG_WORK` intent, the system fetches all of the user's `active` projects (with their database `ID`s) and injects them into the prompt prompt.
*   The LLM maps the user's text to an existing `ID`. If no match is found, the time is logged against `project_id = Null` (useful time, but unassigned to a quest).

### 3.2 The Shortcode / ID System
Users can use exact IDs to bypass fuzzy matching.
*   When listing projects, the bot prefixes them: `[1] Pulse Monolith`, `[2] English`.
*   The user can explicitly state: *"Coded 1h for project 1"*.
*   The LLM is instructed to heavily prioritize matching explicit numbers to Project IDs.

### 3.3 Transparent State Feedback 
Every AI action that alters the database MUST be reflected back to the user clearly so they know exactly what the system understood.
*   *Example Output:* "✅ Logged: 40m -> [1] Pulse. Status: 2h total today."

### 3.4 The Undo / Correction Engine
If the bot misunderstands (e.g., logs 40 instead of 14), the user can immediately type a correction.
*   The system uses the `ActionLog` table to store the previous state before an edit.
*   An `UNDO` intent rolls back the last `ActionLog` entry. 
*   A `CORRECTION` intent (e.g., "Change that to project 2") modifies the latest `TimeLog`.
