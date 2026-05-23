"""The three-headed defender middleware (this1).

Layered response per request:
  layer 0  whitelisted crawlers (verified)        -> allow
  layer 1  invisible PoW already passed?           -> allow
  layer 2  suspicion >= 0.5 (suspicious)           -> demand CAPTCHA (HTTP 401)
  layer 3  suspicion >= 0.9  OR  honeypot hit      -> serve DECOY data
"""
from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ..db import log_request
from ..detection import signals, state
from ..detection.scorer import score
from ..detection.signals import client_ip
from .. import ws as ws_module

# Paths we don't want to score (internal defender + static health + dashboard read API).
SKIP_PATHS = {"/_defender/beacon", "/api/health", "/"}
# Prefixes that are observability/dev surfaces, not protected data.
SKIP_PREFIXES = ("/_defender", "/static", "/api/dashboard", "/api/model", "/docs", "/openapi.json", "/redoc", "/_redoc")
CHALLENGE_THRESHOLD = 0.45
BLOCK_THRESHOLD = 0.75


class DefenderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        ip = client_ip(request)

        # Already confirmed bot? Short-circuit with decoy data flag, but still
        # let the route handler respond so the bot can't tell from timing.
        confirmed = state.is_confirmed_bot(ip)
        if confirmed and path.startswith("/api/"):
            request.state.bot_decoy = True

        if path in SKIP_PATHS or path.startswith(SKIP_PREFIXES):
            return await call_next(request)

        feats = signals.extract(request)
        verdict_info = score(feats)
        susp = verdict_info["suspicion"]

        action = "allow"
        challenge_payload: dict | None = None

        # Suspicious tier — demand CAPTCHA, unless recently passed.
        if (CHALLENGE_THRESHOLD <= susp < BLOCK_THRESHOLD
                and not state.challenge_passed_recently(ip)
                and path.startswith("/api/")):
            action = "challenge"
            from ..challenges import captcha
            challenge_payload = captcha.issue(ip)

        # Confirmed bot tier — silently serve decoy data.
        if susp >= BLOCK_THRESHOLD or feats.get("honeypot_hit"):
            if not confirmed:
                state.mark_confirmed_bot(ip, reason=f"score={susp:.2f}" if not feats.get("honeypot_hit") else "honeypot")
            request.state.bot_decoy = True
            action = "decoy"

        if action == "challenge":
            response = JSONResponse(
                status_code=401,
                content={
                    "error": "captcha_required",
                    "challenge": challenge_payload,
                    "hint": "POST {token, answer} to /_defender/captcha/verify",
                },
            )
        else:
            response = await call_next(request)

        log_request({
            "ts": time.time(),
            "ip": ip,
            "method": request.method,
            "path": path,
            "user_agent": feats.get("_ua"),
            "status": response.status_code,
            "suspicion": verdict_info["suspicion"],
            "verdict": verdict_info["verdict"],
            "action": action,
            "signals": {k: v for k, v in feats.items() if not k.startswith("_")} | {
                "_reasons": verdict_info["reasons"],
                "_method": verdict_info["method"],
                "_ml_p": verdict_info["ml_p"],
                "_rule_p": verdict_info["rule_p"],
            },
        })

        # Live push to dashboard subscribers.
        ws_module.broadcast({
            "ts": time.time(),
            "ip": ip,
            "method": request.method,
            "path": path,
            "ua": feats.get("_ua"),
            "status": response.status_code,
            "suspicion": verdict_info["suspicion"],
            "verdict": verdict_info["verdict"],
            "action": action,
            "reasons": verdict_info["reasons"],
        })

        response.headers["x-this1-suspicion"] = str(verdict_info["suspicion"])
        response.headers["x-this1-verdict"] = verdict_info["verdict"]
        response.headers["x-this1-action"] = action
        return response
