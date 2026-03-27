from aiogram import Router
from .general import router as general_router
from .api_keys import router as api_keys_router
from .persona_tz import router as persona_tz_router
from .system_configs import router as system_configs_router
from .reports import router as reports_router

router = Router()

router.include_router(general_router)
router.include_router(api_keys_router)
router.include_router(persona_tz_router)
router.include_router(system_configs_router)
router.include_router(reports_router)
