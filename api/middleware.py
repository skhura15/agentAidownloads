"""
API Middleware

Custom middleware for authentication, CORS, error handling, and logging.
"""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
from typing import Callable

from core.logging_service import LoggingService

logger = LoggingService.get_logger("api_middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging API requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            LoggingService.log_api_request(
                logger,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms,
                user_id=getattr(request.state, "user_id", None)
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request {request_id} failed after {duration_ms:.2f}ms: {str(e)}",
                exc_info=True
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.window_start = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Reset window if needed
        current_time = time.time()
        if current_time - self.window_start > 60:
            self.request_counts = {}
            self.window_start = current_time
        
        # Check rate limit
        if client_ip in self.request_counts:
            if self.request_counts[client_ip] >= self.requests_per_minute:
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": "60"}
                )
            self.request_counts[client_ip] += 1
        else:
            self.request_counts[client_ip] = 1
        
        # Process request
        response = await call_next(request)
        return response


def setup_cors(app):
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_middleware(app):
    """Setup all middleware"""
    # CORS
    setup_cors(app)
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # Rate limiting (optional, configure as needed)
    # app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
