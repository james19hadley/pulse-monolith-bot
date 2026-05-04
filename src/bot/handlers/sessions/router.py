"""
Telegram handlers for starting, pausing, and ending work sessions.
Refactored to delegate logic to sub-modules.

@Architecture-Map: [HND-SESSIONS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router
from .commands import router as commands_router
from .callbacks import router as callbacks_router

router = Router()
router.include_router(commands_router)
router.include_router(callbacks_router)
