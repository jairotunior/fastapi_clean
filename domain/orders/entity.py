import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=False)
class OrderItem:
    sku: str
    quantity: int


@dataclass
class Order:
    id: uuid.UUID
    customer_id: str
    items: list[dict]
    status: str
    created_at: datetime
