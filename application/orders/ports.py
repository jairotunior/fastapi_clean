import uuid
from typing import Protocol
from src.domain.orders.entity import Order


class OrderRepositoryPort(Protocol):
    async def save(self, order: Order) -> Order: ...
    async def get(self, order_id: uuid.UUID) -> Order | None: ...
    async def list(self) -> list[Order]: ...


class UnitOfWorkPort(Protocol):
    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    order_repository: OrderRepositoryPort
