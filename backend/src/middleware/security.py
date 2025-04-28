from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from typing import Callable, Dict, Optional
from starlette.types import ASGIApp
import time
from config import settings
import logging
from datetime import datetime, timedelta
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Bỏ qua xác thực và rate limit cho tất cả API
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self' https:;"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )

        return response

    async def cleanup_expired_entries(self):
        """Xóa các bản ghi rate limit hết hạn"""
        current_time = datetime.now()
        expired = current_time - timedelta(seconds=self.window_seconds)
        
        removed = 0
        for ip in list(self.clients.keys()):
            if self.clients[ip]["window_start"] <= expired:
                del self.clients[ip]
                removed += 1
        
        if removed > 0:
            logger.info(f"Đã xóa {removed} bản ghi rate limit hết hạn")

def setup_security_middleware(app: FastAPI) -> None:
    """Setup all security related middleware"""
    
    # Session
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET_KEY,
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,  # Convert to seconds
    )
    
    # Security Headers
    app.add_middleware(SecurityMiddleware)
    
    # Trusted Hosts
    if settings.is_production():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure with your domain
        ) 