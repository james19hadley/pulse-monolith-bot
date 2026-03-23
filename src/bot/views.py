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

def session_ended_message(total_minutes: int, focus_minutes: int, void_minutes: int) -> str:
    t_h, t_m = divmod(total_minutes, 60)
    f_h, f_m = divmod(focus_minutes, 60)
    v_h, v_m = divmod(void_minutes, 60)
    
    msg = f"Session closed.\n\n"
    msg += f"**Total Time:** {t_h}h {t_m}m\n"
    msg += f"**Focused:** {f_h}h {f_m}m\n"
    msg += f"**The Void (Lost):** {v_h}h {v_m}m\n"
    return msg

def project_created_message(project_id: int, title: str) -> str:
    return f"✅ Created project: `[{project_id}]` {title}"

def project_list_message(projects: list) -> str:
    if not projects:
        return "No active projects found. Use `/new_project <title>` to create one."
    
    lines = ["📂 **Active Projects:**"]
    for p in projects:
        lines.append(f"`[{p.id}]` {p.title} - {p.total_minutes_spent}m spent")
    return "\n".join(lines)

# FinOps & Stats
def stats_message(prompt_total: int, comp_total: int, cost: float) -> str:
    return (
        f"📊 *FinOps / Token Usage*\n"
        f"Input Tokens: `{prompt_total}`\n"
        f"Output Tokens: `{comp_total}`\n"
        f"Estimated Cost: `${cost:.5f}`\n"
    )

# Settings
def settings_list_message(settings_list: list) -> str:
    msg = "⚙️ **Current Settings**\n\n"
    for s in settings_list:
        msg += f"*{s['name']}*:\n`{s['val']}` ({s['desc']})\nChange: `/settings {s['key']} <value>`\n\n"
    return msg

# Habit
def habit_created_message(h_id: int, title: str, target: int) -> str:
    return f"✅ Created Habit: `[{h_id}]` {title} (Target: {target})"

def habit_updated_message(title: str, current: int, target: int) -> str:
    return f"📈 Habit `{title}` updated: {current}/{target}"

# Inbox
def inbox_saved_message(content: str) -> str:
    return f"📥 Saved to Inbox: _{content}_"

# Action & Undo
def undo_success_message(target_type: str) -> str:
    return f"⏪ Undo successful: Removed/Reverted {target_type}."

def undo_fail_message() -> str:
    return "⚠️ Cannot undo that specific action type yet."

def nothing_to_undo_message() -> str:
    return "⚠️ Nothing to undo."

# Scheduler (Jobs)
def catalyst_ping_message(hours_idle: float) -> str:
    return f"The Void expands. You have not logged focus for {hours_idle} hour(s)."

def stale_session_closed_message() -> str:
    return "🌙 Active session auto-closed retroactively to avoid tracking empty void."

