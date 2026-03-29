import re
with open("src/bot/handlers/entities/projects.py", "r") as f:
    orig = f.read()

s1 = """
    if data[0] == "new":
"""
r1 = """
    if data[0] == "archlist":
        await state.clear()
        with SessionLocal() as db:
            user = get_or_create_user(db, cb.from_user.id)
            projects = db.query(Project).filter(
                Project.user_id == user.id, 
                Project.status == "archived"
            ).all()
            kb = []
            for p in projects:
                kb.append([InlineKeyboardButton(text=f"📦 {p.title}", callback_data=f"ui_proj_{p.id}")])
            kb.append([InlineKeyboardButton(text="🔙 Back to Active", callback_data="ui_projects_list")])
            await cb.message.edit_text(
                "<b>Archived Projects:</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
            )
        return

    if data[0] == "new":
"""

s2 = """                
            await cb.message.edit_text(text, parse_mode="HTML", reply_markup=get_project_view_keyboard(proj.id))
"""
r2 = """                
            await cb.message.edit_text(text, parse_mode="HTML", reply_markup=get_project_view_keyboard(proj.id, status=proj.status))
"""

s3 = """        if action == "arch":
            proj.status = "archived"
            db.commit()
            await cb.answer(f"Sent {proj.title} to archive.")
            await cb_projects_list(cb, state)
"""
r3 = """        if action == "arch":
            proj.status = "archived"
            db.commit()
            await cb.answer(f"Sent {proj.title} to archive.")
            await cb_projects_list(cb, state)

        elif action == "unarch":
            proj.status = "active"
            db.commit()
            await cb.answer(f"Restored {proj.title} from archive.")
            await cb_projects_list(cb, state)

        elif action == "delete":
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
            cb.data = "ui_proj_archlist"
            await cb_project_action(cb, state)
"""

orig = orig.replace(s1, r1)
orig = orig.replace(s2, r2)
orig = orig.replace(s3, r3)

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.write(orig)

