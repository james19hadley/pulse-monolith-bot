# Sprint 14: Initial VPS Deployment 

**Status:** `Active`
**Date Proposed:** 2026-03-24

**Objective:** Move the monolithic bot off the local machine and onto a 24/7 cloud VPS to properly execute its scheduled Catalyst Pings and allow the creator true tracking mobility.

## 🎯 Goals
- Provision a basic Linux VPS (Ubuntu/Debian) on a provider like DigitalOcean or Hetzner.
- Install Docker and deploy the production-ready application stack via git.
- Secure the server via basic firewall rules (ufw).

## 📋 Tasks

### 1. Server Provisioning & Access (User Action)
- [x] Rent a simple 1GB RAM / 1vCPU Linux Server.
- [ ] SSH into the server as root.
- [ ] Ensure `git` and `curl` are installed.

### 2. Docker Installation
- [ ] Install Docker Engine & Docker Compose on the VPS.

### 3. Application Deployment
- [ ] `git clone` the Pulse Monolith repository onto the server.
- [ ] Create the `.env` file on the server using `.env.example` as a template (fill with Telegram Bot Token, Database passwords, etc.).
- [ ] Execute `bash scripts/deploy.sh` to construct and turn on the services.

### 4. Health Checks
- [x] Confirm `docker compose ps` shows 4 instances `Up`.
- [ ] Interact with the bot on Telegram and ensure `/start` operates snappily.

## 🏁 Completion Criteria
- You can turn off your laptop, and the bot still answers on Telegram and successfully triggers the Celery 5-minute schedule pings.

## Update: Fixes Applied Post-Deployment
- [x] Fixed `psycopg2.errors.UndefinedTable` by enforcing `init_db()` in `main.py`
- [x] Relaxed strict `session_id` constraint via `ALTER TABLE time_logs ALTER COLUMN session_id DROP NOT NULL;`

