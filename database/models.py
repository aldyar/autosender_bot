from sqlalchemy import String, BigInteger, DateTime, Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs,async_sessionmaker,create_async_engine,AsyncSession


engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=False)

async_session = async_sessionmaker(engine,class_=AsyncSession)

class Base(AsyncAttrs,DeclarativeBase):
    pass

class Config(Base):
    __tablename__ = 'config'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    api_id: Mapped[int] = mapped_column(Integer, nullable=True)
    api_hash: Mapped[str] = mapped_column(String, nullable=True)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(String, nullable=True)
    time: Mapped[str] = mapped_column(String, nullable=True)
    interval: Mapped[float] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=True)  


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)