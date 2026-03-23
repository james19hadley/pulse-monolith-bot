# Presentation Layer: Pulse Monolith Bot
# Strictly factual and objective responses.

def welcome_message(has_key: bool = False) -> str:
    msg = "Identity verified. I am the Pulse Monolith. Strict monitoring protocol activated.\n\n"
    if not has_key:
        msg += "⚠️ Warning: No AI provider key detected. Please set your API key using:\n`/set_key <provider> <your_api_key>`\n"
        msg += "*Available providers: `google`, `openai`, `anthropic`*\n"
        msg += "*Example:* `/set_key google AIzaSy...`\n\n"
    msg += "Use /start_session to begin a work block."
    return msg

def session_started_message() -> str:
    return "Session initiated. Monitoring active."

def session_already_active_message() -> str:
    return "Error: A session is already active. Close it before initiating a new one."

def no_active_session_message() -> str:
    return "Error: No active session found to close."

def session_ended_message(duration_minutes: int) -> str:
    hours = duration_minutes // 60
    minutes = duration_minutes % 60
    return f"Session closed. Total time recorded: {hours}h {minutes}m."
