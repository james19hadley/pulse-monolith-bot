import os
import datetime
from dotenv import load_dotenv

load_dotenv()

def parse_time(val_str: str) -> datetime.time:
    try:
        h, m = map(int, val_str.split(':'))
        return datetime.time(h, m)
    except Exception:
        raise ValueError("Time must be in HH:MM format")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the .env file. Please configure it.")

if not ENCRYPTION_KEY or ENCRYPTION_KEY == "generate_with_fernet":
    raise ValueError("ENCRYPTION_KEY is not set. Generate one using cryptography.fernet.Fernet.")

USER_SETTINGS_REGISTRY = {
    "catalyst": {
        "db_column": "catalyst_threshold_minutes",
        "type": int,
        "name": "Catalyst Ping Threshold",
        "description": "Minutes before the first ping (0 to disable)",
        "default": 60
    },
    "interval": {
        "db_column": "catalyst_interval_minutes",
        "type": int,
        "name": "Catalyst Repeat Interval",
        "description": "Minutes between recurring pings (0 to disable)",
        "default": 20
    },
    "channel": {
        "db_column": "target_channel_id",
        "type": int,
        "name": "Target Channel ID",
        "description": "The numeric ID of the channel to post accountability reports to.",
        "default": None
    },
    "report": {
        "db_column": "report_config",
        "type": str,
        "name": "Report Context Layout",
        "description": "JSON representation of the daily report",
        "default": None
    },
    "cutoff": {
        "db_column": "day_cutoff_time",
        "type": parse_time,
        "name": "Day Cutoff Time",
        "description": "When does your day end? (Format HH:MM, e.g. 23:00)",
        "default": "23:00"
    },
    "timezone": {
        "db_column": "timezone",
        "type": str,
        "name": "Timezone",
        "description": "Your local timezone (e.g. Europe/Moscow)",
        "default": "UTC"
    },
    "persona": {
        "db_column": "persona_type",
        "type": str,
        "name": "Bot Persona",
        "description": "Bot attitude (e.g. monolith)",
        "default": "monolith"
    },
    "provider": {
        "db_column": "llm_provider",
        "type": str,
        "name": "Active LLM Provider",
        "description": "Which API to use (google, openai, anthropic)",
        "default": "google"
    }
}
