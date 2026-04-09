"""
Registry of supported LLM providers and their specific models.
Used to decouple the bot from a single hardcoded LLM string (e.g. "gemini-3-flash-preview").

@Architecture-Map: [CORE-AI-MODELS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""

class ProviderType:
    GOOGLE = "google"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"

LLM_MODELS = {
    ProviderType.GOOGLE: {
        "default": "gemini-3-flash-preview",
        "options": [
            "gemini-3-flash-preview",   # Fast, extremely cheap, excellent with structured JSON
            "gemini-2.5-flash",         # Stable fallback
            "gemini-2.5-pro"            # Smarter but slower
        ]
    },
    ProviderType.OPENAI: {
        "default": "gpt-4o-mini",
        "options": [
            "gpt-4o-mini",              # Cheapest OpenAI model, great for JSON extraction
            "gpt-4o"                    # Flagship model
        ]
    },
    ProviderType.ANTHROPIC: {
        "default": "claude-3-5-haiku-latest",
        "options": [
            "claude-3-5-haiku-latest",  # Fast, cheap
            "claude-3-5-sonnet-latest"  # Best for coding and complex logic
        ]
    },
    ProviderType.OPENROUTER: {
        "default": "meta-llama/llama-3.3-70b-instruct",
        "options": [
            "meta-llama/llama-3.3-70b-instruct",
            "google/gemini-2.5-flash",
            "openai/gpt-4o-mini"
        ]
    }
}

def get_default_model(provider: str) -> str:
    """Returns the default fast/cheap model for a given provider."""
    return LLM_MODELS.get(provider, LLM_MODELS[ProviderType.GOOGLE])["default"]
