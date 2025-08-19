from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import create_engine

from bot.handlers.user import user_router
from bot.handlers.owner import owner_router
from bot.handlers.user import start_dialog, qr_generation_dialog

from fluentogram import TranslatorHub

from config import Config, load_config
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.middlewares.db_session import DbSessionMiddleware
from bot.middlewares.i18n import TranslatorRunnerMiddleware
from bot.middlewares.middleware_config import ConfigMiddleware

from bot.utils.i18n import create_translator_hub

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import Redis

##### comment for commit
async def main(
        config: Config,
        session_factory: async_sessionmaker
        ) -> None:
    
    if config.redis.use_redis:
        redis = Redis(host=config.redis.redis_host)
        storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    else:
        storage = MemoryStorage()
    translator_hub: TranslatorHub = create_translator_hub()
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)
    dp.update.middleware(ConfigMiddleware(config))
    dp.update.outer_middleware(DbSessionMiddleware(session_factory=session_factory))
    dp.update.middleware(TranslatorRunnerMiddleware())
    dp.include_routers(owner_router)
    dp.include_routers(user_router)
    dp.include_routers(start_dialog)
    dp.include_routers(qr_generation_dialog)
    setup_dialogs(dp)

    await dp.start_polling(bot, _translator_hub=translator_hub)