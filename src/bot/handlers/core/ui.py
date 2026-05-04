"""
UI handlers for tasks, inbox, and stats.
@Architecture-Map: [HND-CORE-UI]
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from src.db.repo import SessionLocal
from src.db.models import Task, Project, Inbox
from src.bot.keyboards import get_main_menu
from src.bot.handlers.utils import get_or_create_user
from src.bot.texts import Buttons

router = Router()

@router.message(F.text == "📋 Tasks")
async def ui_tasks(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        tasks = db.query(Task).filter(Task.user_id == user.id, Task.status == "pending").all()
        
        if not tasks:
            await message.answer("You have no pending tasks. Add one by saying 'Create a task to ...'", reply_markup=get_main_menu(bool(user.active_session_id)))
            return
            
        projs = {p.id: p.title for p in db.query(Project).filter(Project.user_id == user.id).all()}
        
        lines = ["<b>📋 Your Pending Tasks:</b>"]
        for idx, t in enumerate(tasks, 1):
            proj_info = f" [<i>{projs.get(t.project_id)}</i>]" if t.project_id else ""
            dur_info = f" ⏳ {t.estimated_minutes}m" if getattr(t, 'estimated_minutes', None) else ""
            rem_info = f" ⏰ {t.reminder_time.strftime('%H:%M')}" if getattr(t, 'reminder_time', None) else ""
            lines.append(f"{idx}. {t.title}{dur_info}{rem_info}{proj_info}")
            
        await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=get_main_menu(bool(user.active_session_id)))

@router.message(F.text == "📥 Inbox")
async def ui_inbox(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").all()
        
        if not items:
            await message.answer("Your inbox is empty.", reply_markup=get_main_menu(bool(user.active_session_id)))
            return
            
        lines = ["<b>📥 Your Inbox:</b>"]
        for i in items:
            lines.append(f"• {i.raw_text}")
            
        await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=get_main_menu(bool(user.active_session_id)))

@router.message(F.text == Buttons.STATS)
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    from src.bot.handlers.utils import generate_daily_report_text
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        try:
            report_text = generate_daily_report_text(db, user, skip_ai_comment=True)
            try:
                await message.answer(report_text, parse_mode="HTML", reply_markup=get_main_menu(bool(user.active_session_id)))
            except Exception as tg_err:
                from aiogram.exceptions import TelegramBadRequest
                if isinstance(tg_err, TelegramBadRequest) and "parse" in str(tg_err).lower():
                    await message.answer(report_text, parse_mode=None, reply_markup=get_main_menu(bool(user.active_session_id)))
                else:
                    raise tg_err
        except Exception as e:
            import html
            await message.answer(f"Failed to generate stats: {html.escape(str(e))}", parse_mode="HTML", reply_markup=get_main_menu(bool(user.active_session_id)))

@router.message(Command("inbox"))
async def cmd_inbox(message: Message, command):
    import html
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        args = command.args
        if args and args.lower() in ["clear", "empty"]:
            db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").update({"status": "cleared"})
            db.commit()
            await message.answer("🧹 Inbox cleared.", parse_mode="HTML")
            return
            
        items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").all()
        if not items:
            await message.answer("📭 Your inbox is empty.")
            return
            
        text = "📥 <b>Your Inbox:</b>\n\n"
        for i, item in enumerate(items, 1):
            text += f"{i}. <i>{html.escape(item.raw_text)}</i>\n"
            
        text += "\n<i>Use /inbox clear to empty it, or tell me to convert these to tasks.</i>"
        await message.answer(text, parse_mode="HTML")
