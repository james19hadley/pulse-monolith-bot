# Sprint 30: Architectural Refactoring & Modularization

**Status:** `Completed`
**Date Proposed:** March 29, 2026

## 🎯 Motivation: Why do we need this?
Over the past 29 sprints, the codebase has grown rapidly to accommodate powerful new features (AI intent routing, complex FSM states, composite habits, advanced inline tree UI, and smart undo). However, this rapid feature delivery has resulted in severe "module bloating" and an accumulation of technical debt. 

For instance:
- `src/bot/handlers/entities/projects.py` is over 450 lines long, tightly coupling UI generation, business logic (ORM transactions), and Telegram state management.
- `src/bot/keyboards.py` approaches 450 lines, housing every single keyboard markup in the app.
- `src/scheduler/jobs.py` mixes Celery boilerplate with complex daily report text generation.

Before we implement higher-level gamification or real-time web dashboard features, we **must** decompose these monolith files to maintain developer velocity, avoid merge conflicts, and ensure testability.

## ✨ Goals & Refactoring Layers
This sprint introduces zero new user-facing features. The objective is purely structural hygiene.

### 1. Separation of Concerns (Business Logic vs. UI)
Currently, Telegram callback handlers (controllers) directly instantiate `SessionLocal`, query the `Project` model, calculate offsets, and write to `ActionLog`.
- **Target:** Introduce a `src/services/` layer (e.g., `ProjectService`, `UserService`).
- **Benefit:** Handlers will only parse the `types.Message`/`CallbackQuery` and pass parameters to the service. This makes core logic mockable and re-usable (e.g., calling `ProjectService.create_project()` from *both* the CLI fallback and the Telegram Bot).

### 2. Module De-bloating (File Segmentation)
Large files will be chunked into sensible sub-packages.

#### A. Redesign `src/bot/handlers/entities/projects.py`
We will destroy the monolith file and upgrade it to a package:
`src/bot/handlers/entities/projects/`
  ├── `__init__.py` (registers sub-routers)
  ├── `list.py` (handles only the pagination and list-view callbacks)
  ├── `actions.py` (handles edit/archive/delete physical actions)
  └── `create.py` (handles FSM for user-typed manual creation)

#### B. Redesign `src/bot/keyboards/`
Convert `src/bot/keyboards.py` into a package:
`src/bot/keyboards/`
  ├── `main_menu.py`
  ├── `settings.py`
  ├── `projects.py`
  └── `utils.py` (containing the braille padding logic and emoji hash math)

### 3. Cleanup Reports Logic
Move the heavy text-formatting functions out of `jobs.py` and `utils.py` into a dedicated `src/services/reporting.py`. The Celery job should just say `ReportingService.generate_evening_report(user_id)`.

## 📋 Implementation Steps
- [x] **Phase 1 (Keyboards):** Convert `keyboards.py` to a directory module (`src/bot/keyboards/`). Fix all cross-file imports globally.
- [x] **Phase 2 (Services Layer):** Create `src/services/projects.py`. Move creation, editing, and DB commits inside an abstracted service class.
- [x] **Phase 3 (Controllers):** Break down `entities/projects.py` into `list`, `actions`, and `create` files, bridging them via routers.
- [x] **Phase 4 (Reports):** Extract string generation from `jobs.py` into a dedicated reporting service.
- [x] **Integration Test:** Run a full manual regression test (creating a project, completing a task, `/undo`, changing settings) to ensure the newly modularized system behaves exactly identically to Sprint 29.d system behaves exactly identically to Sprint 29.