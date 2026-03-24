# Presentation Layer: Pulse Monolith Bot
# Strictly factual and objective responses.

def welcome_message(has_key: bool = False) -> str:
    msg = "👋 <b>Welcome to Pulse Monolith</b>\n"
    msg += "I am your personal AI accountability partner, designed to track time, build habits, and destroy procrastination.\n\n"
    
    msg += "🌍 <b>I speak all languages.</b>\n"
    msg += "<i>Feel free to message me in English, Russian, Spanish, or any other natural language. You don't need to memorize strict commands!</i>\n\n"
    
    msg += "<b>Examples of what you can say:</b>\n"
    msg += "• <i>\"Расскажи о том что ты умеешь\"</i>\n"
    msg += "• <i>\"Create a new project for learning Python\"</i>\n"
    msg += "• <i>\"I just worked out for 45 minutes\"</i>\n"
    msg += "• <i>\"Set my timezone like in Houston and post my daily report exactly at midnight\"</i>\n\n"

    msg += "<b>⚙️ Customize My Personality:</b>\n"
    msg += "You can change how I talk to you in the settings.\n"
    msg += "<i>Available: <code>monolith</code> (strict), <code>coach</code> (aggressive), <code>butler</code> (polite), <code>sarcastic</code>, <code>tars</code>, <code>friday</code></i>\n\n"
    
    if not has_key:
        msg += "⚠️ <b>Action Required:</b>\n"
        msg += "To start understanding your messages, I need a brain. Please click the <b>⚙️ Settings</b> button below and add your AI Provider key.\n"
    else:
        msg += "✅ <i>AI Engine Connected. Start typing to begin!</i>\n\n📖 <b>Tip:</b> You can read the guide by clicking the <b>❓ Help</b> button below or using the /help command."


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
    msg += f"<b>Total Time:</b> {t_h}h {t_m}m\n"
    msg += f"<b>Focused:</b> {f_h}h {f_m}m\n"
    msg += f"<b>The Void (Lost):</b> {v_h}h {v_m}m\n"
    return msg

def project_created_message(project_id: int, title: str) -> str:
    return f"✅ Created project: <code>[{project_id}]</code> {title}"

def project_list_message(projects: list) -> str:
    if not projects:
        return "No active projects found. Use <code>/new_project &lt;title&gt;</code> to create one."
    
    lines = ["📂 <b>Active Projects:</b>"]
    for p in projects:
        lines.append(f"<code>[{p.id}]</code> {p.title} - {p.total_minutes_spent}m spent")
    return "\n".join(lines)

# FinOps & Stats
def stats_message(prompt_total: int, comp_total: int, cost: float) -> str:
    return (
        f"📊 <b>FinOps / Token Usage</b>\n"
        f"Input Tokens: <code>{prompt_total}</code>\n"
        f"Output Tokens: <code>{comp_total}</code>\n"
        f"Estimated Cost: <code>${cost:.5f}</code>\n"
    )

# Settings
def settings_list_message(settings_list: list) -> str:
    msg = "⚙️ <b>Current Settings</b>\n\n"
    for s in settings_list:
        msg += f"<b>{s['name']}</b>:\n<code>{s['val']}</code> {s['desc']}\nChange: <code>/settings {s['key']} &lt;value&gt;</code>\n\n"
    return msg

# Habit
def habit_created_message(h_id: int, title: str, target: int) -> str:
    return f"✅ Created Habit: <code>[{h_id}]</code> {title} (Target: {target})"

def habit_updated_message(title: str, current: int, target: int) -> str:
    return f"📈 Habit <code>{title}</code> updated: {current}/{target}"

# Inbox
def inbox_saved_message(content: str) -> str:
    return f"📥 Saved to Inbox: <i>{content}</i>"

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

# Accountability Reports (Lego Builder)
def build_daily_report(stats: dict, config: dict, ai_comment: str = None) -> str:
    style = config.get("style", "emoji")
    blocks = config.get("blocks", ["focus", "habits", "inbox", "void"])
    
    # Emojis dictionary
    e = {
        "focus": "⏱" if style != "strict" else "",
        "habits": "📈" if style != "strict" else "",
        "inbox": "📥" if style != "strict" else "",
        "void": "🕳" if style != "strict" else "",
        "header": "📊" if style != "strict" else ""
    }
    
    date_str = stats.get('date', 'Today')
    parts = [f"<b>{e['header']} Daily Accountability Report: {date_str}</b>\n" if e['header'] else f"<b>Daily Accountability Report: {date_str}</b>\n"]
    
    for block in blocks:
        if block == "focus":
            f_h, f_m = divmod(stats.get('focus_minutes', 0), 60)
            parts.append(f"{e['focus']} <b>Deep Work:</b> {f_h}h {f_m}m")
            if stats.get('projects'):
                for p, mins in stats['projects'].items():
                    p_h, p_m = divmod(mins, 60)
                    import html
                    parts.append(f"  - {html.escape(str(p))}: {p_h}h {p_m}m")
        
        elif block == "habits":
            habits = stats.get('habits', [])
            if habits:
                parts.append(f"\n{e['habits']} <b>Habit Execution:</b>")
                for h in habits:
                    import html
                    parts.append(f"  - {html.escape(str(h['title']))}: {h['current']}/{h['target']}")
                    
        elif block == "inbox":
            inbox = stats.get('inbox_count', 0)
            if inbox > 0:
                parts.append(f"\n{e['inbox']} <b>Inbox Captured:</b> {inbox} items")
                
        elif block == "void":
            v_h, v_m = divmod(stats.get('void_minutes', 0), 60)
            parts.append(f"\n{e['void']} <b>The Void (Lost Time):</b> {v_h}h {v_m}m")

    # Clean up empty lines and join
    report = "\n".join([p for p in parts if p]).strip()
    
    if ai_comment:
        import html
        report += f"\n\n<i>{html.escape(str(ai_comment))}</i>"
        
    return report


