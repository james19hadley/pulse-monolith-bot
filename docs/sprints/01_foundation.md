# Sprint 01: Foundation & Database Configuration

**Status:** `Completed`
**Date Proposed:** March 23, 2026
**Objective:** Set up the basic Python environment, the SQLite database, and SQLAlchemy ORM models based on the core architecture document.

## 🎯 Goals
- Establish the development environment safely.
- Create the single source of truth (the database) with Row-Level Security principles in mind.
- Prepare the initial Git repository state.

## 📋 Tasks

### 1. Environment & Dependencies
- [x] Initialize Git repository (if not already initialized).
- [x] Create `.gitignore` to protect sensitive data (`.env`, `venv/`, `*.sqlite3`).
- [x] Create `requirements.txt` with core dependencies (SQLAlchemy, aiogram, python-dotenv).
- [x] Create `.env.example` template.

### 2. Database Models (`src/db/models.py`)
- [x] Set up SQLAlchemy declarative base.
- [x] Implement `Users` table (timezone, llm_provider, cutoff_time).
- [x] Implement `Sessions` table (start_time, end_time, status).
- [x] Implement `Projects` table (title, status, target_minutes, etc.).
- [x] Implement `Habits` table (target_value, current_value).
- [x] Implement `Time_Logs` table (duration_minutes).
- [x] Implement `Action_Logs` table (for the Undo functionality).
- [x] Implement `Inbox` table (for raw thoughts).

### 3. Database Repository Layer (`src/db/repo.py`)
- [x] Create simple initialization script to generate the `db.sqlite3` file and tables locally.
- [x] Write a test script to verify that creating a user and a project works.

## 🔒 Security & Architecture Notes
- All models must reflect the explicit constraints defined in `04_DATABASE_AND_STATE.md`.
- No raw SQL will be used; everything must go through SQLAlchemy ORM.
- Development database will be a local SQLite file to ensure zero infrastructure overhead for the MVP phase.

## 🏁 Completion Criteria
- [x] We can successfully run a python script that creates the local SQLite database with all tables.
- [ ] All code is committed to Git.
