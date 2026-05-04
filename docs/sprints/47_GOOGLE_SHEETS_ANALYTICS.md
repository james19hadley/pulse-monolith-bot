# Sprint 47: Google Sheets Integration (Scoped & Master Exports)

**Status:** `Draft`
**Date Proposed:** 2026-05-04
**Objective:** Provide a way to export data from Pulse Monolith to Google Sheets for advanced analytics, granular sharing, and macro-reflection. Emphasizes the "Professor Use Case" where a user can bind a specific sheet to a specific project to share logs externally without exposing their entire life.

## 🎯 Architectural Philosophy: Sheets vs. Landing Page
*   **The Landing Page (Sprint 49):** The beautiful, B2C, public-facing dashboard. Great for motivation, gamification, and "at-a-glance" status. It is read-only and highly visual.
*   **Google Sheets (Sprint 47):** The "Data Engineer" export. Ultimate flexibility. Great for Pivot Tables, custom graphs, calculating exact billing hours, and **granular privacy** (e.g., sharing a single project's logs with a manager/professor).

## 📋 Tasks

### [Configuration & Setup]
- [ ] Add `GCP_SERVICE_ACCOUNT_JSON` setup logic.
- [ ] Add `google_sheet_url` and optional `google_sheet_project_id` bindings to the DB.
- [ ] Build `/bind_sheet <URL> [Project ID]` command. If Project ID is provided, the bot ONLY syncs logs from that project and its children to the provided sheet.

### [Data Architecture (Master Mode vs Scoped Mode)]
- [ ] **Tab: Raw Logs** (Appends every new time log / progress event). 
- [ ] **Tab: Project State** (Live overview of progress).
- [ ] *Implementation Rule:* If a sheet is "Scoped" (bound to a specific Project ID), the bot filters all Celery sync tasks to only push logs belonging to that project tree.

### [UX / Product Mechanics]
- [ ] Provide clear onboarding for the user on how to share their sheet with the bot's Service Account email.
- [ ] Use Celery for all Google Sheets API calls so Telegram webhooks never hang.
