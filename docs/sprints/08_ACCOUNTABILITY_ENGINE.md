# Sprint 08: Accountability Engine & Dynamic Reports

**Status:** 🟢 Completed
**Date Proposed:** March 23, 2026

**Objective:** Enable the bot to post daily accountability summaries. Crucially, the structure and visual style of this report must be fully customizable via natural language (Prompt-to-Config), combining static data accuracy with AI personalization.

## 🎯 Goals
- Allow users to bind the bot to a specific Telegram Channel for accountability.
- Build a "Lego Builder" system in `views.py` that can assemble reports from discrete stat blocks (Focus, Habits, Inbox) based on a JSON config.
- Implement an LLM Intent that parses a user's natural language request (e.g., "dry report, no emojis, habits first") and saves it as a UI Config in the database.
- Combine deterministic static metric generation with an optional, AI-generated "Chef's Kiss" persona comment at the very end.
- Automate the posting using the scheduler at the user's `day_cutoff_time`.

## 📋 Tasks

### 1. Database & Config
- [x] Add `target_channel_id` (String) to the `User` model.
- [x] Add `report_config` (JSON) to the `User` model containing block order and style preferences (e.g., `{"blocks": ["focus", "habits"], "style": "strict"}`).
- [x] Update `USER_SETTINGS_REGISTRY` to allow manual testing of target channel.

### 2. The View Builder (Lego System)
- [x] Refactor `views.py` to support styles (e.g., `StyleEnum.EMOJI`, `StyleEnum.STRICT`) to strip out emojis if requested.
- [x] Write a `build_daily_report(stats, config)` function that stitches the requested blocks together in the right order.

### 3. LLM Prompt-to-Config Parser
- [x] Create an extraction prompt in `providers.py` that takes a user's wish ("make it strict with no emojis and only show focus time") and returns a structured JSON layout.
- [x] Map this to a new command `/set_report_style <prompt>` or conversational intent.

### 4. Aggregation & Posting
- [x] Implement the SQL queries to gather a day's TimeLogs, completed Habits, and Inbox items based on the day cutoff.
- [x] Add the AI "Chef's Kiss" element that reads the generated report and appends 1-2 persona-driven sentences.
- [x] Add a daily scheduler job to execute the posting.

## 🏁 Completion Criteria
- User can tell the bot how they want their report structured.
- The bot builds the report statically according to that config (saving tokens and ensuring accuracy).
- The final product, enhanced by a small AI roast/comment, is posted to the linked channel.
