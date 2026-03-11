"""Pytest fixtures and overrides for fastapi_clean tests."""

import pytest
from fastapi.testclient import TestClient

from fastapi_clean.main import app
from fastapi_clean.core import config as config_module
from fastapi_clean.infrastructure.driven.auth import jwt_service as jwt_service_module
from fastapi_clean.infrastructure.driven.auth.jwt_service import JwtTokenValidator
from fastapi_clean.infrastructure.driving.api.v1.security import get_oidc_validator


def _get_token_validator():
    """Use JWT validator with HS256 (login-issued tokens) in tests."""
    return JwtTokenValidator()


@pytest.fixture(scope="session")
def client():
    """Test client with auth validator override so login-issued tokens work in tests."""
    # Force HS256 validation: disable OIDC so JwtTokenValidator does not use JWKS
    old_jwks_url = getattr(config_module.settings, "oidc_jwks_url", None)
    old_issuer = getattr(config_module.settings, "oidc_issuer", None)
    config_module.settings.oidc_jwks_url = None
    config_module.settings.oidc_issuer = None
    jwt_service_module._jwks_client = None

    app.dependency_overrides[get_oidc_validator] = _get_token_validator
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
        config_module.settings.oidc_jwks_url = old_jwks_url
        config_module.settings.oidc_issuer = old_issuer
        jwt_service_module._jwks_client = None
