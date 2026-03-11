from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Test API"
    app_version: str = "0.1.1"
    api_v1_prefix: str = "/api/v1"
    # Optional for tests that don't hit the database
    database_url: str | None = None

    time_zone: str = "America/Bogota"

    jwt_secret_key: str = "super-secret-key"
    jwt_algorithm: str = "HS256"
    # Keycloak/OIDC: JWKS URL to verify RS256 tokens (e.g. http://localhost:9000/realms/fastapi/protocol/openid-connect/certs)
    oidc_jwks_url: str | None = None

    # OIDC / OAuth2
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    # Optional tuning
    oidc_metadata_ttl_seconds: int = 3600
    oidc_jwks_ttl_seconds: int = 3600

    class Config:
        env_file = ".env"


settings = Settings()
