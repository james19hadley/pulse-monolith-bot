# Architecture & Traceability Map (Semantic Anchors)

This document contains a registry of unique identifiers (UIDs) used directly inside the Python codebase via `@Architecture-Map: [UID]` tags. This creates a bidirectional link between technical docs and implementation.

## 📁 1. Services Layer (`src/services/`)
- **`[SRV-PROJ-CREATE]`**: `src/services/projects.py` - Core logic for creating a new project entity in the database and checking duplicates.
- **`[SRV-REPORT-CALC]`**: `src/services/reporting.py` - Logic to calculate daily, weekly, or monthly tracked time, summing up child objects correctly.

## 📁 2. Views and Presentation (`src/bot/views.py`)
- **`[UI-REP-BUILDER]`**: `src/bot/views.py` - Collects statistics calculated by `[SRV-REPORT-CALC]` and builds a formatted string for the end-user (e.g. daily evening report). Reads `user.report_config` to show/hide zeroes and absolute hours.

## 📁 3. Handlers and Interactions (`src/bot/handlers/`)
- **`[HND-PROJ-CREATE]`**: `src/bot/handlers/entities/projects/create.py` - The FSM telegram handler that asks the user for the project name and calls the `[SRV-PROJ-CREATE]` service upon completion.
- **`[HND-PROJ-VIEW]`**: `src/bot/handlers/entities/projects/view.py` - Detailed project view rendering.
- **`[HND-PROJ-TASKS]`**: `src/bot/handlers/entities/projects/tasks.py` - Task management at the project level.
- **`[HND-PROJ-MOD]`**: `src/bot/handlers/entities/projects/modifications.py` - Project status changes (archive, complete, delete).

## 📁 4. Schedulers & Background Jobs (`src/scheduler/`)
- **`[JOB-BASE]`**: `src/scheduler/jobs/base.py` - Common configuration for background jobs.
- **`[JOB-CATALYST]`**: `src/scheduler/jobs/catalyst.py` - Idle session pings.
- **`[JOB-CLEANUP]`**: `src/scheduler/jobs/cleanup.py` - Stale session closing.
- **`[JOB-REPORT]`**: `src/scheduler/jobs/reporting.py` - Daily accountability reports.
- **`[JOB-REFLECT]`**: `src/scheduler/jobs/reflection.py` - Evening reflection nudges.
- **`[JOB-REMIND]`**: `src/scheduler/jobs/reminders.py` - One-off task reminders.
- **`[JOB-MORN-PLAN]`**: `src/scheduler/jobs/planner.py` - Pulls pending DB tasks and spoon-feeds priority items to the AI for a curated morning dm summary.

## 📁 5. Core & AI Layer (`src/core/`, `src/ai/`)
- **`[CORE-SYS-CONFIG]`**: `src/core/config.py` - Contains all environment variables and the central USER_SETTINGS_REGISTRY.
- **`[CORE-SEC-AUTH]`**: `src/core/security.py` - Encrypts and decrypts user API keys for database storage.
- **`[CORE-AI-PROMPTS]`**: `src/core/prompts.py` - Global registry of AI prompts used for routing.
- **`[CORE-ADMIN-DASH]`**: `src/admin_dashboard.py` - Admin Dashboard for monitoring bot performance.
- **`[CORE-AI-BASE-PROV]`**: `src/ai/base_provider.py` - Abstract Base Class for LLM API integration.
- **`[CORE-AI-MODELS]`**: `src/ai/models_registry.py` - LLM configuration specifying cost-efficient models for standard parsing.
- **`[CORE-AI-PROVIDERS]`**: `src/ai/providers.py` - LLM Provider implementations (API connections and parsing).
- **`[CORE-AI-SCHEMAS]`**: `src/ai/schemas.py` - Standardized Pydantic schemas for AI extraction and tool calling.
- **`[CORE-AI-ROUTER]`**: `src/ai/router.py` - The central NLP router.
- **`[CORE-AI-TOOLS]`**: `src/ai/tools.py` - Function-calling schemas representing intents.
- **`[CORE-SYS-CONSTANTS]`**: `src/core/constants.py` - Hardcoded constants.
- **`[CORE-SYS-PERSONAS]`**: `src/core/personas.py` - Bot conversational styles.

## 📁 6. Database Layer (`src/db/`)
- **`[DB-MODELS-SCHEMA]`**: `src/db/models.py` - SQLAlchemy ORM definitions mapping tables.
- **`[DB-CORE-SESSION]`**: `src/db/repo.py` - Database engines, scoped sessions (SessionLocal), and initial migration script.

## 📁 7. Application & Bot Entry (`src/main.py`, `src/worker.py`)
- **`[APP-MAIN-ENTRY]`**: `src/main.py` - Main entry point for the FastAPI webhook server and Telegram Bot polling fallback.
- **`[APP-CELERY-WORKER]`**: `src/worker.py` - Celery worker entry point for asynchronous background jobs.

