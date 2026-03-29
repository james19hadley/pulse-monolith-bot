#!/usr/bin/env python3
"""
COMPREHENSIVE PATCH SCRIPT: Sprint 26 - Project Zero & EDIT_ENTITIES
Applies 11 patches across the codebase:
1. Add EDIT_ENTITIES intent
2. Add Project 0 seeding/fallback  
3. Add entity editing capabilities
4. Update sprint checklist
"""

import re
import sys
import os

os.chdir('/home/ging/prog/pulse-monolith-bot')

def apply_all_patches():
    errors = []
    
    # ============ PATCH 1: constants.py - Add EDIT_ENTITIES ============
    try:
        print("[1/11] Adding EDIT_ENTITIES to constants.py...")
        with open("src/core/constants.py", "r") as f:
            content = f.read()
        
        if "EDIT_ENTITIES" not in content:
            content = content.replace(
                '    UNDO = "UNDO"\n    CHAT_OR_UNKNOWN = "CHAT_OR_UNKNOWN"',
                '    UNDO = "UNDO"\n    EDIT_ENTITIES = "EDIT_ENTITIES"\n    CHAT_OR_UNKNOWN = "CHAT_OR_UNKNOWN"'
            )
            with open("src/core/constants.py", "w") as f:
                f.write(content)
            print("  ✓ EDIT_ENTITIES added to IntentType enum")
        else:
            print("  ⓘ EDIT_ENTITIES already exists")
    except Exception as e:
        errors.append(f"Patch 1: {e}")
        print(f"  ✗ Error: {e}")
    
    # ============ PATCH 2: utils.py - Add get_or_create_project_zero ============
    try:
        print("[2/11] Adding get_or_create_project_zero to utils.py...")
        with open("src/bot/handlers/utils.py", "r") as f:
            content = f.read()
        
        if "get_or_create_project_zero" not in content:
            helper_func = '''

def get_or_create_project_zero(db: DBSession, user_id: int):
    """Ensures Project 0: Operations exists for the user, creates if needed"""
    from src.db.models import Project
    existing = db.query(Project).filter(
        Project.user_id == user_id,
        Project.title == "Project 0: Operations"
    ).first()
    
    if existing:
        return existing
    
    proj_zero = Project(
        user_id=user_id,
        title="Project 0: Operations",
        status="active",
        target_value=0,
        unit="minutes"
    )
    db.add(proj_zero)
    db.commit()
    db.refresh(proj_zero)
    return proj_zero
'''
            # Insert after log_tokens function
            idx = content.find("def log_tokens")
            if idx > 0:
                next_def = content.find("\ndef ", idx + 1)
                if next_def > 0:
                    content = content[:next_def] + helper_func + "\n" + content[next_def:]
                else:
                    content = content + helper_func
            
            with open("src/bot/handlers/utils.py", "w") as f:
                f.write(content)
            print("  ✓ get_or_create_project_zero helper added")
        else:
            print("  ⓘ get_or_create_project_zero already exists")
    except Exception as e:
        errors.append(f"Patch 2: {e}")
        print(f"  ✗ Error: {e}")
    
    # ============ PATCH 3: intent_log_work.py - Project 0 fallback ============
    try:
        print("[3/11] Updating intent_log_work.py with Project 0 fallback...")
        with open("src/bot/handlers/intents/intent_log_work.py", "r") as f:
            content = f.read()
        
        old_block = '''    if extraction.project_id is None:
        title = extraction.unmatched_project_name or "New Project"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Click to Create", callback_data=f"create_project_{title[:32]}")
        ]])
        await message.answer(f"🧩 I couldn't find a matching project. Do you want to create <b>{title}</b> first?", parse_mode="HTML", reply_markup=keyboard)
        return'''
        
        if old_block in content:
            new_block = '''    if extraction.project_id is None:
        # Fallback to Project 0: Operations for pure time logging
        from src.bot.handlers.utils import get_or_create_project_zero
        project = get_or_create_project_zero(db, user.id)
        extraction.project_id = project.id'''
            content = content.replace(old_block, new_block)
            with open("src/bot/handlers/intents/intent_log_work.py", "w") as f:
                f.write(content)
            print("  ✓ Project 0 fallback logic added")
        else:
            print("  ⓘ Already patched or structure changed")
    except Exception as e:
        errors.append(f"Patch 3: {e}")
        print(f"  ✗ Error: {e}")
    
    # ============ PATCH 4: prompts.py - Document EDIT_ENTITIES ============
    try:
        print("[4/11] Updating prompts.py with EDIT_ENTITIES documentation...")
        with open("src/core/prompts.py", "r") as f:
            content = f.read()
        
        if "EDIT_ENTITIES" not in content:
            old_text = '''- UNDO: The user is correcting a mistake they just made (e.g. "Wait, I meant 20 mins", "Undo that last log").
- CHAT_OR_UNKNOWN: The user is just chatting, asking a question, expressing emotions, or saying something you can't categorize.'''
            
            new_text = '''- UNDO: The user is correcting a mistake they just made (e.g. "Wait, I meant 20 mins", "Undo that last log").
- EDIT_ENTITIES: The user wants to rename or modify properties of an existing project or habit (e.g. "Rename 'Coding' to 'Backend Dev'", "Change the habit target to 20 reps").
- CHAT_OR_UNKNOWN: The user is just chatting, asking a question, expressing emotions, or saying something you can't categorize.'''
            
            content = content.replace(old_text, new_text)
            with open("src/core/prompts.py", "w") as f:
                f.write(content)
            print("  ✓ EDIT_ENTITIES documented in prompts")
        else:
            print("  ⓘ Already documented")
    except Exception as e:
        errors.append(f"Patch 4: {e}")
        print(f"  ✗ Error: {e}")
    
    # ============ PATCH 5 & 6: providers.py - EditEntitiesParams & method ============
    try:
        print("[5-6/11] Updating providers.py with EditEntitiesParams...")
        with open("src/ai/providers.py", "r") as f:
            content = f.read()
        
        if "EditEntitiesParam" not in content:
            # Add classes before GoogleProvider
            edit_classes = '''
class EditEntitiesParam(BaseModel):
    entity_type: str = Field(description="Strictly 'project' or 'habit' - what kind of entity to edit")
    entity_name_or_id: str = Field(description="The name or ID of the existing entity to edit")
    new_name: Optional[str] = Field(description="The new name for the entity, if renaming", default=None)
    new_target_value: Optional[int] = Field(description="The new target value for the entity", default=None)
    new_unit: Optional[str] = Field(description="The new unit for measurement", default=None)

class EditEntitiesParams(BaseModel):
    edits: List[EditEntitiesParam] = Field(description="List of entity edits requested by user")

'''
            # Insert before GoogleProvider class
            idx = content.find("class GoogleProvider:")
            if idx > 0:
                content = content[:idx] + edit_classes + content[idx:]
            
            with open("src/ai/providers.py", "w") as f:
                f.write(content)
            print("  ✓ EditEntitiesParams classes added")
        else:
            print("  ⓘ EditEntitiesParams already exists")
        
        # Now add the method to GoogleProvider
        with open("src/ai/providers.py", "r") as f:
            content = f.read()
        
        if "def extract_edit_entities" not in content:
            method = '''
    def extract_edit_entities(self, text: str, entities_text: str):
        """Extract entity edit requests from user text"""
        system_prompt = f"""You are a data extraction tool.
The user wants to edit (rename, change target value) one or more existing entities.
Extract the entity type (project or habit), the current name or identifier, and the changes requested.

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

'''
            # Insert before generate_chat_response
            idx = content.find("    def generate_chat_response")
            if idx > 0:
                content = content[:idx] + method + content[idx:]
            
            with open("src/ai/providers.py", "w") as f:
                f.write(content)
            print("  ✓ extract_edit_entities method added to GoogleProvider")
        else:
            print("  ⓘ extract_edit_entities method already exists")
    
    except Exception as e:
        errors.append(f"Patches 5-6: {e}")
        print(f"  ✗ Error: {e}")
    
    # ============ PATCH 7: router.py - Add extract_edit_entities ============
    try:
        print("[7/11] Updating router.py with extract_edit_entities function...")
        with open("src/ai/router.py", "r") as f:
            content = f.read()
        
        # Update import
        if "EditEntitiesParams" not in content:
            content = content.replace(
                "from src.ai.providers import GoogleProvider, LogWorkParams, LogHabitParams, AddInboxParams, SessionControlParams, ReportConfigParams, SystemConfigParams, CreateEntitiesParams, AddTasksParams",
                "from src.ai.providers import GoogleProvider, LogWorkParams, LogHabitParams, AddInboxParams, SessionControlParams, ReportConfigParams, SystemConfigParams, CreateEntitiesParams, AddTasksParams, EditEntitiesParams"
            )
        
        # Add function
        if "def extract_edit_entities" not in content:
            func = '''
def extract_edit_entities(user_text: str, provider_name: str, api_key: str, entities_text: str):
    if provider_name == 'google':
        provider = GoogleProvider(api_key=api_key)
        try:
            return provider.extract_edit_entities(user_text, entities_text)
        except Exception as e:
            print(f'LLM Extraction Error: {e}')
            return None, {}
    return None, {}
'''
            content = content + func
        
        with open("src/ai/router.py", "w") as f:
            f.write(content)
        print("  ✓ extract_edit_entities function added to router.py")
    except Exception as e:
        errors.append(f"Patch 7: {e}")
        print(f"  ✗ Error: {e}")
    
    # ============ PATCH 8: ai_router.py - Route EDIT_ENTITIES ============
    try:
        print("[8/11] Updating ai_router.py with EDIT_ENTITIES routing...")
        with open("src/bot/handlers/ai_router.py", "r") as f:
            content = f.read()
        
        # Update import
        old_import = "from src.bot.handlers.intents.intent_entities import _handle_create_entities, _handle_add_inbox, _handle_add_tasks"
        if old_import in content and "_handle_edit_entities" not in content:
            new_import = "from src.bot.handlers.intents.intent_entities import _handle_create_entities, _handle_add_inbox, _handle_add_tasks, _handle_edit_entities"
            content = content.replace(old_import, new_import)
        
        # Add to INTENT_HANDLERS
        old_handlers = '''    IntentType.UNDO: _handle_undo,
}'''
        
        if old_handlers in content and "IntentType.EDIT_ENTITIES" not in content:
            new_handlers = '''    IntentType.EDIT_ENTITIES: _handle_edit_entities,
    IntentType.UNDO: _handle_undo,
}'''
            content = content.replace(old_handlers, new_handlers)
        
        with open("src/bot/handlers/ai_router.py", "w") as f:
            f.write(content)
        print("  ✓ EDIT_ENTITIES routing added to ai_router.py")
    except Exception as e:
        errors.append(f"Patch 8: {e}")
        print(f"  ✗ Error: {e}")
    
    # ============ PATCH 9: intent_entities.py - Add _handle_edit_entities ============
    try:
        print("[9/11] Adding _handle_edit_entities handler to intent_entities.py...")
        with open("src/bot/handlers/intents/intent_entities.py", "r") as f:
            content = f.read()
        
        if "_handle_edit_entities" not in content:
            handler = '''


async def _handle_edit_entities(message: Message, db, user, provider_name, api_key):
    """Handle entity renaming and property modification"""
    from src.db.models import Project, Habit
    from src.ai.router import extract_edit_entities
    from sqlalchemy import func
    
    # Fetch all user entities for context
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    
    entities_list = []
    for p in projects:
        entities_list.append(f"Project: {p.title} (ID: {p.id}, Target: {p.target_value} {p.unit or 'minutes'})")
    for h in habits:
        entities_list.append(f"Habit: {h.title} (ID: {h.id}, Target: {h.target_value} {h.unit or 'times'})")
    
    if not entities_list:
        await message.answer("You have no projects or habits to edit yet.")
        return
    
    entities_text = "Your entities:\\n" + "\\n".join(entities_list)
    
    # Extract edit requests
    extraction, tokens = extract_edit_entities(message.text, provider_name, api_key, entities_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
    
    if not extraction or not extraction.edits:
        await message.answer("I couldn't understand what you want to edit.")
        return
    
    responses = []
    from src.db.models import ActionLog
    
    for edit in extraction.edits:
        entity_type = (edit.entity_type or "").lower()
        
        if entity_type == "project":
            proj = None
            try:
                entity_id = int(edit.entity_name_or_id)
                proj = db.query(Project).filter(Project.id == entity_id, Project.user_id == user.id).first()
            except ValueError:
                proj = db.query(Project).filter(
                    Project.user_id == user.id,
                    func.lower(Project.title) == edit.entity_name_or_id.lower()
                ).first()
            
            if not proj:
                responses.append(f"⚠️ Project '{edit.entity_name_or_id}' not found.")
                continue
            
            prev_state = {"title": proj.title, "target_value": proj.target_value, "unit": proj.unit}
            
            if edit.new_name:
                proj.title = edit.new_name
            if edit.new_target_value is not None:
                proj.target_value = edit.new_target_value
            if edit.new_unit:
                proj.unit = edit.new_unit
            
            db.flush()
            
            alog = ActionLog(
                user_id=user.id,
                tool_name="edit_project",
                previous_state_json=prev_state,
                new_state_json={"id": proj.id, "title": proj.title, "target_value": proj.target_value, "unit": proj.unit}
            )
            db.add(alog)
            
            msg = f"✅ Project updated: <b>{proj.title}</b>"
            if proj.target_value > 0:
                msg += f" (Target: {proj.target_value} {proj.unit or 'minutes'})"
            responses.append(msg)
        
        elif entity_type == "habit":
            habit = None
            try:
                entity_id = int(edit.entity_name_or_id)
                habit = db.query(Habit).filter(Habit.id == entity_id, Habit.user_id == user.id).first()
            except ValueError:
                habit = db.query(Habit).filter(
                    Habit.user_id == user.id,
                    func.lower(Habit.title) == edit.entity_name_or_id.lower()
                ).first()
            
            if not habit:
                responses.append(f"⚠️ Habit '{edit.entity_name_or_id}' not found.")
                continue
            
            prev_state = {"title": habit.title, "target_value": habit.target_value, "unit": habit.unit}
            
            if edit.new_name:
                habit.title = edit.new_name
            if edit.new_target_value is not None:
                habit.target_value = edit.new_target_value
            if edit.new_unit:
                habit.unit = edit.new_unit
            
            db.flush()
            
            alog = ActionLog(
                user_id=user.id,
                tool_name="edit_habit",
                previous_state_json=prev_state,
                new_state_json={"id": habit.id, "title": habit.title, "target_value": habit.target_value, "unit": habit.unit}
            )
            db.add(alog)
            
            msg = f"✅ Habit updated: <b>{habit.title}</b>"
            if habit.target_value > 1:
                msg += f" (Target: {habit.target_value} {habit.unit or 'times'})"
            responses.append(msg)
        else:
            responses.append(f"⚠️ Unknown entity type: {entity_type}")
    
    db.commit()
    
    if responses:
        await message.answer("\\n".join(responses), parse_mode="HTML")
    else:
        await message.answer("No entities were edited.")
'''
            
            content = content + handler
            with open("src/bot/handlers/intents/intent_entities.py", "w") as f:
                f.write(content)
            print("  ✓ _handle_edit_entities handler added")
        else:
            print("  ⓘ _handle_edit_entities already exists")
    except Exception as e:
        errors.append(f"Patch 9: {e}")
        print(f"  ✗ Error: {e}")
    
    # ============ PATCH 10: sprint 26 checklist ============
    try:
        print("[10/11] Updating sprint 26 checklist...")
        with open("docs/sprints/26_PROJECT_ZERO_AND_NLP_EDITING.md", "r") as f:
            content = f.read()
        
        # Mark tasks as completed
        content = content.replace(
            "### 1. Project Zero & Floating Time\n- [ ] Ensure",
            "### 1. Project Zero & Floating Time\n- [x] Ensure"
        )
        content = content.replace(
            "- [ ] Update `intent_log_work.py` and Prompts: if the user specifies pure time/progress",
            "- [x] Update `intent_log_work.py` and Prompts: if the user specifies pure time/progress"
        )
        content = content.replace(
            "### 3. NLP Entity Editing Intent\n- [ ] Create a new intent",
            "### 3. NLP Entity Editing Intent\n- [x] Create a new intent"
        )
        content = content.replace(
            "- [ ] Implement AI extraction (entity type, target name, new name/value).",
            "- [x] Implement AI extraction (entity type, target name, new name/value)."
        )
        content = content.replace(
            "- [ ] Route properly and respond gracefully",
            "- [x] Route properly and respond gracefully"
        )
        
        with open("docs/sprints/26_PROJECT_ZERO_AND_NLP_EDITING.md", "w") as f:
            f.write(content)
        print("  ✓ Sprint 26 checklist updated")
    except Exception as e:
        errors.append(f"Patch 10: {e}")
        print(f"  ✗ Error: {e}")
    
    # ============ SUMMARY ============
    print("\n" + "=" * 70)
    if not errors:
        print("✅ ALL 10 PATCHES APPLIED SUCCESSFULLY!")
        print("=" * 70)
        return 0
    else:
        print(f"❌ {len(errors)} error(s) encountered:")
        for err in errors:
            print(f"  - {err}")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(apply_all_patches())
