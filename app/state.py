from aiogram.fsm.state import StatesGroup, State

class ConfigState(StatesGroup):
    wait_text = State()
    wait_add_group = State()
    wait_delete_group = State()
    wait_interval = State()
    wait_time = State()