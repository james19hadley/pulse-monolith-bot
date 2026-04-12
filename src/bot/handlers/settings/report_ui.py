"""
UI and Callbacks for customizing the formatting and content blocks of Daily Reports.

@Architecture-Map: [HND-SET-REPORTUI]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
import json

router = Router()

def get_report_menu(config: dict) -> InlineKeyboardMarkup:
    style = config.get("style", "emoji")
    blocks = config.get("blocks", ["focus", "projects_daily", "inbox"])
    
    style_text = "Style: Emoji 🚀" if style == "emoji" else "Style: Strict 📝"
    
    kb = [
        [InlineKeyboardButton(text=style_text, callback_data="repcfg_style")],
        [InlineKeyboardButton(text="Toggle [Focus] Block: " + ("✅" if "focus" in blocks else "❌"), callback_data="repcfg_toggle_focus")],
        [InlineKeyboardButton(text="Toggle [Daily Targets] Block: " + ("✅" if "projects_daily" in blocks else "❌"), callback_data="repcfg_toggle_projects_daily")],
        [InlineKeyboardButton(text="Toggle [Inbox] Block: " + ("✅" if "inbox" in blocks else "❌"), callback_data="repcfg_toggle_inbox")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@router.message(Command("report_config"))
async def cmd_report_config(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        config = user.report_config or {"blocks": ["focus", "projects_daily", "inbox"], "style": "emoji"}
        if isinstance(config, str):
            try: config = json.loads(config)
            except: config = {"blocks": ["focus", "projects_daily", "inbox"], "style": "emoji"}
            
        await message.answer("<b>Report Configuration</b>\nConfigure how your Daily Report looks:", parse_mode="HTML", reply_markup=get_report_menu(config))

@router.callback_query(F.data.startswith("repcfg_"))
async def cq_report_config(cq: CallbackQuery):
    action = cq.data.split("_", 1)[1]
    with SessionLocal() as db:
        user = get_or_create_user(db, cq.from_user.id)
        config = user.report_config or {"blocks": ["focus", "projects_daily", "inbox"], "style": "emoji"}
        if isinstance(config, str):
            try: config = json.loads(config)
            except: config = {"blocks": ["focus", "projects_daily", "inbox"], "style": "emoji"}
            
        if action == "style":
            config["style"] = "strict" if config.get("style", "emoji") == "emoji" else "emoji"
        elif action.startswith("toggle_"):
            block = action.split("_")[1]
            blocks = set(config.get("blocks", ["focus", "projects_daily", "inbox"]))
            if block in blocks:
                blocks.remove(block)
            else:
                blocks.add(block)
            # Maintain logical order
            ordered = []
            for b in ["focus", "projects_daily", "inbox"]:
                if b in blocks: ordered.append(b)
            config["blocks"] = ordered
            
        user.report_config = dict(config)
        db.commit()
        
        await cq.message.edit_reply_markup(reply_markup=get_report_menu(config))
        await cq.answer()
