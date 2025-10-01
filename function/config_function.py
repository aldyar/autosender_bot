from database.models import async_session
from database.models import Config
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest



def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


class ConFunc:

    @connection
    async def get_config(session):
        config = await session.scalar(select(Config))
        if config:
            return config
        

    @connection
    async def create_config(session):
        config = await session.scalar(select(Config))
        if config:
            return
        new_config = Config()
        session.add(new_config)
        await session.commit()


    @connection
    async def set_active_status(session, is_active: bool):
        config = await session.scalar(select(Config))
        if config:
            config.is_active = is_active
            await session.commit()

    @connection
    async def set_text(session,text):
        config = await session.scalar(select(Config))
        config.text = text
        await session.commit()

    
    @connection
    async def set_interval(session, value: float):
        config = await session.scalar(select(Config))
        config.interval = value
        await session.commit()


    @connection
    async def set_time(session, value: str):
        config = await session.scalar(select(Config))
        config.time = value
        await session.commit()

    
    