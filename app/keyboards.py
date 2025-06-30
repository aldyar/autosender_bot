from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(keyboard=([KeyboardButton(text = '📝 Текст рассылки'),
                                           KeyboardButton(text = '📂 Группы для рассылки')],
                                           [KeyboardButton(text = '⏱ Интервал между сообщениями'),
                                            KeyboardButton(text = '🕰 Время старта')],
                                            [KeyboardButton(text = '👤 Аккаунт Telegram'),
                                             KeyboardButton(text = '📤 Рассылка')]),resize_keyboard=True)


group_inline = InlineKeyboardMarkup(inline_keyboard=([InlineKeyboardButton(text = 'Добавить группу',callback_data='SetGroup')],
                                                     [InlineKeyboardButton(text = 'Удалить группу', callback_data= 'DeleteGroup')]))