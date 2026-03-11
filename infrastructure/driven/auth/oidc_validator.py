# app/adapters/driven/auth/oidc_validator.py
from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass

import httpx
import jwt

from fastapi_clean.application.common.auth import AuthContext
from fastapi_clean.domain.common.errors import AuthenticationError
from fastapi_clean.core.config import settings


# JWT = three base64url segments separated by dots
_B64URL_SEGMENT = re.compile(r"^[A-Za-z0-9_-]+$")


def _normalize_and_validate_jwt(token: str) -> str:
    """Ensure token is a string and looks like a JWT (header.payload.sig)."""
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    token = token.strip()
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthenticationError("Invalid token format: expected three segments")
    for i, part in enumerate(parts):
        if not part or not _B64URL_SEGMENT.match(part):
            raise AuthenticationError(
                f"Invalid token format: segment {i + 1} is not base64url"
            )
    return token


@dataclass
class CachedValue:
    value: dict
    expires_at: float


class OIDCValidator:
    def __init__(self) -> None:
        self._metadata_cache: CachedValue | None = None
        self._metadata_lock = asyncio.Lock()

    async def _get_metadata(self) -> dict:
        now = time.time()
        if self._metadata_cache and self._metadata_cache.expires_at > now:
            return self._metadata_cache.value

        async with self._metadata_lock:
            now = time.time()
            if self._metadata_cache and self._metadata_cache.expires_at > now:
                return self._metadata_cache.value

            url = f"{settings.oidc_issuer.rstrip('/')}/.well-known/openid-configuration"

            timeout = httpx.Timeout(5.0)
            limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)

            async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                metadata = resp.json()

            self._metadata_cache = CachedValue(
                value=metadata,
                expires_at=time.time() + settings.oidc_metadata_ttl_seconds,
            )
            return metadata

    async def validate_access_token(self, token: str) -> AuthContext:
        token = _normalize_and_validate_jwt(token)

        metadata = await self._get_metadata()
        jwks_uri = metadata["jwks_uri"]

        try:
            jwk_client = jwt.PyJWKClient(jwks_uri)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                audience=settings.oidc_audience,
                issuer=settings.oidc_issuer,
                options={
                    "require": ["exp", "iat", "iss", "sub"],
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )
        except jwt.PyJWTError as exc:
            raise AuthenticationError("Invalid or expired access token") from exc

        scopes = set((claims.get("scope") or "").split())
        roles = set()

        realm_access = claims.get("realm_access") or {}
        roles.update(realm_access.get("roles") or [])

        resource_access = claims.get("resource_access") or {}
        api_access = resource_access.get(settings.oidc_audience) or {}
        roles.update(api_access.get("roles") or [])

        client_id = claims.get("azp") or claims.get("client_id")
        subject = claims["sub"]

        return AuthContext(
            subject=subject,
            issuer=claims["iss"],
            audience=claims.get("aud", []),
            scopes=scopes,
            roles=roles,
            email=claims.get("email"),
            is_service=bool(client_id and subject == client_id),
        )
