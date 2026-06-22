"""OWASP-aligned HTTP response headers middleware.

Implements the headers recommended by the OWASP Secure Headers Project
(https://owasp.org/www-project-secure-headers/) for a web API serving
a React/Next.js frontend.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class OWASPHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        # Clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # HSTS — only meaningful over HTTPS, but harmless on localhost
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Permissions policy (locks down camera, mic, geolocation, etc.)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # Content Security Policy — strict for an API
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        # Cache control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response
