from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError,PhoneCodeExpiredError
from telethon.errors import RPCError
import asyncio
from telethon.errors import RPCError, ChatWriteForbiddenError, UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest
from config import ADMIN
from aiogram import Bot
import app.state

# Словарь для хранения хэшей по номерам (можно заменить на FSMContext при желании)
code_hashes = {}

async def login_telegram(api_id, api_hash, phone, code=None):
    client = TelegramClient(phone, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        if code is None:
            sent = await client.send_code_request(phone)
            # Сохраняем phone_code_hash
            code_hashes[phone] = sent.phone_code_hash
            return "code_required", client

        phone_code_hash = code_hashes.get(phone)
        if not phone_code_hash:
            return "missing_hash", client

        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        except PhoneCodeInvalidError:
            return "invalid_code", client
        except PhoneCodeExpiredError:
            return "code_expired", client
        except Exception:
            return "unexpected_error", client

    return "ok", client


# async def send_bulk(config, groups):
#     client = TelegramClient('anon_session', config.api_id, config.api_hash)
#     await client.connect()

#     if not await client.is_user_authorized():
#         return {"success": 0, "failed": len(groups)}

#     success, failed = 0, 0

#     for group in groups:
#         try:
#             await client.send_message(group.name, config.text, parse_mode='html')
#             success += 1
#         except RPCError:
#             failed += 1
#         await asyncio.sleep(config.interval or 2)

#     await client.disconnect()
#     return {"success": success, "failed": failed}

async def send_bulk(config, groups, bot: Bot):
    # if app.state.IS_SENDING:
    #     print("⚠️ Рассылка уже идёт. Повторный запуск невозможен.")
    #     return {"success": 0, "failed": 0}

    app.state.IS_SENDING = True  # включаем флаг

    client = TelegramClient(config.phone, config.api_id, config.api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.disconnect()
        app.state.IS_SENDING = False  # сброс флага
        for admin_id in ADMIN:
            try:
                await bot.send_message(admin_id, "❌ Сессия неактивна. Войдите заново.")
            except Exception as e:
                print(f"Не удалось отправить сообщение админу {admin_id}: {e}")
        return {"success": 0, "failed": len(groups)}

    if bot:
        for admin_id in ADMIN:
            try:
                await bot.send_message(admin_id, f"⏳ *Началась рассылка...*\nКоличество кругов: {config.lap_count}", parse_mode="Markdown")
            except Exception as e:
                print(f"❌ Ошибка при отправке уведомления админу {admin_id}: {e}")

    total_success, total_failed = 0, 0

    try:
        for lap in range(1, (config.lap_count or 1) + 1):
            if not app.state.IS_SENDING:
                print("🛑 Рассылка остановлена перед кругом.")
                break

            success, failed = 0, 0
            for group in groups:
                if not app.state.IS_SENDING:
                    print("🛑 Рассылка остановлена во время цикла.")
                    break

                try:
                    await client.send_message(group.name, config.text, parse_mode='html')
                    success += 1
                except ChatWriteForbiddenError:
                    try:
                        await client(JoinChannelRequest(group.name))
                        await asyncio.sleep(1)
                        await client.send_message(group.name, config.text, parse_mode='html')
                        success += 1
                    except (RPCError, Exception):
                        failed += 1
                except RPCError:
                    failed += 1

                await asyncio.sleep(config.interval or 2)

            total_success += success
            total_failed += failed

            if bot:
                for admin_id in ADMIN:
                    try:
                        await bot.send_message(admin_id, f"✅ Круг {lap} завершён. Успешно: {success}, Неудач: {failed}")
                    except Exception as e:
                        print(f"Не удалось отправить сообщение админу {admin_id}: {e}")

            await asyncio.sleep(3)

    finally:
        app.state.IS_SENDING = False  # всегда сбрасываем флаг
        await client.disconnect()

    return {"success": total_success, "failed": total_failed}


    # # Финальное сообщение
    # if bot:
    #     for admin_id in ADMIN:
    #         try:
    #             await bot.send_message(admin_id, f"🎯 Рассылка завершена.\nВсего успешных: {total_success}\nВсего неудачных: {total_failed}")
    #         except Exception as e:
    #             print(f"Не удалось отправить сообщение админу {admin_id}: {e}")





# async def is_session_active(config) -> bool:
#     try:
#         client = TelegramClient("anon_session", config.api_id, config.api_hash)
#         await client.connect()

#         if not await client.is_user_authorized():
#             await client.disconnect()
#             return False

#         # Пробуем получить информацию о себе
#         await client.get_me()
#         await client.disconnect()
#         return True

#     except RPCError:
#         return False
#     except Exception:
#         return False
    

async def is_session_active(config) -> bool:
    try:
        client = TelegramClient(config.phone, config.api_id, config.api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            await client.disconnect()
            return False

        await client.get_me()
        await client.disconnect()
        return True

    except Exception as e:
        print(f"[Session Check Error] {e}")
        return False
