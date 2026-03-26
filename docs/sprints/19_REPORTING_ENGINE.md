# Sprint 19: Reporting Engine & Time Accuracy

**Status:** `Draft`
**Date Proposed:** March 26, 2026
**Objective:** Completely rebuild the Accountability Daily Report so it feels "fresh", visually appealing, and respects the user's specific timezone and cutoff boundaries instead of a naive UTC 24-hour window.

## 🎯 Goals
1. **Timezone Perfection:** Replace the buggy `last_24h = utcnow() - 24h` logic with a proper query boundary based on the user's `timezone` and `day_cutoff_time` (e.g., matching the exact logical "day").
2. **Visual Progress Integration:** Display the new `unit` based progress metrics developed in Sprint 18 directly in the Evening Report.
3. **Data Integrity:** Investigate and patch the "lost logs" bug where recent natural language logs don't instantly appear in the generated report.

## 📋 Tasks
### Reporting Logic
- [ ] Migrate `generate_daily_report_text` to strictly respect timezone bounds.
- [ ] Refactor the Jinja/HTML string builder in `views.py` so the report doesn't look "silly" (improve spacing, symbols, logic).
- [ ] Include actual AI summary blocks recursively, avoiding placeholder text.

### Data Validation
- [ ] Write a script or command to force-sync today's logs to verify everything tracks correctly.
- [ ] Ensure that `total_minutes_spent` from Projects matches the summed `TimeLog` daily delta exactly when building the report.

## 🔒 Security & Architecture Notes
- The report generation function must be perfectly deterministic so it can be called seamlessly by the Cron Scheduler without crashing or duplicating data.

## 🏁 Completion Criteria
- When a user asks for `/test_report` immediately after logging "0.5h", the report generated precisely reflects that recent transaction with a beautiful visual layout.
