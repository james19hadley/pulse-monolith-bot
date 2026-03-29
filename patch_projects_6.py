import re
with open("src/bot/handlers/entities/projects.py", "r") as f:
    orig = f.read()

s1 = """        elif action == "add":
            await state.update_data(eid=proj.id)
            await state.set_state(EntityState.waiting_for_add_project_time)
            await cb.message.edit_text(f"Enter minutes to log for <code>{proj.title}</code>:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))"""

r1 = """        elif action == "add":
            await state.update_data(eid=proj.id)
            await state.set_state(EntityState.waiting_for_add_project_time)
            unit_str = proj.unit if proj.unit and proj.unit not in ['minutes', 'hours'] else 'minutes'
            await cb.message.edit_text(f"Enter <b>{unit_str}</b> to log for <code>{proj.title}</code>:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))"""

orig = orig.replace(s1, r1)

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.write(orig)

