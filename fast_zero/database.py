from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.settings import settings

engine = create_async_engine(settings.DATABASE_URL)


async def get_session():
    """Returns a session"""
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
