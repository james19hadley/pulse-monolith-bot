from pydantic import BaseModel, Field
from typing import Optional, List, Tuple
import json
from google import genai
from google.genai import types
from src.core.prompts import INTENT_ROUTER_SYSTEM_PROMPT
from src.core.constants import IntentType

class IntentResponse(BaseModel):
    intent: IntentType

class LogWorkParams(BaseModel):
    duration_minutes: int = Field(description="The total time spent, strictly converted to minutes. E.g., '1.5 hours' becomes 90.")
    project_id: Optional[int] = Field(description="The integer ID of the matching project. Null if no project matches.", default=None)
    description: Optional[str] = Field(description="A brief 1-5 word summary of what was done.", default=None)

class LogHabitParams(BaseModel):
    habit_id: Optional[int] = Field(description="The integer ID of the matching habit. Null if no habit matches.", default=None)
    amount_completed: int = Field(description="The numeric amount completed. If user just says 'did pushups', default to 1 unless specified.", default=1)
    unmatched_habit_name: Optional[str] = Field(description="If no habit matches, provide the inferred name of the new habit here (e.g. 'Drink water').", default=None)
    unmatched_habit_name: Optional[str] = Field(description="If no habit matches, provide the inferred name of the new habit here (e.g. 'Drink water').", default=None)

class AddInboxParams(BaseModel):
    raw_content: str = Field(description="The actual idea, note, or thought, omitting conversational filler like 'save this idea' or 'remind me to'")

class SessionControlParams(BaseModel):
    action: str = Field(description="Strictly 'START' or 'END' depending on whether they are starting a session or finishing one.")

class ReportConfigParams(BaseModel):
    blocks: List[str] = Field(description="Blocks to include in the report. Allowed values: 'focus', 'habits', 'inbox', 'void'. Output in the order requested by user.", default=["focus", "habits", "inbox", "void"])
    style: str = Field(description="Stylistic theme: 'strict', 'emoji', 'casual', or user's custom style.", default="emoji")

class SingleConfigParam(BaseModel):
    setting_key: str = Field(description="The internal key of the setting to change (e.g., 'cutoff', 'timezone', 'persona')")
    setting_value: str = Field(description="The requested correct value of the setting (e.g., '23:00', 'Europe/Moscow', 'butler')")

class SystemConfigParams(BaseModel):
    settings: List[SingleConfigParam] = Field(description="List of settings to change")

class CreateProjectParams(BaseModel):
    title: str = Field(description="The name of the new project.")
    target_minutes: int = Field(description="The target estimated effort in minutes. If they specify hours, multiply by 60. Default is 0.", default=0)

class CreateHabitParams(BaseModel):
    title: str = Field(description="The name of the new habit.")

class CreateEntitiesParams(BaseModel):
    projects: List[CreateProjectParams] = Field(description="List of new projects to create.")
    habits: List[CreateHabitParams] = Field(description="List of new habits to create.")

class CreateProjectParams(BaseModel):
    title: str = Field(description="The name of the new project.")
    target_minutes: int = Field(description="The target estimated effort in minutes. If they specify hours, multiply by 60. Default is 0.", default=0)

class CreateHabitParams(BaseModel):
    title: str = Field(description="The name of the new habit.")

class CreateEntitiesParams(BaseModel):
    projects: List[CreateProjectParams] = Field(description="List of new projects to create.")
    habits: List[CreateHabitParams] = Field(description="List of new habits to create.")

class CreateProjectParams(BaseModel):
    title: str = Field(description="The name of the new project.")
    target_minutes: int = Field(description="The target estimated effort in minutes. If they specify hours, multiply by 60. Default is 0.", default=0)

class CreateHabitParams(BaseModel):
    title: str = Field(description="The name of the new habit.")

class CreateEntitiesParams(BaseModel):
    projects: List[CreateProjectParams] = Field(description="List of new projects to create.")
    habits: List[CreateHabitParams] = Field(description="List of new habits to create.")

