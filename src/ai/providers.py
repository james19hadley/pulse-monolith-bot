"""
LLM Provider implementations (Google Gemini, OpenAI). Handles API connections and payload parsing.

@Architecture-Map: [CORE-AI-PROVIDERS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from typing import Optional, List, Tuple
from datetime import datetime
import json
from google import genai
from google.genai import types
from src.core.constants import IntentType
from src.ai.schemas import (
    IntentResponse, LogWorkMultiParams, AddInboxParams, SessionControlParams,
    ReportConfigParams, SystemConfigParams, CreateEntitiesParams, 
    EditEntitiesParams, AddTasksParams, UpdateMemoryParams
)
from src.ai.base_provider import BaseLLMProvider

class GoogleProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_id: str = "gemini-3-flash-preview"):
        super().__init__(api_key, model_id)
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
        
    def classify_intents(self, text: str, user_memory: dict = None) -> Tuple[List[IntentType], dict]:
        from src.core.prompts import get_intent_router_system_prompt
        system_prompt = get_intent_router_system_prompt(user_memory)
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type='application/json',
                response_schema=IntentResponse,
                temperature=0.0
            ),
        )
        data = IntentResponse.model_validate_json(response.text)
        return data.intents, self._get_usage(response)

    def extract_log_work_parameters(self, text: str, active_projects_text: str) -> Tuple[Optional[LogWorkMultiParams], dict]:
        system_prompt = f"""You are a precise data extraction tool.
The user is logging work time. Extract the duration in minutes, the project ID, and a short description.
If the user specifies moving time (e.g. 'subtract X from Y and add X to Z'), generate multiple log entries (one negative, one positive).
If no project matches the text, return project_id as null.
Always convert hours to minutes (e.g. 1 hour = 60 mins).
IMPORTANT: If the user says they "did", "completed", or are "done" with a habit/project, and that project has a Target listed, you MUST calculate the remaining amount (Target - Current Progress) and log exactly that remaining amount to reach the target.

CURRENT ACTIVE PROJECTS:
{active_projects_text}
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type='application/json',
                response_schema=LogWorkMultiParams,
                temperature=0.0
            ),
        )
        return LogWorkMultiParams.model_validate_json(response.text), self._get_usage(response)


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

    def extract_session_control(self, text: str, active_projects_text: str = "") -> Tuple[Optional[SessionControlParams], dict]:
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=f"Determine if the user is starting, ending, pausing (rest/break), or resuming a work session. If starting, extract the project ID if mentioned.\nCURRENT ACTIVE PROJECTS:\n{active_projects_text}",
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
Available blocks: 'focus', 'projects', 'inbox', 'void'.
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


    def extract_create_entities(self, text: str, active_projects_text: str = "") -> Tuple[Optional[CreateEntitiesParams], dict]:
        system_prompt = "You are a data extraction tool. The user wants to create one or more projects. Extract their names and target metrics (like target hours for a project). If they specify this project as a child or sub-project of an existing project, use the provided active projects list to find the parent_project_id."
        if active_projects_text:
            system_prompt += f"\n\nExisting Projects:\n{active_projects_text}"
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


    def extract_edit_entities(self, text: str, entities_text: str):
        """Extract entity edit requests from user text"""
        system_prompt = f"""You are a data extraction tool.
The user wants to edit (rename, change target value, complete) one or more existing entities (projects or tasks).
Extract the entity type, the current name or identifier, and the changes requested.
When completing a task, set action='edit' and new_status='completed'.

CRITICAL: The user might say "complete task 1" (using an ordinal number).
You MUST look at the list below, find "Task 1", and extract its DB_ID for the `entity_name_or_id` field. Do not return "1" if "1" is just the ordinal number. Return the DB_ID!

CURRENT ENTITIES:
{entities_text}
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type='application/json',
                response_schema=EditEntitiesParams,
                temperature=0.0
            ),
        )
        return EditEntitiesParams.model_validate_json(response.text), self._get_usage(response)

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

    def extract_add_tasks_parameters(self, text: str, active_projects_text: str) -> Tuple[Optional[AddTasksParams], dict]:
        prompt = f"User input:\n{text}\n\nExtract the tasks the user wants to add.\n\n{active_projects_text}"
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AddTasksParams,
                temperature=0.0
            ),
        )
        return AddTasksParams.model_validate_json(response.text), self._get_usage(response)

    def extract_update_memory(self, text: str) -> Tuple[Optional[UpdateMemoryParams], dict]:
        system_prompt = "Extract the fact or preference the user wants the bot to remember."
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=UpdateMemoryParams,
                temperature=0.0
            ),
        )
        return UpdateMemoryParams.model_validate_json(response.text), self._get_usage(response)
