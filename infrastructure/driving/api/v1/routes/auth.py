from fastapi import APIRouter, HTTPException, status
from src.infrastructure.driven.auth.token_issuer import JwtTokenIssuer
from src.infrastructure.driving.api.v1.schemas.auth import LoginIn, TokenOut


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn):
    if payload.username != "jairo" or payload.password != "1234":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    issuer = JwtTokenIssuer()
    token = issuer.create_access_token(
        subject="user-123",
        email="jairo@example.com",
        roles=["user"],
        scopes=["orders:read", "orders:write"],
    )
    return TokenOut(access_token=token)
