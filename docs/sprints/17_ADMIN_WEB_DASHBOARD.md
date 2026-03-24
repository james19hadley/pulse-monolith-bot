# Sprint 17: Admin Web Dashboard & Telemetry

## Goal
Build an embedded web dashboard to monitor the bot's health, user metrics, and errors without connecting to the server logs directly. The dashboard must be secure and fast, reusing the existing `aiohttp` web server created for the webhook.

## Technical Requirements
1. **Routing:** Add a new GET route `/admin/dashboard` in `src/main.py`.
2. **Security:** Implement `Basic Auth` middleware/check on the admin route using `ADMIN_LOGIN` and `ADMIN_PASSWORD` (or checking against `ADMIN_ID` via some bot handshake, but simple Basic Auth is easiest).
3. **Data Source:**
   - DB Queries for simple aggregates: total users, active focus sessions, total tokens used, total time logged today.
   - In-memory `aiogram` status if possible (uptime).
4. **Presentation:** Return a lightweight, responsive HTML template (can be injected directly into the response or using a tiny engine like `jinja2`). 
   - No external frontend dependencies needed, just simple CSS.

## Logging & Privacy Recap
(Done in Sprint 16): Logging was restricted globally using `SafeLoggingMiddleware()`. Only message lengths and commands are recorded. No user content (PII) exists in logs. The dashboard will only display aggregate telemetry data.

## Tasks
- [ ] Parse new ENV variables for HTTP basic auth.
- [ ] Create simple metrics queries in `repo.py`.
- [ ] Create HTML string template for the dashboard.
- [ ] Attach `aiohttp` handler to display the template.
- [ ] Test via browser with the given domain and route.
