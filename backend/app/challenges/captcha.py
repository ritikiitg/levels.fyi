"""In-house CAPTCHA. No third-party dep. Two flavors:
  1. text — render a 5-char obfuscated string, user retypes it.
  2. choice — present 4 emojis, ask "click the cat".

We start with `choice` because it's near-impossible for naive scrapers
and easy for humans. Frontend renders the emoji grid; backend stores the
expected answer keyed by token."""
from __future__ import annotations

import random
import secrets
import time

_active: dict[str, dict] = {}
TTL_S = 120

CHOICES = [
    ("cat", "🐈"),
    ("dog", "🐕"),
    ("fish", "🐟"),
    ("bird", "🐦"),
    ("frog", "🐸"),
    ("horse", "🐴"),
]


def _gc():
    now = time.time()
    for k in [k for k, v in _active.items() if now - v["issued_at"] > TTL_S]:
        _active.pop(k, None)


def issue(ip: str) -> dict:
    _gc()
    options = random.sample(CHOICES, 4)
    target = random.choice(options)
    token = secrets.token_hex(12)
    _active[token] = {
        "ip": ip, "answer": target[0], "issued_at": time.time(),
    }
    return {
        "token": token,
        "prompt": f"Click the {target[0]}",
        "options": [{"id": name, "emoji": emoji} for name, emoji in options],
    }


def verify(token: str, answer: str, ip: str) -> dict:
    rec = _active.get(token)
    if not rec:
        return {"ok": False, "reason": "unknown token"}
    if rec["ip"] != ip:
        return {"ok": False, "reason": "ip mismatch"}
    ok = rec["answer"] == answer
    _active.pop(token, None)
    if ok:
        from ..detection import state
        state.mark_challenge_passed(ip)
    return {"ok": ok}
