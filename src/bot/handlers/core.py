"""
Core bot handlers like /start, /help, and global keyboard interactions.

@Architecture-Map: [HND-BOT-CORE]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_MEMBER, IS_ADMIN, IS_NOT_MEMBER

from src.db.repo import SessionLocal
from src.bot.views import welcome_message
from src.bot.keyboards import get_main_menu
from src.bot.handlers.utils import get_or_create_user
from src.bot.texts import Buttons

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        has_key = bool(user.api_keys)
        
    await message.answer(welcome_message(has_key), parse_mode="HTML", reply_markup=get_main_menu())

@router.message(Command("help"))
@router.message(lambda msg: msg.text == "❓ Help")
async def cmd_help(message: Message):
    help_text = """
<b>Pulse Monolith - Manual Overrides</b>
Talk to me naturally, but if the AI is slow or offline, use these slash commands:

<b>Tracking (Zero-AI)</b>
/start_session - Begin a new tracking session
/end_session - End current session and summarize
/log &lt;min&gt; [desc] - Quick log (e.g. /log 30 reading)
/inbox &lt;text&gt; - Fast idea dump
/undo - Revert the last time log

<b>Data & Config</b>
/projects - List active projects and IDs
/new_project &lt;name&gt; | [target_hours] - Create a new project
/settings - View or change your configurations
/persona - View or change your AI Persona
/tokens - View AI Token usage & API costs
/test_report - Force generate your daily report

<b>API Keys</b>
/add_key &lt;provider&gt; &lt;key&gt; [name] - Set your API key
/my_key - Check your current aliases
/delete_key &lt;name&gt; - Remove an alias
"""
    await message.answer(help_text, parse_mode="HTML")

@router.my_chat_member()
async def on_my_chat_member(event: ChatMemberUpdated):
    if event.chat.type == "channel":
        if event.new_chat_member.status in ["administrator", "member", "creator"]:
            with SessionLocal() as db:
                user = get_or_create_user(db, event.from_user.id)
                user.target_channel_id = event.chat.id
                db.commit()
            try:
                await event.bot.send_message(
                    event.from_user.id,
                    f"✅ I noticed you added me to the channel <b>{event.chat.title}</b>!\nI've automatically set it as your target.",
                    parse_mode="HTML"
                )
            except Exception:
                pass

@router.message(Command("faq", "manual"))
async def cmd_faq(message: Message):
    faq_text = """
<b>Pulse Monolith - Documentation</b>

📖 <b>English Manual:</b> <a href="https://telegra.ph/Pulse-Monolith-AI-Bot---Quickstart--FAQ-01-01">Read Here</a>
🇷🇺 <b>Русский Мануал:</b> <a href="https://telegra.ph/Pulse-Monolith-AI-Bot---Quickstart--FAQ-RU-01-01">Читать здесь</a>

