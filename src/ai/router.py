from typing import Optional
from src.ai.providers import GoogleProvider, LogWorkParams, LogHabitParams, AddInboxParams, SessionControlParams
from src.core.constants import IntentType

def get_intent(user_text: str, provider_name: str, api_key: str) -> IntentType:
    """
    Factory function that routes the request to the correct provider.
    Currently only supports Google.
    """
    if provider_name == "google":
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.classify_intent(user_text)
        except Exception as e:
            print(f"LLM Error: {e}")
            return IntentType.ERROR
    else:
        return IntentType.UNKNOWN_PROVIDER

def extract_log_work(user_text: str, provider_name: str, api_key: str, active_projects_text: str) -> Optional[LogWorkParams]:
    """
    Routes the parameter extraction request.
    """
    if provider_name == "google":
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_log_work_parameters(user_text, active_projects_text)
        except Exception as e:
            print(f"LLM Extraction Error: {e}")
            return None
    return None

def extract_log_habit(user_text: str, provider_name: str, api_key: str, active_habits_text: str) -> Optional[LogHabitParams]:
    if provider_name == "google":
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_habit_parameters(user_text, active_habits_text)
        except Exception as e:
            print(f"LLM Extraction Error: {e}")
            return None
    return None

def extract_inbox(user_text: str, provider_name: str, api_key: str) -> Optional[AddInboxParams]:
    if provider_name == "google":
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_inbox_parameters(user_text)
        except Exception as e:
            print(f"LLM Extraction Error: {e}")
            return None
    return None

def extract_session_control(user_text: str, provider_name: str, api_key: str) -> Optional[SessionControlParams]:
    if provider_name == "google":
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_session_control(user_text)
        except Exception as e:
            print(f"LLM Extraction Error: {e}")
            return None
    return None
