from .handlers.core import router as core_router
from .handlers.sessions import router as sessions_router
from .handlers.projects_habits import router as projects_habits_router
from .handlers.projects_ui import router as projects_ui_router
from .handlers.settings_keys import router as settings_keys_router
from .handlers.ai_router import router as ai_router

routers = [
    core_router,
    sessions_router,
    projects_habits_router,
    projects_ui_router,
    settings_keys_router,
    ai_router
]
