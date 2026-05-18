"""
FastAPI middleware.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..logging import app_logger, get_request_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging with detailed information."""

    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate a unique ID for this request
        request_id = str(uuid.uuid4())

        # Create a contextualized logger for this request
        log = get_request_logger(request_id)

        # Start timer
        start_time = time.time()

        # Extract request details
        path = request.url.path
        method = request.method
        client_host = request.client.host if request.client else "unknown"

        # Add request ID to headers
        request.state.request_id = request_id

        # Log the incoming request
        log.info(
            "Request started: {} {}",
            method,
            path,
            client=client_host,
            path=path,
            method=method,
        )

        try:
            # Process the request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log the successful response
            log.info(
                "Request completed: {} {} - Status: {} - Time: {:.3f}s",
                method,
                path,
                response.status_code,
                process_time,
                status_code=response.status_code,
                duration=process_time,
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate processing time
            process_time = time.time() - start_time

            # Log the exception
            log.exception(
                "Request failed: {} {} - Error: {} - Time: {:.3f}s",
                method,
                path,
                str(e),
                process_time,
                duration=process_time,
                error=str(e),
            )

            # Re-raise the exception for FastAPI to handle
            raise
