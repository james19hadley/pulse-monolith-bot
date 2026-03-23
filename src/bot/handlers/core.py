from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_MEMBER, IS_ADMIN, IS_NOT_MEMBER

from src.db.repo import SessionLocal
from src.bot.views import welcome_message
from src.bot.handlers.utils import get_or_create_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        has_key = bool(user.api_keys)
        
    await message.answer(welcome_message(has_key))

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
*Pulse Monolith - Manual Overrides*
Talk to me naturally, but if the AI is slow or offline, use these slash commands:

*Tracking (Zero-AI)*
`/start_session` - Begin a new tracking session
`/end_session` - End current session and summarize
`/log <min> [desc]` - Quick log (e.g. `/log 30 reading`)
`/habit <id/name> [val]` - Mark habit (e.g. `/habit workout 1`)
<code>/inbox &lt;text&gt;</code> - Fast idea dump

*Data & Config*
`/projects` - List active projects and IDs
<code>/new_project &lt;name&gt;</code> - Create a new project
`/new_habit <name>` - Create a new habit
`/settings` - View or change your configurations
`/stats` - View Token & API costs
`/test_report` - Force generate your daily report

*API Keys*
`/set_key <provider> <key> [name]` - Set your API key
<code>/my_key</code> - Check your current aliases
`/delete_key <name>` - Remove an alias
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
