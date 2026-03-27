from aiogram.fsm.state import State, StatesGroup

class AddKeyState(StatesGroup):
    waiting_for_provider = State()
    waiting_for_key = State()

class SettingsState(StatesGroup):
    waiting_for_tz_text = State()
    waiting_for_catalyst = State()
    waiting_for_interval = State()
    waiting_for_channel = State()
    waiting_for_cutoff = State()

class EntityState(StatesGroup):
    waiting_for_project_name = State()
    waiting_for_project_target = State()
    
    waiting_for_habit_name = State()
    waiting_for_habit_target = State()
    
    waiting_for_edit_project_target = State()
    waiting_for_add_project_time = State()
    
    waiting_for_edit_habit_target = State()
    waiting_for_add_habit_progress = State()
    
    waiting_for_habit_periodicity = State()
    waiting_for_habit_nudge = State()