class GoogleProvider:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-3-flash-preview'

    def _get_usage(self, response) -> dict:
        usage = getattr(response, 'usage_metadata', None)
        return {
            'prompt_tokens': getattr(usage, 'prompt_token_count', 0) if usage else 0,
            'completion_tokens': getattr(usage, 'candidates_token_count', 0) if usage else 0,
            'total_tokens': getattr(usage, 'total_token_count', 0) if usage else 0,
            'model_name': self.model_id
        }
        
    def classify_intent(self, text: str) -> Tuple[IntentType, dict]:
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=INTENT_ROUTER_SYSTEM_PROMPT,
                response_mime_type='application/json',
                response_schema=IntentResponse,
                temperature=0.0
            ),
        )
        data = json.loads(response.text)
        return IntentType(data.get('intent', IntentType.CHAT_OR_UNKNOWN)), self._get_usage(response)

    def extract_log_work_parameters(self, text: str, active_projects_text: str) -> Tuple[Optional[LogWorkParams], dict]:
        system_prompt = f"""You are a precise data extraction tool.
The user is logging work time. Extract the duration in minutes, the project ID, and a short description.
If no project matches the text, return project_id as null.
Always convert hours to minutes (e.g. 1 hour = 60 mins).

CURRENT ACTIVE PROJECTS:
{active_projects_text}
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type='application/json',
                response_schema=LogWorkParams,
                temperature=0.0
            ),
        )
        return LogWorkParams.model_validate_json(response.text), self._get_usage(response)

    def extract_habit_parameters(self, text: str, active_habits_text: str) -> Tuple[Optional[LogHabitParams], dict]:
        system_prompt = f"""You are a precise data extraction tool.
The user is logging a habit. Extract the habit ID and the amount completed.
If no habit matches, return null for habit_id.

CURRENT HABITS:
{active_habits_text}
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type='application/json',
                response_schema=LogHabitParams,
                temperature=0.0
            ),
        )
        return LogHabitParams.model_validate_json(response.text), self._get_usage(response)

    def extract_inbox_parameters(self, text: str) -> Tuple[Optional[AddInboxParams], dict]:
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction="Extract the core idea from the user's message, removing filler words.",
                response_mime_type='application/json',
                response_schema=AddInboxParams,
                temperature=0.0
            ),
        )
        return AddInboxParams.model_validate_json(response.text), self._get_usage(response)

    def extract_session_control(self, text: str) -> Tuple[Optional[SessionControlParams], dict]:
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction="Determine if the user is starting or ending a work session.",
                response_mime_type='application/json',
                response_schema=SessionControlParams,
                temperature=0.0
            ),
        )
        return SessionControlParams.model_validate_json(response.text), self._get_usage(response)


    def extract_system_config(self, text: str, registry_keys: list[str]) -> Tuple[Optional[SystemConfigParams], dict]:
        keys_info = ", ".join(registry_keys)
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=f"Extract the requested system setting configuration(s). The user might request multiple settings at once. Available internal keys: {keys_info}. Map natural language (e.g. 'post at midnight' -> 'cutoff', '00:00')",
                response_mime_type='application/json',
                response_schema=SystemConfigParams,
                temperature=0.0
            ),
        )
        return SystemConfigParams.model_validate_json(response.text), self._get_usage(response)

    def extract_report_config(self, text: str) -> Tuple[Optional[ReportConfigParams], dict]:
        system_prompt = """You are a configuration parser.
The user is describing how they want their daily accountability report to look.
Extract their preferred visual style (e.g. strict, emoji, casual) and the blocks they want included (and in what order).
Available blocks: 'focus', 'habits', 'inbox', 'void'.
If you are unsure of the style, default to 'emoji'.
If they don't specify blocks, use the default list."""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type='application/json',
                response_schema=ReportConfigParams,
                temperature=0.0
            ),
        )
        return ReportConfigParams.model_validate_json(response.text), self._get_usage(response)


    def extract_create_entities(self, text: str) -> Tuple[Optional[CreateEntitiesParams], dict]:
        system_prompt = "You are a data extraction tool. The user wants to create one or more projects and/or habits. Extract their names and any target metrics (like target hours for a project)."
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type='application/json',
                    response_schema=CreateEntitiesParams,
                    temperature=0.0
                ),
            )
            data = json.loads(response.text)
            return CreateEntitiesParams(**data), self._get_usage(response)
        except Exception as e:
            print(f"Extraction error: {e}")
            return None, {}

    def extract_create_entities(self, text: str) -> Tuple[Optional[CreateEntitiesParams], dict]:
        system_prompt = "You are a data extraction tool. The user wants to create one or more projects and/or habits. Extract their names and any target metrics (like target hours for a project)."
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type='application/json',
                    response_schema=CreateEntitiesParams,
                    temperature=0.0
                ),
            )
            data = json.loads(response.text)
            return CreateEntitiesParams(**data), self._get_usage(response)
        except Exception as e:
            print(f"Extraction error: {e}")
            return None, {}

    def generate_chat_response(self, text: str, persona_prompt: str) -> Tuple[Optional[str], dict]:
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=persona_prompt,
                    temperature=0.7 # conversational
                ),
            )
            return response.text, self._get_usage(response)
        except Exception as e:
            print(f"Chat generation error: {e}")
            return None, {}
