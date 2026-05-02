"""
Global registry of AI prompts used for routing and NLP intent classification.

@Architecture-Map: [CORE-AI-PROMPTS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
import json

INTENT_DESCRIPTIONS = {
    "LOG_WORK": 'The user is reporting time spent working or progressing on a project/quest, completing a daily habit or routine, or assigning a split part of time, or transferring time between projects. (e.g. "I coded for 40 mins", "Did 2 hours of writing", "habit done", "typing done", "subtract 10 from A and add 10 to B", "all to project 1", "half to admin").',
    "ADD_TASKS": 'The user is adding actionable to-do items, steps, or tasks to a plan/project (e.g. "Add tasks: buy milk, call Bob", "For Frontend project I need to design UI and fix bugs").',
    "ADD_INBOX": "The user is dumping a random raw idea, thought, or note to save for later (e.g. \"Idea: add stripe later\", \"Don't forget to buy milk\").",
    "CREATE_ENTITIES": 'The user wants to create a new project (possibly with a target number of hours/minutes) (e.g. "Create a project \'Write Book\' with a 50h goal", "создай проект Х").',
    "SESSION_CONTROL": 'The user wants to start, pause, resume, or end a work session via text (e.g. "I\'m starting a work block", "Taking a break, stopped at SQL", "Back to work", "I\'m done for now").',
    "SYSTEM_CONFIG": 'The user wants to change bot settings. Settings include timezone, cutoff time, target channel, persona etc (e.g. "Set my cutoff to midnight", "Change timezone to Europe/Moscow", "Be more sarcastic").',
    "CONFIG_REPORT": 'The user is configuring how their daily accountability report should look (e.g. "Make my report strict without emojis", "Show projects first then focus time").',
    "GENERATE_REPORT": 'The user wants the daily report generated right NOW instantly, out of schedule (e.g. "Send the report now", "Show me the daily report", "Post report to the channel").',
    "UNDO": 'The user is correcting a mistake they just made (e.g. "Wait, I meant 20 mins", "Undo that last log").',
    "EDIT_ENTITIES": 'The user wants to delete, rename, complete, or modify properties of existing projects or tasks (e.g. "Rename \'Coding\' to \'Backend Dev\'", "Change the project daily target to 20 reps", "Complete task 3", "Done with task 2", "Finished task 5", "Archive project"). NOTE: If the user says they finished a DAILY HABIT or ROUTINE (e.g., "typing done", "habit done", "did yoga"), route to LOG_WORK, not here.',
    "PROJECT_STATUS": 'The user is asking for the status, details, or progress of a specific project (e.g. "What is the status of Pulse?", "How much time is left on project X?").',
    "UPDATE_MEMORY": 'The user is explicitly telling the bot to remember, update, or forget a personal fact or preference (e.g. "Remember that I lunch at 13:00", "I prefer to be addressed as Boss", "Forget my previous instruction about mornings").',
    "CHAT_OR_UNKNOWN": 'The user is just chatting, asking a question, expressing emotions, or saying something you can\'t categorize.'
}

def get_intent_router_system_prompt(user_memory_json=None) -> str:
    intents_list = "\n".join([f"- {k}: {v}" for k, v in INTENT_DESCRIPTIONS.items()])
    
    memory_injection = ""
    if user_memory_json:
        memory_injection = f"\n\nUSER MEMORY (Facts to consider for context):\n{json.dumps(user_memory_json, ensure_ascii=False, indent=2)}\n"

    return f"""You are the internal Intent Router for the Pulse Monolith Bot.
Your ONLY job is to read the user's natural language message and classify it into an exact operational intent.
If the user's message contains multiple distinct requests (e.g. "Create a project X AND log 2 hours to it"), return a list of intents in the logical order of execution.
Return strictly valid JSON and nothing else. Do NOT include markdown code blocks (e.g. ```json).

Categorize the user's input into one or more of the following exact intents:
{intents_list}
{memory_injection}"""

def get_capabilities_text() -> str:
    """Returns a list of capabilities based on the intent descriptions for the Persona Fallback prompt."""
    return "\n".join([f"- {k}: {v}" for k, v in INTENT_DESCRIPTIONS.items() if k != "CHAT_OR_UNKNOWN" and k != "ERROR" and k != "UNKNOWN_PROVIDER"])
