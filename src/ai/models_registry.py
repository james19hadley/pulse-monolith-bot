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
        "default": "gemini-3-flash", # Убрано -preview для использования стабильной ветки
        "options":[
            "gemini-3-flash",           # Fast, extremely cheap, excellent with structured JSON
            "gemini-3.1-flash-lite-preview", # Опционально: новая сверхдешевая модель 2026 года
            "gemini-2.5-flash",         # Stable fallback
            "gemini-2.5-pro"            # Smarter but slower
        ]
    },
    ProviderType.OPENAI: {
        "default": "gpt-4o-mini",
        "options":[
            "gpt-4o-mini",              # Cheapest OpenAI model, great for JSON extraction
            "gpt-4o"                    # Flagship model
        ]
    },
    ProviderType.ANTHROPIC: {
        "default": "claude-3-5-haiku-20241022", # ИСПРАВЛЕНО: -latest выдает 404!
        "options":[
            "claude-3-5-haiku-20241022", # Быстро и дешево (фиксированная дата)
            "claude-3-7-sonnet-latest"   # ИСПРАВЛЕНО: Актуальный лидер для кода на 2026 год
        ]
    },
    ProviderType.OPENROUTER: {
        "default": "meta-llama/llama-3.3-70b-instruct",
        "options":[
            "meta-llama/llama-3.3-70b-instruct",
            "google/gemini-2.5-flash",
            "openai/gpt-4o-mini"
        ]
    }
}

def get_default_model(provider: str) -> str:
    """Returns the default fast/cheap model for a given provider."""
    return LLM_MODELS.get(provider, LLM_MODELS[ProviderType.GOOGLE])["default"]
