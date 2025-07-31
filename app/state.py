from aiogram.fsm.state import StatesGroup, State

IS_SENDING = False

class ConfigState(StatesGroup):
    wait_text = State()
    wait_add_group = State()
    wait_delete_group = State()
    wait_interval = State()
    wait_time = State()

    wait_api_id = State()
    wait_api_hash = State()
    wait_phone = State()
    wait_code = State()
    wait_lap_count = State()
