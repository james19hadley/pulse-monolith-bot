"""
Centralized hub for all static non-AI bot copy (messages) for localization / quick edits.

@Architecture-Map: [UI-TEXTS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
# Global Text and Button Registry
# This file serves as the Single Source of Truth (SSOT) for all strings and button labels.

class Buttons:
    NUDGE_WORKING = "Я работаю 🧘‍♂️"
    NUDGE_FINISH = "Завершить 🛑"
    START_SESSION = "🟢 Start Session"
    END_SESSION = "🛑 End Session"
    END_DAY = "🌙 End Day"
    INBOX = "📥 Inbox"
    SETTINGS = "⚙️ Settings"
    PROJECTS = "🗂 Projects"
    HABITS = "🎯 Habits"
    HELP = "❓ Help"
    UNDO = "↩️ Undo"

class Prompts:
    NUDGE_ACTIVE_SESSION = "⏳ Слышишь, ты уже в контексте сессии {hours_idle} часа(ов) без логов. Всё еще в потоке, или пора завершить сессию?"
    NUDGE_REST_SESSION = "⏸️ Перерыв затянулся: меня не было {mins_rested} минут.{ctx_text} Возвращаемся или заканчиваем на сегодня?"
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

PROJECT_EMOJIS = [
    "🚀", "⚡", "💡", "🧠", "🔥", "✨", "🌟", "🎯", "🏆", "💎", 
    "🎮", "🕹️", "🧩", "🎨", "🎭", "🎬", "🎸", "🎧", "📚", "📖", 
    "🔬", "🔭", "📡", "🧭", "🛠️", "⚙️", "📈", "📉", "📊", "📌", 
    "🖊️", "🪴", "🌿", "🍀", "🍎", "🍏", "🍕", "🍔", "☕", "🍵", 
    "🚗", "⛵", "🚁", "🛸"
]
