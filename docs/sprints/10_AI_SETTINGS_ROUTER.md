# Sprint 10: Deep Customization & AI Settings Router

**Status:** `Completed`
**Date Proposed:** March 23, 2026
**Objective:** Expand the bot's configuration capabilities (timezone, cutoff times, personas) and allow the LLM to understand natural language requests to change settings, making the CLI (`/settings`) optional for power users. This sprint also scaled to encompass critical database rework for multi-key storage and a major structural decoupling of the generic handler monolith.

## 🎯 Goals
- Add explicit new settings: `timezone` (e.g., "Europe/Moscow"), `cutoff` (e.g., "00:00"), and `persona` (e.g., "monolith", "butler").
- Train the `IntentRouter` to catch `SYSTEM_CONFIG` and automatically map phrases like "post my daily report at midnight" to the correct database column.
- Allow natural language triggers for immediate actions.

## 📋 Tasks

### 1. Expanding the Registry (`config.py`)
- [x] Add `timezone` to `USER_SETTINGS_REGISTRY`.
- [x] Add `cutoff` to parse strings like "23:00" into `datetime.time` objects securely.
- [x] Add `persona` to customize the AI's speaking style.
- [x] Add strict validation mapping IANA strings correctly via `zoneinfo` and presenting logical UTC offsets (e.g., UTC+3).

### 2. The AI Config Parser (`providers.py` & `router.py`)
- [x] Add `SystemConfigParams(BaseModel)` to extract `setting_key` and `setting_value` from user prompts.
- [x] Allow for batch extraction: switch from a single config extraction to `List[SingleConfigParam]` so users can instruct multiple setting changes in one prompt.
- [x] Inject the available `USER_SETTINGS_REGISTRY` keys into the prompt so the LLM knows what it can configure.

### 3. Database & Multiple Provider Iteration (`models.py` & `main.py`)
- [x] Update standard `api_key_encrypted` row into an auto-translating `@property def api_keys` that handles multi-key JSON nesting `{alias: {provider, key}}`.
- [x] Inject `/my_key`, `/set_key`, `/delete_key` directly into the Telegram command menu natively.

### 4. Structural Handlers Refactor (Unscheduled MVP Tech Debt)
- [x] Completely dismantle the `850+` line `handlers.py` legacy monolith.
- [x] Extract `handlers/core.py` for `/start`, `/help` and channel triggers.
- [x] Extract `handlers/utils.py` for standard user retrieval and token logging.
- [x] Extract `handlers/settings_keys.py` for settings and API operations.
- [x] Extract `handlers/projects_habits.py` and `handlers/sessions.py` to separate tracker workflows.
- [x] Extract `handlers/ai_router.py` to route all non-commands to the LLM NLP filter.
- [x] Mount all decomposed directories securely into the root `main.py` entrypoint.
- [x] Deprecate and remove legacy `handlers.py` entirely.

## 🔒 Security & Architecture Notes
- Timezone must be handled safely so APScheduler doesn't crash on invalid zones.
- API Key migrations execute purely in-memory over the DB mapping via Python `@property` getter/setters, negating the need for a rigid alembic schema drift.

## 🏁 Completion Criteria
- User can say: "Change my daily report drop to 23:30 and timezone to Europe/Moscow" and the bot updates both reliably in a single request.
- User can define "my_openai_1" and "my_gemini" simultaneously under aliases.
- Handlers package builds and tests cleanly.

### 5. Post-Refactoring Stabilization & Bug Fixes
- [x] Fix Markdown escaping errors in Telegram messages (`TelegramBadRequest: can't parse entities`).
- [x] Fix dictionary unpacking tuple mismatch in the `log_tokens` utility function to accurately record AI tokens per request.
- [x] Fix enum typo `IntentType.LOG_TIME` -> `IntentType.LOG_WORK` causing 500 crashes during NLP.
- [x] Implement graceful connection/quota fallbacks informing the user organically about invalid or exhausted API keys rather than silently crashing.
- [x] Rename `/set_key` to `/add_key` for clarity, and implement a distinct `/use_key <alias>` command to handle active AI provider switching seamlessly.
- [x] Fix `TypeError` in Inbox model instantiation (`raw_text` vs `content`).
- [x] Enhance `/inbox` handler to support parameterless execution (view pending items) and add `/clear_inbox`.
- [x] Fix Pydantic attribute mapping (`updates` -> `settings`) in `SystemConfigParams` within `ai_router.py` causing 500s during NLP system config execution.
- [x] Fix Markdown escaping errors in the `/settings` command where implicit underscores in config names conflicted with italic wrappers.
- [x] Fixed: Migrated `cmd_settings` in `settings_keys.py` to use `parse_mode="HTML"` to eliminate Telegram Markdown exception `Can't find end of the entity` triggered by variable values containing unescaped characters (such as underscores in timezones or JSON schemas).
- [x] Fixed: Outdated `/set_key` references in `ai_router.py` error messages updated to `/add_key`.
- [x] Fixed: `TypeError` during `/start_session` and `/end_session` where outdated model kwargs (`project_id`, `is_active`) caused instantiation crashes over the updated simplistic `Session` ORM model.
- [x] Fixed: `AttributeError` on `/test_report` caused by SQLite failing to natively deserialize `JSON` types, leading to a raw string being passed instead of a dictionary.
- [x] Refined: The `/settings` menu now instructs the user that they can leverage NLP via simple text input instead of displaying the legacy raw command usage.
- [x] Fixed: Converted Markdown formatting (`**Bold**`, `_Italic_`) to HTML tags (`<b>`, `<i>`) across the daily report builder (`build_daily_report`) and swapped dispatcher `parse_mode` to "HTML" to prevent `TelegramBadRequest: can't parse entities` during `/test_report` formatting edge-cases.
- [x] Refactored: Executed a codebase-wide sweep replacing `parse_mode="Markdown"` with `parse_mode="HTML"`. Replaced all inline markdown syntax (`**text**`, `*text*`, `_text_`, `` `text` ``) with explicit HTML tags (`<b>`, `<i>`, `<code>`) in string templates across `views.py`, `core.py`, `projects_habits.py`, `sessions.py`, `settings_keys.py`, and scheduler tasks (`jobs.py`) to permanently prevent Telegram `Can't find end of the entity` exceptions on variable injection.
