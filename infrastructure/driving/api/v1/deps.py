from typing import Annotated

from fastapi import Depends
from fastapi_clean.application.orders.use_cases import (
    CreateOrderUseCase,
    GetOrderUseCase,
    ListOrdersUseCase,
)
from fastapi_clean.infrastructure.driven.db.sqlalchemy.session import get_db
from fastapi_clean.infrastructure.driven.db.sqlalchemy.uow import SqlAlchemyUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession

SharedDbResource = Depends(get_db)


def get_uow(session: AsyncSession = SharedDbResource) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def create_order_uc(
    uow=Annotated[SqlAlchemyUnitOfWork, SharedDbResource],
) -> CreateOrderUseCase:
    return CreateOrderUseCase(uow)


def get_order_uc(
    uow=Annotated[SqlAlchemyUnitOfWork, SharedDbResource],
) -> GetOrderUseCase:
    return GetOrderUseCase(uow)


def list_orders_uc(
    uow=Annotated[SqlAlchemyUnitOfWork, SharedDbResource],
) -> ListOrdersUseCase:
    return ListOrdersUseCase(uow)
