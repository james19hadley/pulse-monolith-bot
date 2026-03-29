import re
with open("src/bot/handlers/entities/projects.py", "r") as f:
    orig = f.read()

s1 = """        elif action == "edit":
            await state.update_data(eid=proj.id)
            await state.set_state(EntityState.waiting_for_edit_project_target)
            await cb.message.edit_text(
                f"Enter new target <b>hours</b> for project <code>{proj.title}</code> (0 to disable target):", 
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]])
            )"""

r1 = """        elif action == "edit":
            await state.update_data(eid=proj.id)
            await state.set_state(EntityState.waiting_for_edit_project_target)
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            unit_str = "hours" if is_time_based else proj.unit
            await cb.message.edit_text(
                f"Enter new target <b>{unit_str}</b> for project <code>{proj.title}</code> (0 to disable target):", 
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]])
            )"""

orig = orig.replace(s1, r1)

s2 = """@router.message(EntityState.waiting_for_edit_project_target)
async def state_edit_project_target(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("eid")
    
    try:
        hours = float(message.text.strip())
        minutes = int(hours * 60)
    except:
        await message.answer("Please enter a valid number.")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if proj:
            proj.target_value = minutes
            db.commit()
            await message.answer(f"✅ Target for `{proj.title}` updated to {hours:g}h.", parse_mode="Markdown")"""

r2 = """@router.message(EntityState.waiting_for_edit_project_target)
async def state_edit_project_target(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("eid")
    
    try:
        val = float(message.text.strip())
    except:
        await message.answer("Please enter a valid number.")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if proj:
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            if is_time_based:
                proj.target_value = int(val * 60)
                db.commit()
                await message.answer(f"✅ Target for `{proj.title}` updated to {val:g}h.", parse_mode="Markdown")
            else:
                proj.target_value = val
                db.commit()
                await message.answer(f"✅ Target for `{proj.title}` updated to {val:g} {proj.unit}.", parse_mode="Markdown")"""

orig = orig.replace(s2, r2)


s3 = """        msg = f"✅ Project created: {proj.title}"
        if proj.target_value > 0:
            msg += f" (Target: {proj.target_value / 60:g}h)"
        await message.answer(msg)"""

r3 = """        msg = f"✅ Project created: {proj.title}"
        if proj.target_value > 0:
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            if is_time_based:
                msg += f" (Target: {proj.target_value / 60:g}h)"
            else:
                msg += f" (Target: {proj.target_value:g} {proj.unit})"
        await message.answer(msg)"""

orig = orig.replace(s3, r3)

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.write(orig)

