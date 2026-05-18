"""
Model benchmarking service.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import os
import statistics
import time

import psutil
import torch

from ..core.config import settings
from ..core.logging import app_logger
from .model_service import generate_response


def benchmark_model(
    tokenizer, model, prompt, max_tokens, num_runs=3, temperature: float | None = None
):
    """
    Benchmark model performance.

    Args:
        tokenizer: HuggingFace tokenizer
        model: HuggingFace model
        prompt: Text prompt to use for benchmarking
        max_tokens: Maximum tokens to generate
        num_runs: Number of benchmark runs to average
        temperature: Temperature for generation (optional)

    Returns:
        Dictionary with benchmark results
    """
    app_logger.info(
        "Starting model benchmark",
        prompt_length=len(prompt),
        max_tokens=max_tokens,
        num_runs=num_runs,
        temperature=temperature,
    )
    times = []
    token_counts = []

    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_mem = process.memory_info().rss / 1024 / 1024  # MB
    app_logger.debug("Initial memory usage", memory_mb=initial_mem)

    # Optionally skip if disabled
    if not getattr(settings, "RESPONSE_BENCH", False):
        num_runs = 1

    # Perform multiple runs
    for run_idx in range(num_runs):
        app_logger.debug("Benchmark run", run=run_idx + 1, total_runs=num_runs)

        # Measure generation time
        start_time = time.time()
        text = generate_response(tokenizer, model, prompt, max_tokens, temperature)
        end_time = time.time()

        # Calculate token count (approximate)
        token_count = len(text.split())

        # Record metrics
        elapsed = end_time - start_time
        times.append(elapsed)
        token_counts.append(token_count)
        app_logger.debug(
            "Run completed",
            run=run_idx + 1,
            elapsed=elapsed,
            tokens=token_count,
            tokens_per_sec=token_count / elapsed if elapsed > 0 else 0,
        )

    # Get peak memory usage
    final_mem = process.memory_info().rss / 1024 / 1024  # MB
    mem_used = final_mem - initial_mem

    # Calculate averages
    avg_time = statistics.mean(times)
    avg_tokens = statistics.mean(token_counts)
    tokens_per_sec = avg_tokens / avg_time if avg_time > 0 else 0

    # Get device info
    device = str(model.device)

    result = {
        "avg_time": avg_time,
        "avg_tokens": avg_tokens,
        "tokens_per_sec": tokens_per_sec,
        "memory_usage_mb": mem_used,
        "device": device,
    }

    app_logger.info(
        "Benchmark completed",
        avg_time=avg_time,
        avg_tokens=avg_tokens,
        tokens_per_sec=tokens_per_sec,
        memory_mb=mem_used,
        device=device,
    )

    return result
