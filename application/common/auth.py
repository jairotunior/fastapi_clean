from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class AuthContext:
    subject: str
    email: Optional[str]
    issuer: str = None
    audience: str | list[str] = None
    scopes: set[str] = field(default_factory=set)
    roles: set[str] = field(default_factory=set)
    is_service: bool = False
