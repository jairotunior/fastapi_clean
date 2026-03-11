from typing import Protocol
from src.application.common.auth import AuthContext


class TokenValidatorPort(Protocol):
    async def validate_token(self, token: str) -> AuthContext: ...
