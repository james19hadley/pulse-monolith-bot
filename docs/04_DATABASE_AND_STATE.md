# `04_DATABASE_AND_STATE.md`

## 1. Database Philosophy & Data Integrity
The database is the single source of truth. The LLM is merely a translation layer that reads from it and requests changes to it via Tool Calling. 
*   **Application-Level Row-Level Security (RLS):** The LLM NEVER writes raw SQL. The Python backend intercepts all LLM tool calls and strictly injects `user_id` into every single database query (e.g., `WHERE id = ? AND user_id = ?`). This guarantees complete data isolation between users.
*   **Soft Deletes vs. Hard Deletes:** To preserve history for the "Undo" feature, we prefer status changes (e.g., `status = 'archived'`) over dropping rows from the database.

## 2. Core Entities & Schema (ORM Models)

### 2.1. `Users` Table (Core Settings)
Stores user preferences, SaaS state, and LLM configurations.
*   `id` (Primary Key)
*   `telegram_id` (Unique, Indexed)
*   `timezone` (String, e.g., 'Europe/Berlin'. Default: 'UTC')
*   `day_cutoff_time` (Time, e.g., 03:00 AM. Defines when the "day" officially ends for reporting)
*   `llm_provider` (String: 'google', 'openai', 'anthropic')
*   `api_key_encrypted` (String, nullable. For Bring-Your-Own-Key functionality)
*   `active_session_id` (Foreign Key -> `Sessions`, nullable. Tracks if the user is currently in a work block)
*   `last_ping_message_id` (Integer, nullable. Used to DELETE the previous nudge message to avoid chat spam)
*   `target_channel_id` (String, nullable. The Telegram ID of the user's personal channel where the Evening Report is published. E.g., '-1001234567890').


### 2.2. `Sessions` Table (The Boundaries of Time)
Crucial for calculating Project 0 / unassigned time. A user's day consists of one or multiple sessions.
*   `id` (PK)
*   `user_id` (FK -> `Users`, Indexed)
*   `start_time` (DateTime, UTC)
*   `end_time` (DateTime, UTC, nullable. Null means the session is currently active)
*   `status` (String: 'active', 'closed', 'force_closed_by_cron')

### 2.3. `Projects` Table (The Witcher's Quests)
Long-term, cumulative goals. Only `active` projects are injected into the LLM context to save tokens.
*   `id` (PK)
*   `user_id` (FK -> `Users`, Indexed)
*   `title` (String, e.g., "C++ Text RPG")
*   `status` (String: 'active', 'paused', 'completed')
*   `target_minutes` (Integer. The estimated size of the quest, e.g., 1800 for 30 hours)
*   `total_minutes_spent` (Integer. Cumulative sum of all time logs for this project)
*   `next_action_text` (String. The granular step used for pings, e.g., "Read pointers chapter")

### 2.4. `Projects` Table (Daily Routine)
Unlike projects, projects do not accumulate infinitely. They reset daily.
*   `id` (PK)
*   `user_id` (FK -> `Users`, Indexed)
*   `title` (String, e.g., "Pushups")
*   `target_value` (Integer, e.g., 10)
*   `current_value` (Integer, e.g., 0)
*   `type` (String: 'counter' or 'boolean')
*   `last_reset_date` (Date. Checked by Python; if it's a new day, `current_value` is set to 0 before the LLM reads it)

### 2.5. `Time_Logs` Table (The Ledger)
Every time the user reports focused work, a transaction is recorded here.
*   `id` (PK)
*   `user_id` (FK -> `Users`)
*   `session_id` (FK -> `Sessions`. Links the work to a specific time boundary)
*   `project_id` (FK -> `Projects`, nullable. Can be null if it's general focused work)
*   `duration_minutes` (Integer)
*   `description` (String, optional)
*   `created_at` (DateTime, UTC)

### 2.6. `Action_Logs` Table (The Undo Engine)
Records state changes initiated by the LLM Tool Calling to allow the user to revert mistakes.
*   `id` (PK)
*   `user_id` (FK -> `Users`)
*   `tool_name` (String, e.g., 'add_time_to_project')
*   `previous_state_json` (JSON. The values before the change)
*   `new_state_json` (JSON. The values after the change)
*   `created_at` (DateTime, UTC)

### 2.7. `Inbox` Table (Brain Dump)
*   `id` (PK)
*   `user_id` (FK -> `Users`)
*   `raw_text` (Text)
*   `status` (String: 'pending', 'cleared')

## 3. State Management & Lifecycle Rules

### 3.1. Calculating Project 0 / Unassigned Time (SQL Logic)
When a session is closed, the Python backend executes the following logic (Pseudocode for the AI coder):
1. `session_duration` = `session.end_time` - `session.start_time`
2. `focused_time` = `SUM(duration_minutes)` from `Time_Logs` where `session_id == current_session.id`
3. `the_void` = `session_duration` - `focused_time`
4. If `the_void` < 0 (user logged more time than the session lasted), clamp it to 0 or flag as an anomaly.

### 3.2. The Midnight Cutoff (Day Reset)
Standard databases reset at 00:00 UTC. This project relies on the user's local timezone and their custom `day_cutoff_time` (e.g., 03:00 AM Berlin time).
*   A background worker (Cron/APScheduler) continuously checks the current local time for each user.
*   If `Current_Local_Time >= day_cutoff_time` and the user's day hasn't been closed:
    1. Force-close any `active` session.
    2. Generate and send the Evening Report ("Kompromat").
    3. Reset all `Projects.current_value` to 0.

### 3.3. The Undo Execution (Reversing Transactions)
If the AI Router detects an `UNDO` intent:
1. Python fetches the latest entry for this `user_id` from `Action_Logs`.
2. It parses the `previous_state_json` and `tool_name`.
3. It reverses the operation (e.g., if `tool_name` was `add_time_to_project`, it subtracts the minutes from `Projects.total_minutes_spent` and deletes the corresponding row in `Time_Logs`).
4. It sends a confirmation to the user.

