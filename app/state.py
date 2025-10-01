from aiogram.fsm.state import StatesGroup, State

class ConfigState(StatesGroup):
    wait_text = State()
    wait_interval = State()
    wait_time = State()

    wait_phone = State()
    wait_code = State()
    delete_account = State()
    test_state = State()