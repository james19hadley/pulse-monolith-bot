import re

with open("src/bot/handlers/intents/intent_entities.py", "r") as f:
    text = f.read()

# Fix the broken extract_inbox line
text = text.replace(
    'extraction, tokens = extract_inbox, extract_add_tasks(message.text, provider_name, api_key)',
    'extraction, tokens = extract_inbox(message.text, provider_name, api_key)'
)

# Insert the missing _handle_add_tasks and rename the current broken one back to _handle_edit_entities
MISSING_ADD_TASKS = """async def _handle_add_tasks(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project, Task
    from src.ai.router import extract_add_tasks
    import html
    from src.bot.handlers.utils import log_tokens
    
    # 1. Fetch active projects formatting for AI prompt
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    projects_text = "Active Projects:\\n" + "\\n".join([f"- {p.title} (ID: {p.id})" for p in projects]) if projects else "No active projects."
    
    # Extract tasks
    extraction, tokens = extract_add_tasks(message.text, provider_name, api_key, projects_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or not extraction.tasks:
        await message.answer("I couldn't identify any tasks to add.")
        return
        
    responses = []
    msg_lines = []
    count = 0
    from src.db.models import ActionLog
    
    for t in extraction.tasks:
        # Create Task
        new_task = Task(
            user_id=user.id,
            title=t.title,
            project_id=t.project_id if t.project_id else None,
            status='pending'
        )
        db.add(new_task)
        count += 1
        
        proj_name = "Inbox"
        if t.project_id:
            db_proj = db.query(Project).filter(Project.id == t.project_id).first()
            if db_proj:
                proj_name = db_proj.title
            
        msg_lines.append(f"• {t.title} 📂 <i>{html.escape(proj_name)}</i>")
        
    db.commit()
    
    nl = '\\n'
    await message.answer(f"✅ <b>Added {count} task(s):</b>\\n{nl.join(msg_lines)}", parse_mode="HTML")

async def _handle_edit_entities(message: Message, db, user, provider_name, api_key):
"""

text = text.replace('async def _handle_add_tasks(message: Message, db, user, provider_name, api_key):', MISSING_ADD_TASKS)

with open("src/bot/handlers/intents/intent_entities.py", "w") as f:
    f.write(text)

