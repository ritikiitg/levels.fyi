"""Suspicion scorer. Phase-3 version is rule-only; in Phase 5 we'll add
the trained ML model and blend its probability with these rules."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import joblib  # type: ignore
except Exception:  # pragma: no cover
    joblib = None

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"
_model_bundle: dict | None = None


def _load_model() -> dict | None:
    global _model_bundle
    if _model_bundle is not None:
        return _model_bundle
    if joblib is None or not MODEL_PATH.exists():
        return None
    try:
        _model_bundle = joblib.load(MODEL_PATH)
        return _model_bundle
    except Exception:
        return None


# Order must match ml/train.py feature_cols.
FEATURE_COLS = (
    "rate_10s", "rate_60s", "path_entropy", "path_history_len",
    "header_completeness", "has_accept_language", "js_seen_recently",
    "seq_id_streak", "honeypot_hit",
    "req_per_sec", "nav_diversity", "interaction_score", "tls_inconsistency",
    "ua_missing", "ua_known_bot", "ua_known_good_crawler",
    "ua_has_browser_token", "ua_len",
)


def _rule_score(s: dict) -> tuple[float, list[str]]:
    """Cheap, explainable score 0..1 plus reasons. Used as fallback and
    blended into the ML probability."""
    reasons: list[str] = []
    score = 0.0

    if s["honeypot_hit"]:
        return 1.0, ["honeypot_hit"]

    if s["ua_missing"]:
        score += 0.35
        reasons.append("missing user-agent")
    elif s["ua_known_bot"] and not s["ua_known_good_crawler"]:
        score += 0.55
        reasons.append("known-bot user-agent")

    if s["rate_10s"] > 20:
        score += 0.30
        reasons.append(f"high rate ({s['rate_10s']}/10s)")
    elif s["rate_10s"] > 10:
        score += 0.15
        reasons.append(f"elevated rate ({s['rate_10s']}/10s)")

    if s["header_completeness"] < 0.75:
        score += 0.15
        reasons.append(f"sparse headers ({s['header_completeness']:.0%})")

    if s["path_history_len"] >= 10 and s["path_entropy"] < 0.5:
        score += 0.20
        reasons.append("low path entropy (sequential traversal)")

    if s["seq_id_streak"] >= 5:
        score += 0.15
        reasons.append("sequential-id streak")

    if not s["js_seen_recently"] and s["path_history_len"] >= 5:
        score += 0.10
        reasons.append("no JS execution evidence")

    if s.get("tls_inconsistency"):
        score += 0.20
        reasons.append("UA claims Chrome but missing sec-fetch / sec-ch-ua")

    if s.get("req_per_sec", 0) > 2.0:
        score += 0.10
        reasons.append(f"sustained {s['req_per_sec']:.1f} req/s")

    if s.get("path_history_len", 0) >= 8 and s.get("nav_diversity", 1) < 0.25:
        score += 0.10
        reasons.append("low nav diversity (hammers same path)")

    if s.get("interaction_score", 0) == 0 and s.get("path_history_len", 0) >= 4:
        score += 0.05
        reasons.append("no mouse/scroll/key interaction")

    if s.get("spoofed_crawler"):
        # UA claims to be Googlebot/Bingbot but the IP is loopback/private —
        # cannot possibly be a real search-engine crawler. Heavy penalty.
        score += 0.25
        reasons.append("spoofed crawler UA (IP not in crawler range)")

    cohort = s.get("cohort_size", 0)
    if cohort >= 5:
        # Many distinct IPs sharing the same UA + sparse-header fingerprint
        # is the hallmark of a distributed scraping campaign — each IP looks
        # innocent on its own but the cohort is unmistakable.
        score += min(0.35, 0.05 * cohort)
        reasons.append(f"distributed-attack cohort (n={cohort})")

    return min(score, 0.99), reasons


def score(s: dict) -> dict:
    """Return suspicion 0..1, verdict, reasons, and a list of triggered rules."""
    rule_p, reasons = _rule_score(s)
    ml_p = None

    bundle = _load_model()
    if bundle is not None:
        try:
            import numpy as np
            X = np.array([[s.get(c, 0) for c in FEATURE_COLS]], dtype=float)
            # Use Random Forest probability (index 1 = "bot" class).
            ml_p = float(bundle["rf"].predict_proba(X)[0, 1])
        except Exception:
            ml_p = None

    if ml_p is not None:
        # Blend: rules carry the live signal (work from request 1), ML adds
        # cohort wisdom (works once a few requests accumulate). When rules
        # are confident, they dominate so live demos catch bots fast.
        blend = ml_p * 0.4 + rule_p * 0.6
        if rule_p >= 0.6:
            p = max(blend, rule_p)         # rule-confident → trust rule fully
        elif rule_p >= 0.4 and ml_p >= 0.4:
            p = max(blend, (rule_p + ml_p) / 2 + 0.1)  # both agree → escalate
        else:
            p = blend
        if s["honeypot_hit"]:
            p = 1.0
        method = "ml+rules"
    else:
        p = rule_p
        method = "rules"

    if s["ua_known_good_crawler"]:
        # "Verified" search engines get a score cap — but only if their request
        # shape matches a real crawler. A spoofed UA combined with TLS-header
        # inconsistency or honeypot bait fails this check.
        spoof_signals = (
            s.get("tls_inconsistency", 0)
            or s.get("honeypot_hit", 0)
            or s.get("seq_id_streak", 0) >= 5
            or s.get("rate_10s", 0) > 15
        )
        if not spoof_signals:
            p = min(p, 0.2)
            reasons.append("verified-shape crawler — score capped")
        else:
            reasons.append("spoofed crawler UA (failed shape check)")

    verdict = (
        "bot" if p >= 0.9 else
        "suspicious" if p >= 0.5 else
        "watch" if p >= 0.3 else
        "human"
    )
    return {
        "suspicion": round(p, 4),
        "verdict": verdict,
        "reasons": reasons,
        "method": method,
        "ml_p": ml_p,
        "rule_p": round(rule_p, 4),
    }
