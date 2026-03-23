# Sprint 10: Deep Customization & AI Settings Router

**Status:** `Completed`
**Date Proposed:** March 23, 2026
**Objective:** Expand the bot's configuration capabilities (timezone, cutoff times, personas) and allow the LLM to understand natural language requests to change settings, making the CLI (`/settings`) optional for power users.

## 🎯 Goals
- Add explicit new settings: `timezone` (e.g., "Europe/Moscow"), `cutoff` (e.g., "00:00"), and `persona` (e.g., "monolith", "butler").
- Train the `IntentRouter` to catch `SYSTEM_CONFIG` and automatically map phrases like "post my daily report at midnight" to the correct database column.
- Allow natural language triggers for immediate actions (e.g., "send my report now" triggers the end-day protocol).

## 📋 Tasks

### 1. Expanding the Registry (`config.py`)
- [x] Add `timezone` to `USER_SETTINGS_REGISTRY`.
- [x] Add `cutoff` to parse strings like "23:00" into `datetime.time` objects securely. 
- [x] Add `persona` to customize the AI's speaking style.

### 2. The AI Config Parser (`providers.py` & `router.py`)
- [x] Add `SystemConfigParams(BaseModel)` to extract `setting_key` and `setting_value` from user prompts.
- [x] Inject the available `USER_SETTINGS_REGISTRY` keys into the prompt so the LLM knows what it can configure.

### 3. Wiring the Brain (`handlers.py`)
- [x] Catch `intent == IntentType.SYSTEM_CONFIG`.
- [x] Execute the backend change and reply with "✅ Configuration updated".
- [x] Map "send report now" natural language to either `SESSION_CONTROL` (END) or a direct view call, giving the user instant satisfaction when they demand a report out of schedule.

## 🔒 Security & Architecture Notes
- Timezone must be handled safely so APScheduler doesn't crash on invalid zones.
- The time parser for `cutoff` should default gracefully if the AI hallucinates a weird format.

## 🏁 Completion Criteria
- User can say: "Change my daily report drop to 23:30 and timezone to Moscow" and the bot applies the settings directly without needing `/settings` commands.