"""
The central NLP router that passes user messages to the Intent classifier to figure out which handler to invoke.

@Architecture-Map: [CORE-AI-ROUTER]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from typing import Optional, Tuple, Union
from src.ai.providers import GoogleProvider, LogWorkParams, AddInboxParams, SessionControlParams, ReportConfigParams, SystemConfigParams, CreateEntitiesParams, AddTasksParams, EditEntitiesParams
from src.core.constants import IntentType

def get_intent(user_text: str, provider_name: str, api_key: str) -> Tuple[IntentType, dict, Optional[str]]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            intent, tokens = provider.classify_intent(user_text)
            return intent, tokens, None
        except Exception as e:
            print(f'LLM Error: {e}')
            return IntentType.ERROR, {}, str(e)
    return IntentType.UNKNOWN_PROVIDER, {}, "Unknown provider"

def extract_log_work(user_text: str, provider_name: str, api_key: str, active_projects_text: str) -> Tuple[Optional[LogWorkParams], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_log_work_parameters(user_text, active_projects_text)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}

def extract_inbox(user_text: str, provider_name: str, api_key: str) -> Tuple[Optional[AddInboxParams], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_inbox_parameters(user_text)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}

def extract_session_control(user_text: str, provider_name: str, api_key: str, active_projects_text: str = "") -> Tuple[Optional[SessionControlParams], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_session_control(user_text, active_projects_text)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}

def extract_report_config(user_text: str, provider_name: str, api_key: str) -> Tuple[Optional[ReportConfigParams], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_report_config(user_text)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}

def extract_system_config(user_text: str, provider_name: str, api_key: str, registry_keys: list[str]) -> Tuple[Optional[SystemConfigParams], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_system_config(user_text, registry_keys)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}

def extract_entities(user_text: str, provider_name: str, api_key: str, active_projects_text: str = "") -> Tuple[Optional[Union[CreateEntitiesParams, AddTasksParams]], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_create_entities(user_text, active_projects_text)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}

def generate_chat(user_text: str, provider_name: str, api_key: str, persona_prompt: str) -> Tuple[Optional[str], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.generate_chat_response(user_text, persona_prompt)
        except Exception as e:
            print(f'LLM Chat Error: {e}')
            return None, {}
    return None, {}


def extract_add_tasks(user_text: str, provider_name: str, api_key: str, active_projects_text: str) -> Tuple[Optional[AddTasksParams], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_add_tasks_parameters(user_text, active_projects_text)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}

def extract_edit_entities(user_text: str, provider_name: str, api_key: str, entities_text: str):
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_edit_entities(user_text, entities_text)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}
