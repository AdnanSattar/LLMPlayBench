"""
Schemas for API request/response models.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ResponseRequest(BaseModel):
    """Request schema for /v1/response endpoint."""

    model: str = Field(..., description="Model identifier")
    prompt: str = Field(..., description="Input prompt text")
    max_tokens: Optional[int] = Field(128, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    quantization: Optional[str] = Field(
        "int8", description="Quantization level (int8, int4, none)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "model": "google/flan-t5-small",
                "prompt": "Explain quantum computing in simple terms",
                "max_tokens": 128,
                "temperature": 0.7,
                "quantization": "int8",
            }
        }
    }


class ResponseChoice(BaseModel):
    """Individual response choice."""

    text: str = Field(..., description="Generated text")
    index: int = Field(0, description="Choice index")
    finish_reason: str = Field("stop", description="Reason for finish")


class UsageInfo(BaseModel):
    """Token usage information."""

    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    response_tokens: int = Field(..., description="Number of tokens in the response")
    total_tokens: int = Field(..., description="Total tokens used")


class ResponseResponse(BaseModel):
    """Response schema for /v1/response endpoint."""

    id: str = Field(..., description="Response ID")
    object: str = Field("response", description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[ResponseChoice] = Field(..., description="Generated choices")
    usage: UsageInfo = Field(..., description="Token usage statistics")


class ModelInfoResponse(BaseModel):
    """Model information response."""

    id: str = Field(..., description="Model identifier")
    object: str = Field("model", description="Object type")
    created: Optional[int] = Field(None, description="Creation timestamp")
    owned_by: str = Field("owner", description="Model owner")
    quantization: Optional[str] = Field(None, description="Quantization level")
    permission: List[Dict[str, str]] = Field(
        default_factory=list, description="Permissions"
    )


class BenchmarkInfoResponse(BaseModel):
    """Model benchmark information."""

    avg_time: float = Field(..., description="Average inference time in seconds")
    avg_tokens: float = Field(..., description="Average tokens generated")
    tokens_per_sec: float = Field(..., description="Tokens per second")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    device: str = Field("cuda", description="Device used for inference")


class MetricsRequest(BaseModel):
    """Request schema for fetching metrics."""

    model: Optional[str] = Field(None, description="Filter by model")
    from_timestamp: Optional[int] = Field(None, description="Start timestamp")
    to_timestamp: Optional[int] = Field(None, description="End timestamp")
    limit: Optional[int] = Field(100, description="Limit results")


class MetricEntry(BaseModel):
    """Single metrics entry."""

    id: str = Field(..., description="Metric ID")
    timestamp: int = Field(..., description="Timestamp")
    model: str = Field(..., description="Model name")
    latency_s: float = Field(..., description="Latency in seconds")
    tokens: int = Field(..., description="Tokens generated")
    tokens_per_sec: float = Field(..., description="Tokens per second")
    quantization: str = Field(..., description="Quantization level")
    prompt_length: int = Field(..., description="Prompt length in characters")


class MetricsResponse(BaseModel):
    """Response schema for metrics endpoint."""

    metrics: List[MetricEntry] = Field(..., description="Metrics entries")
