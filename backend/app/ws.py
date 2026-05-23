"""WebSocket fan-out for the dashboard live feed.

Middleware calls broadcast() on every scored request; subscribers (the
dashboard React app) receive each event in real time.
"""
from __future__ import annotations

import asyncio
import json
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

_subs: Set[WebSocket] = set()
_loop: asyncio.AbstractEventLoop | None = None


def set_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _loop
    _loop = loop


def broadcast(event: dict) -> None:
    """Thread-safe broadcast from the sync middleware path."""
    if _loop is None or not _subs:
        return
    msg = json.dumps(event, default=str)
    asyncio.run_coroutine_threadsafe(_fanout(msg), _loop)


async def _fanout(msg: str) -> None:
    dead = []
    for ws in list(_subs):
        try:
            await ws.send_text(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _subs.discard(ws)


@router.websocket("/_defender/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    _subs.add(ws)
    # Immediate hello so the dashboard flips out of "connecting…" before any
    # real traffic arrives.
    await ws.send_text(json.dumps({"type": "hello", "subscribers": len(_subs)}))
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        _subs.discard(ws)
    except Exception:
        _subs.discard(ws)
