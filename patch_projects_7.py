import re
with open("src/bot/handlers/entities/projects.py", "r") as f:
    orig = f.read()

s1 = """@router.message(EntityState.waiting_for_add_project_time)
async def state_add_project_time(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("eid")
    
    try:
        minutes = int(message.text.strip())
    except:
        await message.answer("Please enter a valid number of minutes.")
        return
        
    with SessionLocal() as db:
        from src.db.models import TimeLog
        from datetime import datetime
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if proj:
            log = TimeLog(user_id=user.id, project_id=proj.id, duration_minutes=minutes, description="Manual entry via UI", created_at=datetime.utcnow())
            db.add(log)
            db.commit()
            await message.answer(f"✅ Logged {minutes}m to `{proj.title}`.", parse_mode="Markdown")"""

r1 = """@router.message(EntityState.waiting_for_add_project_time)
async def state_add_project_time(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("eid")
    
    try:
        val = float(message.text.strip())
    except:
        await message.answer("Please enter a valid number.")
        return
        
    with SessionLocal() as db:
        from src.db.models import TimeLog
        from datetime import datetime
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if proj:
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            if is_time_based:
                log = TimeLog(user_id=user.id, project_id=proj.id, duration_minutes=int(val), description="Manual entry via UI", created_at=datetime.utcnow())
                msg_text = f"✅ Logged {int(val)}m to `{proj.title}`."
            else:
                log = TimeLog(user_id=user.id, project_id=proj.id, duration_minutes=0, progress_amount=val, description="Manual entry via UI", created_at=datetime.utcnow())
                msg_text = f"✅ Logged {val:g} {proj.unit} to `{proj.title}`."
                
            db.add(log)
            db.commit()
            await message.answer(msg_text, parse_mode="Markdown")"""

orig = orig.replace(s1, r1)

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.write(orig)

