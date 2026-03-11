from fastapi import APIRouter, Depends, HTTPException, status, Security
from uuid import UUID
from fastapi_clean.infrastructure.driving.api.v1.schemas.orders import OrderCreate, OrderOut
from fastapi_clean.infrastructure.driving.api.v1.security import get_current_auth, require_scope
from fastapi_clean.application.common.auth import AuthContext
from fastapi_clean.application.orders.commands import CreateOrderCommand
from fastapi_clean.application.orders.use_cases import (
    CreateOrderUseCase,
    GetOrderUseCase,
    ListOrdersUseCase,
)
from fastapi_clean.domain.orders.errors import OrderNotFoundError
from fastapi_clean.infrastructure.driving.api.v1.deps import (
    create_order_uc,
    get_order_uc,
    list_orders_uc,
)


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    auth: AuthContext = Depends(get_current_auth),
    uc: CreateOrderUseCase = Depends(create_order_uc),
):
    cmd = CreateOrderCommand(
        customer_id=payload.customer_id, items=[i.model_dump() for i in payload.items]
    )
    return await uc.execute(cmd, auth)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: UUID,
    auth: AuthContext = Security(require_scope("orders:read")),
    uc: GetOrderUseCase = Depends(get_order_uc),
):
    try:
        return await uc.execute(order_id, auth)
    except OrderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("", response_model=list[OrderOut])
async def list_orders(
    auth: AuthContext = Security(require_scope("orders:read")),
    uc: ListOrdersUseCase = Depends(list_orders_uc),
):
    return await uc.execute(auth)
