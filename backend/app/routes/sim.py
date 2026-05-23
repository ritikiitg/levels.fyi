"""In-dashboard attack launcher.

Lets the React dashboard kick off the bot simulator scenarios via a button.
The scenarios already live in simulator/scenarios/. We import them and run
them as fire-and-forget asyncio tasks against this very backend.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

# Add the simulator/ folder to sys.path so `import scenarios` works.
_SIM_DIR = Path(__file__).resolve().parent.parent.parent.parent / "simulator"
if str(_SIM_DIR) not in sys.path:
    sys.path.insert(0, str(_SIM_DIR))

try:
    from scenarios import REGISTRY  # type: ignore
except Exception as e:  # pragma: no cover
    REGISTRY = {}
    _IMPORT_ERR = str(e)
else:
    _IMPORT_ERR = ""

router = APIRouter()

# Track running tasks so we can cancel & report status.
_running: dict[str, asyncio.Task] = {}


@router.get("/api/dashboard/scenarios")
def list_scenarios():
    if not REGISTRY:
        return {"error": _IMPORT_ERR, "scenarios": []}
    return {
        "scenarios": [
            {"id": k, "name": k, "description": v.description}
            for k, v in REGISTRY.items()
        ]
    }


def _self_target() -> str:
    """The URL the simulator should hit to reach THIS app instance.
    Honors $PORT (set by Render and most PaaS). Defaults to 8000 for local."""
    port = os.environ.get("PORT", "8000")
    return f"http://127.0.0.1:{port}"


@router.post("/api/dashboard/simulate")
async def launch_attack(scenario: str, duration: float = 10.0, qps: float = 5.0):
    if scenario not in REGISTRY:
        raise HTTPException(404, f"unknown scenario: {scenario}")
    if scenario in _running and not _running[scenario].done():
        raise HTTPException(409, "scenario already running")

    cls = REGISTRY[scenario]
    s = cls(target=_self_target(), duration=duration, qps=qps)

    async def _run():
        try:
            await s.run()
        except Exception:
            pass

    task = asyncio.create_task(_run())
    _running[scenario] = task
    return {
        "ok": True,
        "scenario": scenario,
        "duration": duration,
        "qps": qps,
    }


@router.get("/api/dashboard/simulate/status")
def status():
    return {
        s: {
            "done": t.done(),
            "cancelled": t.cancelled(),
        }
        for s, t in _running.items()
    }


@router.post("/api/dashboard/simulate/stop")
def stop_all():
    cancelled = []
    for k, t in list(_running.items()):
        if not t.done():
            t.cancel()
            cancelled.append(k)
    return {"cancelled": cancelled}
