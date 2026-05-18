"""
Benchmarks API endpoint.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

from fastapi import APIRouter

from ...core.config import settings
from ...core.logging import get_request_logger
from ...schemas.api_schemas import BenchmarkInfoResponse
from ...services.benchmark_service import benchmark_model
from ...services.model_service import load_model

router = APIRouter()


@router.get("/benchmarks", response_model=BenchmarkInfoResponse)
def get_benchmark(model: str, quantization: str = "int8"):
    """Run benchmark on specified model."""
    logger = get_request_logger(None)
    tokenizer, model_obj = load_model(model, quantization)
    logger.info("Running benchmark", model=model, quantization=quantization)
    bench = benchmark_model(
        tokenizer,
        model_obj,
        "Hello",
        settings.MAX_NEW_TOKENS,
        temperature=None,
    )
    logger.info(
        "Benchmark completed",
        model=model,
        avg_time=bench["avg_time"],
        avg_tokens=bench["avg_tokens"],
        tokens_per_sec=bench["tokens_per_sec"],
        device=bench["device"],
    )
    return bench
