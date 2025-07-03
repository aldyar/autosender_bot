from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from app.state import ConfigState
from aiogram.utils.text_decorations import html_decoration
from database.requests import Func
from aiogram.filters import StateFilter

user = Router()

@user.message(F.text == '📝 Текст рассылки')
async def text_handler(message:Message,state:FSMContext):
    await state.clear()
    await state.set_state(ConfigState.wait_text)
    await message.answer("✏️ Введите *новый текст рассылки*:", parse_mode="Markdown",reply_markup=kb.back_button)


@user.message(ConfigState.wait_text)
async def wait_text_handler(message:Message,state:FSMContext):
    text = html_decoration.unparse(message.text, message.entities)
    await Func.set_text(text)
    await state.clear()
    await message.answer('*✅ Новый текст сохранен*',parse_mode='Markdown',reply_markup=kb.main_menu)
