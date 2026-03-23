# `05_INFRASTRUCTURE_ROADMAP.md`

## 1. Architectural Philosophy (Progressive Enhancement)
The project is built to scale from a single-user local script to a multi-tenant SaaS application. To achieve this without rewriting the codebase, we enforce **strict separation of concerns** from Day 1:
*   The LLM logic (`AI_Router`, `Tool_Caller`) must be decoupled from the Telegram framework.
*   The Database logic (`Repositories`/`ORM`) must be abstracted so switching from SQLite to PostgreSQL requires only changing the connection string.
*   Background tasks (Pings, Evening Reports) must be modular so the scheduler can be swapped.

## 2. Phase 1: Local MVP (Proof of Concept)
**Goal:** Build, test, and iterate on the user's local machine with zero infrastructure overhead. The priority is perfecting the Fi-friendly UX and the "Void" math.

*   **Telegram Delivery:** `Long Polling` (e.g., `bot.polling()`). The bot continuously asks the Telegram API for new messages. No domain or SSL certificate required.
*   **Database:** `SQLite` (`db.sqlite3`). A single local file. Perfect for 1-10 users and fast schema iterations.
*   **Task Scheduler:** `APScheduler` (BackgroundScheduler). Runs in the same memory space as the bot process.
    *   *Pros:* Zero setup. Just define `@scheduler.scheduled_job`.
    *   *Cons:* If the bot process restarts, pending pings and timers are lost (acceptable for MVP).
*   **Hosting:** The developer's laptop or a basic $5 VPS running a `systemd` service or a simple Docker container.

## 3. Phase 2: Production & SaaS-Ready (The Scale)
**Goal:** Make the system bulletproof, handle concurrent users without race conditions, ensure background tasks survive server reboots, and implement monetization.

*   **Telegram Delivery:** `Webhooks`. Telegram pushes events to our server via HTTP POST. 
    *   *Why:* Saves server CPU, responds instantly, and is required for proper horizontal scaling. Requires a domain name and an SSL certificate (e.g., Nginx + Let's Encrypt or Cloudflare Tunnels).
*   **Database:** `PostgreSQL`. 
    *   *Why:* Handles concurrent writes (crucial when 50 users end their sessions at the same time).
*   **Task Scheduler:** `Celery` + `Redis` (Message Broker).
    *   *Why:* When a user starts a session, the bot schedules a "Ping" 1 hour in the future. With Celery, this task is stored safely in Redis. Even if the main bot server crashes and restarts, the Celery worker will still execute the ping at the exact right time. The "Kompromat" reports at 03:00 AM are also guaranteed to fire.
*   **Hosting:** Docker Compose (Bot Container + Celery Worker Container + Redis Container + PostgreSQL Container).

## 4. Monetization & API Key Security
Since the bot uses external LLMs (Google Gemini, OpenAI), tokens cost money. The system supports two modes:

### 4.1. Bring Your Own Key (BYOK) - Free Tier
*   Users register their own API keys via a bot command (e.g., `/set_key google AIzaSy...`).
*   **Security Requirement:** Keys MUST NOT be stored in plain text. The Python backend must use symmetric encryption (e.g., `cryptography.fernet`) with a master `SECRET_KEY` stored in the `.env` file to encrypt user keys before saving them to the `Users` table.

### 4.2. SaaS Subscription (Managed Mode)
*   The user pays a monthly fee to use the creator's corporate API keys.
*   **Integration:** Use the Telegram Payments API (supporting Telegram Stars or Stripe).
*   **Flow:** 
    1. User hits a paywall when starting a session.
    2. User pays via Telegram UI.
    3. Telegram sends a `pre_checkout_query` to the bot.
    4. Bot updates `Users.subscription_tier = 'premium'` and `Users.subscription_expires_at`.

## 5. Failover Mechanisms (Disaster Recovery)

### 5.1. Multi-LLM Router
If the primary provider (e.g., Google) goes down:
*   The `LLMRouter` catches the `Timeout` or `5xx Server Error`.
*   It immediately attempts to process the message using the fallback provider defined in the `.env` (e.g., `FALLBACK_PROVIDER=openai`).
*   This happens silently; the user only experiences a slight delay.

### 5.2. The CLI Fallback (Zero-AI Mode)
If ALL AI providers are down, or the user runs out of API tokens/money, the Monolith must not become a brick. 
The bot must support hardcoded, traditional CLI commands that directly map to database tools:
*   `/log_time [Project_ID] [Minutes]` -> Bypasses LLM, directly runs the SQL update.
*   `/habit [Habit_ID] [Value]`
*   `/inbox [Text]`
*   `/end_session` (Always available, strictly Python-based).
The bot should reply: *"AI processors offline. Reverting to manual override. Data logged successfully."

