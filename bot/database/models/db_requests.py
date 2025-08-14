from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy import select
from bot.database.models import User
from bot.database.models import Actions

async def init_owner(
        session_factory,
        telegram_ids: list[int]
):
    async with session_factory() as session:
        for user_id in telegram_ids:
            stmt = upsert(User).values(
                telegram_id=user_id,
                first_name=None,
                last_name=None,
                is_owner=True,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=['telegram_id'],
                set_={"is_owner": True},
            )
            await session.execute(stmt)
        await session.commit()

async def upsert_user(
    session: AsyncSession,
    telegram_id: int,
    first_name: str,
    last_name: str | None = None,
):
    stmt = upsert(User).values(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,            
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=['telegram_id'],
        set_=dict(
            first_name=first_name,
            last_name=last_name,
        ),
    )
    await session.execute(stmt)
    await session.commit()

async def upsert_actions(session: AsyncSession, telegram_id: int, qr_request: str):
    stmt = upsert(Actions).values(
        telegram_id=telegram_id,
        qr_request=qr_request
    )
    await session.execute(stmt)
    await session.commit()

async def is_owner(session: AsyncSession, telegram_id: int) -> bool:
    stmt = select(User.is_owner).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    owner_flag = result.scalar_one_or_none()
    return owner_flag is True