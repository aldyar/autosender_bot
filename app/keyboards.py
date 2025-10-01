from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu(is_active: bool):
    toggle_text = "🔴 Отключить" if is_active else "🟢 Активировать"
    inline_menu = InlineKeyboardMarkup(inline_keyboard=(
        [InlineKeyboardButton(text=toggle_text, callback_data='toggle_sender'),
         InlineKeyboardButton(text = '📋 Список аккаунтов',callback_data='account_list')],
        [InlineKeyboardButton(text = '📱 Добавить аккаунт',callback_data='add_account'),
        InlineKeyboardButton(text='📝 Изменить текст', callback_data='change_text')],
        [InlineKeyboardButton(text='⏳ Изменить интервал', callback_data='change_interval'),
        InlineKeyboardButton(text='⏰ Установить время', callback_data='set_time')
        ]
    ))
    return inline_menu

back_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = '❌ Отмена')]],resize_keyboard=True)

inline_delete_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '🗑 Удалить номер', callback_data='delete_acc')]])
