"""Defender-side endpoints: beacon (JS-execution proof) + challenge stubs.
PoW + CAPTCHA endpoints get fleshed out in Phase 6."""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..challenges import captcha, pow as pow_challenge
from ..detection import state

router = APIRouter()


class Beacon(BaseModel):
    ua: str | None = None
    ts: int | None = None
    mouse: int = 0
    scroll: int = 0
    key: int = 0
    path: str | None = None


@router.post("/_defender/beacon")
def beacon(request: Request, payload: Beacon):
    ip = request.client.host if request.client else "unknown"
    state.mark_js_seen(ip)
    state.record_beacon(ip, payload.mouse, payload.scroll, payload.key)
    # AUTO-REDEMPTION: a confirmed-bot IP that suddenly shows real human
    # interaction (mouse + scroll/key) is most likely a false positive from
    # an earlier demo attack. Clear the confirmed mark so the user gets real
    # data again instead of being permanently stuck on decoy.
    if (payload.mouse >= 3 and (payload.scroll >= 1 or payload.key >= 1)
            and state.is_confirmed_bot(ip)):
        state.clear_ip(ip)
    return {"ok": True, "redeemed": False}


# ---------- Proof of Work ----------

class PowSolve(BaseModel):
    prefix: str
    nonce: int
    hash: str | None = None
    difficulty: int | None = None
    solveMs: float | None = None


@router.get("/_defender/pow/challenge")
def pow_challenge_endpoint(request: Request):
    ip = request.client.host if request.client else "unknown"
    # Difficulty escalates by recent suspicion.
    confirmed = state.is_confirmed_bot(ip)
    difficulty = 5 if confirmed else 4
    return pow_challenge.issue(ip, difficulty=difficulty)


@router.post("/_defender/pow/verify")
def pow_verify(request: Request, payload: PowSolve):
    ip = request.client.host if request.client else "unknown"
    return pow_challenge.verify(payload.prefix, payload.nonce, payload.solveMs, ip)


# ---------- CAPTCHA ----------

class CaptchaSolve(BaseModel):
    token: str
    answer: str


@router.get("/_defender/captcha/challenge")
def captcha_challenge_endpoint(request: Request):
    ip = request.client.host if request.client else "unknown"
    return captcha.issue(ip)


@router.post("/_defender/captcha/verify")
def captcha_verify(request: Request, payload: CaptchaSolve):
    ip = request.client.host if request.client else "unknown"
    return captcha.verify(payload.token, payload.answer, ip)


# ---------- Operator: mark feedback ----------

class Feedback(BaseModel):
    request_id: int
    truth: str  # "bot" | "human"


@router.post("/_defender/feedback")
def feedback(payload: Feedback):
    import time
    from ..db import get_conn
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO feedback (request_id, truth, ts) VALUES (?,?,?)",
            (payload.request_id, payload.truth, time.time()),
        )
    return {"ok": True}


# ---------- Operator: clear state ----------

@router.post("/_defender/reset")
def reset(ip: str | None = None):
    """Clear confirmed-bot status + rolling counters. Pass ?ip= to clear one IP,
    omit to wipe all state. Useful when a real user gets stuck after demo attacks."""
    if ip:
        was = state.clear_ip(ip)
        return {"ok": True, "ip": ip, "was_confirmed": was}
    n = state.clear_all()
    return {"ok": True, "cleared_ips": n}
