# Sprint 33: Domain Traceability & Semantic Anchors

**Status:** `Completed`
**Date Proposed:** April 9, 2026
**Objective:** Propagate the new Bidirectional Traceability standard (Plain-Text Semantic Anchors) strictly defined in docs/explanation/WORK_POLICY.md to every single Python file in the repository. Provide robust navigational links for AI context.

## 🎯 Goals
- Identify the primary architectural footprint of every functional file.
- Register all new UIDs in `docs/reference/07_ARCHITECTURE_MAP.md`.
- Add `@Architecture-Map: [UID]` to docstrings throughout the codebase.

## 📋 Tasks

### AI / Core / DB Layer
- [x] `src/admin_dashboard.py`
- [x] `src/ai/providers.py`
- [x] `src/ai/router.py`
- [x] `src/ai/tools.py`
- [x] `src/core/config.py`
- [x] `src/core/constants.py`
- [x] `src/core/personas.py`
- [x] `src/core/prompts.py`
- [x] `src/core/security.py`
- [x] `src/db/models.py`
- [x] `src/db/repo.py`

### Services Layer
- [x] `src/services/projects.py` (Completed)
- [x] `src/services/reporting.py` (Completed)

### Presentation / Handlers / Router Layer
- [x] `src/main.py`
- [x] `src/worker.py`
- [x] `src/bot/handlers/ai_router.py`
- [x] `src/bot/handlers/core.py`
- [x] `src/bot/handlers/sessions.py`
- [x] `src/bot/handlers/utils.py`
- [x] `src/bot/handlers/entities/commands.py`
- [x] `src/bot/handlers/entities/menu.py`
- [x] `src/bot/handlers/entities/router.py`
- [x] `src/bot/handlers/entities/projects/actions.py`
- [x] `src/bot/handlers/entities/projects/create.py`
- [x] `src/bot/handlers/entities/projects/list.py`
- [x] `src/bot/handlers/intents/intent_core.py`
- [x] `src/bot/handlers/intents/intent_entities.py`
- [x] `src/bot/handlers/intents/intent_log_work.py`
- [x] `src/bot/handlers/intents/intent_session.py`
- [x] `src/bot/handlers/settings/api_keys.py`
- [x] `src/bot/handlers/settings/general.py`
- [x] `src/bot/handlers/settings/persona_tz.py`
- [x] `src/bot/handlers/settings/reports.py`
- [x] `src/bot/handlers/settings/router.py`
- [x] `src/bot/handlers/settings/system_configs.py`

### Views / Keyboards
- [x] `src/bot/views.py` (Completed)
- [x] `src/bot/keyboards/core.py`
- [x] `src/bot/keyboards/entities.py`
- [x] `src/bot/keyboards/settings.py`
- [x] `src/bot/states.py`
- [x] `src/bot/texts.py`

### Scheduling
- [x] `src/scheduler/jobs.py` (Completed)
- [x] `src/scheduler/tasks.py`


### Documentation Restructuring & Automation
- [x] Reorganize `docs/` folder into the Diátaxis framework (`reference/`, `explanation/`, etc.).
- [x] `src/scripts/audit_docs.py` (Automated Document Auditing).
- [x] Install `pre-push` git hook (`scripts/install_hooks.sh`) to block undocumented commits.
- [x] Update `WORK_POLICY.md` with AI Auditing Guardrails.

## 🔒 Security & Architecture Notes
- UIDs must use `[LAYER-DOMAIN-ACTION]` format. DO NOT use line numbers.
- Keep mapping explanations in `docs/reference/07_ARCHITECTURE_MAP.md` human-readable and concise.

## 🏁 Completion Criteria
- Every `.py` file containing logic is checked off.
- `07_ARCHITECTURE_MAP.md` accurately resolves every tag added to the docstrings.
