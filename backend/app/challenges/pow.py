"""Proof-of-work challenge.

Server hands out (prefix, difficulty). Client must find nonce s.t.
sha256(prefix + nonce) starts with `difficulty` hex zeros. On verify,
we recompute and accept if it matches.

Difficulty 4 ≈ 50ms on a laptop. Difficulty 5 ≈ ~0.8s. Difficulty 6 ≈ ~12s.
We escalate per IP based on current suspicion score.
"""
from __future__ import annotations

import hashlib
import secrets
import time

from ..detection import state

# Active challenges issued, keyed by prefix.
_active: dict[str, dict] = {}
TTL_S = 90


def _gc():
    now = time.time()
    for k in [k for k, v in _active.items() if now - v["issued_at"] > TTL_S]:
        _active.pop(k, None)


def issue(ip: str, difficulty: int = 4) -> dict:
    _gc()
    prefix = secrets.token_hex(8)
    _active[prefix] = {"ip": ip, "difficulty": difficulty, "issued_at": time.time()}
    return {"prefix": prefix, "difficulty": difficulty}


def verify(prefix: str, nonce: int, solve_ms: float | None, ip: str) -> dict:
    rec = _active.get(prefix)
    if not rec:
        return {"ok": False, "reason": "unknown challenge"}
    if rec["ip"] != ip:
        return {"ok": False, "reason": "ip mismatch"}
    h = hashlib.sha256(f"{prefix}{nonce}".encode()).hexdigest()
    if not h.startswith("0" * rec["difficulty"]):
        return {"ok": False, "reason": "bad hash"}
    _active.pop(prefix, None)
    state.mark_challenge_passed(ip)
    return {"ok": True, "hash": h, "solve_ms": solve_ms}
