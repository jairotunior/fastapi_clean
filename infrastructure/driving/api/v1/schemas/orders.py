import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, List


class OrderItem(BaseModel):
    sku: str = Field(description="The stock keeping unit of the item")
    quantity: int = Field(description="The quantity of the item", ge=1)


class OrderCreate(BaseModel):
    customer_id: str = Field(
        description="The ID of the customer", min_length=1, max_length=64
    )
    items: list[OrderItem]


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # SQLAlchemy -> Pydantic

    id: uuid.UUID
    customer_id: str
    items: List[OrderItem]
    status: Literal["created", "paid", "cancelled"]
    created_at: datetime
