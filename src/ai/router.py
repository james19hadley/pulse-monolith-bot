from typing import Optional, Tuple
from src.ai.providers import GoogleProvider, LogWorkParams, LogHabitParams, AddInboxParams, SessionControlParams, ReportConfigParams, SystemConfigParams
from src.core.constants import IntentType

def get_intent(user_text: str, provider_name: str, api_key: str) -> Tuple[IntentType, dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.classify_intent(user_text)
        except Exception as e:
            print(f'LLM Error: {e}')
            return IntentType.ERROR, {}
    return IntentType.UNKNOWN_PROVIDER, {}

def extract_log_work(user_text: str, provider_name: str, api_key: str, active_projects_text: str) -> Tuple[Optional[LogWorkParams], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_log_work_parameters(user_text, active_projects_text)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}

def extract_log_habit(user_text: str, provider_name: str, api_key: str, active_habits_text: str) -> Tuple[Optional[LogHabitParams], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_habit_parameters(user_text, active_habits_text)
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

def extract_session_control(user_text: str, provider_name: str, api_key: str) -> Tuple[Optional[SessionControlParams], dict]:
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_session_control(user_text)
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
