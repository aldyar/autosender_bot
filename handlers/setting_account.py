from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.utils.text_decorations import html_decoration
from database.requests import Func
from app.state import ConfigState
from app.telethon import login_telegram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

user = Router()


@user.message(F.text == '👤 Аккаунт Telegram')
async def account_settings(message: Message,state:FSMContext):
    await state.clear()
    config = await Func.get_config()
    
    if config.api_id and config.api_hash and config.phone:
        text = (
            "👤 <b>Текущий аккаунт:</b>\n"
            f"• <b>API ID:</b> <code>{config.api_id}</code>\n"
            f"• <b>API Hash:</b> <code>{config.api_hash}</code>\n"
            f"• <b>Телефон:</b> <code>{config.phone}</code>\n\n"
            "🔧 Хочешь изменить аккаунт?"
        )
    else:
        text = "⚠️ Аккаунт Telegram не настроен.\n\nНажми «Изменить», чтобы ввести данные."

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✏️ Изменить аккаунт', callback_data='change_account')]
    ])
    
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


@user.callback_query(F.data == 'change_account')
async def change_account_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("🔐 Введите <b>API ID</b>:", parse_mode="HTML")
    await state.set_state(ConfigState.wait_api_id)


@user.message(ConfigState.wait_api_id)
async def get_api_id(message: Message, state: FSMContext):
    await state.update_data(api_id=int(message.text))
    await message.answer("🔐 Введите <b>API Hash</b>:", parse_mode="HTML")
    await state.set_state(ConfigState.wait_api_hash)


@user.message(ConfigState.wait_api_hash)
async def get_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_hash=message.text.strip())
    await message.answer("📱 Введите <b>номер телефона</b> в формате +XXXXXXXXXXX:", parse_mode="HTML")
    await state.set_state(ConfigState.wait_phone)


@user.message(ConfigState.wait_phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())

    data = await state.get_data()

    status, client = await login_telegram(data['api_id'], data['api_hash'], data['phone'])

    if status == 'code_required':
        await state.update_data(client=client)
        await message.answer("✉️ Введите <b>код подтверждения</b> из Telegram:", parse_mode="HTML")
        await state.set_state(ConfigState.wait_code)
    else:
        await message.answer("❌ Ошибка при подключении. Попробуй снова.")
        await state.clear()


@user.message(ConfigState.wait_code)
async def get_code(message: Message, state: FSMContext):
    data = await state.get_data()

    status, _ = await login_telegram(
        data['api_id'], data['api_hash'], data['phone'],
        code=message.text.strip()
    )

    if status == 'ok':
        await Func.save_config(data)
        await message.answer("✅ Аккаунт успешно сохранён и авторизован!")
        await state.clear()
    elif status == 'invalid_code':
        await message.answer("❌ Неверный код. Попробуй снова.")
    else:
        await message.answer("❌ Ошибка. Авторизация не удалась.")
        await state.clear()