<i>External links will open in Telegraph. Setup guides, command references, and troubleshooting tips are available.</i>
"""
    await message.answer(faq_text, parse_mode="HTML", disable_web_page_preview=True)


@router.message(F.text == "📋 Tasks")
async def ui_tasks(message: Message):
    from src.db.models import Task, Project
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        tasks = db.query(Task).filter(Task.user_id == user.id, Task.status == "pending").all()
        
        if not tasks:
            await message.answer("You have no pending tasks. Add one by saying 'Create a task to ...'", reply_markup=get_main_menu())
            return
            
        projs = {p.id: p.title for p in db.query(Project).filter(Project.user_id == user.id).all()}
        
        lines = ["<b>📋 Your Pending Tasks:</b>"]
        for idx, t in enumerate(tasks, 1):
            proj_info = f" [<i>{projs.get(t.project_id)}</i>]" if t.project_id else ""
            lines.append(f"{idx}. {t.title}{proj_info}")
            
        await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=get_main_menu())

@router.message(F.text == "📥 Inbox")
async def ui_inbox(message: Message):
    from src.db.models import Inbox
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").all()
        
        if not items:
            await message.answer("Your inbox is empty.", reply_markup=get_main_menu())
            return
            
        lines = ["<b>📥 Your Inbox:</b>"]
        for i in items:
            lines.append(f"• {i.raw_text}")
            
        await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=get_main_menu())

@router.message(F.text == Buttons.STATS)
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    from src.bot.handlers.utils import generate_daily_report_text
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        try:
            report_text = generate_daily_report_text(db, user, skip_ai_comment=True)
            try:
                await message.answer(report_text, parse_mode="HTML", reply_markup=get_main_menu())
            except Exception as tg_err:
                import html
                # The text might have invalid HTML, try without parse mode or escape
                from aiogram.exceptions import TelegramBadRequest
                if isinstance(tg_err, TelegramBadRequest) and "parse" in str(tg_err).lower():
                    # Fallback: Strip HTML or just send without formatting
                    await message.answer(report_text, parse_mode=None, reply_markup=get_main_menu())
                else:
                    raise tg_err
        except Exception as e:
            import html
            await message.answer(f"Failed to generate stats: {html.escape(str(e))}", parse_mode="HTML", reply_markup=get_main_menu())

@router.message(Command("inbox"))
async def cmd_inbox(message: Message, command):
    from src.db.models import Inbox
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

@router.message(Command("undo"))
@router.message(lambda msg: msg.text == "↩️ Undo")
async def cmd_undo(message: Message, state: FSMContext):
    from src.db.models import ActionLog, Project, TimeLog
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        # Get the most recent action
        action = db.query(ActionLog).filter(ActionLog.user_id == user.id).order_by(ActionLog.created_at.desc()).first()
        
        if not action:
            await message.answer("Nothing to undo.")
            return
            
        tool = action.tool_name
        try:
            if tool == "create_project":
                pid = action.new_state_json.get("project_id")
                p = db.query(Project).filter(Project.id == pid).first()
                if p:
                    # If it was an unarchive, restore the archived state
                    prev_status = action.previous_state_json.get("status")
                    if prev_status == "archived":
                        p.status = "archived"
                        msg_text = f"⏪ Отменено: Проект <b>{p.title}</b> возвращен в архив."
                    else:
                        title = p.title
                        db.delete(p)
                        msg_text = f"⏪ Отменено: Создание проекта <b>{title}</b>."
                        
            elif tool == "delete_project":
                pid = action.previous_state_json.get("id")
                p = db.query(Project).filter(Project.id == pid).first()
                if p:
                    p.status = action.previous_state_json.get("status", "active")
                    p.title = action.previous_state_json.get("title", p.title)
                    p.target_value = action.previous_state_json.get("target_value", p.target_value)
                    p.unit = action.previous_state_json.get("unit", p.unit)
                    p.parent_id = action.previous_state_json.get("parent_id", p.parent_id)
                    msg_text = f"⏪ Отменено: Удаление проекта <b>{p.title}</b> отменено (проект восстановлен)."
                    
            elif tool == "edit_project":
                pid = action.previous_state_json.get("id")
                p = db.query(Project).filter(Project.id == pid).first()
                if p:
                    p.title = action.previous_state_json.get("title", p.title)
                    p.target_value = action.previous_state_json.get("target_value", p.target_value)
                    p.unit = action.previous_state_json.get("unit", p.unit)
                    p.parent_id = action.previous_state_json.get("parent_id", p.parent_id)
                    msg_text = f"⏪ Отменено: Редактирование проекта <b>{p.title}</b>."
                    
            elif tool == "log_work":
                lid = action.new_state_json.get("log_id")
                pid = action.new_state_json.get("project_id")
                mins = action.previous_state_json.get("amount", 0)
                prog = action.previous_state_json.get("progress_amount", 0)
                
                log_entry = db.query(TimeLog).filter(TimeLog.id == lid).first()
                if log_entry:
                    db.delete(log_entry)
                    p = db.query(Project).filter(Project.id == pid).first()
                    if p:
                        # Fallback correctly if prog is None
                        delta = prog if prog is not None else mins
                        p.current_value = max(0, (p.current_value or 0) - delta)
                        
                        if p.daily_target_value is not None:
                            was_complete = (p.daily_progress or 0) >= p.daily_target_value
                            p.daily_progress = max(0, (p.daily_progress or 0) - delta)
                            is_complete = p.daily_progress >= p.daily_target_value
                            
                            if was_complete and not is_complete:
                                p.total_completions = max(0, (p.total_completions or 0) - 1)
                                p.current_streak = max(0, (p.current_streak or 0) - 1)
                                
                    msg_text = f"⏪ Отменено: Логирование времени отменено."
            else:
                msg_text = f"⚠️ Undo for action '{tool}' is not currently supported."
            
            # Clean up the log so we don't undo it twice
            db.delete(action)
            db.commit()
            
            # Send message with ✅ and ❌ buttons 
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                 InlineKeyboardButton(text="✅", callback_data="ui_undo_ok"),
                 InlineKeyboardButton(text="❌", callback_data="ui_undo_bad")
            ]])
            await message.answer(msg_text, reply_markup=markup, parse_mode="HTML")
            
        except Exception as e:
            db.rollback()
            await message.answer(f"⚠️ Failed to undo: {e}")
            import traceback
            traceback.print_exc()
    if state: await state.clear()
    
    # Do not print 'Action canceled.' if we successfully undid or errored. We handled it.
    # We will just return to main menu quietly or send the menu again if needed.
    from src.bot.keyboards import get_main_menu
    if state: await state.clear()
    
from aiogram.types import CallbackQuery

@router.callback_query(F.data == "ui_undo_ok")
async def cq_undo_ok(callback_query: CallbackQuery):
    # Add a green checkmark to the existing message and remove buttons
    text = callback_query.message.html_text
    new_text = "✅ " + text
    await callback_query.message.edit_text(new_text, reply_markup=None, parse_mode="HTML")

@router.callback_query(F.data == "ui_undo_bad")
async def cq_undo_bad(callback_query: CallbackQuery):
    text = callback_query.message.html_text
    new_text = text + "\n\n<i>⚠️ Автоматический возврат (Redo) пока в разработке. Пожалуйста, повторите оригинальное действие вручную.</i>"
    await callback_query.message.edit_text(new_text, reply_markup=None, parse_mode="HTML")

