from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.utils.text_decorations import html_decoration
from config import API_ID,API_HASH
from function.config_function import ConFunc
from function.account_function import AccountFunc
from app.state import ConfigState
from function.telethon import Telethon
from app.asyncio_task import start_broadcast
from function.custom_parser import CustomHTML, CustomMarkdown
from telethon import TelegramClient

user = Router()


@user.callback_query(F.data == 'add_account')
async def add_phone(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer("📱 Введите <b>номер телефона</b> в формате +XXXXXXXXXXX:", parse_mode="HTML")
    await state.set_state(ConfigState.wait_phone)
    await callback.answer()


@user.message(ConfigState.wait_phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())

    data = await state.get_data()

    status, client = await Telethon.login_telegram(API_ID, API_HASH, data['phone'])

    if status == 'code_required':
        await state.update_data(client=client)
        await message.answer("✉️ Введите <b>код подтверждения</b> из Telegram:", parse_mode="HTML")
        await state.set_state(ConfigState.wait_code)
    elif status == 'email_required':
        await message.answer("❌ Аккаунт требует подтверждение через email и не может быть использован для бота.")
        await state.clear()
    else:
        await message.answer("❌ Ошибка при подключении. Попробуй снова.")
        await state.clear()


@user.message(ConfigState.wait_code)
async def get_code(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data['phone']
    status, _ = await Telethon.login_telegram(
        API_ID, API_HASH, data['phone'],
        code=message.text.strip()
    )

    if status == 'ok':
        await AccountFunc.save_account(phone)
        await message.answer("✅ Аккаунт успешно сохранён и авторизован!")
        await state.clear()
    elif status == 'invalid_code':
        await message.answer("❌ Неверный код. Попробуй снова.")
    else:
        await message.answer("❌ Ошибка. Авторизация не удалась.")
        await state.clear()


@user.callback_query(F.data == 'account_list')
async def account_list(callback:CallbackQuery,state:FSMContext):
    accounts = await AccountFunc.get_all_accounts()  # получаем список номеров

    if not accounts:
        await callback.answer("❌ Нет добавленных номеров")
        return

    # Если нужны только телефоны
    text = "📱 Список номеров:\n\n"
    text += "\n".join(f"• `{acc.phone}`" for acc in accounts)

    await callback.message.answer(text,parse_mode='Markdown',reply_markup=kb.inline_delete_button)
    await callback.answer()

@user.callback_query(F.data == 'delete_acc')
async def delete_account(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    await callback.message.answer('*Введите пожалуйста номер который хотите удалить*',parse_mode='Markdown')
    await state.set_state(ConfigState.delete_account)


@user.message(ConfigState.delete_account)
async def process_delete(message:Message,state:FSMContext):
    acc = message.text
    try:
        await AccountFunc.delete_account(acc)
        await message.answer(f"✅ Аккаунт {acc} и его сессия удалены")
    except Exception as e:
        await message.answer(f"❌ Не удалось удалить аккаунт {acc}\nОшибка: {e}")
    
    await state.clear()
    print('зашел')


########################################################################################################################
########################################################################################################################
########################################################################################################################


@user.message(F.text == 'test')
async def test(message:Message):
    config = await ConFunc.get_config()
    accounts = await AccountFunc.get_all_accounts()
    print('дошел сюда')
    task = await start_broadcast(config,accounts)
    #await message.answer(task, parse_mode="HTML")



@user.message(F.text == 'tele')
async def test(message: Message):
    # --- вручную указываем данные ---
    API_ID = 123          # <- твой API_ID
    API_HASH = '123' # <- твой API_HASH
    SESSION = '+123.session'   # <- имя файла сессии (создастся .session)

    # Создаем Telethon клиент
    client = TelegramClient(SESSION, API_ID, API_HASH)
    client.parse_mode = CustomHTML()  # подключаем кастомный Markdown

    await client.start()
    print("Telethon client started")

    #await client(JoinChannelRequest('@autosenderr2'))
    # Текст с кастомным эмодзи и спойлером
    text = """
<b>Устал искать карты?</b><b><tg-emoji emoji-id="5393498271073185899">🧐</tg-emoji></b><b>
Их уже не нужно искать, у нас всё есть!!!</b><tg-emoji emoji-id="5255881578969574929">👍</tg-emoji>

<u>Дебетовые карты под:</u>
<tg-emoji emoji-id="5224257782013769471">💰</tg-emoji>Белое
<tg-emoji emoji-id="5224257782013769471">💰</tg-emoji>Серое
<tg-emoji emoji-id="5224257782013769471">💰</tg-emoji>Черное

<tg-emoji emoji-id="5267300544094948794">💳</tg-emoji><b>Премиум Сбербанк </b>
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Сбер
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> ВТБ 
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Т-Банк 
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Альфа банк 
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Газпром
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Райффайзен
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Промсвязь
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Совком
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Зенит
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> АК Барс
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> МТС
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Почта банк 
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Уралсиб
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Россельхоз

<b>Комплектация:</b>
- Банковская карта 
- Сим-карта
- Доступ к личному кабинету 
- Паспорт/регистрация 
- Кодовое слово
- Пин код

<i>... так же можно приобрести отдельно ЛК (без дебетовки)</i>
"""
    text2 = """
<b>test</b>
<i>test</i>
<blockquote>test</blockquote>
<pre>test</pre>
"""
    # Отправка в личный чат "me"
    await client.send_message('@autosenderr2', text)
    print("Message sent!")

    await client.disconnect()
    await message.answer("✅ Тестовое сообщение отправлено через Telethon!")





@user.message(F.text =='antest')
async def anum_test(message:Message):
    text = """
<b>Устал искать карты?</b><b><tg-emoji emoji-id="5393498271073185899">🧐</tg-emoji></b><b>
Их уже не нужно искать, у нас всё есть!!!</b><tg-emoji emoji-id="5255881578969574929">👍</tg-emoji>

<u>Дебетовые карты под:</u>
<tg-emoji emoji-id="5224257782013769471">💰</tg-emoji>Белое
<tg-emoji emoji-id="5224257782013769471">💰</tg-emoji>Серое
<tg-emoji emoji-id="5224257782013769471">💰</tg-emoji>Черное

<tg-emoji emoji-id="5267300544094948794">💳</tg-emoji><b>Премиум Сбербанк </b>
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Сбер
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> ВТБ 
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Т-Банк 
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Альфа банк 
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Газпром
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Райффайзен
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Промсвязь
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Совком
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Зенит
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> АК Барс
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> МТС
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Почта банк 
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Уралсиб
<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> Россельхоз

<b>Комплектация:</b>
- Банковская карта 
- Сим-карта
- Доступ к личному кабинету 
- Паспорт/регистрация 
- Кодовое слово
- Пин код

<i>... так же можно приобрести отдельно ЛК (без дебетовки)</i>
"""


    # Отправляем
    await message.answer(text,parse_mode='HTML')