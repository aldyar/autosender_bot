from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError,PhoneCodeExpiredError
from telethon.errors import RPCError
import asyncio
from telethon.errors import RPCError, ChatWriteForbiddenError, UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest


code_hashes = {}

class Telethon:
    

    async def login_telegram(api_id, api_hash, phone, code=None):
        client = TelegramClient(phone, api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            if code is None:
                sent = await client.send_code_request(phone)

                # 🔎 Для отладки печатаем всё, что вернулось
                print("=== SEND CODE REQUEST ===")
                print("Type:", sent.type)           # Куда придёт (app, sms, call)
                print("Timeout:", sent.timeout)     # Секунд до следующей попытки
                print("Phone hash:", sent.phone_code_hash)

                if type(sent.type).__name__ == 'SentCodeTypeSetUpEmailRequired':
                    # Аккаунт заблокирован для обычного входа
                    print(f"❌ Аккаунт {phone} требует подтверждение через email. Нельзя авторизовать.")
                    await client.disconnect()
                    return "email_required", None  # или client, если нужно хранить

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
            except Exception as e:
                print("Unexpected error:", e)
                return "unexpected_error", client

        await client.disconnect()  # пока закомментируем
        return "ok", client
