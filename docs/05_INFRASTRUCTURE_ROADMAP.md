# Infrastructure & Deployment Architecture

## General Concept
The project is strictly deployed to a remote VPS. Development (this repository) happens locally, but **execution and testing** happen in the unified production/staging environment via CI/CD.

## CI/CD Pipeline
- We commit and push changes to `main` branch.
- Github Actions (or similar CI/CD) automatically pulls changes on the VPS and restarts the Docker containers.
- **DO NOT** attempt to run `docker compose up` or `systemctl` locally. All services run on the remote machine.

## Components
1. **Caddy (Reverse Proxy):** Handles HTTPS, domain routing (`65.21.57.159.nip.io`), and IP whitelisting. Routes external traffic to the Bot.
2. **Bot Container:** Runs `aiogram` combined with an `aiohttp` web server. The web server listens for Telegram webhooks and also serves the `/admin/logs` endpoint.
3. **Database & Redis:** PostgreSQL container for persistence and Redis for Celery/tasks.

## Debugging Workflow
- Server logs are exposed via `https://65.21.57.159.nip.io/admin/logs`.
- **Note:** If the Python bot container triggers a crash loop on startup (e.g., from an ImportError), the `aiohttp` web server will not boot, and Caddy will return a `502 Bad Gateway`. In this case, fixing the core crash is needed to restore the admin endpoint.
