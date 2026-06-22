"""
KINZ Secure Commerce Hub — FastAPI entrypoint.

Boots the FastAPI application, wires security middleware (rate-limiter,
OWASP headers, audit logging, JWT auth), and mounts all routers under
the /api/v1 prefix.

Run locally:
    uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import logging
import os
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
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("kinz.api")

# ---------- Rate limiter ----------
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

# ---------- Audit logger ----------
audit = AuditLogger(path=settings.AUDIT_LOG_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("KINZ Secure Commerce Hub API starting up")
    audit.log("system.startup", user="system", detail=f"version={settings.APP_VERSION}")
    yield
    audit.log("system.shutdown", user="system", detail="graceful")
    logger.info("KINZ Secure Commerce Hub API shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Security-first e-commerce intelligence API for KINZ (Tunisian natural cosmetics).",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------- Middleware ----------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.add_middleware(OWASPHeadersMiddleware)


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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Never leak stack traces to the client."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Contact security@kinzoils.com."},
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
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT_API, reload=True)
