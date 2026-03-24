from aiogram.fsm.state import State, StatesGroup

class AddKeyState(StatesGroup):
    waiting_for_provider = State()
    waiting_for_key = State()

class SettingsState(StatesGroup):
    waiting_for_tz_text = State()
    waiting_for_catalyst = State()
    waiting_for_interval = State()
    waiting_for_channel = State()
