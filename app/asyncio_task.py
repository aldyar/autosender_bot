import asyncio
import datetime
from telethon import TelegramClient
from database.models import Account, Config
from function.config_function import ConFunc
from function.account_function import AccountFunc
from config import API_HASH, API_ID
from aiogram import Bot
from config import ADMIN
from function.custom_parser import CustomHTML

# --- функция рассылки от одного аккаунта ---
async def send_from_account(acc, text, interval):
    session_file = f"{acc.phone}.session"
    client = TelegramClient(session_file, API_ID, API_HASH)
    client.parse_mode = CustomHTML()
    await client.start()
    print(f"[{acc.phone}] Клиент запущен")

    success_count = 0
    fail_count = 0
    failed_groups = []

    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await client.send_message(dialog.id, text, parse_mode='HTML')
                print(f"[{acc.phone}] → {dialog.name}")
                success_count += 1
                await asyncio.sleep(interval)
            except Exception as e:
                error_text = str(e)
                print(f"[{acc.phone}] Ошибка в {dialog.name}: {error_text}")
                fail_count += 1
                failed_groups.append(f"{dialog.name} (@{getattr(dialog.entity, 'username', 'нет username')}): {error_text}")

    await client.disconnect()

    # Возвращаем статистику
    return {
        "phone": acc.phone,
        "success": success_count,
        "fail": fail_count,
        "failed_groups": failed_groups
    }


# --- функция, которая запускает рассылку со всех аккаунтов ---
async def start_broadcast(config, accounts,bot:Bot):
    tasks = [asyncio.create_task(send_from_account(acc, config.text, float(config.interval)))
             for acc in accounts]

    results = await asyncio.gather(*tasks)

    # Формируем красивый отчёт
    report = "📊 <b>Отчёт по рассылке:</b>\n\n"
    for res in results:
        report += f"📱 <b>{res['phone']}</b>\n"
        report += f"✅ Отправлено: {res['success']}\n"
        report += f"❌ Ошибок: {res['fail']}\n"
        if res['failed_groups']:
            report += "⚠ Не удалось отправить в:\n"
            for g in res['failed_groups']:
                report += f"• {g}\n"   # убрал лишний @
        report += "\n"

    # Отправка отчёта по кускам
    MAX_LENGTH = 4000
    for admin_id in ADMIN:
        try:
            if len(report) > MAX_LENGTH:
                for i in range(0, len(report), MAX_LENGTH):
                    await bot.send_message(chat_id=admin_id,text=report[i:i+MAX_LENGTH],parse_mode='HTML')
            else:
                await bot.send_message(chat_id=admin_id,text=report,parse_mode='HTML')
        except Exception as e:
            print(f"❌ Не удалось отправить сообщение админу {admin_id}: {e}")
    #return report


# --- "следилка за временем" ---
async def scheduler(bot:Bot):
    while True:
        now = datetime.datetime.now().strftime("%H:%M")

        # берём активный конфиг
        config = await ConFunc.get_config()

        if config and now == config.time:  # если время совпало
            print(f"⏰ Наступило время {config.time}, начинаем рассылку...")
            # Отправка отчёта всем админам

            for admin_id in ADMIN:
                try:
                    await bot.send_message(chat_id=admin_id, text='🚀 Рассылка запущена')
                except Exception as e:
                    print(f"❌ Не удалось отправить сообщение админу {admin_id}: {e}")

            # берём все аккаунты
            accounts = await AccountFunc.get_all_accounts()

            if accounts:
                await start_broadcast(config, accounts,bot)
            else:
                print("⚠️ Нет аккаунтов для рассылки")

            # ждём минуту, чтобы не запустить повторно в ту же минуту
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(10)  # проверка каждые 10 сек

