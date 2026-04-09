"""
Router registry that aggregates all entity-related handlers (projects, menus).

@Architecture-Map: [HND-ENT-ROUTER]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router
from .menu import router as menu_router
from .projects import router as projects_router

router = Router()

router.include_router(menu_router)
router.include_router(projects_router)
from .commands import router as commands_router
router.include_router(commands_router)
