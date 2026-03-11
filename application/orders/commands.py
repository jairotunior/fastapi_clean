from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: str
    items: list[dict]  # keep simple; could be list[OrderItemDTO]
