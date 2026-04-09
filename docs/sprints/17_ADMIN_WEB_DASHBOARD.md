# Sprint 17: Security, Middleware & Core Cleanup

**Status:** `Completed`

## Goal
Originally planned as an embedded web dashboard, this sprint was reprioritized to implement Caddy IP-based security for admin endpoints, introduce a global crash handler, and clean up temporary dev scripts to stabilize the foundation.

## Tasks Completed
- [x] Configure Caddyfile with `remote_ip` restrictions for `/admin/*`.
- [x] Create `SafeLoggingMiddleware` to catch global exceptions and notify users gracefully.
- [x] Fix database import issues (SQLAlchemy `func` import).
- [x] Resolve file bloat by cleaning up loose `fix_*.py` and legacy scripts from the project root.
- [x] Fix container startup crash loop by restoring missing definitions in `keyboards.py`.
- [x] Document infrastructure topology in `05_INFRASTRUCTURE.md`.
