from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.utils.text_decorations import html_decoration
#from config import ADMIN
from function.config_function import ConFunc
from app.state import ConfigState

user = Router()

@user.message(CommandStart())
async def cmd_start(message:Message,state:FSMContext):
    await menu(message,state)


@user.message(F.text == '❌ Отмена')
async def menu(message:Message,state:FSMContext):
    await state.clear()
    config = await ConFunc.get_config()
    keyboard = kb.main_menu(config.is_active)
     # если есть данные, но некоторые поля пустые → подставляем заглушки
    text = config.text if config.text else "❌ Текст не установлен"
    time = config.time if config.time else "❌ Время не установлено"
    interval = config.interval if config.interval else "❌ Интервал не установлен"
    status = "✅ Активна" if config.is_active else "⛔ Не активна"

    response = (
        f"📩 Текущий конфиг:\n\n"
        f"📝 Текст:\n {text}\n"
        f"⏰ Время: {time}\n"
        f"🔄 Интервал: {interval}\n"
        f"⚡️ Статус: {status}"
    )

    await message.answer(response,reply_markup=keyboard,parse_mode='HTML')

@user.callback_query(F.data == 'toggle_sender')
async def toggle_sender(query: CallbackQuery,state:FSMContext):
    
    config = await ConFunc.get_config()
    new_status = not config.is_active

    await ConFunc.set_active_status(new_status)

    status = "🟢 активирована" if new_status else "🔴 деактивирована"
    await query.answer(f"Рассылка {status}")
    await query.message.delete()
    await menu(query.message,state)


@user.callback_query(F.data == 'change_text')
async def text_handler(message:CallbackQuery,state:FSMContext):
    await state.clear()
    await state.set_state(ConfigState.wait_text)
    await message.message.answer("✏️ Введите *новый текст рассылки*:", parse_mode="Markdown",reply_markup=kb.back_button)
    await message.answer()


@user.message(ConfigState.wait_text)
async def wait_text_handler(message:Message,state:FSMContext):
    text = html_decoration.unparse(message.text, message.entities)
    await ConFunc.set_text(text)
    await state.clear()
    await message.answer('*✅ Новый текст сохранен*',parse_mode='Markdown')


@user.callback_query(F.data == 'change_interval')
async def interval_message(message: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ConfigState.wait_interval)
    await message.message.answer("⏱ Введите *интервал в секундах* между сообщениями (например, `5`):", parse_mode="Markdown",reply_markup=kb.back_button)
    await message.answer()


@user.message(ConfigState.wait_interval)
async def save_interval(message: Message, state: FSMContext):
    try:
        interval = float(message.text.strip())
        if interval <= 0:
            raise ValueError
        await ConFunc.set_interval(interval)
        await message.answer(f"✅ Интервал установлен: *{interval} сек*", parse_mode="Markdown")
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите корректное число (например, `3.5`)", parse_mode="Markdown")


@user.callback_query(F.data == 'set_time')
async def start_time(message: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ConfigState.wait_time)
    await message.message.answer("🕰 Введите *время начала рассылки* в формате `ЧЧ:ММ` (например, `14:30`):", parse_mode="Markdown",reply_markup=kb.back_button)
    await message.answer()


@user.message(ConfigState.wait_time)
async def save_start_time(message: Message, state: FSMContext):
    time_text = message.text.strip()
    import re
    if re.match(r'^\d{1,2}:\d{2}$', time_text):
        await ConFunc.set_time(time_text)
        await message.answer(f"✅ Время старта установлено: *{time_text}*", parse_mode="Markdown")
        await state.clear()
    else:
        await message.answer("❌ Неверный формат. Пример правильного: `08:30`", parse_mode="Markdown")


