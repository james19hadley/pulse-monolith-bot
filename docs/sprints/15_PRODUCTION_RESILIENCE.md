# Sprint 15: Production Resilience (Webhooks & Backups)

**Status:** `Active`
**Date Proposed:** 2026-03-24

**Objective:** Stabilize long-term production by migrating Telegram connectivity from Long Polling to Webhooks (eliminating connection drop errors) and implementing a rolling local database backup strategy.

## 🎯 Goals
- Implement a local PostgreSQL backup script that runs automatically and retains only the last 2 snapshots.
- Refactor the application entry point to serve an HTTP endpoint for Telegram Webhooks.
- Secure the Webhook endpoint with SSL/TLS (Telegram requirement).

## 📋 Tasks

### 1. Local Database Backups
- [x] Create `scripts/backup_db.sh` using `docker exec pg_dump`.
- [x] Implement logic to delete all but the 2 most recent backups.
- [ ] Add the script to the server's crontab (e.g., run every midnight).

### 2. Webhooks & SSL Server Setup
- [x] Determine domain strategy (`nip.io` dynamic domain).
- [x] Refactor `src/main.py` to use `aiohttp` wrapped around the Aiogram dispatcher.
- [x] Update `docker-compose.yml` to include Caddy web server mapping to the bot container to handle SSL natively.
- [x] Update `.env.example` to hold the `WEBHOOK_DOMAIN` and `WEBHOOK_PATH`.

## 🏁 Completion Criteria
- A cron job natively backs up Postgres every night.
- The `aiogram` process runs purely as a web server receiving pushes from Telegram, with zero `[Errno 104]` exceptions in the logs.
