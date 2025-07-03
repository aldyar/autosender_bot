from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError,PhoneCodeExpiredError
from telethon.errors import RPCError
import asyncio
from telethon.errors import RPCError, ChatWriteForbiddenError, UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest
from config import ADMIN
from aiogram import Bot

# Словарь для хранения хэшей по номерам (можно заменить на FSMContext при желании)
code_hashes = {}

async def login_telegram(api_id, api_hash, phone, code=None):
    client = TelegramClient('anon_session', api_id, api_hash)
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

async def send_bulk(config, groups,bot:Bot):

    # session_ok = await is_session_active(config)
    # if not session_ok:
    #     if bot:
    #         for admin_id in ADMIN:
    #             try:
    #                 await bot.send_message(admin_id, "❌ Сессия неактивна. Войдите заново.")
    #             except Exception:
    #                 pass
    #     return {"success": 0, "failed": len(groups)}
    
    client = TelegramClient('anon_session', config.api_id, config.api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.disconnect()
        for admin_id in ADMIN:
            try:
                await bot.send_message(admin_id, "❌ Сессия неактивна. Войдите заново.")
            except Exception as e:
                print(f"Не удалось отправить сообщение админу {admin_id}: {e}")
        return {"success": 0, "failed": len(groups)}
    
    if bot:
        for admin_id in ADMIN:
            try:
                await bot.send_message(admin_id, "⏳ *Началась рассылка...*", parse_mode="Markdown")
            except Exception as e:
                print(f"❌ Ошибка при отправке уведомления админу {admin_id}: {e}")

    success, failed = 0, 0

    try:
        for group in groups:
            try:
                # первая попытка отправить сообщение
                await client.send_message(group.name, config.text, parse_mode='html')
                success += 1
            except ChatWriteForbiddenError:
                # если нет прав на отправку — пробуем вступить
                try:
                    await client(JoinChannelRequest(group.name))
                    await asyncio.sleep(1)  # подождём немного после вступления
                    await client.send_message(group.name, config.text, parse_mode='html')
                    success += 1
                except (RPCError, Exception):
                    failed += 1
            except RPCError:
                failed += 1

            await asyncio.sleep(config.interval or 2)
    finally:
        await client.disconnect()

    return {"success": success, "failed": failed}


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
