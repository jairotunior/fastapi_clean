from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_clean.application.orders.ports import UnitOfWorkPort
from fastapi_clean.infrastructure.driven.db.sqlalchemy.repositories import (
    SqlAlchemyOrderRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWorkPort):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repository = SqlAlchemyOrderRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
