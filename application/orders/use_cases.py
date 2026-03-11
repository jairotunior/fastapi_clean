import uuid
from datetime import datetime
from fastapi_clean.application.common.auth import AuthContext
from fastapi_clean.domain.orders.entity import Order, OrderItem
from fastapi_clean.application.orders.ports import UnitOfWorkPort
from fastapi_clean.application.orders.commands import CreateOrderCommand
from fastapi_clean.domain.orders.errors import OrderNotFoundError


class CreateOrderUseCase:
    def __init__(self, uow: UnitOfWorkPort):
        self.uow = uow

    async def execute(self, cmd: CreateOrderCommand, auth: AuthContext) -> Order:
        if "orders:write" not in auth.scopes:
            raise PermissionError("Not allowed to create orders")

        order = Order(
            id=uuid.uuid4(),
            customer_id=cmd.customer_id,
            items=[
                OrderItem(
                    sku=item["sku"],
                    quantity=item["quantity"],
                )
                for item in cmd.items
            ],
            status="created",
            created_at=datetime.now(),
        )
        await self.uow.order_repository.save(order)
        await self.uow.commit()
        return order


class GetOrderUseCase:
    def __init__(self, uow: UnitOfWorkPort):
        self.uow = uow

    async def execute(self, order_id: uuid.UUID, auth: AuthContext) -> Order | None:
        order = await self.uow.order_repository.get(order_id)
        if not order:
            raise OrderNotFoundError

        if "orders:read" not in auth.scopes and order.customer_id != auth.subject:
            raise PermissionError("Not allowed to access this order")

        return order


class ListOrdersUseCase:
    def __init__(self, uow: UnitOfWorkPort):
        self.uow = uow

    async def execute(self, auth: AuthContext) -> list[Order]:
        if "orders:read" not in auth.scopes:
            raise PermissionError("Not allowed to list orders")

        return await self.uow.order_repository.list()
