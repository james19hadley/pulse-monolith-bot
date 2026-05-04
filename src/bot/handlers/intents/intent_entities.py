"""
Processing AI-parsed entity creation intents (Project, Quest, Habit).
Refactored to delegate logic to sub-modules.

@Architecture-Map: [HND-INTENT-ENT]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram.types import Message
from .handlers.projects import handle_create_entities as _handle_create_entities
from .handlers.inbox import handle_add_inbox as _handle_add_inbox
from .handlers.tasks import handle_add_tasks as _handle_add_tasks
from .handlers.edit import handle_edit_entities as _handle_edit_entities
