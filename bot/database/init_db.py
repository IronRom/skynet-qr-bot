from config import Config
from bot.database import models
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

async def create_engine_and_session(config: Config):
    engine = create_async_engine(config.db.dsn)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return engine, session_factory

async def init_db(engine, config: Config):
    async with engine.begin() as connection:
        await connection.run_sync(models.Base.metadata.drop_all)
        await connection.run_sync(models.Base.metadata.create_all)

