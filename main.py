from fastapi import FastAPI, Query, Path
from typing import Annotated
from fastapi_clean.core.config import settings
from fastapi_clean.infrastructure.driving.api.v1.schemas.orders import OrderItem
from fastapi_clean.infrastructure.driving.api.v1.routes.orders import router as orders_router
from fastapi_clean.infrastructure.driving.api.v1.routes.auth import router as auth_router

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("health", tags=["health"], include_in_schema=False)
async def health():
    return {"status": "ok"}


app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(orders_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 0):
    return {"skip": skip, "limit": limit}


@app.post("/items/")
async def create_item(item: OrderItem):
    return item


@app.get("/items/{item_id}")
# async def read_item(item_id: int, q: str | None = None, short: bool = False):
# async def read_item(item_id: int, q: str | None = Query(default=None, max_length=50), short: bool = False):
# async def read_item(item_id: int, q: Annotated[List[str] | None, Query(min_length=3, max_length=50, pattern="^[a-z]+$")] = None, short: bool = False):
async def read_item(
    item_id: Annotated[int, Path(title="The ID of the item", ge=1, le=1000000)],
    q: Annotated[
        str | None,
        Query(
            alias="item-query",
            title="Query String",
            min_length=3,
            description="Query string for the item",
            max_length=50,
            pattern="^[a-z]+$",
            deprecated=True,
            # include_in_schema=False
        ),
    ] = None,
    short: bool = False,
):
    item = {"item_id": item_id}
    if q:
        item.update({"item_id": item_id, "q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "user_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: OrderItem):
    return {"item_id": item_id, "item": item.name}
