from aiogram import Router, F
from aiogram.filters import Command
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
/habit &lt;id/name&gt; [val] - Mark habit (e.g. /habit workout 1)
/inbox &lt;text&gt; - Fast idea dump
/undo - Revert the last time log or habit log

<b>Data & Config</b>
/projects - List active projects and IDs
/habits - List active habits and IDs
/new_project &lt;name&gt; | [target_hours] - Create a new project
/new_habit &lt;name&gt; - Create a new habit
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
async def cmd_undo(message: Message):
    await message.answer(
        "To undo an action, please tap the **↩️ Undo** inline button attached to the exact confirmation message (like when you log a habit or time).\n\n<i>This prevents accidentally deleting the wrong data!</i>", 
        parse_mode="HTML"
    )
