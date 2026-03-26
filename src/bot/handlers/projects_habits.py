from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy import func

from src.db.repo import SessionLocal
from src.db.models import User, Project, Habit, Inbox
from src.bot.handlers.utils import get_or_create_user

router = Router()

@router.message(Command("projects"))
async def cmd_projects(message: Message):
    """List all active projects."""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        projects = db.query(Project).filter(
            Project.user_id == user.id, 
            Project.status == "active"
        ).all()
        
        if not projects:
            await message.answer("You don't have any active projects right now.\nUse <code>/new_project &lt;name&gt;</code> to start one.", parse_mode="HTML")
            return
            
        lines = ["<b>Your Active Projects:</b>"]
        for p in projects:
            info = f"• <code>{p.title}</code> (<i>ID: {p.id}</i>)"
            if p.target_value > 0:
                info += f" — Target: {p.target_value / 60:g}h"
            lines.append(info)
            
        await message.answer("\n".join(lines), parse_mode="HTML")

@router.message(Command("habits"))
async def cmd_habits(message: Message):
    """List all tracked habits."""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        habits = db.query(Habit).filter(Habit.user_id == user.id).all()
        
        if not habits:
            await message.answer("No habits tracked. Let the AI know via natural language, e.g., 'Track me writing 500 words daily'.")
            return
            
        lines = ["<b>Your Habits:</b>"]
        for h in habits:
            emoji = '📈'
            progress = f"{h.current_value}/{h.target_value}" if h.target_value else str(h.current_value)
            lines.append(f"{emoji} {h.title} (<i>ID: {h.id}</i>): <code>{progress}</code>")
            
        await message.answer("\n".join(lines), parse_mode="HTML")

@router.message(Command("new_project"))
async def cmd_new_project(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: <code>/new_project &lt;name&gt; [| target_hours]</code>", parse_mode="HTML")
        return
        
    args_text = command.args
    target_value = 0
    title = args_text
    
    if "|" in args_text:
        parts = args_text.split("|", 1)
        title = parts[0].strip()
        try:
            target_value = int(float(parts[1].strip()) * 60)
        except ValueError:
            pass

    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        proj = Project(user_id=user.id, title=title, status="active", target_value=target_value)
        db.add(proj)
        db.commit()
        
        msg = f"Project created: {proj.title}"
        if proj.target_value > 0:
            msg += f" (Target: {proj.target_value / 60:g}h)"
        await message.answer(msg)

@router.message(Command("new_habit"))
async def cmd_new_habit(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: <code>/new_habit &lt;name&gt; [target_value]</code>", parse_mode="HTML")
        return
    parts = command.args.split()
    target = None
    if len(parts) > 1 and parts[-1].isdigit():
        target = int(parts.pop())
    title = " ".join(parts)
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        habit = Habit(user_id=user.id, title=title, target_value=target, current_value=0)
        db.add(habit)
        db.commit()
        await message.answer(f"Habit created: {habit.title}")

@router.message(Command("habit"))
async def cmd_habit(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: <code>/habit &lt;name&gt; [amount]</code>", parse_mode="HTML")
        return
    parts = command.args.split()
    amount = 1
    if len(parts) > 1 and parts[-1].isdigit():
        amount = int(parts.pop())
    title = " ".join(parts).lower()
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        habits = db.query(Habit).filter(Habit.user_id == user.id).all()
        matched = next((h for h in habits if title in h.title.lower()), None)
        if matched:
            matched.current_value += amount
            db.commit()
            await message.answer(f"Habit updated: {matched.title} is now {matched.current_value}")
        else:
            await message.answer("Habit not found.")

@router.message(Command("inbox"))
@router.message(lambda msg: msg.text == "📥 Inbox")

async def cmd_inbox(message: Message, command: CommandObject = None):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        if not command or not command.args:
            items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").all()
            if not items:
                await message.answer("Your inbox is empty. To add a thought, use <code>/inbox &lt;text&gt;</code>", parse_mode="HTML")
                return
            lines = ["<b>Your Inbox:</b>"]
            for idx, item in enumerate(items, 1):
                lines.append(f"{idx}. {item.raw_text}")
            lines.append("\nUse <code>/clear_inbox</code> to empty it.")
            await message.answer("\n".join(lines), parse_mode="HTML")
            return
            
        item = Inbox(user_id=user.id, raw_text=command.args)
        db.add(item)
        db.commit()
        await message.answer("✅ Saved to inbox.")

@router.message(Command("clear_inbox"))
async def cmd_clear_inbox(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").all()
        for item in items:
            item.status = "cleared"
        db.commit()
        await message.answer("🧹 Inbox cleared.")

