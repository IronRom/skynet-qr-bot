from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.database.models.db_requests import is_owner
from sqlalchemy.ext.asyncio import AsyncSession

class OwnerFilter(BaseFilter):
    async def __call__(self, message: Message, **data) -> bool:
        session = data.get("session")
        return await is_owner(session=session, telegram_id=message.from_user.id)