from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_MEMBER, IS_ADMIN, IS_NOT_MEMBER

from src.db.repo import SessionLocal
from src.bot.views import welcome_message
from src.bot.keyboards import get_main_menu
from src.bot.handlers.utils import get_or_create_user

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

@router.message(F.forward_from_chat)
async def cmd_bind_channel_via_forward(message: Message):
    if message.forward_from_chat.type == "channel":
        channel_id = message.forward_from_chat.id
        channel_title = message.forward_from_chat.title
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.target_channel_id = channel_id
            db.commit()
        await message.answer(f"✅ Awesome! I have bound your accountability reports to the channel: <b>{channel_title}</b>", parse_mode="HTML")

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
                    title = p.title
                    db.delete(p)
                    await message.answer(f"↩️ Project creation undone: <b>{title}</b>", parse_mode="HTML")
                    
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
                        if prog:
                            p.current_value = max(0, (p.current_value or 0) - prog)
                        else:
                            p.current_value = max(0, (p.current_value or 0) - mins)
                    await message.answer("↩️ Time log successfully undone.", parse_mode="HTML")
            
            # Clean up the log so we don't undo it twice
            db.delete(action)
            db.commit()
            
        except Exception as e:
            await message.answer(f"Failed to undo: {e}")
    await state.clear()
    await message.answer("Action canceled.", reply_markup=get_main_menu())

from aiogram.types import CallbackQuery

@router.callback_query(F.data.startswith("undo_"))
async def handle_undo_callbacks(callback: CallbackQuery):
    data = callback.data
    
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        
        # Format: undo_c_proj_{id}
        if data.startswith("undo_c_proj_"):
            proj_id = int(data.split("_")[3])
            from src.db.models import Project
            proj = db.query(Project).filter(Project.id == proj_id, Project.user_id == user.id).first()
            if proj:
                db.delete(proj)
                db.commit()
                await callback.message.edit_text(f"↩️ Project creation undone: <b>{proj.title}</b>", parse_mode="HTML")
            else:
                await callback.answer("Project not found or already deleted.")
                
        # Format: undo_c_hab_{id}
        elif data.startswith("undo_c_hab_"):
            hab_id = int(data.split("_")[3])
            
            hab = db.query().filter(.id == hab_id.user_id == user.id).first()
            if hab:
                db.delete(hab)
                db.commit()
                await callback.message.edit_text(f"↩️ creation undone: <b>{hab.title}</b>", parse_mode="HTML")
            else:
                await callback.answer(" not found or already deleted.")
                
        # Format: undo_work_{log_id}
        elif data.startswith("undo_work_"):
            log_id = int(data.split("_")[2])
            from src.db.models import TimeLog
            log_entry = db.query(TimeLog).filter(TimeLog.id == log_id, TimeLog.user_id == user.id).first()
            if log_entry:
                db.delete(log_entry)
                db.commit()
                await callback.message.edit_text("↩️ Time log successfully undone.", parse_mode="HTML")
            else:
                await callback.answer("Log not found or already undone.")
                
        # Format: undo_habit_{habit_id}_{amount}
        
    await callback.answer()
