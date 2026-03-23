import os
from dotenv import load_dotenv

load_dotenv()

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
        "description": "Minutes before the first ping",
        "default": 60
    },
    "interval": {
        "db_column": "catalyst_interval_minutes",
        "type": int,
        "name": "Catalyst Repeat Interval",
        "description": "Minutes between recurring pings (0 to disable)",
        "default": 20
    }
}
