# app/adapters/driven/db/sqlalchemy/repositories.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_clean.application.orders.ports import OrderRepositoryPort
from fastapi_clean.domain.orders.entity import Order, OrderItem
from fastapi_clean.infrastructure.driven.db.sqlalchemy.models import Order as OrderModel


def _item_to_domain(i: dict) -> OrderItem:
    # DB stores "qty", domain uses "quantity"
    return OrderItem(sku=i["sku"], quantity=i.get("quantity", i.get("qty", 0)))


def to_domain(m: OrderModel) -> Order:
    return Order(
        id=m.id,
        customer_id=m.customer_id,
        items=[_item_to_domain(i) for i in m.items],
        status=m.status,
        created_at=m.created_at,
    )


def to_model(o: Order) -> OrderModel:
    return OrderModel(
        id=o.id,
        customer_id=o.customer_id,
        items=[{"sku": i.sku, "qty": i.quantity} for i in o.items],
        status=o.status,
        created_at=o.created_at,
    )


class SqlAlchemyOrderRepository(OrderRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, order: Order) -> Order:
        self.session.add(to_model(order))
        await self.session.flush()  # get ID etc. if needed
        return order

    async def get(self, order_id: UUID) -> Order | None:
        res = await self.session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        m = res.scalar_one_or_none()
        return to_domain(m) if m else None

    async def list(self) -> list[Order]:
        res = await self.session.execute(
            select(OrderModel).order_by(OrderModel.created_at.desc())
        )
        return [to_domain(m) for m in res.scalars().all()]
