# Global Text and Button Registry
# This file serves as the Single Source of Truth (SSOT) for all strings and button labels.

class Buttons:
    START_SESSION = "🟢 Start Session"
    END_SESSION = "🛑 End Session"
    END_DAY = "🌙 End Day"
    INBOX = "📥 Inbox"
    SETTINGS = "⚙️ Settings"
    PROJECTS = "🗂 Projects"
    HELP = "❓ Help"
    UNDO = "↩️ Undo"

class Prompts:
    UNKNOWN_COMMAND = "Unknown command: <code>{text}</code>\\n\\nUse /help to see available commands."
    ERROR_GLOBAL = "⚠️ Простите, на сервере произошла ошибка. Пожалуйста, обратитесь позднее."
    INBOX_EMPTY = "Your inbox is empty. To add a thought, use <code>/inbox &lt;text&gt;</code>"
    INBOX_CLEARED = "🧹 Inbox cleared."

class Commands:
    START_SESSION = "start_session"
    END_SESSION = "end_session"
    END_DAY = "end_day"
    INBOX = "inbox"
    SETTINGS = "settings"
    PROJECTS = "projects"
    HELP = "help"
    UNDO = "undo"
    CLEAR_INBOX = "clear_inbox"
