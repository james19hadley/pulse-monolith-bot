"""
Handlers for paginated output of all user projects.

@Architecture-Map: [HND-PROJ-LIST]
@Docs: docs/07_ARCHITECTURE_MAP.md
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User, Project
from src.bot.states import EntityState
from datetime import datetime, timezone
from src.bot.keyboards import get_projects_tree_keyboard, get_project_view_keyboard

router = Router()
@router.callback_query(lambda c: c.data == "ui_projects_list" or c.data.startswith("ui_prjl_"))
async def cb_projects_list(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    page = 0
    toggled_ids = set()
    
    if cb.data.startswith("ui_prjl_"):
        try:
            parts = cb.data.split("_")
            page = int(parts[2])
            if len(parts) > 3 and parts[3]:
                toggled_ids = set(int(x) for x in parts[3].split(".") if x)
        except Exception:
            pass
            
    with SessionLocal() as db:
        user = get_or_create_user(db, cb.from_user.id)
        
        all_projects = db.query(Project).filter(
            Project.user_id == user.id,
            Project.status == "active"
        ).all()
        
        title = "<b>Your Active Projects:</b>"
        
        try:
            await cb.message.edit_text(
                title,
                parse_mode="HTML",
                reply_markup=get_projects_tree_keyboard(all_projects, page=page, toggled_ids=toggled_ids)
            )
        except Exception:
            pass
        await cb.answer()


