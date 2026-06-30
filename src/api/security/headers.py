"""OWASP-aligned HTTP response headers middleware.

Implements the headers recommended by the OWASP Secure Headers Project
(https://owasp.org/www-project-secure-headers/) for a web API serving
a React/Next.js frontend.

Includes the newer CORP/COEP/COOP trio that hardens the API against
Spectre-style side-channel attacks and cross-origin document isolation.
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
        # HSTS — only meaningful over HTTPS, but harmless on localhost.
        # 2 years + preload + includeSubDomains per OWASP recommendation.
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
        # Referrer policy — only leak origin, not full URL or path.
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Permissions policy — lock down camera, mic, geolocation, etc.
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        # Content Security Policy — strict for an API (no inline, no frames).
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )
        # Cross-Origin isolation headers — defense against Spectre-class
        # side-channel attacks. The API returns JSON only, so CORP/COEP
        # are safe to enable.
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        # DNS prefetch control — disable to prevent information leakage.
        response.headers["X-DNS-Prefetch-Control"] = "off"
        # Cache control for API responses — never cache authenticated responses.
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response
