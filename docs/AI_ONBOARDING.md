# 🤖 AI Agent Onboarding & Context Recovery

Welcome! If your context has just been reset, or you are a newly instantiated AI assistant working on the **Pulse Monolith Bot**, **READ THIS FILE FIRST**. 

This repository follows strict engineering, documentation, and product guidelines. Here is your roadmap to recover context and understand the project.

## 🧭 1. Where are we right now?
To find out what task we are currently working on, read the master sprint index:
👉 **`docs/sprints/00_SPRINTS_MASTER.md`**
*Look for the sprint marked as `🟡 Active`. Then, open that specific sprint file (e.g., `docs/sprints/34_AI_AGNOSTICISM.md`) to see the unchecked `[ ]` tasks.*

## 📜 2. What are the rules of this repository?
Before you write any code, execute any terminal commands, or commit to git, you MUST read the work policy. It contains critical instructions on Atomic Commits, Testing philosophies, and our Pre-Push Documentation Hooks.
👉 **`docs/explanation/WORK_POLICY.md`**

## 🗺️ 3. How do I navigate the codebase?
We do NOT use file-to-file documentation or line-number referencing. We use **Semantic Anchors** (e.g., `[SRV-PROJ-CREATE]`).
If you need to understand how the AI Router works, where database writes happen, or how the Telegram keyboards are generated, consult the architecture map:
👉 **`docs/reference/07_ARCHITECTURE_MAP.md`**

## 🧠 4. What is the product philosophy?
Pulse Monolith is not a standard Jira/GTD to-do list. It is an AI accountability partner built on specific psychological principles (Single-tasking, Spoon-feeding). If you are asked to design an interaction, you must grasp the vibe first:
👉 **`docs/explanation/01_PHILOSOPHY_AND_PSYCHOLOGY.md`**
👉 **`docs/explanation/02_CORE_UX_AND_MECHANICS.md`**

## 💾 5. How is the Database structured?
For understanding JSON fields like `report_config` or how nested projects work:
👉 **`docs/reference/04_DATABASE_AND_STATE.md`**

## ☁️ 6. How is the Bot Deployed and Logged?
If you need to debug a server crash, fetch logs, or understand where the bot actually runs (VPS, Docker, CI/CD):
👉 **`docs/reference/05_INFRASTRUCTURE.md`**

---

### 🚨 Your First Action After Reading This:
1. Verify the currently `Active` sprint in `00_SPRINTS_MASTER.md`.
2. Acknowledge your context recovery to the user by summarizing what task you believe we are doing right now.
3. Wait for the user's command to proceed.
