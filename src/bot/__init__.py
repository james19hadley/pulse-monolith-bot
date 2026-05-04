from .handlers.core.router import router as core_router
from .handlers.sessions.router import router as sessions_router
from .handlers.entities.router import router as entities_router
from .handlers.settings.router import router as settings_router
from .handlers.ai_router import router as ai_router

routers = [
    core_router,
    sessions_router,
    entities_router,
    settings_router,
    ai_router
]
