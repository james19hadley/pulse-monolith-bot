"""
Contains all environment variables and the central USER_SETTINGS_REGISTRY.

@Architecture-Map: [CORE-SYS-CONFIG]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
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

WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8080"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

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

ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if not ADMIN_PASSWORD or ADMIN_PASSWORD == "changeme":
    raise ValueError("ADMIN_PASSWORD must be configured in .env and cannot be \"changeme\".")
