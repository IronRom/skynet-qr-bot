from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.db_requests import upsert_user

from fluentogram import TranslatorRunner
from bot.filters.filters import OwnerFilter

owner_router = Router()
owner_router.message.filter(OwnerFilter())

@owner_router.message(CommandStart())
async def cmd_start(
    message: Message,
    session: AsyncSession,
    i18n: TranslatorRunner
    ):
    answer = i18n.owner.command.start()
 
    await upsert_user(session, message.from_user.id,
                      message.from_user.first_name,
                      message.from_user.last_name)
    await message.answer(text=answer)