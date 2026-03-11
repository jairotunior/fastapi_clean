import logging

from fastapi import HTTPException, status
from jwt import (
    InvalidAlgorithmError,
    PyJWKClient,
    PyJWKClientConnectionError,
    PyJWKClientError,
    PyJWTError,
    decode,
)

from src.application.common.auth import AuthContext
from src.core.config import settings

logger = logging.getLogger(__name__)


def _keycloak_claims_to_auth_context(payload: dict) -> AuthContext:
    """Map Keycloak/OIDC token claims to AuthContext."""
    subject = payload.get("sub")
    email = payload.get("email") or payload.get("preferred_username")
    # Realm roles
    realm = payload.get("realm_access") or {}
    roles: list[str] = list(realm.get("roles") or [])
    # Optional: add resource_access roles for the main client
    resource = payload.get("resource_access") or {}
    for _client, access in resource.items():
        if isinstance(access, dict) and "roles" in access:
            roles.extend(access.get("roles") or [])
    # Scopes: Keycloak puts space-separated scope in 'scope' claim
    scope_str = payload.get("scope") or ""
    scopes = scope_str.split() if isinstance(scope_str, str) else []
    return AuthContext(
        subject=subject,
        email=email,
        roles=roles,
        scopes=scopes,
        is_service=False,
    )


def _payload_to_auth_context(payload: dict) -> AuthContext:
    """Map generic JWT payload to AuthContext (HS256 / custom tokens)."""
    subject = payload.get("sub")
    email = payload.get("email")
    roles = list(payload.get("roles") or [])
    scopes = list(payload.get("scopes") or [])
    return AuthContext(
        subject=subject,
        email=email,
        roles=roles,
        scopes=scopes,
        is_service=False,
    )


_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient | None:
    global _jwks_client
    if settings.oidc_jwks_url and _jwks_client is None:
        _jwks_client = PyJWKClient(settings.oidc_jwks_url, cache_jwk_set=True)
    return _jwks_client


class JwtTokenValidator:
    @property
    def _jwks_client(self) -> PyJWKClient | None:
        return _get_jwks_client()

    async def validate_access_token(self, token: str) -> AuthContext:
        logger.info("Validating token: %s", token)
        try:
            jwks = self._jwks_client
            if jwks is not None:
                # Keycloak/OIDC: verify with RS256 using JWKS
                signing_key = jwks.get_signing_key_from_jwt(token)
                payload = decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    options={"verify_signature": True},
                )
                auth = _keycloak_claims_to_auth_context(payload)
            else:
                # Local/HS256: verify with shared secret
                payload = decode(
                    token,
                    settings.jwt_secret_key,
                    algorithms=[settings.jwt_algorithm.strip().upper()],
                    options={"verify_signature": True},
                )
                auth = _payload_to_auth_context(payload)

            if not auth.subject:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject",
                )
            logger.info("Subject: %s", auth.subject)
            return auth

        except InvalidAlgorithmError as e:
            logger.warning("Token algorithm not allowed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: algorithm not allowed",
            ) from e
        except (PyJWKClientConnectionError, PyJWKClientError) as e:
            logger.warning("JWKS key fetch failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service temporarily unavailable",
            ) from e
        except PyJWTError as e:
            logger.warning("JWT validation failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from e
