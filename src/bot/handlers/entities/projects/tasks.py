"""
Task management logic for specific projects.
@Architecture-Map: [HND-PROJ-TASKS]
"""
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
from src.db.models import Project, Task
from src.bot.states import EntityState

async def handle_project_tasks(cb: CallbackQuery, db: Session, user, proj: Project):
    pending_tasks = db.query(Task).filter(Task.project_id == proj.id, Task.status == 'pending').limit(10).all()
    
    kb = []
    kb.append([InlineKeyboardButton(text="➕ Add Task", callback_data=f"ui_proj_addtask_{proj.id}")])
    
    for t in pending_tasks:
        prefix = "🎯 " if getattr(t, 'is_focus_today', False) else ""
        row = [
            InlineKeyboardButton(text=f"✅ {prefix}{t.title}", callback_data=f"ui_proj_comptask_{proj.id}_{t.id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"ui_proj_deltask_{proj.id}_{t.id}")
        ]
        kb.append(row)
        if not getattr(t, 'is_focus_today', False):
            kb.append([InlineKeyboardButton(text=f"🎯 Set Focus: {t.title}", callback_data=f"ui_proj_setfocus_{proj.id}_{t.id}")])
            
    kb.append([InlineKeyboardButton(text="🔙 Back to Project", callback_data=f"ui_proj_{proj.id}")])
    
    msg_text = f"<b>Tasks for {proj.title}</b>"
    if pending_tasks:
        msg_text += "\nSelect a task to complete it, or set it as today's focus:"
    else:
        msg_text += "\nNo pending tasks. Add one to clear your mind!"
        
    await cb.message.edit_text(
        msg_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

async def handle_complete_task(cb: CallbackQuery, db: Session, user, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = "completed"
        db.commit()
        
        # Check for gentle AI follow up
        if getattr(task, 'is_focus_today', False) and user.api_keys:
            from src.core.security import decrypt_key
            from src.ai.providers import GoogleProvider
            import asyncio
            try:
                # Use current provider
                provider_name = user.llm_provider or 'google'
                key_data = user.api_keys.get(provider_name)
                if key_data:
                    api_key = decrypt_key(key_data["key"])
                    ai = GoogleProvider(api_key=api_key)
                    prompt = f"The user just finished their 'Focus of the Day' task: '{task.title}'. Be a gentle productivity sherpa. Congratulate them warmly but briefly, and ask gently if they'd like to tackle one more, or call it a day to avoid burnout."
                    
                    async def send_followup(text, chat_id):
                        from src.main import bot
                        if bot:
                            await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
                    
                    followup_text, _ = await ai.generate_chat_response(prompt, "You are a helpful productivity assistant.")
                    if followup_text:
                        asyncio.create_task(send_followup(followup_text, cb.from_user.id))
            except Exception:
                pass

        await cb.answer(f"Task '{task.title}' completed!")
        return task.project_id
    return None
