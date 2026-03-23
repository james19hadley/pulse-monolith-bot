# Development Work Policy & Practices

This document outlines the agreements between the User and the AI Developer (Monolith Bot Project) to ensure a high-quality, maintainable, and "ecological" development process.

## 1. Git Commit Strategy (Atomic Commits)
**Philosophy:** Commits are "save points", not "finished products". 
*   We commit **frequently** and **atomically**. 
*   A commit like `Initial database schema setup` or `Setup environment` is perfectly valid and desired. If we break the bot logic later, we can roll back to the clean database state without losing everything.
*   **Rule of thumb:** If a Sprint task or sub-task is completed and works independently (even if it's just infrastructure), it gets committed.

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
*   The router will check the user's `llm_provider`, instantiate the correct class, and call `.generate_response()`. This ensures adding a new provider in the future only takes ~50 lines of isolated code.