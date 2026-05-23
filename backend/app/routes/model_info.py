"""Expose the trained-model metadata so the dashboard can render the
confusion matrix + feature importances."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..detection.scorer import _load_model

router = APIRouter()


@router.get("/api/model/info")
def model_info():
    bundle = _load_model()
    if not bundle:
        raise HTTPException(503, "model not trained yet — run `python -m ml.train`")
    return {
        "feature_names": bundle["feature_names"],
        "confusion": bundle["confusion"],
        "report": bundle["report"],
        "feature_importances": bundle["feature_importances"],
    }
