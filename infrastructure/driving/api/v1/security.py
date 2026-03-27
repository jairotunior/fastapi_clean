from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_clean.application.common.auth import AuthContext
from fastapi_clean.domain.common.errors import AuthenticationError
from fastapi_clean.infrastructure.driven.auth.jwt_service import JwtTokenValidator
from fastapi_clean.infrastructure.driven.auth.oidc_validator import OIDCValidator

bearer_scheme = HTTPBearer(auto_error=True)


def get_token_validator() -> JwtTokenValidator:
    return JwtTokenValidator()


def get_oidc_validator() -> OIDCValidator:
    return OIDCValidator()


async def get_current_auth(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    validator: JwtTokenValidator = Depends(get_oidc_validator),
) -> AuthContext:
    token = credentials.credentials

    try:
        return await validator.validate_access_token(token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


def require_scope(required_scope: str):
    async def checker(auth: AuthContext = Depends(get_current_auth)) -> AuthContext:
        if required_scope not in auth.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {required_scope}",
            )
        return auth

    return checker
