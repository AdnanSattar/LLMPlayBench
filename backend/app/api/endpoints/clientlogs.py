"""
Client logs API endpoint.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request

from ...core.logging import app_logger
from ...core.security.auth import User, get_read_user
from ...schemas.api_schemas import ClientLogRequest

router = APIRouter()


@router.post("/clientlogs")
async def save_client_log(
    log_entry: ClientLogRequest,
    request: Request,
    current_user: User = Depends(get_read_user),
):
    """
    Save client-side logs from the frontend.

    The logs are stored in the backend log files but can be
    forwarded to any log aggregation service.
    """
    # Get logger with request context
    logger = app_logger.bind(
        client_log=True,
        user=current_user.username,
        ip=request.client.host if request.client else None,
    )

    # Log at appropriate level based on client level
    level = log_entry.level.upper()
    message = f"[CLIENT LOG] {log_entry.message}"

    # Extract metadata
    meta = {k: v for k, v in log_entry.dict().items() if k not in ("level", "message")}

    if level == "ERROR":
        logger.error(message, **meta)
    elif level == "WARN" or level == "WARNING":
        logger.warning(message, **meta)
    elif level == "INFO":
        logger.info(message, **meta)
    elif level == "DEBUG":
        logger.debug(message, **meta)
    else:
        logger.trace(message, **meta)

    return {"status": "success"}
