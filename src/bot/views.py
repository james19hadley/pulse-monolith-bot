# Presentation Layer: Pulse Monolith Bot
# Strictly factual and objective responses.

def welcome_message(has_key: bool = False) -> str:
    msg = "👋 <b>Welcome to Pulse Monolith</b>\n"
    msg += "I am your personal AI accountability partner, designed to track time, build projects, and destroy procrastination.\n\n"
    
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
    return "\nSession initiated. Monitoring active."

def session_already_active_message() -> str:
    return "\nError: A session is already active. Close it before initiating a new one."

def no_active_session_message() -> str:
    return "\nError: No active session found to close."

def session_ended_message(total_minutes: int, focus_minutes: int) -> str:
    t_h, t_m = divmod(total_minutes, 60)
    f_h, f_m = divmod(focus_minutes, 60)
        
    msg = f"Session closed.\n\n"
    msg += f"<b>Total Time:</b> {t_h}h {t_m}m\n"
    msg += f"<b>Focused:</b> {f_h}h {f_m}m\n"
    return msg

def build_progress_bar(current: int, target: int, length: int = 10) -> str:
    if target <= 0:
        return "\n"
    ratio = min(max(current / target, 0.0), 1.0)
    filled = int(round(ratio * length))
    empty = length - filled
    return f"[{'█' * filled}{'░' * empty}] {int(ratio * 100)}%"

def project_created_message(project_id: int, title: str) -> str:
    return f"✅ Created project: <code>[{project_id}]</code> {title}"

def project_list_message(projects: list) -> str:
    if not projects:
        return "\nNo active projects found. Use <code>/new_project &lt;title&gt;</code> to create one."
    lines = ["📂 <b>Active Projects:</b>"]
    for p in projects:
        if getattr(p, "unit", None) and p.unit != "minutes":
            p_bar = build_progress_bar(p.current_value or 0, p.target_value or 0, length=8)
            val_str = f"{p.current_value or 0}/{p.target_value or 0} {p.unit} {p_bar}"
        else:
            cur_h = (p.current_value or 0) / 60
            if getattr(p, "target_value", 0):
                tgt_h = p.target_value / 60
                p_bar = build_progress_bar(p.current_value or 0, p.target_value or 0, length=8)
                val_str = f"{cur_h:g}/{tgt_h:g} hours {p_bar}"
            else:
                val_str = f"{cur_h:g} hours"
        lines.append(f"🔹 <b>{p.title}</b>: {val_str}")
    return "\n".join(lines)

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


# Inbox
def inbox_saved_message(content: str) -> str:
    return f"📥 Saved to Inbox: <i>{content}</i>"

# Action & Undo
def undo_success_message(target_type: str) -> str:
    return f"⏪ Undo successful: Removed/Reverted {target_type}."

def undo_fail_message() -> str:
    return "\n⚠️ Cannot undo that specific action type yet."

def nothing_to_undo_message() -> str:
    return "\n⚠️ Nothing to undo."

# Scheduler (Jobs)
def catalyst_ping_message(hours_idle: float) -> str:
    return f"No unassigned project. You have not logged focus for {hours_idle} hour(s)."

def stale_session_closed_message() -> str:
    return "\n🌙 Active session auto-closed retroactively to avoid tracking empty unassigned time."

# Accountability Reports (Lego Builder)
def build_daily_report(stats: dict, config: dict, ai_comment: str = None) -> str:
    style = config.get("style", "emoji")
    blocks = config.get("blocks", ["focus", "projects_daily", "inbox"])
    
    # Emojis dictionary
    e = {
        "focus": "⏱" if style != "strict" else "",
        "projects_daily": "📈" if style != "strict" else "",
        "inbox": "📥" if style != "strict" else "",
        "header": "📊" if style != "strict" else ""
    }
    
    date_str = stats.get('date', 'Today')
    parts = [f"<b>{e['header']} Daily Report: {date_str}</b>\n" if e['header'] else f"<b>Daily Report: {date_str}</b>\n"]
    
    for block in blocks:
        if block == "focus":
            f_h, f_m = divmod(stats.get('focus_minutes', 0), 60)
            parts.append(f"{e['focus']} <b>Focus:</b> {f_h}h {f_m}m")
            if stats.get('projects'):
                for p, data in stats['projects'].items():
                    # Handle both old format (int minutes) and new format (dict)
                    if isinstance(data, dict):
                        mins = data["minutes"]
                        prog = data["progress"]
                        unit = data["unit"]
                        
                        p_h, p_m = divmod(mins, 60)
                        import html
                        
                        msg = f"  └ <i>{html.escape(str(p))}</i>:"
                        if mins > 0:
                            msg += f" <b>{p_h}h {p_m}m</b>"
                        if unit and unit != "minutes":
                            target = data.get("target_value", 0)
                            current = data.get("current_value", 0)
                            p_bar = build_progress_bar(current, target, length=8)
                            msg += f" | {current}/{target} {unit} {p_bar}"
                            if prog > 0:
                                msg += f" (+{prog:g})"
                        else:
                            if prog > 0:
                                msg += f" (+{prog:g} items)"
                        parts.append(msg)
                    else:
                        mins = data
                        p_h, p_m = divmod(mins, 60)
                        import html
                        parts.append(f"  └ <i>{html.escape(str(p))}</i>: <b>{p_h}h {p_m}m</b>")
        
        elif block == "projects_daily":
            habits = stats.get('projects_daily', [])
            if habits:
                parts.append(f"\n{e['projects_daily']} <b>Daily Targets:</b>")
                for h in habits:
                    import html
                    done = "✅" if h['current'] >= h['target'] else "⏳"
                    parts.append(f"  └ {done} <i>{html.escape(str(h['title']))}</i>: <b>{h['current']}/{h['target']}</b> {h.get('unit', '')}".strip() )
                    
        elif block == "inbox":
            inbox = stats.get('inbox_count', 0)
            if inbox > 0:
                parts.append(f"\n{e['inbox']} <b>Inbox Captured:</b> {inbox} items")
                


    # Clean up empty lines and join
    report = "\n".join([p for p in parts if p]).strip()
    
    if ai_comment:
        report += f"\n\n<blockquote>💡 {str(ai_comment)}</blockquote>"
        
    return report


