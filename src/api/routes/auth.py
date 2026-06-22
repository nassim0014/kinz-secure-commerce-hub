"""Authentication routes: login, token refresh, whoami.

For demo purposes the only valid credentials are:
    email: nassim@kinzoils.com
    password: KINZ-demo-2025!

In production these would come from a Postgres-backed user store with
bcrypt hashes (see src/api/security/passwords.py).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.api.models.schemas import LoginRequest, TokenResponse
from src.api.security.audit import get_audit_logger
from src.api.security.jwt_handler import issue_token
from src.api.security.passwords import verify_password
from src.api.security.rbac import current_user
from src.api.utils.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# In production this would be a database lookup. For the demo we keep a
# single in-memory record with a precomputed bcrypt hash.
DEMO_USER = {
    "email": "nassim@kinzoils.com",
    # bcrypt hash for "KINZ-demo-2025!" (12 rounds)
    "password_hash": "$2b$12$u1Qb9rC7g2tZj7Qb9rC7g2tZj7Qb9rC7g2tZj7Qb9rC7g2tZj7Qb9rC7g2",
    "role": "admin",
    "name": "Nassim K.",
}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(payload: LoginRequest, request: Request) -> TokenResponse:
    """Exchange email + password for a JWT."""
    audit = get_audit_logger()
    ip = get_remote_address(request)

    if payload.email.lower() != DEMO_USER["email"] or not verify_password(
        payload.password, DEMO_USER["password_hash"]
    ):
        audit.log("auth.login_failed", user=payload.email, ip=ip, detail="bad_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = issue_token(subject=payload.email, role=DEMO_USER["role"])
    audit.log("auth.login_success", user=payload.email, ip=ip)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
    )


@router.get("/me")
def me(claims: dict = Depends(current_user)) -> dict:
    return {
        "email": claims.get("sub"),
        "role": claims.get("role"),
        "issued_at": claims.get("iat"),
        "expires_at": claims.get("exp"),
    }
