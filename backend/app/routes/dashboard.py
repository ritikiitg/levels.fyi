"""Dashboard read API — feeds the React dashboard."""
from __future__ import annotations

from fastapi import APIRouter

from ..db import recent_requests, verdict_counts

router = APIRouter()


@router.get("/api/dashboard/feed")
def feed(limit: int = 200):
    return recent_requests(limit)


@router.get("/api/dashboard/summary")
def summary(window_seconds: int = 3600):
    counts = verdict_counts(window_seconds)
    total = sum(counts.values()) or 1
    return {
        "window_seconds": window_seconds,
        "counts": counts,
        "rates": {k: round(v / total, 4) for k, v in counts.items()},
        "total": total,
    }
