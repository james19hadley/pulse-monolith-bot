from pydantic import BaseModel, Field
from typing import Optional, List
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

class AddInboxParams(BaseModel):
    raw_content: str = Field(description="The actual idea, note, or thought, omitting conversational filler like 'save this idea' or 'remind me to'")

class SessionControlParams(BaseModel):
    action: str = Field(description="Strictly 'START' or 'END' depending on whether they are starting a session or finishing one.")

class GoogleProvider:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        # Using gemini-2.5-flash as it's the fastest and cheapest for strict JSON routing
        self.model_id = "gemini-2.5-flash"
        
    def classify_intent(self, text: str) -> IntentType:
        """Sends the text to Gemini and forces it to return an Intent string via Structured Outputs."""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=INTENT_ROUTER_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=IntentResponse,
                temperature=0.0 # Deterministic output
            ),
        )
        # Parse the JSON string returned by Gemini into a dictionary
        data = json.loads(response.text)
        return IntentType(data.get("intent", IntentType.CHAT_OR_UNKNOWN))

    def extract_log_work_parameters(self, text: str, active_projects_text: str) -> LogWorkParams:
        """Extracts minutes and project ID based on the user's intent and current projects."""
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
                response_mime_type="application/json",
                response_schema=LogWorkParams,
                temperature=0.0
            ),
        )
        return LogWorkParams.model_validate_json(response.text)

    def extract_habit_parameters(self, text: str, active_habits_text: str) -> LogHabitParams:
        """Extracts habit ID and amount."""
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
                response_mime_type="application/json",
                response_schema=LogHabitParams,
                temperature=0.0
            ),
        )
        return LogHabitParams.model_validate_json(response.text)

    def extract_inbox_parameters(self, text: str) -> AddInboxParams:
        """Extracts the core idea."""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction="Extract the core idea from the user's message, removing filler words.",
                response_mime_type="application/json",
                response_schema=AddInboxParams,
                temperature=0.0
            ),
        )
        return AddInboxParams.model_validate_json(response.text)

    def extract_session_control(self, text: str) -> SessionControlParams:
        """Extracts START or END action."""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction="Determine if the user is starting or ending a work session.",
                response_mime_type="application/json",
                response_schema=SessionControlParams,
                temperature=0.0
            ),
        )
        return SessionControlParams.model_validate_json(response.text)

