from typing import Protocol
from fastapi_clean.application.common.auth import AuthContext


class TokenValidatorPort(Protocol):
    async def validate_token(self, token: str) -> AuthContext: ...
