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

