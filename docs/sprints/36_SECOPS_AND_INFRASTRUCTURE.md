# Sprint 36: SecOps & Infrastructure Hardening

**Status:** `Draft`
**Date Proposed:** April 9, 2026
**Objective:** Secure the production VPS environment against common attack vectors. Eliminate default fallbacks, protect webhook communication, and restrict admin dashboard access properly for multiple IPs.

## 🎯 Goals
- [ ] Remove hardcoded fallbacks like `changeme` for critical passwords (`ADMIN_PASSWORD`).
- [ ] Implement Caddy IP whitelisting correctly for multiple IPs.
- [ ] Protect webhook endpoints from being spoofed by unauthorized sources.
- [ ] Ensure database and internal routing are safely isolated.

## 📋 Tasks

### 1. Credentials & Configuration
- [ ] Edit `src/core/config.py` to raise an explicit system error if `ADMIN_PASSWORD` is not set in `.env` (remove `"changeme"`).

### 2. Caddy & IP Whitelisting Fix
- [ ] Review `Caddyfile` syntax for allowing multiple IPs. The correct Caddy v2 syntax for multiple IPs involves matchers: `@admin remote_ip 1.2.3.4 5.6.7.8`.
- [ ] Test the matcher to secure the `/admin/*` routes properly so we don't lock ourselves out.

### 3. Webhook Authentication
- [ ] Configure the bot to use Telegram's `secret_token` for incoming webhooks.
- [ ] Validate the `X-Telegram-Bot-Api-Secret-Token` header on every incoming `aiohttp` request to `/webhook` to prevent spoofing.

### 4. Docker Network Isolation
- [ ] Audit `docker-compose.yml`. Ensure the `db` (PostgreSQL) and `redis` ports are not globally published (e.g., remove `5432:5432` exposing them to internet).

## 🏁 Completion Criteria
- Server crashes aggressively if `.env` lacks `ADMIN_PASSWORD`.
- `/admin/logs` returns 403 Forbidden for unauthorized IPs but allows multiple authorized ones.
- Fake webhooks sent via curl without the correct secret token are rejected.
