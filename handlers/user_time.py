from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.utils.text_decorations import html_decoration
from database.requests import Func
from app.state import ConfigState
from aiogram.filters import StateFilter

user = Router()


@user.message(F.text == '⏱ Интервал между сообщениями')
async def interval_message(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ConfigState.wait_interval)
    await message.answer("⏱ Введите *интервал в секундах* между сообщениями (например, `5`):", parse_mode="Markdown",reply_markup=kb.back_button)

@user.message(ConfigState.wait_interval)
async def save_interval(message: Message, state: FSMContext):
    try:
        interval = float(message.text.strip())
        if interval <= 0:
            raise ValueError
        await Func.set_interval(interval)
        await message.answer(f"✅ Интервал установлен: *{interval} сек*", parse_mode="Markdown",reply_markup=kb.main_menu)
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите корректное число (например, `3.5`)", parse_mode="Markdown")


@user.message(F.text == '🕰 Время старта')
async def start_time(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ConfigState.wait_time)
    await message.answer("🕰 Введите *время начала рассылки* в формате `ЧЧ:ММ` (например, `14:30`):", parse_mode="Markdown",reply_markup=kb.back_button)

@user.message(ConfigState.wait_time)
async def save_start_time(message: Message, state: FSMContext):
    time_text = message.text.strip()
    import re
    if re.match(r'^\d{1,2}:\d{2}$', time_text):
        await Func.set_time(time_text)
        await message.answer(f"✅ Время старта установлено: *{time_text}*", parse_mode="Markdown",reply_markup=kb.main_menu)
        await state.clear()
    else:
        await message.answer("❌ Неверный формат. Пример правильного: `08:30`", parse_mode="Markdown")