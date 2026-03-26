import json
from aiogram.types import Message
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from src.db.models import User, Session as AppSession, TimeLog, Project, Habit, Inbox
from src.ai.providers import GoogleProvider
from src.bot.views import unknown_command_message

async def _handle_create_entities(message: Message, db: DBSession, user: User, provider_name: str, api_key: str):
    """Handles IntentType.CREATE_PROJECT and IntentType.CREATE_HABIT via multi-tool call"""
    provider = GoogleProvider(api_key=api_key)
    
    prompt = f"The user wants to create a new project and/or habit. Extract the details from: '{message.text}'"
    
    # We use a combined schema that can return lists of projects/habits to create
    response, tokens = provider.generate_structured_response(prompt, "CreateEntitiesParams")
    from src.bot.handlers.utils import log_tokens
    log_tokens(db, user.telegram_id, tokens)
    
    if not response:
        await message.answer(unknown_command_message())
        return

    created_msgs = []
    
    # Create projects
    if getattr(response, "projects", None):
        for p in response.projects:
            # We map target_minutes abstraction to the generic "Sprint 18" fields
            t_val = getattr(p, "target_value", None) or getattr(p, "target_minutes", 0)
            proj = Project(
                user_id=user.id,
                title=p.title,
                target_value=t_val,
                unit=getattr(p, "unit", "minutes")
            )
            db.add(proj)
            db.commit()
            db.refresh(proj)
            from src.bot.views import project_created_message
            created_msgs.append(project_created_message(proj.id, proj.title))
            
    # Create habits
    if getattr(response, "habits", None):
        for h in response.habits:
            habit = Habit(
                user_id=user.id,
                title=h.title,
                target_value=getattr(h, "target_value", 1),
                type=getattr(h, "type", "counter")
            )
            db.add(habit)
            db.commit()
            db.refresh(habit)
            from src.bot.views import habit_created_message
            created_msgs.append(habit_created_message(habit.id, habit.title, habit.target_value))

    if not created_msgs:
        await message.answer("I couldn't identify any specific projects or habits to create.")
    else:
        await message.answer("\n".join(created_msgs))

async def _handle_add_inbox(message: Message, db: DBSession, user: User, provider_name: str, api_key: str):
    """Handles IntentType.CATCH_TO_INBOX"""
    # Extremely fast & cheap: we just save the raw text directly. 
    # No LLM extraction needed unless we want to summarize it.
    item = Inbox(user_id=user.id, raw_text=message.text)
    db.add(item)
    db.commit()
    from src.bot.views import inbox_saved_message
    await message.answer(inbox_saved_message(message.text[:50] + "..."))
