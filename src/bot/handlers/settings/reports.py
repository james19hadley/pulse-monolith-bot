from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User
from src.bot.keyboards import get_reports_keyboard, get_back_settings_keyboard
from src.db.models import TokenUsage
from sqlalchemy import func
from src.bot.views import stats_message, build_daily_report

router = Router()

@router.message(Command("tokens"))
async def cmd_tokens(message: Message):
    """Shows AI Token Usage"""
    from datetime import datetime, timezone, timedelta
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        # Total
        prompt_total = db.query(func.sum(TokenUsage.prompt_tokens)).filter(TokenUsage.user_id == user.id).scalar() or 0
        comp_total = db.query(func.sum(TokenUsage.completion_tokens)).filter(TokenUsage.user_id == user.id).scalar() or 0
        cost = (prompt_total / 1000000.0) * 0.075 + (comp_total / 1000000.0) * 0.30

        # Today
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        prompt_today = db.query(func.sum(TokenUsage.prompt_tokens)).filter(TokenUsage.user_id == user.id, TokenUsage.created_at >= today_start).scalar() or 0
        comp_today = db.query(func.sum(TokenUsage.completion_tokens)).filter(TokenUsage.user_id == user.id, TokenUsage.created_at >= today_start).scalar() or 0
        cost_today = (prompt_today / 1000000.0) * 0.075 + (comp_today / 1000000.0) * 0.30
        
        msg = f"📊 <b>Token Usage Statistics</b>\n\n"
        msg += f"<b>Today (UTC):</b>\n"
        msg += f"• Prompts: <code>{prompt_today}</code>\n"
        msg += f"• Completions: <code>{comp_today}</code>\n"
        msg += f"• Est. Cost: <b>${cost_today:.4f}</b>\n\n"
        
        msg += f"<b>All-Time:</b>\n"
        msg += f"• Prompts: <code>{prompt_total}</code>\n"
        msg += f"• Completions: <code>{comp_total}</code>\n"
        msg += f"• Est. Cost: <b>${cost:.4f}</b>"

        await message.answer(msg, parse_mode="HTML")


@router.callback_query(F.data.startswith("set_report_"))
async def cq_set_report(callback: CallbackQuery):
    dest = callback.data.replace("set_report_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        config = user.report_config
        import json
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except:
                config = {}
        if not config: config = {}
        config['destination'] = dest
        user.report_config = config
        db.commit()
        db.refresh(user)
        text = get_control_panel_text(user)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await callback.answer(f"Report destination set to {dest}!")


@router.message(Command("test_report"))
async def cmd_test_report(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        from src.bot.handlers.utils import generate_daily_report_text
        report_text = generate_daily_report_text(db, user)
        await message.answer(report_text, parse_mode="HTML")


@router.callback_query(F.data == "settings_test_report")
async def cq_test_report(callback: CallbackQuery):
    await callback.message.bot.send_chat_action(chat_id=callback.from_user.id, action="typing")
    from src.db.repo import SessionLocal
    from src.bot.handlers.utils import get_or_create_user
    from src.bot.views import build_daily_report
    
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        from src.bot.handlers.utils import generate_daily_report_text
        report_text = generate_daily_report_text(db, user, force_date="[TEST REPORT]", is_auto_cron=False)
        await callback.message.answer(report_text, parse_mode="HTML")
        await callback.answer()


