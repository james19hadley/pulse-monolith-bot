# Sprint 13: Phase 2 - SaaS Infrastructure & Scale

**Status:** `Draft`
**Date Proposed:** 2026-03-24

**Objective:** Transition the application from a Local MVP (SQLite, inline APScheduler) into a production-ready Webhook-driven bot, backed by PostgreSQL and Celery/Redis for reliable task execution, securely containerized with Docker Compose.

## 🎯 Goals
- Migrate SQLite to PostgreSQL.
- Replace `APScheduler` embedded jobs with `Celery` + `Redis` queue.
- Containerize the entire application (Python Bot, Postgres, Redis, Celery Worker).
- Move away from `Long Polling` to robust application state handling (preparing for Webhooks).

## 📋 Tasks

### 1. Database Migration (PostgreSQL)
- [ ] Add `psycopg2-binary` (or `asyncpg`) to `requirements.txt`.
- [ ] Update `src/db/repo.py` to connect via `DATABASE_URL` environment variable matching the Postgres container.
- [ ] Validate Alembic/SQLAlchemy can successfully build the schema into Postgres.

### 2. Task Queue (Celery + Redis)
- [ ] Add `celery` and `redis` to `requirements.txt`.
- [ ] Setup `src/worker.py` (Celery app initialization).
- [ ] Extract jobs from `src/scheduler/jobs.py` into Celery tasks.
- [ ] Re-wire `trigger_catalyst_ping` so it enqueues a Celery task with an ETA (Estimated Time of Arrival) instead of using in-memory APScheduler logic.
- [ ] Setup Celery Beat for scheduled intervals (like the midnight `daily_accountability_job`).

### 3. Containerization (Docker)
- [ ] Create a robust `Dockerfile` for the Python application.
- [ ] Create `docker-compose.yml` to orchestrate 4 services: 
  1. `db` (Postgres)
  2. `redis` (Message Broker)
  3. `bot` (The main aiogram runner)
  4. `worker` (Celery worker process for background tasks)

### 4. Configuration & Environment
- [ ] Update `.env.example` with Postgres/Redis connection strings.
- [ ] Make sure bot fails gracefully if `DATABASE_URL` is missing.

## 🏁 Completion Criteria
- You can run `docker compose up --build -d` and the entire bot ecosystem starts seamlessly.
- You can start a session, which enqueues a Celery task in Redis, and if you restart the `bot` container, Celery still executes the ping at the exact right moment.
- The state is persisted flawlessly in Postgres.
