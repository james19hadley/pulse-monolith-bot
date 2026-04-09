"""
Slash commands for managing entities (e.g., bypassing menus).

@Architecture-Map: [HND-ENT-CMDS]
@Docs: docs/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy import func

from src.db.repo import SessionLocal
from src.db.models import Project, TimeLog
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



