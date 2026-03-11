from datetime import datetime, timedelta, timezone
from jwt import encode
from fastapi_clean.core.config import settings


class JwtTokenIssuer:
    def create_access_token(
        self, subject: str, email: str, roles: list[str], scopes: list[str]
    ) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "email": email,
            "roles": roles,
            "scopes": scopes,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
        }
        return encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )
