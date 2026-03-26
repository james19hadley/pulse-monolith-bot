# Sprint 20: Entity Management UI (Interactive Inline Panels)

**Status:** `Draft`
**Date Proposed:** March 26, 2026
**Objective:** Replace text-only dumps for `/projects` and `/habits` with interactive inline keyboards, allowing the user to view, edit, and archive entities effortlessly via Telegram UI.

## 🎯 Goals
1. **Interactive Lists:** When a user calls `/projects`, return a clean text list paired with inline buttons for each active project.
2. **Entity Action Panels:** Tapping a project opens a specific detail view (e.g. "Pulse Monolith [3h/50h]") with buttons to [Edit Target (Set Final Goal)], [Archive], [Add Time].
3. **Habit Management:** Apply the exact same pattern for `/habits`, allowing users to adjust targets or toggle the tracking type.

## 📋 Tasks
- [ ] Update `cmd_projects` to generate `InlineKeyboardMarkup` mapped to `project_view_<id>`.
- [ ] Create callback handlers (`@router.callback_query()`) for Project detail, Edit Goal, Edit Unit, and Archive.
- [ ] Update `cmd_habits` (if exists) to output a similar inline UI layout.
- [ ] Safely handle "Archive" actions so we don't delete `TimeLog` records tied to dead projects, but just flip `status='archived'`.

## 🔒 Security & Architecture Notes
- All interactive UI flows must check `user_id == message.from_user.id` to prevent modifying someone else's project via stale inline buttons.

## 🏁 Completion Criteria
- User taps "⚙️ Settings" -> or calls `/projects` and can tap `[Pulse Monolith]` -> `[Archive]` seamlessly without ever typing a slash command.
