"""Honeypot URLs. These are rendered as hidden <a> links in the site HTML.
Only a non-human scraper would ever request them. Anyone hitting these is
upgraded to confirmed-bot immediately."""
from __future__ import annotations

from fastapi import APIRouter, Request

from ..detection.state import mark_confirmed_bot

router = APIRouter()


HONEY_PATHS = ["/internal/admin", "/api/.env", "/api/__debug__", "/api/all-salaries.json"]


@router.get("/internal/admin")
@router.get("/api/.env")
@router.get("/api/__debug__")
@router.get("/api/all-salaries.json")
def honeypot(request: Request):
    ip = request.client.host if request.client else "unknown"
    mark_confirmed_bot(ip, reason="honeypot")
    return {"ok": True}  # bait — looks like a valid response
