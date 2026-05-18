from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class RequestMetric(Base):
    __tablename__ = "request_metrics"
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, index=True)
    quant = Column(String)
    prompt = Column(String)
    latency_s = Column(Float)
    tokens = Column(Integer)
    tokens_per_sec = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
