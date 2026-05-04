"""
Undo logic for recent user actions.
@Architecture-Map: [HND-CORE-UNDO]
"""
import traceback
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.db.repo import SessionLocal
from src.db.models import ActionLog, Project, TimeLog, Session, Task
from src.bot.handlers.utils import get_or_create_user
from src.bot.keyboards import get_main_menu

router = Router()

@router.message(Command("undo"))
@router.message(F.text == "↩️ Undo")
async def cmd_undo(message: Message, state: FSMContext):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        action = db.query(ActionLog).filter(ActionLog.user_id == user.id).order_by(ActionLog.created_at.desc()).first()
        
        if not action:
            await message.answer("Nothing to undo.")
            return
            
        tool = action.tool_name
        msg_text = ""
        try:
            if tool == "create_project":
                pid = action.new_state_json.get("project_id")
                p = db.query(Project).filter(Project.id == pid).first()
                if p:
                    prev_status = action.previous_state_json.get("status")
                    if prev_status == "archived":
                        p.status = "archived"
                        msg_text = f"⏪ Отменено: Проект <b>{p.title}</b> возвращен в архив."
                    else:
                        title = p.title
                        db.query(TimeLog).filter(TimeLog.project_id == p.id).update({TimeLog.project_id: None})
                        db.query(Task).filter(Task.project_id == p.id).update({Task.project_id: None})
                        db.query(Session).filter(Session.project_id == p.id).update({Session.project_id: None})
                        db.query(Project).filter(Project.parent_id == p.id).update({Project.parent_id: None})
                        db.delete(p)
                        msg_text = f"⏪ Отменено: Создание проекта <b>{title}</b>."
                        
            elif tool == "delete_project":
                pid = action.previous_state_json.get("id")
                p = db.query(Project).filter(Project.id == pid).first()
                if p:
                    p.status = action.previous_state_json.get("status", "active")
                    p.title = action.previous_state_json.get("title", p.title)
                    p.target_value = action.previous_state_json.get("target_value", p.target_value)
                    p.unit = action.previous_state_json.get("unit", p.unit)
                    p.parent_id = action.previous_state_json.get("parent_id", p.parent_id)
                    msg_text = f"⏪ Отменено: Удаление проекта <b>{p.title}</b> отменено (проект восстановлен)."
                    
            elif tool == "edit_project":
                pid = action.previous_state_json.get("id")
                p = db.query(Project).filter(Project.id == pid).first()
                if p:
                    p.title = action.previous_state_json.get("title", p.title)
                    p.target_value = action.previous_state_json.get("target_value", p.target_value)
                    p.unit = action.previous_state_json.get("unit", p.unit)
                    p.parent_id = action.previous_state_json.get("parent_id", p.parent_id)
                    msg_text = f"⏪ Отменено: Редактирование проекта <b>{p.title}</b>."
                    
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
                        delta = prog if prog is not None else mins
                        p.current_value = max(0, (p.current_value or 0) - delta)
                        if p.daily_target_value is not None:
                            was_complete = (p.daily_progress or 0) >= p.daily_target_value
                            p.daily_progress = max(0, (p.daily_progress or 0) - delta)
                            is_complete = p.daily_progress >= p.daily_target_value
                            if was_complete and not is_complete:
                                p.total_completions = max(0, (p.total_completions or 0) - 1)
                                p.current_streak = max(0, (p.current_streak or 0) - 1)
                        if action.previous_state_json.get("was_session_end"):
                            user.active_session_id = action.previous_state_json.get("session_id")
                            session_obj = db.query(Session).filter(Session.id == user.active_session_id).first()
                            if session_obj:
                                session_obj.status = "active"
                                session_obj.end_time = None
                            msg_text = f"⏪ Отменено: Завершение сессии. Сессия снова активна! (убрано {mins} м. из <b>{p.title}</b>)."
                        elif mins and prog:
                            msg_text = f"⏪ Отменено: Логирование {mins} м. и {prog} прогресса для <b>{p.title}</b>."
                        elif mins:
                            msg_text = f"⏪ Отменено: Логирование {mins} м. для <b>{p.title}</b>."
                        elif prog:
                            msg_text = f"⏪ Отменено: Логирование {prog} прогресса для <b>{p.title}</b>."
                        else:
                            msg_text = f"⏪ Отменено: Логирование для <b>{p.title}</b> отменено."
            else:
                msg_text = f"⚠️ Undo for action '{tool}' is not currently supported."
            
            db.delete(action)
            db.commit()
            
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                 InlineKeyboardButton(text="✅", callback_data="ui_undo_ok"),
                 InlineKeyboardButton(text="❌", callback_data="ui_undo_bad")
            ]])
            await message.answer(msg_text, reply_markup=markup, parse_mode="HTML")
            
            if action.previous_state_json.get("was_session_end"):
                await message.answer("🔄 Главное меню обновлено (сессия возвращена).", reply_markup=get_main_menu(bool(user.active_session_id)))
            
        except Exception as e:
            db.rollback()
            await message.answer(f"⚠️ Failed to undo: {e}")
            traceback.print_exc()
    if state: await state.clear()

@router.callback_query(F.data == "ui_undo_ok")
async def cq_undo_ok(callback_query: CallbackQuery):
    text = callback_query.message.html_text
    new_text = "✅ " + text
    await callback_query.message.edit_text(new_text, reply_markup=None, parse_mode="HTML")

@router.callback_query(F.data == "ui_undo_bad")
async def cq_undo_bad(callback_query: CallbackQuery):
    text = callback_query.message.html_text
    new_text = text + "\n\n<i>⚠️ Автоматический возврат (Redo) пока в разработке. Пожалуйста, повторите оригинальное действие вручную.</i>"
    await callback_query.message.edit_text(new_text, reply_markup=None, parse_mode="HTML")
