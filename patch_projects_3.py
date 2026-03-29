import re
with open("src/bot/handlers/entities/projects.py", "r") as f:
    orig = f.read()

s1 = """        elif action == "delete":
            # Real delete
            from src.db.models import ActionLog
            import json
            delete_log = ActionLog(
                user_id=user.id,
                tool_name="delete_project",
                previous_state_json=json.dumps({
                    "id": proj.id,
                    "title": proj.title,
                    "target_value": proj.target_value,
                    "unit": proj.unit
                }),
                new_state_json={}
            )
            db.add(delete_log)
            db.delete(proj)
            db.commit()
            await cb.answer(f"Deleted {proj.title}.")
            # Hack to invoke archlist
            cb = cb.model_copy(update={"data": "ui_proj_archlist"})
            await cb_project_action(cb, state)"""

r1 = """        elif action == "delete":
            # Real delete
            status = proj.status
            from src.db.models import ActionLog
            import json
            delete_log = ActionLog(
                user_id=user.id,
                tool_name="delete_project",
                previous_state_json=json.dumps({
                    "id": proj.id,
                    "title": proj.title,
                    "target_value": proj.target_value,
                    "unit": proj.unit
                }),
                new_state_json={}
            )
            db.add(delete_log)
            db.delete(proj)
            db.commit()
            await cb.answer(f"Deleted {proj.title}.")
            if status == "archived":
                cb = cb.model_copy(update={"data": "ui_proj_archlist"})
                await cb_project_action(cb, state)
            else:
                await cb_projects_list(cb, state)"""

orig = orig.replace(s1, r1)

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.write(orig)

