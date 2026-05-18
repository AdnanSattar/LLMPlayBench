"""
Models API endpoint.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import time

from fastapi import APIRouter

from ...schemas.api_schemas import ModelInfoResponse
from ...services.model_service import list_loaded_models

router = APIRouter()


@router.get("/models", response_model=list[ModelInfoResponse])
def list_models():
    """List all available models."""
    models = list_loaded_models()

    # Convert to proper response format
    result = []
    for model in models:
        result.append(
            ModelInfoResponse(
                id=model["id"],
                object="model",
                created=int(time.time()),
                owned_by="local",
                quantization=model["quantization"],
                permission=[],
            )
        )

    return result
