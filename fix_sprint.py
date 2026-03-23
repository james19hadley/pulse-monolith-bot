with open("docs/sprints/06_AUTONOMY_AND_HABITS.md", "r") as f:
    text = f.read()

tasks = """
### 4. Void Fixes & Configuration Refactoring
- [x] Implement Retroactive Close in `stale_session_killer` so we don't track 16 hours of sleep.
- [x] Create `USER_SETTINGS_REGISTRY` in `config.py` for settings structure.
- [x] Refactor `/settings` in `handlers.py` to map from the registry dynamically instead of IF/ELSE chains.
- [x] Use purely English for all config code.

## 🏁 Completion Criteria"""

text = text.replace("## 🏁 Completion Criteria", tasks)
with open("docs/sprints/06_AUTONOMY_AND_HABITS.md", "w") as f:
    f.write(text)
