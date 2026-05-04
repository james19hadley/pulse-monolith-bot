# Sprint 50: Model-Agnostic Structured Outputs & Codebase Refactoring

**Status:** `Planned`
**Date Proposed:** 2026-05-04
**Objective:** Upgrade the existing Two-Step AI pipeline (Router -> Extractor) to use provider-agnostic Structured Outputs / Function Calling mechanisms (ensuring compatibility with OpenAI, Anthropic, Gemini, etc.). Additionally, refactor large files (>300 lines) into smaller, logical modules.

## 🧠 Why we are doing this
1. **AI Reliability:** Our Two-Step architecture is correct and saves tokens, but relying on text-to-JSON prompts is brittle. Using native Tool Calling / Structured Outputs guarantees 100% strict type adherence. This must be provider-independent so we aren't locked into Google Gemini.
2. **Code Maintainability:** Some handler files have grown too large (approaching or exceeding 300 lines). Breaking them down into smaller components will improve readability and testability.

## 📋 Tasks

### [Phase 1: Provider-Agnostic Tool Calling]
- [ ] **Task 1:** Update `src/ai/providers.py` to support standard structured output APIs across multiple LLM providers (standardizing how we pass tools to OpenAI, Anthropic, and Gemini).
- [ ] **Task 2:** Define Pydantic models / Data Schemas for every extraction. Examples:
  - `LogWorkSchema(project_id: int, duration_minutes: int)`
  - `AddTasksSchema(tasks: list[TaskModel])`

### [Phase 2: Router & Extractor Polish]
- [ ] **Task 3:** Clean up the extraction logic in handlers (`src/bot/handlers/intents/*.py`) to handle the new guaranteed typed objects instead of raw text parsing.
- [ ] **Task 4:** Measure latency improvements and ensure the `ProcessingSpinner` remains active for both the Routing and Extraction steps.

### [Phase 3: Large File Refactoring]
- [ ] **Task 5:** Audit the codebase for files exceeding ~300 lines. Focus especially on core modules and handler files.
- [ ] **Task 6:** Split large files into logical sub-modules (e.g., separating database queries, UI text generation, and business logic into different cohesive blocks).

## 🎯 Definition of Done
- The fundamental Two-Step architecture remains intact.
- All LLM calls use structured, provider-agnostic schemas without brittle text parsing.
- The AI pipeline supports at least one other provider natively (or is built to easily plug one in).
- No single file in the business logic or handler layers exceeds ~300 lines.
