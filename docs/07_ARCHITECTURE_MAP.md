# Architecture & Traceability Map (Semantic Anchors)

This document contains a registry of unique identifiers (UIDs) used directly inside the Python codebase via `@Architecture-Map: [UID]` tags. This creates a bidirectional link between technical docs and implementation.

## 📁 1. Services Layer (`src/services/`)
- **`[SRV-PROJ-CREATE]`**: `src/services/projects.py` - Core logic for creating a new project entity in the database and checking duplicates.
- **`[SRV-REPORT-CALC]`**: `src/services/reporting.py` - Logic to calculate daily, weekly, or monthly tracked time, summing up child objects correctly.

## 📁 2. Views and Presentation (`src/bot/views.py`)
- **`[UI-REP-BUILDER]`**: `src/bot/views.py` - Collects statistics calculated by `[SRV-REPORT-CALC]` and builds a formatted string for the end-user (e.g. daily evening report). Reads `user.report_config` to show/hide zeroes and absolute hours.

## 📁 3. Handlers and Interactions (`src/bot/handlers/`)
- **`[HND-PROJ-CREATE]`**: `src/bot/handlers/entities/projects/create.py` - The FSM telegram handler that asks the user for the project name and calls the `[SRV-PROJ-CREATE]` service upon completion.

## 📁 4. Schedulers & Background Jobs (`src/scheduler/`)
- **`[JOB-MORN-PLAN]`**: `src/scheduler/jobs.py` (`morning_planner_job`) - Pulls pending DB tasks and spoon-feeds priority items to the AI for a curated morning dm summary.

## 📁 5. Core & AI Layer (`src/core/`, `src/ai/`)
- **`[CORE-SYS-CONFIG]`**: `src/core/config.py` - Contains all environment variables and the central USER_SETTINGS_REGISTRY.
- **`[CORE-SEC-AUTH]`**: `src/core/security.py` - Encrypts and decrypts user API keys for database storage.
- **`[CORE-AI-PROMPTS]`**: `src/core/prompts.py` - Global registry of AI prompts used for routing.
- **`[CORE-ADMIN-DASH]`**: `src/admin_dashboard.py` - Admin Dashboard for monitoring bot performance.
- **`[CORE-AI-PROVIDERS]`**: `src/ai/providers.py` - LLM Provider implementations (API connections and parsing).
- **`[CORE-AI-ROUTER]`**: `src/ai/router.py` - The central NLP router.
- **`[CORE-AI-TOOLS]`**: `src/ai/tools.py` - Function-calling schemas representing intents.
- **`[CORE-SYS-CONSTANTS]`**: `src/core/constants.py` - Hardcoded constants.
- **`[CORE-SYS-PERSONAS]`**: `src/core/personas.py` - Bot conversational styles.

## 📁 6. Database Layer (`src/db/`)
- **`[DB-MODELS-SCHEMA]`**: `src/db/models.py` - Defines exactly the tables and relationships the whole app uses.
- **`[DB-CORE-SESSION]`**: `src/db/repo.py` - Database engines, scoped sessions (SessionLocal), and initial migration script.
