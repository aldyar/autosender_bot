from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.utils.text_decorations import html_decoration
from database.requests import Func
from app.state import ConfigState
from config import ADMIN

user = Router()

@user.message(F.text == '❌ Отмена')
@user.message(CommandStart())
async def cmd_start(message: Message,state:FSMContext):
    if message.from_user.id not in ADMIN:
        return  # не админ — ничего не отвечаем
    
    await state.clear()
    text = (
        "👋 *Привет!* Это панель управления *рассылкой*.\n\n"
        "Здесь ты можешь:\n"
        "• *📝 Текст рассылки* — изменить текст отправляемого сообщения\n"
        "• *📂 Группы для рассылки* — добавить или удалить группы\n"
        "• *⏱ Интервал между сообщениями* — указать паузу между отправками\n"
        "• *🕰 Время старта* — задать, во сколько запускать рассылку\n"
        "• *👤 Аккаунт Telegram* — выбрать или поменять аккаунт\n"
        "• *📤 Рассылка* — запустить рассылку вручную\n\n"
        "_Выбери нужный пункт из меню ниже 👇_"
    )
    await message.answer(text,parse_mode='Markdown',reply_markup=kb.main_menu)

