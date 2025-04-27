from fastapi import Request
from pythonjsonlogger import jsonlogger
import logging
import time
from typing import Callable
import uuid

# Configure JSON logger
logger = logging.getLogger("api")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(request_id)s %(method)s %(url)s %(status_code)s %(response_time)s %(message)s"
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

async def logging_middleware(request: Request, call_next: Callable):
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else None,
            "status_code": None,
            "response_time": None
        }
    )
    
    # Time the request
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "response_time": f"{process_time:.3f}s"
        }
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response 