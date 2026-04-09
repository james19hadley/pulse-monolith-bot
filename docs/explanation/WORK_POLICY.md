# Development Work Policy & Practices

This document outlines the agreements between the User and the AI Developer (Monolith Bot Project) to ensure a high-quality, maintainable, and "ecological" development process.

## 1. Git Commit Strategy (Atomic Commits)
**Philosophy:** Commits are "save points", not "finished products". 
*   We commit **frequently** and **atomically**. 
*   A commit like `Initial database schema setup` or `Setup environment` is perfectly valid and desired. If we break the bot logic later, we can roll back to the clean database state without losing everything.
*   **Rule of thumb:** If a Sprint task or sub-task is completed and works independently (even if it's just infrastructure), it gets committed.
*   **STRICT POLICY:** The AI Assistant must **NEVER** push (`git push`) to the remote repository or trigger CI/CD pipelines without explicitly declaring its intentions in the chat and receiving prior approval from the User. Since `main` is connected to production CI/CD, pushing silently causes unmonitored deployments and violates the collaborative trust model.

## 2. Testing Philosophy (Avoiding "Garbage" AI Tests)
AI-generated Unit Tests often become a mock-heavy mess that tests the framework, not the logic. 
Instead, we focus on **Pragmatic Quality Assurance**:
*   **Core Logic Tests:** We will only write automated Python tests for pure math/logic functions (e.g., the function that calculates "The Void" time or timezone conversions). 
*   **Database Assertions:** We will use simple `test_db.py` scripts that assert we can create, read, and update records without throwing SQL errors. We do not need heavy unit-testing frameworks for the MVP.
*   **Black-Box / E2E Testing:** The main testing loop will be manual. We will run the bot locally, send it commands, and observe the database changes and Telegram outputs. This fits the "ecological" vibe of building a UX-first tool.

## 3. Provider-Agnostic LLM Architecture
The system is built to not depend entirely on one corporation (Google, OpenAI, Anthropic).
*   **Database Field:** The `llm_provider` field acts as an internal flag (e.g., `google`, `openai`).
*   **Code Interface:** We will implement a `BaseLLMProvider` class.
*   **Concrete Implementations:** 
    *   `GoogleProvider` (uses `google-genai` or API directly).
    *   `OpenAIProvider` (uses `openai` python package).
*   The router will check the user's `llm_provider`, instantiate the correct class, and call `.generate_response()`. This ensures adding a new provider in the future only takes ~50 lines of isolated code.## 4. Technical Debt & Rolling Sprints

*   **Strict Sprint Scope:** We strictly adhere to the current Sprint objectives. If we discover technical debt or architectural improvements (e.g., refactoring magic strings to Enums) during a sprint, we **do not bloat** the current sprint.
*   **Just-in-Time Planning:** Instead of fixing non-critical debt immediately, we log it as the **first task** of the *next* sprint. This ensures forward momentum while maintaining a clear, transparent record of what needs to be fixed without derailing the current feature delivery.

## 5. Codebase Traceability & Semantic Anchors (Engineering Docs)
To ensure AI agents and human developers can navigate the monolithic elements and logical files, we use **Bidirectional Traceability** via **Plain-Text Semantic Anchors**. 
- We do not rely on line numbers, which break during refactoring.
- We use a standardized UID format: `[LAYER-DOMAIN-ACTION]`. 
  - Layers: `SRV` (services database ops), `HND` (aiogram handlers), `UI` (bot views and keyboards), `JOB` (celery/async scheduler), `CORE` (ai and config).
- **Rule for Code:** Key architectural functions must include `@Architecture-Map: [UID]` in their Python `docstring`.
- **Rule for Docs:** The UID must be registered in `docs/reference/07_ARCHITECTURE_MAP.md` along with a human-readable explanation of why the component exists and what it connects to.

## 6. AI Automation & Audit Guardrails
- **Pre-Push Linter Check:** We enforce a `pre-push` git hook (via `scripts/install_hooks.sh`) that strictly blocks any repository pushes if `src/scripts/audit_docs.py` detects missing Semantic Anchors.
- **Agent Accountability:** Whenever finishing a Sprint and performing Git commits, the AI Agent must proactively parse `07_ARCHITECTURE_MAP.md` and ensure UIDs align. The agent must resolve any architecture audit errors independently before declaring a feature complete.
