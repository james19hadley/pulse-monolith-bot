"""
Core bot handlers like /start, /help, and global keyboard interactions.
Refactored to delegate logic to sub-modules.

@Architecture-Map: [HND-BOT-CORE]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router
from .core.basic import router as basic_router
from .core.ui import router as ui_router
from .core.undo import router as undo_router

router = Router()
router.include_router(basic_router)
router.include_router(ui_router)
router.include_router(undo_router)

