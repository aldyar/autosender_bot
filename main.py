import asyncio
from aiogram import Dispatcher, Bot
from config import TOKEN
from database.models import async_main
from function.config_function import ConFunc
from handlers.user import user
from handlers.account import user as telethon_handler
from app.asyncio_task import scheduler
from aiogram import Bot

async def main():
    bot = Bot(token=TOKEN)
    
    dp = Dispatcher()
    dp.include_routers(user,telethon_handler)
    dp.startup.register(on_startup)

    asyncio.create_task(scheduler(bot))
    await dp.start_polling(bot)


async def on_startup():
    print('✅BOT STARTED')
    await async_main()
    await ConFunc.create_config()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass