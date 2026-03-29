import re
import glob

def repl(file):
    try:
        with open(file, 'r') as f:
            c = f.read()
        c = c.replace('habits', 'projects')
        c = c.replace('habit', 'project')
        c = c.replace('Habit', 'Project')
        c = c.replace('Habits', 'Projects')
        with open(file, 'w') as f:
            f.write(c)
    except Exception as e:
        print(f"Error {file}: {e}")

files = [
    'docs/02_CORE_UX_AND_MECHANICS.md',
    'docs/03_MEMORY_AND_AI_PIPELINE.md',
    'docs/04_DATABASE_AND_STATE.md',
    'docs/BACKLOG.md'
]

for file in files:
    repl(file)

with open("docs/sprints/27_THE_GREAT_MIGRATION.md", "r") as f:
    text = f.read()
text = text.replace("- [ ] `docs/02_CORE_UX_AND_MECHANICS.md`", "- [x] `docs/02_CORE_UX_AND_MECHANICS.md`")
text = text.replace("- [ ] `docs/03_MEMORY_AND_AI_PIPELINE.md`", "- [x] `docs/03_MEMORY_AND_AI_PIPELINE.md`")
text = text.replace("- [ ] `docs/04_DATABASE_AND_STATE.md`", "- [x] `docs/04_DATABASE_AND_STATE.md`")
text = text.replace("- [ ] `docs/BACKLOG.md`", "- [x] `docs/BACKLOG.md`")
text = text.replace("Status:** `Draft`", "Status:** `Completed`")
with open("docs/sprints/27_THE_GREAT_MIGRATION.md", "w") as f:
    f.write(text)

