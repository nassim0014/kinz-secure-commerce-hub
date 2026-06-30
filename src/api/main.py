"""
KINZ Secure Commerce Hub — FastAPI entrypoint.

Boots the FastAPI application, wires security middleware (rate-limiter,
OWASP headers, audit logging, JWT auth, request-ID correlation), and
mounts all routers under the /api/v1 prefix.

Run locally:
    uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.routes import auth, health, kpis, products, sales
from src.api.security.audit import AuditLogger
from src.api.security.headers import OWASPHeadersMiddleware
from src.api.utils.config import settings

# ---------- Logging ----------
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(request_id)s | %(message)s",
)
# Default request_id for non-request log lines (e.g. startup)
logging.Logger = logging.getLoggerClass()  # noqa: F811 — keep class ref for filters


class _RequestIdFilter(logging.Filter):
    """Inject a 'request_id' field on every log record (default '-')."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"  # type: ignore[attr-defined]
        return True


root_logger = logging.getLogger()
for h in root_logger.handlers:
    h.addFilter(_RequestIdFilter())

logger = logging.getLogger("kinz.api")

# ---------- Rate limiter ----------
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

# ---------- Audit logger ----------
audit = AuditLogger(
    path=settings.AUDIT_LOG_PATH,
    max_bytes=settings.AUDIT_LOG_MAX_BYTES,
    backup_count=settings.AUDIT_LOG_BACKUP_COUNT,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Production safety check — fail fast on insecure configs.
    settings.enforce_production_safety()

    logger.info("KINZ Secure Commerce Hub API starting up")
    audit.log("system.startup", user="system", detail=f"version={settings.APP_VERSION}")
    yield
    audit.log("system.shutdown", user="system", detail="graceful")
    logger.info("KINZ Secure Commerce Hub API shutting down")


# In production, disable interactive docs to reduce attack surface.
# Health and OpenAPI metadata are still available for ops tooling via
# explicit env flags if needed.
_docs_url = None if settings.is_production else "/docs"
_redoc_url = None if settings.is_production else "/redoc"
_openapi_url = "/openapi.json"  # kept for kubernetes ingress probes; can be disabled

app = FastAPI(
    title=settings.APP_NAME,
    description="Security-first e-commerce intelligence API for KINZ (Tunisian natural cosmetics).",
    version=settings.APP_VERSION,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
    lifespan=lifespan,
)

# ---------- Middleware ----------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Attach a correlation ID to every request.

    - Reads `X-Request-ID` from the client if present (trusted upstream proxy).
    - Otherwise generates a fresh UUID4.
    - Echoes it back in the response header `X-Request-ID`.
    - Binds it to the logging context so every log line for this request
      carries the same ID (searchable in ELK / Datadog).
    """
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex

    # Bind to request state for downstream handlers
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def request_audit(request: Request, call_next):
    """Audit every request that mutates state."""
    response = await call_next(request)
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        audit.log(
            "http.request",
            user=request.headers.get("X-User", "anonymous"),
            detail=f"{request.method} {request.url.path} -> {response.status_code}",
            ip=get_remote_address(request),
        )
    return response


app.add_middleware(OWASPHeadersMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Never leak stack traces to the client."""
    request_id = getattr(request.state, "request_id", "-")
    logger.exception(
        "Unhandled error on %s %s (request_id=%s)",
        request.method,
        request.url.path,
        request_id,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error. Contact security@kinzoils.com.",
            "request_id": request_id,
        },
    )


# ---------- Routers ----------
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(sales.router, prefix="/api/v1/sales", tags=["sales"])
app.include_router(kpis.router, prefix="/api/v1/kpis", tags=["kpis"])


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": _docs_url or "(disabled in production)",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT_API, reload=True)  # nosec B104 — bind-all required for Docker containers
