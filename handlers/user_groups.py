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


@user.message(F.text == '📂 Группы для рассылки')
async def group_handler(message: Message,state:FSMContext):
    await state.clear()
    groups = await Func.get_groups()
    
    if groups:
        group_list = "\n".join([f"• `@{g.name}`" for g in groups if g.name])
        text = f"📂 *Группы для рассылки:*\n\n{group_list}"
    else:
        text = "⚠️ *Группы для рассылки пока не добавлены.*"

    await message.answer(text, parse_mode="Markdown",reply_markup=kb.group_inline)


@user.callback_query(F.data == 'SetGroup')
async def add_group(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ConfigState.wait_add_group)
    await callback.message.answer("➕ Введите *названия групп* (можно несколько, через новую строку):", parse_mode="Markdown",reply_markup=kb.back_button)

@user.callback_query(F.data == 'DeleteGroup')
async def delete_group(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ConfigState.wait_delete_group)
    await callback.message.answer("🗑 Введите *названия групп*, которые нужно удалить (по одной на строке):", parse_mode="Markdown",reply_markup=kb.back_button)


@user.message(ConfigState.wait_add_group)
async def process_add_group(message: Message, state: FSMContext):
    group_names = [name.strip().lstrip('@') for name in message.text.split('\n') if name.strip()]
    await Func.add_groups(group_names)
    await message.answer(f"✅ Добавлено групп: *{len(group_names)}*", parse_mode="Markdown",reply_markup=kb.main_menu)
    await state.clear()

@user.message(ConfigState.wait_delete_group)
async def process_delete_group(message: Message, state: FSMContext):
    group_names = [name.strip().lstrip('@') for name in message.text.split('\n') if name.strip()]
    await Func.delete_groups(group_names)
    await message.answer(f"🗑 Удалено групп: *{len(group_names)}*", parse_mode="Markdown",reply_markup=kb.main_menu)
    await state.clear()