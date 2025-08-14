import asyncio

from config import Config, load_config
from bot.bot import main
from bot.database.models.db_requests import init_owner
from bot.database.init_db import create_engine_and_session, init_db
from sqlalchemy.ext.asyncio import AsyncSession

config: Config = load_config()

async def startup():
    config = load_config()
    engine, session_factory = await create_engine_and_session(config)
    await(init_db(engine, config=config))    
    await(init_owner(session_factory=session_factory, telegram_ids=config.bot.owner_ids))
    await(main(config, session_factory))

asyncio.run(startup())