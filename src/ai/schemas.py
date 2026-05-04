"""
Standardized Pydantic schemas for AI extraction and tool calling.
These models are used across all LLM providers to ensure type safety and consistent structured output.

@Architecture-Map: [CORE-AI-SCHEMAS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Union
from src.core.constants import IntentType

class IntentResponse(BaseModel):
    intents: List[IntentType] = Field(description="The operational intents found in the user's message. Can be a single intent, or multiple if the user asked to do several distinct things. Order matters.")

class LogWorkParams(BaseModel):
    duration_minutes: int = Field(description="The total time spent, strictly converted to minutes. Can be negative for subtraction. E.g., '1.5 hours' -> 90. Use 0 if the user explicitly sets absolute progress OR if they simply say they finished a habit without specifying time (e.g., 'typing done', 'сделал планку').")
    progress_amount: Optional[float] = Field(description="The exact numeric amount of progress. If user says 'установи прогресс на 1.5', put 1.5 here. If user simply says they completed a habit without specifying an amount (e.g. 'did yoga', 'сделал планку'), leave this as null so the system can auto-fill.", default=None)
    is_absolute_progress: Optional[bool] = Field(description="CRITICAL: True ONLY if the user uses words like 'ровно', 'set to', 'установи' to specify an EXACT replacement completion point (e.g. 'установи прогресс на 1.5').", default=False)
    progress_unit: Optional[str] = Field(description="The unit of the progress made if specified, e.g. pages, km, tasks, chapters, hours, часов. MUST be extracted if mentioned.", default=None)
    project_id: Optional[int] = Field(description="The integer ID of the matching project. Null if no project matches.", default=None)
    unmatched_project_name: Optional[str] = Field(description="If no project matches, provide the inferred name of the project here", default=None)
    description: Optional[str] = Field(description="A brief 1-5 word summary of what was done.", default=None)

class LogWorkMultiParams(BaseModel):
    logs: List[LogWorkParams] = Field(description="A list of work logs to record. Usually just one, but can be multiple if the user mentions moving or transferring time between multiple projects.")

class AddInboxParams(BaseModel):
    raw_content: str = Field(description="The actual idea, note, or thought, omitting conversational filler like 'save this idea' or 'remind me to'")

class SessionControlParams(BaseModel):
    action: str = Field(description="Strictly 'START', 'END', 'REST', or 'RESUME' depending on whether they are starting a session, finishing one, taking a break, or coming back from a break.")
    project_id: Optional[int] = Field(description="If they mention a specific project id they are starting to work on, extract it here.", default=None)
    context: Optional[str] = Field(description="If action is 'REST', this captures what they were just working on as a save-state context. e.g., 'fixing the SQL query'.", default=None)

class ReportConfigParams(BaseModel):
    blocks: List[str] = Field(description="Blocks to include in the report. Allowed values: 'focus', 'projects', 'inbox'. Output in the order requested by user.", default=["focus", "projects", "inbox"])
    style: str = Field(description="Stylistic theme: 'strict', 'emoji', 'casual', or user's custom style.", default="emoji")

class SingleConfigParam(BaseModel):
    setting_key: str = Field(description="The internal key of the setting to change (e.g., 'cutoff', 'timezone', 'persona')")
    setting_value: str = Field(description="The requested correct value of the setting (e.g., '23:00', 'Europe/Moscow', 'butler')")

class SystemConfigParams(BaseModel):
    settings: List[SingleConfigParam] = Field(description="List of settings to change")

class CreateProjectParams(BaseModel):
    title: str = Field(description="The name of the new project. You can creatively prefix it with a suitable emoji (like '📚 Reading' or '🏋️ Sport') so it looks nice. If it's a generic technical topic, use an abstract emoji. Ensure the emoji is strictly the very first character if used.")
    lifetime_target_value: int = Field(description="The absolute, total lifetime goal for this project. If they specify hours, multiply by 60 to get minutes. Default is 0.", default=0)
    periodic_target_value: Optional[int] = Field(description="The recurring goal per period (e.g. '15 mins a day', '3 times a week'). If hours, multiply by 60. Default is null.", default=None)
    target_period: Optional[str] = Field(description="The period for the periodic_target_value. Strictly 'daily', 'weekly', or 'monthly'. Leave null if there is only a lifetime goal.", default=None)
    unit: Optional[str] = Field(description="The unit of measurement (e.g. pages, reps, hours, minutes). Default is minutes.", default="minutes")
    parent_project_id: Optional[int] = Field(description="The numeric ID of the parent project if this is created as a sub-project or child. Requires context of existing projects with IDs.", default=None)

class CreateEntitiesParams(BaseModel):
    projects: List[CreateProjectParams] = Field(description="List of new projects to create.")

class TaskParam(BaseModel):
    title: str = Field(description="The short actionable title of the task. Strip any duration numbers from this title.")
    estimated_minutes: Optional[int] = Field(description="If the user specifies an estimated duration for the task (e.g. '1.5 hours', '30 mins'), extract it here in minutes. Do not leave the duration in the title.", default=None)
    project_id: Optional[int] = Field(description="The ID of the matching project if the user specified one or context implies it. Null if standalone.", default=None)
    unmatched_project_name: Optional[str] = Field(description="If the user specified a project but it's not in the active projects list, put its inferred name here.", default=None)
    reminder_time: Optional[str] = Field(description="If the user explicitly mentions an exact time to do the task or be reminded (e.g. 'at 14:30', 'in 2 hours'), calculate the ISO-8601 datetime using the user's local time provided in the prompt context.", default=None)

class AddTasksParams(BaseModel):
    tasks: List[TaskParam] = Field(description="List of tasks to create.")
    clear_inbox: Optional[bool] = Field(description="True if the user explicitly or implicitly asked to convert/empty their Inbox while adding these tasks.", default=False)

class EditEntitiesParam(BaseModel):
    entity_type: str = Field(description="Strictly 'project' or 'task' - what kind of entity to edit")
    action: str = Field(description="Strictly 'edit' or 'delete'", default="edit")
    entity_name_or_id: str = Field(description="The name or ID of the existing entity to edit or delete")
    new_name: Optional[str] = Field(description="The new name for the entity, if renaming", default=None)
    new_target_value: Optional[int] = Field(description="The new target value for the entity", default=None)
    new_unit: Optional[str] = Field(description="The new unit for measurement", default=None)
    new_parent_project_id: Optional[int] = Field(description="The ID of the new parent project if they want to move/link this project under another one. Send -1 to unlink.", default=None)
    new_status: Optional[str] = Field(description="The new status for a task (e.g. 'completed', 'cancelled', 'pending')", default=None)

class EditEntitiesParams(BaseModel):
    edits: List[EditEntitiesParam] = Field(description="List of entity edits requested by user")

class UpdateMemoryParams(BaseModel):
    memory_key: str = Field(description="A short, concise snake_case key identifying the context (e.g. 'lunch_time', 'address_preference', 'manager_name')")
    memory_value: str = Field(description="The actual value or fact to remember")