## 📁 8. Bot Handlers: Intent Classifiers (`src/bot/handlers/intents/`)
- **`[HND-INTENT-CORE]`**: `src/bot/handlers/intents/intent_core.py` - Execution mapping for NLP intents.
- **`[HND-INTENT-ENT]`**: `src/bot/handlers/intents/intent_entities.py` - Delegation layer for entity creation intents.
- **`[HND-INTENT-ENT-PROJ]`**: `src/bot/handlers/intents/handlers/projects.py` - Project/Habit creation.
- **`[HND-INTENT-ENT-INBOX]`**: `src/bot/handlers/intents/handlers/inbox.py` - Inbox capture.
- **`[HND-INTENT-ENT-TASK]`**: `src/bot/handlers/intents/handlers/tasks.py` - Task creation logic.
- **`[HND-INTENT-ENT-EDIT]`**: `src/bot/handlers/intents/handlers/edit.py` - Entity editing/deletion.
- **`[HND-INTENT-WORK]`**: `src/bot/handlers/intents/intent_log_work.py` - Processes work-logging intents.
- **`[HND-INTENT-SESS]`**: `src/bot/handlers/intents/intent_session.py` - Processes NLP session commands.
- **`[HND-INTENT-INBOX]`**: `src/bot/handlers/intents/intent_inbox.py` - Processes inbox cleanup intents.

## 📁 9. Bot Handlers: Entities & Menus (`src/bot/handlers/entities/`, `src/bot/handlers/`)
- **`[HND-AI-ROUTER]`**: `src/bot/handlers/ai_router.py` - Intercepts all unhandled raw text and forwards it to Intent Router.
- **`[HND-BOT-CORE]`**: `src/bot/handlers/core/router.py` - Delegation layer for root structural commands.
- **`[HND-CORE-BASIC]`**: `src/bot/handlers/core/basic.py` - /start, /help, /faq.
- **`[HND-CORE-UI]`**: `src/bot/handlers/core/ui.py` - Stats, Tasks, Inbox menus.
- **`[HND-CORE-UNDO]`**: `src/bot/handlers/core/undo.py` - Smart Undo logic.
- **`[HND-SESSIONS]`**: `src/bot/handlers/sessions/router.py` - Delegation layer for focus timers.
- **`[HND-SESS-CMD]`**: `src/bot/handlers/sessions/commands.py` - Start/Stop/End session commands.
- **`[HND-SESS-CB]`**: `src/bot/handlers/sessions/callbacks.py` - Project assignment and nudge callbacks.
- **`[HND-SPINNER]`**: `src/bot/handlers/spinner.py` - Animated loading indicator for long-running AI operations.
- **`[HND-UTILS]`**: `src/bot/handlers/utils.py` - Universal helper components.
- **`[HND-ENT-CMDS]`**: `src/bot/handlers/entities/commands.py` - Specific textual commands like /new or /stats.
- **`[HND-ENT-MENU]`**: `src/bot/handlers/entities/menu.py` - Entry points to entity sub-menus.
- **`[HND-ENT-ROUTER]`**: `src/bot/handlers/entities/router.py` - Glues all entity routes together into 'entities_router'.
- **`[HND-PROJ-ACTIONS]`**: `src/bot/handlers/entities/projects/actions.py` - Delegation layer for project actions.
- **`[HND-PROJ-CREATE]`**: `src/bot/handlers/entities/projects/create.py` - Registration state machine for a new project.
- **`[HND-PROJ-LIST]`**: `src/bot/handlers/entities/projects/list.py` - Displays a scrollable list of entities.
- **`[HND-STATES]`**: `src/bot/states.py` - Stores Python classes defining Aiogram Finite State Machines.

## 📁 10. Bot Handlers: Settings (`src/bot/handlers/settings/`)
- **`[HND-SET-APIKEYS]`**: `src/bot/handlers/settings/api_keys.py` - Handles user uploading their own Provider API Keys.
- **`[HND-SET-GENERAL]`**: `src/bot/handlers/settings/general.py` - Settings main menu.
- **`[HND-SET-PERSONA]`**: `src/bot/handlers/settings/persona_tz.py` - Controls Timezone overrides and Bot Tone.
- **`[HND-SET-REPORTUI]`**: `src/bot/handlers/settings/report_ui.py` - Configures the formatting and blocks shown in daily evening reports.
- **`[HND-SET-REPORTS]`**: `src/bot/handlers/settings/reports.py` - Toggles evening report preferences.
- **`[HND-SET-AICONV]`**: `src/bot/handlers/settings/ai_conv.py` - Talkativeness and Evening Reflection UI.
- **`[HND-SET-ROUTER]`**: `src/bot/handlers/settings/router.py` - Glues all settings options together.
- **`[HND-SET-SYSCONF]`**: `src/bot/handlers/settings/system_configs.py` - Advanced logic configuration menus.

## 📁 11. Presentation Layer (Keyboards & Texts)
- **`[UI-KEY-CORE]`**: `src/bot/keyboards/core.py` - Pagination, structural grids, arrows.
- **`[UI-KEY-NUDGE]`**: `src/bot/keyboards/nudge.py` - Inline buttons for proactive session reminders.
- **`[UI-KEY-ENT]`**: `src/bot/keyboards/entities.py` - Grids customized to handle db entities like rendering a project card inline menu.
- **`[UI-KEY-SET]`**: `src/bot/keyboards/settings.py` - Toggle boards for configuration edits.
- **`[UI-TEXTS]`**: `src/bot/texts.py` - Universal dictionary (or set of constants) defining strings bot replies with.

## 📁 12. Asynchronous Tasks (`src/scheduler/`)
- **`[JOB-CELERY-MOD]`**: `src/scheduler/tasks.py` - Setup mapping connecting Python functions in 'jobs.py' to cron-like Celery behaviors.

## 📁 13. Data Scripts & Migrations (`src/scripts/`)
- **`[SCRIPT-MIGRATE-LANG]`**: `src/scripts/migrate_language.py` - Single-run migration script to populate a default language column in the database.
- **`[SCRIPT-AUDIT-DOCS]`**: `src/scripts/audit_docs.py` - Automated CI/CD script to audit the Project Architecture mapping.
