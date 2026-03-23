from pydantic import BaseModel
import json
from google import genai
from google.genai import types
from src.core.prompts import INTENT_ROUTER_SYSTEM_PROMPT

class IntentResponse(BaseModel):
    intent: str

class GoogleProvider:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        # Using gemini-2.5-flash as it's the fastest and cheapest for strict JSON routing
        self.model_id = "gemini-2.5-flash"
        
    def classify_intent(self, text: str) -> str:
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
        return data.get("intent", "CHAT_OR_UNKNOWN")
