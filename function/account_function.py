from database.models import async_session
from database.models import Config, Account
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest
import os



def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner

class AccountFunc:

    @connection
    async def save_account(session, phone: str):
        account = Account(phone=phone)
        session.add(account)
        await session.commit()


    @connection 
    async def get_all_accounts(session):
        result = await session.scalars(select(Account))
        return result.all() 
    
    @connection
    async def delete_account(session, phone):
        acc = await session.scalar(select(Account).where(Account.phone == phone))
        if not acc:
            raise ValueError(f"Аккаунт {phone} не найден в базе")

        await session.delete(acc)
        await session.commit()

        # 2. Удаляем файл сессии, если он существует
        session_file = f"{phone}.session"
        if os.path.exists(session_file):
            os.remove(session_file)
            print(f"🗑 Сессия {session_file} удалена")
        else:
            print(f"⚠ Файл {session_file} не найден")