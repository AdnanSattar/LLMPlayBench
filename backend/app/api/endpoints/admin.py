"""
Admin API endpoints.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...core.security.auth import User, get_admin_user
from ...services.cache_service import clear_cache_pattern
from ...services.model_service import list_loaded_models, load_model, unload_model

router = APIRouter(tags=["Admin"])


@router.post("/admin/reload_model")
async def reload_model(
    model_name: Annotated[
        str,
        Query(
            description="Hugging Face model id to load",
            examples=["google/flan-t5-small"],
        ),
    ],
    quantization: Annotated[
        str,
        Query(
            description="Quantization hint (kept for compatibility; CPU-safe load)",
            examples=["int8"],
        ),
    ] = "int8",
    current_user: User = Depends(get_admin_user),
):
    """
    Admin endpoint to reload a specific model.

    This first unloads the model if it exists, then loads it again.

    Suggested models:
    - google/flan-t5-small
    - HuggingFaceTB/SmolLM2-135M-Instruct
    - google/gemma-3-270m

    curl examples:
    - curl -X POST "http://localhost:8000/v1/admin/reload_model?model_name=google/flan-t5-small&quantization=int8" -H "X-API-Key: admin_api_key_replace_in_production"
    - curl -X POST "http://localhost:8000/v1/admin/reload_model?model_name=HuggingFaceTB/SmolLM2-135M-Instruct&quantization=int8" -H "X-API-Key: admin_api_key_replace_in_production"
    - curl -X POST "http://localhost:8000/v1/admin/reload_model?model_name=google/gemma-3-270m&quantization=int8" -H "X-API-Key: admin_api_key_replace_in_production"
    """
    # First try to unload (will be a no-op if model isn't loaded)
    unload_result = unload_model(model_name, quantization)

    try:
        # Then load the model
        tokenizer, model = load_model(model_name, quantization)
        return {
            "status": "success",
            "message": f"Model {model_name} ({quantization}) has been reloaded",
            "device": str(model.device),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload model: {str(e)}",
        )


@router.delete("/admin/unload_model")
async def admin_unload_model(
    model_name: Annotated[
        str,
        Query(
            description="Hugging Face model id to unload",
            examples=["google/flan-t5-small"],
        ),
    ],
    quantization: Annotated[
        str,
        Query(description="Quantization hint", examples=["int8"]),
    ] = "int8",
    current_user: User = Depends(get_admin_user),
):
    """Admin endpoint to unload a specific model from memory."""
    result = unload_model(model_name, quantization)

    if result:
        # Invalidate metrics cache when unloading a model
        try:
            clear_cache_pattern("model_metrics:*")
        except Exception:
            pass
        return {
            "status": "success",
            "message": f"Model {model_name} ({quantization}) has been unloaded",
        }
    else:
        return {
            "status": "not_found",
            "message": f"Model {model_name} ({quantization}) was not loaded",
        }


@router.post("/admin/clear_caches")
async def clear_caches(current_user: User = Depends(get_admin_user)):
    """Clear Redis caches for metrics and model responses."""
    try:
        cleared_metrics = clear_cache_pattern("model_metrics:*")
        cleared_responses = clear_cache_pattern("model_response:*")
        return {
            "status": "success",
            "message": "Caches cleared",
            "cleared_metrics": int(cleared_metrics or 0),
            "cleared_responses": int(cleared_responses or 0),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear caches: {str(e)}",
        )
