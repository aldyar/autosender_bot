from database.models import async_session
from database.models import Config, Group
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


class Func:

    @connection
    async def create_config(session):
        config = await session.scalar(select(Config))
        if config:
            return
        new_config = Config()
        session.add(new_config)
        await session.commit()


    @connection
    async def set_text(session,text):
        config = await session.scalar(select(Config))
        config.text = text
        await session.commit()


    @connection
    async def get_text(session):
        config = await session.scalar(select(Config))
        if config.text:
            return config.text
        elif not config.text:
            return False
        
    @connection
    async def get_groups(session):
        result = await session.scalars(select(Group))
        groups = result.all()
        return groups
    
    @connection
    async def add_groups(session, group_names: list[str]):
        for name in group_names:
            session.add(Group(name=name.strip()))
        await session.commit()

    @connection
    async def delete_groups(session, group_names: list[str]):
        await session.execute(
            delete(Group).where(Group.name.in_(group_names))
        )
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