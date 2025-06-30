from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.utils.text_decorations import html_decoration
from database.requests import Func
from app.state import ConfigState

user = Router()


@user.message(F.text == '👤 Аккаунт Telegram')
async def account_settings(message:Message):
    pass

