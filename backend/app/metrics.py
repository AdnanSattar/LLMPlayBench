from .db import SessionLocal
from .models import RequestMetric


def save_request_metric(model, prompt, quant, latency_s, tokens, tokens_per_sec):
    db = SessionLocal()
    rec = RequestMetric(
        model=model,
        quant=quant,
        prompt=prompt[:1000],
        latency_s=latency_s,
        tokens=tokens,
        tokens_per_sec=tokens_per_sec,
    )
    db.add(rec)
    db.commit()
    db.close()


def get_recent_metrics(limit=100):
    db = SessionLocal()
    rows = (
        db.query(RequestMetric)
        .order_by(RequestMetric.created_at.desc())
        .limit(limit)
        .all()
    )
    db.close()
    return rows
