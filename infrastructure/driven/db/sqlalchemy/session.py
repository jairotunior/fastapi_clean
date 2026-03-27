from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastapi_clean.core.config import settings

engine = create_async_engine(settings.database_url, echo=True, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
