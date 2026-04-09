# Sprint 33: Domain Traceability & Semantic Anchors

**Status:** `Active`
**Date Proposed:** April 9, 2026
**Objective:** Propagate the new Bidirectional Traceability standard (Plain-Text Semantic Anchors) strictly defined in WORK_POLICY.md to every single Python file in the repository. Provide robust navigational links for AI context.

## 🎯 Goals
- Identify the primary architectural footprint of every functional file.
- Register all new UIDs in `docs/07_ARCHITECTURE_MAP.md`.
- Add `@Architecture-Map: [UID]` to docstrings throughout the codebase.

## 📋 Tasks

### AI / Core / DB Layer
- [ ] `src/admin_dashboard.py`
- [ ] `src/ai/providers.py`
- [ ] `src/ai/router.py`
- [ ] `src/ai/tools.py`
- [ ] `src/core/config.py`
- [ ] `src/core/constants.py`
- [ ] `src/core/personas.py`
- [ ] `src/core/prompts.py`
- [ ] `src/core/security.py`
- [ ] `src/db/models.py`
- [ ] `src/db/repo.py`

### Services Layer
- [x] `src/services/projects.py` (Completed)
- [x] `src/services/reporting.py` (Completed)

### Presentation / Handlers / Router Layer
- [ ] `src/main.py`
- [ ] `src/worker.py`
- [ ] `src/bot/handlers/ai_router.py`
- [ ] `src/bot/handlers/core.py`
- [ ] `src/bot/handlers/sessions.py`
- [ ] `src/bot/handlers/utils.py`
- [ ] `src/bot/handlers/entities/commands.py`
- [ ] `src/bot/handlers/entities/menu.py`
- [ ] `src/bot/handlers/entities/router.py`
- [ ] `src/bot/handlers/entities/projects/actions.py`
- [ ] `src/bot/handlers/entities/projects/create.py`
- [ ] `src/bot/handlers/entities/projects/list.py`
- [ ] `src/bot/handlers/intents/intent_core.py`
- [ ] `src/bot/handlers/intents/intent_entities.py`
- [ ] `src/bot/handlers/intents/intent_log_work.py`
- [ ] `src/bot/handlers/intents/intent_session.py`
- [ ] `src/bot/handlers/settings/api_keys.py`
- [ ] `src/bot/handlers/settings/general.py`
- [ ] `src/bot/handlers/settings/persona_tz.py`
- [ ] `src/bot/handlers/settings/reports.py`
- [ ] `src/bot/handlers/settings/router.py`
- [ ] `src/bot/handlers/settings/system_configs.py`

### Views / Keyboards
- [x] `src/bot/views.py` (Completed)
- [ ] `src/bot/keyboards/core.py`
- [ ] `src/bot/keyboards/entities.py`
- [ ] `src/bot/keyboards/settings.py`
- [ ] `src/bot/states.py`
- [ ] `src/bot/texts.py`

### Scheduling
- [x] `src/scheduler/jobs.py` (Completed)
- [ ] `src/scheduler/tasks.py`

## 🔒 Security & Architecture Notes
- UIDs must use `[LAYER-DOMAIN-ACTION]` format. DO NOT use line numbers.
- Keep mapping explanations in `docs/07_ARCHITECTURE_MAP.md` human-readable and concise.

## 🏁 Completion Criteria
- Every `.py` file containing logic is checked off.
- `07_ARCHITECTURE_MAP.md` accurately resolves every tag added to the docstrings.
