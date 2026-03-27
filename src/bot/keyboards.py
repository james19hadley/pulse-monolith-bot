from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.bot.texts import Buttons

def get_main_menu() -> ReplyKeyboardMarkup:
    # Uses true persistent text matching properly routed via decorators
    kb = [
        [
            KeyboardButton(text=Buttons.START_SESSION),
            KeyboardButton(text=Buttons.END_SESSION),
            KeyboardButton(text=Buttons.END_DAY)
        ],
        [
            KeyboardButton(text=Buttons.INBOX),
            KeyboardButton(text=Buttons.PROJECTS),
            KeyboardButton(text=Buttons.HABITS),
            KeyboardButton(text=Buttons.SETTINGS)
        ],
        [
            KeyboardButton(text=Buttons.HELP),
            KeyboardButton(text=Buttons.UNDO)
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)

def get_providers_keyboard() -> InlineKeyboardMarkup:
    """Returns an inline keyboard with AI providers for the Add Key flow."""
    kb = [
        [
            InlineKeyboardButton(text="Google (Gemini)", callback_data="provider_google"),
            InlineKeyboardButton(text="OpenAI", callback_data="provider_openai"),
            InlineKeyboardButton(text="Anthropic", callback_data="provider_anthropic")
        ],
        [
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_fsm")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Returns the main settings menu inline keyboard."""
    kb = [
        [
            InlineKeyboardButton(text="🔑 API Keys", callback_data="settings_keys"),
            InlineKeyboardButton(text="🎭 Persona", callback_data="settings_persona")
        ],
        [
            InlineKeyboardButton(text="🌍 Timezone", callback_data="settings_timezone"),
            InlineKeyboardButton(text="⏰ Report Time", callback_data="settings_cutoff")
        ],
        [
            InlineKeyboardButton(text="📊 Report", callback_data="settings_reports"),
            InlineKeyboardButton(text="📢 Target Channel", callback_data="settings_channel")
        ],
        [
            InlineKeyboardButton(text="💓 Pulse Intervals", callback_data="settings_pulse")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_pulse_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏱️ Catalyst Limit", callback_data="settings_catalyst")
    builder.button(text="🔁 Ping Interval", callback_data="settings_interval")
    builder.button(text="🔙 Back", callback_data="settings_main")
    builder.adjust(1, 1, 1)
    return builder.as_markup()

def get_cutoff_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="21:00", callback_data="set_cutoff_21:00")
    builder.button(text="22:00", callback_data="set_cutoff_22:00")
    builder.button(text="23:00", callback_data="set_cutoff_23:00")
    builder.button(text="00:00", callback_data="set_cutoff_00:00")
    builder.button(text="Custom Time", callback_data="set_cutoff_custom")
    builder.button(text="🔙 Back", callback_data="settings_main")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()

def get_back_settings_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to return to the main settings control panel."""
    kb = [[InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_persona_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to pick a bot persona."""
    kb = [
        [
            InlineKeyboardButton(text="⬛ Monolith", callback_data="set_persona_monolith"),
            InlineKeyboardButton(text="🤖 TARS", callback_data="set_persona_tars")
        ],
        [
            InlineKeyboardButton(text="👩‍💻 Friday", callback_data="set_persona_friday"),
            InlineKeyboardButton(text="🤵‍♂️ Alfred", callback_data="set_persona_alfred")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_timezone_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to pick a common timezone."""
    kb = [
        [
            InlineKeyboardButton(text="UTC-5 (EST)", callback_data="set_tz_UTC-5"),
            InlineKeyboardButton(text="UTC+0 (GMT)", callback_data="set_tz_UTC")
        ],
        [
            InlineKeyboardButton(text="UTC+1 (CET)", callback_data="set_tz_UTC+1"),
            InlineKeyboardButton(text="UTC+3 (MSK)", callback_data="set_tz_UTC+3")
        ],
        [
            InlineKeyboardButton(text="UTC+8 (CST)", callback_data="set_tz_UTC+8"),
            InlineKeyboardButton(text="UTC+9 (JST)", callback_data="set_tz_UTC+9")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_reports_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to select report destination and format."""
    kb = [
        [
            InlineKeyboardButton(text="📩 Send to DM", callback_data="set_report_dm"),
            InlineKeyboardButton(text="📢 Send to Channel", callback_data="set_report_channel")
        ],
        [
            InlineKeyboardButton(text="❌ Disable Reports", callback_data="set_report_none"),
            InlineKeyboardButton(text="🧪 Test Report", callback_data="settings_test_report")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_back_settings_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to return to the main settings control panel."""
    kb = [[InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_persona_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to pick a bot persona."""
    kb = [
        [
            InlineKeyboardButton(text="⬛ Monolith", callback_data="set_persona_monolith"),
            InlineKeyboardButton(text="🤖 TARS", callback_data="set_persona_tars")
        ],
        [
            InlineKeyboardButton(text="👩‍💻 Friday", callback_data="set_persona_friday"),
            InlineKeyboardButton(text="🤵‍♂️ Alfred", callback_data="set_persona_alfred")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_timezone_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to pick a common timezone."""
    kb = [
        [
            InlineKeyboardButton(text="UTC-5 (EST)", callback_data="set_tz_UTC-5"),
            InlineKeyboardButton(text="UTC+0 (GMT)", callback_data="set_tz_UTC")
        ],
        [
            InlineKeyboardButton(text="UTC+1 (CET)", callback_data="set_tz_UTC+1"),
            InlineKeyboardButton(text="UTC+3 (MSK)", callback_data="set_tz_UTC+3")
        ],
        [
            InlineKeyboardButton(text="UTC+8 (CST)", callback_data="set_tz_UTC+8"),
            InlineKeyboardButton(text="UTC+9 (JST)", callback_data="set_tz_UTC+9")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_reports_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to select report destination and format."""
    kb = [
        [
            InlineKeyboardButton(text="📩 Send to DM", callback_data="set_report_dm"),
            InlineKeyboardButton(text="📢 Send to Channel", callback_data="set_report_channel")
        ],
        [
            InlineKeyboardButton(text="❌ Disable Reports", callback_data="set_report_none"),
            InlineKeyboardButton(text="🧪 Test Report", callback_data="settings_test_report")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_api_keys_manage_keyboard(keys: dict = None, active_key: str = None) -> InlineKeyboardMarkup:
    """Manage API Keys Main Menu, allowing switching active keys."""
    kb = []
    
    if keys:
        for k in keys.keys():
            if k == active_key:
                text = f"✅ {k} (Active)"
                cb_data = "ignore_active"
            else:
                text = f"🔄 Switch to {k}"
                cb_data = f"switch_key_{k}"
            kb.append([InlineKeyboardButton(text=text, callback_data=cb_data)])
            
    kb.append([InlineKeyboardButton(text="➕ Add New Key", callback_data="settings_add_key")])
    kb.append([InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_api_keys_manage_keyboard(keys: dict = None, active_key: str = None) -> InlineKeyboardMarkup:
    """Manage API Keys Main Menu, allowing switching active keys."""
    kb = []
    
    if keys:
        for k in keys.keys():
            if k == active_key:
                text = f"✅ {k} (Active)"
                cb_data = "ignore_active"
            else:
                text = f"🔄 Switch to {k}"
                cb_data = f"switch_key_{k}"
            kb.append([InlineKeyboardButton(text=text, callback_data=cb_data)])
            
    kb.append([InlineKeyboardButton(text="➕ Add New Key", callback_data="settings_add_key")])
    kb.append([InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_catalyst_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="15 Min", callback_data="set_catalyst_15")
    builder.button(text="30 Min", callback_data="set_catalyst_30")
    builder.button(text="60 Min", callback_data="set_catalyst_60")
    builder.button(text="120 Min", callback_data="set_catalyst_120")
    builder.button(text="Custom", callback_data="set_catalyst_custom")
    builder.button(text="🔙 Back", callback_data="settings_pulse")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()

def get_interval_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="15 Min", callback_data="set_interval_15")
    builder.button(text="30 Min", callback_data="set_interval_30")
    builder.button(text="60 Min", callback_data="set_interval_60")
    builder.button(text="Custom", callback_data="set_interval_custom")
    builder.button(text="🔙 Back", callback_data="settings_pulse")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def get_channel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Untie Channel", callback_data="set_channel_clear")
    builder.button(text="Custom", callback_data="set_channel_custom")
    builder.button(text="🔙 Back", callback_data="settings_main")
    builder.adjust(1, 1, 1)
    return builder.as_markup()

def get_entities_main_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="📁 Manage Projects", callback_data="ui_projects_list")
        ],
        [
            InlineKeyboardButton(text="🎯 Manage Habits", callback_data="ui_habits_list")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_projects_list_keyboard(projects) -> InlineKeyboardMarkup:
    kb = []
    for p in projects:
        kb.append([InlineKeyboardButton(text=f"📁 {p.title}", callback_data=f"ui_proj_{p.id}")])
    kb.append([InlineKeyboardButton(text="➕ New Project", callback_data="ui_proj_new")])
    kb.append([InlineKeyboardButton(text="🔙 Back", callback_data="ui_entities_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_habits_list_keyboard(habits) -> InlineKeyboardMarkup:
    kb = []
    for h in habits:
        kb.append([InlineKeyboardButton(text=f"🎯 {h.title}", callback_data=f"ui_hab_{h.id}")])
    kb.append([InlineKeyboardButton(text="➕ New Habit", callback_data="ui_hab_new")])
    kb.append([InlineKeyboardButton(text="🔙 Back", callback_data="ui_entities_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_project_view_keyboard(proj_id) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="📋 Manage Tasks", callback_data=f"ui_proj_tasks_{proj_id}")
        ],
        [
            InlineKeyboardButton(text="✏️ Edit Target", callback_data=f"ui_proj_edit_{proj_id}"),
            InlineKeyboardButton(text="⏱ Add Time", callback_data=f"ui_proj_add_{proj_id}")
        ],
        [
            InlineKeyboardButton(text="📦 Archive", callback_data=f"ui_proj_arch_{proj_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="ui_projects_list")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_habit_view_keyboard(hab_id) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="✏️ Edit Target", callback_data=f"ui_hab_edit_{hab_id}"),
            InlineKeyboardButton(text="➕ Add Progress", callback_data=f"ui_hab_add_{hab_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Delete/Archive", callback_data=f"ui_hab_arch_{hab_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="ui_habits_list")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
