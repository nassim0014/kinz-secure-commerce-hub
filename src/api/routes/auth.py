"""Authentication routes: login, whoami.

Demo mode (DEMO_USER_ENABLED=true):
    Credentials are read from env vars DEMO_USER_EMAIL and
    DEMO_USER_PASSWORD_HASH. The password hash MUST be a real bcrypt
    hash (60 chars, $2b$...). Generate one with:
        python -c "import bcrypt; print(bcrypt.hashpw(b'YOUR_PASSWORD', bcrypt.gensalt(rounds=12)).decode())"

Production mode (DEMO_USER_ENABLED=false):
    Disable the demo user and back auth with a real Postgres user store.
"""
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


def _get_demo_user() -> dict | None:
    """Return the demo user record, or None if demo mode is disabled."""
    if not settings.DEMO_USER_ENABLED:
        return None
    if not settings.DEMO_USER_PASSWORD_HASH:
        # Misconfiguration: demo mode enabled but no hash set.
        # Fail closed — no demo login possible.
        return None
    return {
        "email": settings.DEMO_USER_EMAIL,
        "password_hash": settings.DEMO_USER_PASSWORD_HASH,
        "role": settings.DEMO_USER_ROLE,
        "name": settings.DEMO_USER_NAME,
    }


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(payload: LoginRequest, request: Request) -> TokenResponse:
    """Exchange email + password for a JWT."""
    audit = get_audit_logger()
    ip = get_remote_address(request)

    demo_user = _get_demo_user()
    if demo_user is None:
        # Don't reveal whether demo mode is on or off — same error as bad creds.
        audit.log("auth.login_failed", user=payload.email, ip=ip, detail="demo_disabled_or_misconfigured")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if payload.email.lower() != demo_user["email"].lower() or not verify_password(
        payload.password, demo_user["password_hash"]
    ):
        audit.log("auth.login_failed", user=payload.email, ip=ip, detail="bad_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = issue_token(subject=demo_user["email"], role=demo_user["role"])
    audit.log("auth.login_success", user=demo_user["email"], ip=ip)
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
        "issuer": claims.get("iss"),
        "audience": claims.get("aud"),
        "jti": claims.get("jti"),
    }
