
from aiogram import Router
from .list import router as list_router
from .actions import router as actions_router
from .create import router as create_router

router = Router()
router.include_router(list_router)
router.include_router(actions_router)
router.include_router(create_router)
