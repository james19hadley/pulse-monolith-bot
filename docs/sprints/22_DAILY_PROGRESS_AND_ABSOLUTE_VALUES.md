# Sprint 22: Daily Progress Tracking and Absolute Values

**Status:** `Draft`
**Date Proposed:** March 27, 2026
**Objective:** Enhance the project tracking capabilities by displaying daily progress and time since last activity, and allow users to set absolute progress values instead of only additive deltas.

## 🎯 Goals
1. Record and display daily progress and time elapsed since last activity for each project.
2. Enable users to set progress to absolute values (e.g., "Set progress to 40%").

## 📋 Tasks
### UI & Core Data
- [x] Update project stats retrieval to calculate and return "Progress today" and "Last active" metrics.
- [x] Modify the UI presentation in inline menus or messages to cleanly display these new metrics.

### AI & Router Extraction
- [x] Update `prompts.py` (Intent Router and/or Extractors) to deduce whether the user wants to add an incremental value or set an absolute value (`set_to_value=X` vs `add_value=Y`).
- [x] Implement logic in handlers to calculate the delta (`delta = X - current_value`) when an absolute value is provided, ensuring `TimeLog` records reflect the accurate change without overwriting state redundantly.

## 🔒 Security & Architecture Notes
- Maintain database integrity: Absolute value updates should still generate a `TimeLog` or `ActionLog` item representing the computed delta, so history isn't lost.

## 🏁 Completion Criteria
- UI shows "+Y% today" and "Last active: X hours ago" accurately.
- User can say "I am on page 20" or "Set progress to 40%" and the bot correctly calculates the difference and updates the project state.
