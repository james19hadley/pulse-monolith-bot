import re
with open("src/bot/handlers/entities/projects.py", "r") as f:
    orig = f.read()

orig = orig.replace('cb.data = "ui_proj_archlist"', 'cb = cb.model_copy(update={"data": "ui_proj_archlist"})')
orig = orig.replace('cb.data = f"ui_proj_tasks_{task.project_id}"', 'cb = cb.model_copy(update={"data": f"ui_proj_tasks_{task.project_id}"})')

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.write(orig)

