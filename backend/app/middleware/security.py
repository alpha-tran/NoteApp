from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
from ..config import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        if settings.SECURITY_HEADERS:
            # HSTS
            if settings.is_production():
                response.headers["Strict-Transport-Security"] = f"max-age={settings.HSTS_SECONDS}; includeSubDomains"
            
            # Frame options
            if settings.FRAME_DENY:
                response.headers["X-Frame-Options"] = "DENY"
            
            # XSS protection
            if settings.XSS_PROTECTION:
                response.headers["X-XSS-Protection"] = "1; mode=block"
            
            # Content type options
            if settings.CONTENT_TYPE_NOSNIFF:
                response.headers["X-Content-Type-Options"] = "nosniff"
            
            # Additional security headers
            response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            if settings.is_production():
                response.headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "font-src 'self' data: https:; "
                    "connect-src 'self' https:; "
                    "frame-ancestors 'none';"
                )
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests
        self.requests = {ip: reqs for ip, reqs in self.requests.items() 
                        if current_time - reqs[-1] < 60}
        
        # Check rate limit
        if client_ip in self.requests:
            requests = self.requests[client_ip]
            if len(requests) >= settings.RATE_LIMIT_PER_MINUTE:
                if current_time - requests[0] < 60:
                    return Response(
                        content="Rate limit exceeded",
                        status_code=429
                    )
                self.requests[client_ip] = requests[1:] + [current_time]
            else:
                self.requests[client_ip].append(current_time)
        else:
            self.requests[client_ip] = [current_time]
        
        return await call_next(request)

def setup_security_middleware(app: FastAPI) -> None:
    """Setup all security related middleware"""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Session
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET_KEY,
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,  # Convert to seconds
    )
    
    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate Limiting
    app.add_middleware(RateLimitMiddleware)
    
    # Trusted Hosts
    if settings.is_production():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure with your domain
        ) 