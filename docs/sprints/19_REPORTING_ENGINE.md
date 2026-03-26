# Sprint 19: Reporting Engine & Time Accuracy

**Status:** `Draft`
**Date Proposed:** March 26, 2026
**Objective:** Completely rebuild the Accountability Daily Report so it feels "fresh", visually appealing, and respects the user's specific timezone and cutoff boundaries instead of a naive UTC 24-hour window. This also includes fully connecting the natural language `CONFIG_REPORT` intent and making the AI Summary context-aware.

## 🎯 Goals
1. **Timezone Perfection:** Replace the buggy `last_24h = utcnow() - 24h` logic with a proper query boundary based on the user's `timezone` and `day_cutoff_time`.
2. **Visual Progress Integration:** Display the new `unit` based progress metrics developed in Sprint 18 directly in the Evening Report.
3. **Context-Aware AI Summaries:** Fix the "blind LLM" issue. Pass the actual projects, habits, and time stats to the AI prompt in `utils.py`, and include a flag (`is_auto` vs `is_manual`) so the LLM knows if the user clicked "End Day" or if the cronjob auto-fired. 
4. **Natural Language Config:** Implement the missing `_handle_config_report()` function in `ai_router.py` mapped to `IntentType.CONFIG_REPORT`, allowing users to literally say "Remove emojis from my report".

## 📋 Tasks
### Reporting Logic & NLP Config
- [ ] Migrate `generate_daily_report_text` to strictly respect timezone bounds.
- [ ] Refactor `build_daily_report` HTML layout (fix duplicate headers, improve spacing).
- [ ] Implement `IntentType.CONFIG_REPORT` route and extraction AI tool to properly update the JSON `report_config` field.

### AI Persona Integration
- [ ] Inject the `stats` dictionary into the prompt for the generative AI summary.
- [ ] Add boolean parameter `is_auto_cron` and instruct the Persona to react appropriately (e.g. roasting the user if they abandoned the session without closing it manually).

## 🔒 Security & Architecture Notes
- The report generation function must remain perfectly deterministic and idempotent.

## 🏁 Completion Criteria
- User can say "Make my reports strict without emojis".
- Pressing `🌙 End Day` generates a gorgeous report where the AI comment specifically references actual completed tasks (e.g. "Good job logging 2h on Pulse Monolith, but you missed your Workout.").
