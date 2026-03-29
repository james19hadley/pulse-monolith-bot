import re

with open("docs/sprints/26_PROJECT_ZERO_AND_NLP_EDITING.md", "r") as f:
    text = f.read()

replacement = """### 3. NLP Entity Editing Intent
- [x] Create a new intent `EDIT_ENTITIES`.
- [x] Implement AI extraction (entity type, target name, new name/value).
- [x] Route properly and respond gracefully if the user asks for something unsupported.

### 4. Sprint 24 Debt: Session Control Bugfix
- [x] Fix intent unpacking assignment where `tokens` dict evaluated as truthy `err`, causing valid AI commands like "начал сессию" to throw "Я не смог разобрать команду" without actually failing context mapping.
"""

text = re.sub(r'### 3\. NLP Entity Editing Intent.*?- \[x\] Route properly and respond gracefully if the user asks for something unsupported\.', replacement, text, flags=re.DOTALL)

with open("docs/sprints/26_PROJECT_ZERO_AND_NLP_EDITING.md", "w") as f:
    f.write(text)

