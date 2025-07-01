from database.requests import Func
from app.telethon import send_bulk
from aiogram import Bot
import aiocron
import asyncio
from config import ADMIN
import datetime

# async def scheduled_sender(bot: Bot):
#     config = await Func.get_config()

#     if not config or not config.is_active:
#         print("⛔️ Рассылка неактивна или нет конфига")
#         return

#     groups = await Func.get_groups()
#     if not groups:
#         print("⚠️ Нет групп для рассылки")
#         return

#     result = await send_bulk(config, groups)

#     await bot.send_message(
#         chat_id= ADMIN,  # если хочешь получать отчёт в ЛС
#         text=f"📤 Рассылка завершена:\n✅ Успешно: {result['success']}\n❌ Ошибки: {result['failed']}"
#     )

# async def schedule_cron(bot: Bot):
#     config = await Func.get_config()
#     if not config or not config.time:
#         print("⚠️ Время рассылки не указано.")
#         return

#     hour, minute = map(int, config.time.split(':'))
#     cron_expr = f'{minute} {hour} * * *'

#     aiocron.crontab(cron_expr, func=lambda: asyncio.create_task(scheduled_sender(bot)))
#     print(f"📆 Рассылка назначена: каждый день в {hour:02}:{minute:02}")

async def run_scheduler(bot: Bot):
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        config = await Func.get_config()

        if config and config.is_active and config.time == now:
            groups = await Func.get_groups()

            if groups:
                result = await send_bulk(config, groups,bot)

                report_text = (
                    f"📤 Рассылка завершена:\n"
                    f"✅ Успешно: {result['success']}\n"
                    f"❌ Ошибки: {result['failed']}"
                )
            else:
                report_text = "⚠️ Нет групп для рассылки."

            # Отправка отчёта всем админам
            admin_ids = ADMIN if isinstance(ADMIN, list) else [ADMIN]
            for admin_id in admin_ids:
                try:
                    await bot.send_message(admin_id, report_text)
                except Exception as e:
                    print(f"❌ Не удалось отправить сообщение админу {admin_id}: {e}")

            await asyncio.sleep(60)  # чтобы не повторилось в ту же минуту

        await asyncio.sleep(1)