from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.driven.db.sqlalchemy.session import get_db
from src.infrastructure.driven.db.sqlalchemy.uow import SqlAlchemyUnitOfWork
from src.application.orders.use_cases import (
    CreateOrderUseCase,
    GetOrderUseCase,
    ListOrdersUseCase,
)


def get_uow(session: AsyncSession = Depends(get_db)) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def create_order_uc(uow=Depends(get_uow)) -> CreateOrderUseCase:
    return CreateOrderUseCase(uow)


def get_order_uc(uow=Depends(get_uow)) -> GetOrderUseCase:
    return GetOrderUseCase(uow)


def list_orders_uc(uow=Depends(get_uow)) -> ListOrdersUseCase:
    return ListOrdersUseCase(uow)
