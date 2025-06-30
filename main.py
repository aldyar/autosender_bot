import asyncio
from aiogram import Dispatcher, Bot
from config import TOKEN
from handlers.user import user 
from handlers.user_text import user as user_text
from handlers.user_groups import user as user_groups
from handlers.user_time import user as user_time
from database.models import async_main
from database.requests import Func

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(user, user_text, user_groups, user_time)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

async def on_startup(bot:Bot):
    print('✅BOT STARTED')
    await async_main()
    await Func.create_config()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass