"""Role-based access control dependencies."""
from __future__ import annotations

from typing import Literal

from fastapi import Depends, Header, HTTPException, status
from jwt import PyJWTError

from src.api.security.jwt_handler import verify_token

Role = Literal["viewer", "analyst", "admin"]


def _extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.split(" ", 1)[1].strip()


def current_user(authorization: str | None = Header(default=None)) -> dict:
    """Decode the JWT and return its claims. Raises 401 on any failure."""
    token = _extract_token(authorization)
    try:
        claims = verify_token(token)
    except PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc.__class__.__name__}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    # Defense in depth: reject tokens whose role is not in the allowed set,
    # even if the signature is valid (catches legacy tokens issued before
    # role validation was added).
    if claims.get("role") not in ("viewer", "analyst", "admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has an invalid role claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return claims


def require_role(*allowed: Role):
    """Dependency factory: require the JWT role to be one of `allowed`."""

    def _checker(claims: dict = Depends(current_user)) -> dict:
        if claims.get("role") not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed)}",
            )
        return claims

    return _checker
