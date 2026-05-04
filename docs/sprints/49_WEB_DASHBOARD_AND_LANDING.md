# Sprint 49: Web Dashboard & Landing Page (aiohttp + Tailwind)

**Status:** `Active`
**Date Proposed:** 2026-05-04
**Objective:** Evolve Pulse Monolith from a pure Telegram bot into a full-fledged SaaS platform with a web-based dashboard and marketing landing page, utilizing our existing PostgreSQL database and `aiohttp` web server.

## 🎯 Architecture
To keep development "LLM-friendly" and maintainable without complex JavaScript build steps (Webpack/npm), we will use a pure Python-driven monolithic stack:
- **Backend:** `aiohttp.web` (already running our webhooks, no need to introduce FastAPI).
- **Frontend:** Pure HTML + Tailwind CSS (via CDN) + Jinja2 Templates (`aiohttp-jinja2`).
- **Charts:** Chart.js or ApexCharts injected directly into HTML.
- **Auth:** Telegram Login Widget (seamless integration with existing user DB).
- **Design System:** Deep blue background (`bg-slate-950`) with glowing orange accents (`text-orange-500`, `shadow-orange-500/50`) representing the Monolith against a cold landscape.

## 📋 Tasks

### [Infrastructure & Routing]
- [ ] Update `requirements.txt` to include `aiohttp-jinja2` and `jinja2`.
- [ ] Configure `aiohttp_jinja2` in `src/main.py` pointing to `src/web/templates`.
- [ ] Reconfigure `Caddyfile` so that root `/` goes to the Python web server instead of a static directory.

### [Authentication (Telegram Login)]
- [ ] Create `/auth/telegram` route to verify the cryptographic hash sent by the Telegram Login Widget using `TELEGRAM_BOT_TOKEN`.
- [ ] Set secure, HTTP-only JWT cookies for the user session upon successful login.
- [ ] Create middleware or decorators to protect dashboard routes.

### [Views & Frontend]
- [ ] **Landing Page (`/`)**: Dark-themed cyberpunk/monolith aesthetic. Explains the product philosophy. Includes the Telegram Login button.
- [ ] **Dashboard (`/app`)**: Main user view. 
  - Visual grid of Active Projects.
  - Heatmap or Bar Chart of Focus Time for the last 14 days.
  - Interactive "Daily Report" historical viewer.

## 🔒 Security Notes
- All web sessions must be strictly verified against the Telegram hash.
- Ensure CORS and Cookie settings are strict (`SameSite=Lax`, `Secure`).
