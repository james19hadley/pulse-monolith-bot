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
async def cmd_help(message: Message):
    help_text = """
<b>Pulse Monolith - Manual Overrides</b>
Talk to me naturally, but if the AI is slow or offline, use these slash commands:

<b>Tracking (Zero-AI)</b>
<code>/start_session</code> - Begin a new tracking session
<code>/end_session</code> - End current session and summarize
<code>/log &lt;min&gt; [desc]</code> - Quick log (e.g. <code>/log 30 reading</code>)
<code>/habit &lt;id/name&gt; [val]</code> - Mark habit (e.g. <code>/habit workout 1</code>)
<code>/inbox &lt;text&gt;</code> - Fast idea dump

<b>Data & Config</b>
<code>/projects</code> - List active projects and IDs
<code>/habits</code> - List active habits and IDs
<code>/new_project &lt;name&gt; | [target_hours]</code> - Create a new project
<code>/new_habit &lt;name&gt;</code> - Create a new habit
<code>/settings</code> - View or change your configurations
<code>/persona</code> - View or change your AI Persona
<code>/tokens</code> - View AI Token usage & API costs
<code>/test_report</code> - Force generate your daily report

<b>API Keys</b>
<code>/add_key &lt;provider&gt; &lt;key&gt; [name]</code> - Set your API key
<code>/my_key</code> - Check your current aliases
<code>/delete_key &lt;name&gt;</code> - Remove an alias
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
