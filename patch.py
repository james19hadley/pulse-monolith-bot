from src.bot.handlers import router

handlers_code = """
@router.message(Command("test_report"))
async def cmd_test_report(message: Message):
    \"\"\"Developer command to instantly generate an accountability report regardless of the hour.\"\"\"
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        now = datetime.datetime.utcnow()
        last_24h = now - datetime.timedelta(hours=24)
        config = user.report_config if user.report_config else {"blocks": ["focus", "habits", "inbox", "void"], "style": "emoji"}
        
        user_logs = db.query(TimeLog).filter(TimeLog.user_id == user.id, TimeLog.created_at >= last_24h).all()
        focus_time = sum(l.duration_minutes for l in user_logs if l.project_id is not None)
        void_time = sum(l.duration_minutes for l in user_logs if l.project_id is None)
        
        proj_stats = {}
        for log in user_logs:
            if log.project_id:
                proj = db.query(Project).filter(Project.id == log.project_id).first()
                p_title = proj.title if proj else "Unknown Project"
                proj_stats[p_title] = proj_stats.get(p_title, 0) + log.duration_minutes
                
        user_habits = db.query(Habit).filter(Habit.user_id == user.id).all()
        habits_data = [{"title": h.title, "current": h.current_value, "target": h.target_value} for h in user_habits]
        
        inbox_items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").count()
        
        stats = {
            "date": now.strftime("%Y-%m-%d (Test)"),
            "focus_minutes": focus_time,
            "void_minutes": void_time,
            "projects": proj_stats,
            "habits": habits_data,
            "inbox_count": inbox_items
        }
        
        ai_comment = None
        if user.api_key_encrypted and user.llm_provider == "google":
            try:
                provider = GoogleProvider(api_key=decrypt_key(user.api_key_encrypted))
                prompt = f"Write a 1-sentence {user.persona_type} style comment for this end-of-day report. Just output the sentence."
                response = provider.client.models.generate_content(model=provider.model_id, contents=prompt)
                ai_comment = response.text
            except Exception as e:
                print(f"Failed to generate AI comment: {e}")
                
        report_text = build_daily_report(stats, config, ai_comment)
        await message.answer(report_text, parse_mode="Markdown")

@router.message(F.forward_from_chat)
async def cmd_bind_channel_via_forward(message: Message):
    \"\"\"Allows user to bind a channel simply by forwarding any message from it.\"\"\"
    if message.forward_from_chat.type == "channel":
        channel_id = message.forward_from_chat.id
        channel_title = message.forward_from_chat.title
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.target_channel_id = channel_id
            db.commit()
        await message.answer(f"✅ Awesome! I have bound your accountability reports to the channel: **{channel_title}**", parse_mode="Markdown")

from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_MEMBER, IS_ADMIN, IS_NOT_MEMBER

@router.my_chat_member()
async def on_my_chat_member(event: ChatMemberUpdated):
    \"\"\"Automatically bind a channel if the bot is added to it.\"\"\"
    if event.chat.type == "channel":
        if event.new_chat_member.status in ["administrator", "member", "creator"]:
            with SessionLocal() as db:
                user = get_or_create_user(db, event.from_user.id)
                user.target_channel_id = event.chat.id
                db.commit()
            try:
                await event.bot.send_message(
                    event.from_user.id,
                    f"✅ I noticed you added me to the channel **{event.chat.title}**!\nI've automatically set it as your target for Daily Accountability Reports."
                )
            except Exception:
                pass
"""

with open("src/bot/handlers.py", "r") as f:
    content = f.read()

# Insert before 'async def handle_freeform_text'
target = "@router.message(F.text)\nasync def handle_freeform_text(message: Message):"
content = content.replace(target, handlers_code + "\n" + target)

with open("src/bot/handlers.py", "w") as f:
    f.write(content)
print("done")
