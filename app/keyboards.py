from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(keyboard=([KeyboardButton(text = '📝 Текст рассылки'),
                                           KeyboardButton(text = '📂 Группы для рассылки')],
                                           [KeyboardButton(text = '⏱ Интервал между сообщениями'),
                                            KeyboardButton(text = '🕰 Время старта')],
                                            [KeyboardButton(text = '👤 Аккаунт Telegram'),
                                             KeyboardButton(text = '📤 Рассылка')]),resize_keyboard=True)


group_inline = InlineKeyboardMarkup(inline_keyboard=([InlineKeyboardButton(text = 'Добавить группу',callback_data='SetGroup')],
                                                     [InlineKeyboardButton(text = 'Удалить группу', callback_data= 'DeleteGroup')]))


def sender_menu(is_active: bool) -> InlineKeyboardMarkup:
    toggle_text = "🔴 Отключить" if is_active else "🟢 Активировать"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=toggle_text, callback_data='toggle_sender')],
        [InlineKeyboardButton(text='🚀 Запустить рассылку', callback_data='start_manual'),
         InlineKeyboardButton(text = "⏹️ Остановить", callback_data= 'stop_manual')],
        [InlineKeyboardButton(text = '🔄 Круги', callback_data='setlap')]
    ])

back_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = '❌ Отмена')]],resize_keyboard=True)