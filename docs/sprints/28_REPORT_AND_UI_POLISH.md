# Sprint 27: Report Engine Polish & Mathematical Fixes

**Status:** `Draft`
**Date Proposed:** March 29, 2026
**Objective:** Fix progress accumulation bugs in the Daily Report and customize the "Chef's Kiss" AI commentary for better localization.

## 🎯 Goals
1. Fix the bug where adding incremental progress (`+15 pages`) successfully creates a TimeLog but fails to update the global `0/114 pages` state reliably in the Evening Report.
2. Perfect the "Chef's Kiss" element: ensure the bot translates the final witty or encouraging summary into the user's language (e.g., Russian) and gives it configurable formatting.

## 📋 Tasks

### 1. Progress State Math Correction
- [ ] Audit `intent_log_work.py` and absolute value calculations from Sprint 22.
- [ ] Ensure that `project.current_value` is explicitly tracked, persisted, and accurately summed when computing the `[░░░░░░░░] 0%` UI bar.
- [ ] Make sure adding "+15 pages" updates both the `TimeLog` and actively increments `Project.current_value`.

### 2. Localization & "Chef's Kiss" Tuning
- [ ] Add rules to the AI Report generation prompt (Chef's Kiss) to respect the user's implicit or explicit language (Russian).
- [ ] Investigate UI parameters for defining how this final AI text block is formatted.

## 🔒 Security & Architecture Notes
- Only structural UI formatting; must not leak context between users.

## 🏁 Completion Criteria
- User logs +15 pages, and the report shows `15/114 pages [█░░░░░░░] 13%`.
- The final AI summary is written in native Russian matching the personality.
