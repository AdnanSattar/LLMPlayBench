"""
Database models for SQLAlchemy.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import time

from sqlalchemy import Boolean, Column, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RequestMetric(Base):
    """Request metrics model."""

    __tablename__ = "request_metrics"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, index=True, unique=True)
    timestamp = Column(Integer, default=lambda: int(time.time()))
    model = Column(String, index=True)
    prompt = Column(Text)
    prompt_length = Column(Integer)
    response = Column(Text)
    latency_s = Column(Float)
    tokens = Column(Integer)
    tokens_per_sec = Column(Float)
    quantization = Column(String)
    benchmarked = Column(Boolean, default=True, index=True)
    temperature = Column(Float, nullable=True)
    top_p = Column(Float, nullable=True)
    top_k = Column(Integer, nullable=True)
    system_prompt = Column(Text, nullable=True)

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": self.request_id,
            "timestamp": self.timestamp,
            "model": self.model,
            "latency_s": self.latency_s,
            "tokens": self.tokens,
            "tokens_per_sec": self.tokens_per_sec,
            "quantization": self.quantization,
            "benchmarked": self.benchmarked,
            "prompt_length": self.prompt_length,
            "prompt": self.prompt,
            "response": self.response,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "system_prompt": self.system_prompt,
        }
