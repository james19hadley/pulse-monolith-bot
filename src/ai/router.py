from typing import Optional
from src.ai.providers import GoogleProvider
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
