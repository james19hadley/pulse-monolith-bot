"""
Abstract Base Class for LLM Providers.
Forces concrete implementations (Google, OpenAI) to adhere to the same parsing interfaces.

@Architecture-Map: [CORE-AI-BASE-PROV]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any
from src.core.constants import IntentType
from src.ai.providers import (
    IntentResponse, LogWorkParams, AddInboxParams, SessionControlParams,
    SystemConfigParams, ReportConfigParams, CreateEntitiesParams, 
    EditEntitiesParams, AddTasksParams
)

class BaseLLMProvider(ABC):
    def __init__(self, api_key: str, model_id: str):
        self.api_key = api_key
        self.model_id = model_id

    @abstractmethod
    def classify_intent(self, text: str) -> Tuple[IntentType, dict]:
        pass

    @abstractmethod
    def extract_log_work_parameters(self, text: str, active_projects_text: str) -> Tuple[Optional[LogWorkParams], dict]:
        pass

    @abstractmethod
    def extract_inbox_parameters(self, text: str) -> Tuple[Optional[AddInboxParams], dict]:
        pass

    @abstractmethod
    def extract_session_control(self, text: str, active_projects_text: str = "") -> Tuple[Optional[SessionControlParams], dict]:
        pass

    @abstractmethod
    def extract_system_config(self, text: str, registry_keys: list[str]) -> Tuple[Optional[SystemConfigParams], dict]:
        pass

    @abstractmethod
    def extract_report_config(self, text: str) -> Tuple[Optional[ReportConfigParams], dict]:
        pass

    @abstractmethod
    def extract_create_entities(self, text: str, active_projects_text: str = "") -> Tuple[Optional[CreateEntitiesParams], dict]:
        pass

    @abstractmethod
    def extract_edit_entities(self, text: str, entities_text: str) -> Tuple[Optional[EditEntitiesParams], dict]:
        pass

    @abstractmethod
    def generate_chat_response(self, text: str, persona_prompt: str) -> Tuple[Optional[str], dict]:
        pass

    @abstractmethod
    def extract_add_tasks_parameters(self, text: str, active_projects_text: str) -> Tuple[Optional[AddTasksParams], dict]:
        pass
