"""
Response API endpoint.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import os
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ...core.logging import get_request_logger
from ...core.security.auth import User, get_read_user
from ...schemas.api_schemas import ResponseRequest, ResponseResponse
from ...services.benchmark_service import benchmark_model
from ...services.metrics_service import save_request_metric
from ...services.model_service import generate_response, load_model

router = APIRouter()


@router.post("/response", response_model=ResponseResponse)
def response_endpoint(
    req: ResponseRequest, request: Request, current_user: User = Depends(get_read_user)
):
    """Generate a response from the model."""
    from ...core.config import settings

    # Get logger for this request
    logger = get_request_logger(getattr(request.state, "request_id", None))

    model_name = req.model
    quant = req.quantization or "int8"
    max_tokens = req.max_tokens or settings.MAX_NEW_TOKENS

    logger.info(
        "Processing generation request",
        model=model_name,
        quantization=quant,
        max_tokens=max_tokens,
        temperature=req.temperature,
        prompt_length=len(req.prompt),
        system_prompt_len=len(req.system_prompt) if req.system_prompt else 0,
        username=current_user.username,
    )

    try:
        # Load model
        logger.debug("Loading model {}", model_name)
        tokenizer, model = load_model(model_name, quant)

        # Run benchmark (opt-in via query param benchmark=true or env RESPONSE_BENCH)
        do_bench = request.query_params.get("benchmark")
        should_bench = (do_bench and str(do_bench).lower() == "true") or getattr(
            settings, "RESPONSE_BENCH", False
        )
        logger.debug("Running benchmark for model {}", model_name)
        bench_start = time.time()
        bench = (
            benchmark_model(
                tokenizer, model, req.prompt, max_tokens, temperature=req.temperature
            )
            if should_bench
            else {
                "avg_time": 0.0,
                "avg_tokens": 0.0,
                "tokens_per_sec": 0.0,
                "memory_usage_mb": 0.0,
                "device": str(model.device),
            }
        )
        bench_duration = time.time() - bench_start

        avg_time, avg_tokens, tps = (
            bench["avg_time"],
            bench["avg_tokens"],
            bench["tokens_per_sec"],
        )

        if should_bench:
            logger.info(
                "Benchmark completed for {}",
                model_name,
                avg_time=avg_time,
                avg_tokens=avg_tokens,
                tokens_per_sec=tps,
                benchmark_duration=bench_duration,
            )

        # Generate final response
        logger.debug("Generating final response")
        gen_start = time.time()
        text = generate_response(
            tokenizer,
            model,
            req.prompt,
            max_tokens,
            temperature=req.temperature,
            system_prompt=req.system_prompt,
            top_p=req.top_p,
            top_k=req.top_k,
            model_name=model_name,
            quantization=quant,
            use_cache=getattr(settings, "USE_REDIS_CACHE", True),
        )
        gen_duration = time.time() - gen_start

        logger.info(
            "Response generated successfully",
            generation_time=gen_duration,
            output_length=len(text),
        )

        # Persist metric with generation parameters only if benchmarking was done
        # This prevents 0.000s latency records from cluttering the dashboard
        if should_bench:
            save_request_metric(
                model=model_name,
                prompt=req.prompt,
                quant=quant,
                latency_s=avg_time,
                tokens=int(avg_tokens),
                tokens_per_sec=tps,
                response=text,
                temperature=req.temperature,
                top_p=getattr(req, "top_p", 0.9),
                top_k=getattr(req, "top_k", 50),
                system_prompt=req.system_prompt,
                benchmarked=True,
            )

        # Create response object
        resp_id = f"resp-{int(time.time()*1000)}"
        resp = ResponseResponse(
            id=resp_id,
            object="response",
            created=int(time.time()),
            model=model_name,
            choices=[{"text": text, "index": 0, "finish_reason": "stop"}],
            usage={
                "prompt_tokens": len(req.prompt.split()),
                "response_tokens": int(avg_tokens),
                "total_tokens": len(req.prompt.split()) + int(avg_tokens),
            },
        )

        logger.info("Request completed successfully", response_id=resp_id)

        return resp

    except Exception as e:
        logger.exception(
            "Error generating response: {}", str(e), model=model_name, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}",
        )
