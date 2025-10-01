from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from sqlalchemy.ext.asyncio import AsyncAttrs,async_sessionmaker,create_async_engine,AsyncSession

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3',echo=False)

async_session = async_sessionmaker(engine,class_=AsyncSession)

class Base(AsyncAttrs,DeclarativeBase):
    pass

class Config(Base):
    __tablename__ ='config'

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text:Mapped[str] = mapped_column(String, nullable=True)
    time:Mapped[str] = mapped_column(String, nullable=True)
    interval:Mapped[str] = mapped_column(String, nullable=True)
    is_active:Mapped[int] = mapped_column(Integer, default=1)


class Account(Base):
    __tablename__ = 'acoounts'

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone:Mapped[str] = mapped_column(String, nullable=True)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)