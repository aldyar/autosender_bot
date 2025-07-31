from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.utils.text_decorations import html_decoration
from database.requests import Func
from app.state import ConfigState
from app.telethon import send_bulk,is_session_active
from aiogram import Bot
from app import state

user = Router()


@user.message(F.text == '📤 Рассылка')
async def sender_handler(message: Message,state:FSMContext):
    await state.clear()
    config = await Func.get_config()
    groups = await Func.get_groups()

    if not config or not config.api_id or not config.api_hash or not config.phone:
        await message.answer("❌ Аккаунт не настроен.\nДобавьте Telegram-аккаунт.")
        return

    # # 🧪 Проверка активности сессии
    # session_ok = await is_session_active(config)
    # if not session_ok:
    #     await message.answer("⚠️ Сессия Telegram недействительна или слетела.\nЗайдите повторно в аккаунт.")
    #     return
    
    group_count = len(groups)
    text = config.text or '❌ не задан'
    interval = f"{config.interval} сек." if config.interval else "❌ не задан"
    time = config.time or "❌ не задан"
    active = "🟢 Активна" if config.is_active else "🔴 Неактивна"
    lap_count = config.lap_count or 1
    lap_display = "∞" if lap_count == 1000 else str(lap_count)

    msg = (
        f"<b>📤 Настройки рассылки:</b>\n\n"
        f"📝 Текст:\n{text}\n"
        f"📂 Групп: <b>{group_count}</b>\n"
        f"🔁 Кругов: <b>{lap_display}</b>\n"
        f"⏱ Интервал: <b>{interval}</b>\n"
        f"🕰 Время старта: <b>{time}</b>\n"
        f"👤 Аккаунт: <code>{config.phone}</code>\n"
        f"⚙️ Статус: <b>{active}</b>"
    )

    await message.answer(msg, parse_mode="HTML", reply_markup=kb.sender_menu(config.is_active))


@user.callback_query(F.data == 'toggle_sender')
async def toggle_sender(query: CallbackQuery,state:FSMContext):
    await query.message.delete()
    config = await Func.get_config()
    new_status = not config.is_active

    await Func.set_active_status(new_status)

    status = "🟢 активирована" if new_status else "🔴 деактивирована"
    await query.answer(f"Рассылка {status}")
    await sender_handler(query.message,state)



@user.callback_query(F.data == 'start_manual')
async def start_manual_sender(query: CallbackQuery,bot:Bot):

    if state.IS_SENDING:
        await query.answer("⚠️ Рассылка уже идёт. Подождите окончания.", show_alert=True)
        return
    
    config = await Func.get_config()
    groups = await Func.get_groups()

    if not config.is_active:
        await query.answer("❌ Рассылка неактивна.", show_alert=True)
        return

    if not config.text or not groups:
        await query.answer("⚠️ Текст или список групп пустой.", show_alert=True)
        return

    await query.answer("🚀 Рассылка запущена!")

    result = await send_bulk(config, groups,bot)
    await query.message.answer(
        f"📬 Рассылка завершена:\n✅ Успешно: <b>{result['success']}</b>\n❌ Ошибок: <b>{result['failed']}</b>",
        parse_mode="HTML"
    )

@user.callback_query(F.data == 'setlap')
async def set_lap_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🔁 *Укажите количество кругов рассылки:*\n\n"
        "— Введите число от `1` и выше\n"
        "— Или введите `∞`, чтобы сделать рассылку цикличной (условно 1000 кругов)",
        parse_mode='Markdown'
    )
    await state.set_state(ConfigState.wait_lap_count)
    await callback.answer()


@user.message(ConfigState.wait_lap_count)
async def process_lap_count(message: Message, state: FSMContext):
    input_text = message.text.strip()

    if input_text == "∞":
        lap_count = 1000
    else:
        if not input_text.isdigit():
            await message.answer("❌ Пожалуйста, введите целое число или `∞`.")
            return
        lap_count = int(input_text)
        if lap_count < 1:
            await message.answer("❌ Количество кругов должно быть не меньше 1.")
            return

    await Func.set_lap_count(lap_count)

    await message.answer(f"✅ Количество кругов установлено: {input_text}")
    await state.clear()


@user.callback_query(F.data == 'stop_manual')
async def stop_manual_sender(query: CallbackQuery, bot: Bot):
    if not state.IS_SENDING:
        await query.answer("⚠️ Сейчас нет активной рассылки.")
        return

    state.IS_SENDING = False
    await query.answer("🛑 Рассылка будет остановлена через 5-10 секунд...", show_alert=True)