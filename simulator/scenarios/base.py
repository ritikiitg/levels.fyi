"""Base class for attack scenarios."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Iterable

import httpx


@dataclass
class Stats:
    sent: int = 0
    ok: int = 0
    blocked: int = 0
    challenged: int = 0
    decoy_suspected: int = 0
    started_at: float = field(default_factory=time.time)
    last_log: float = field(default_factory=time.time)


class Scenario:
    """Subclass and implement `requests()` (an async generator of (path, headers))."""

    name = "base"
    description = "base scenario"

    def __init__(self, target: str, duration: float = 60.0, qps: float = 5.0,
                 source_label: str = "single"):
        self.target = target.rstrip("/")
        self.duration = duration
        self.qps = qps
        self.source_label = source_label
        self.stats = Stats()

    async def requests(self) -> Iterable:  # type: ignore[override]
        """Subclasses yield tuples of (path, headers_dict) at their own cadence."""
        raise NotImplementedError

    def _classify(self, response: httpx.Response) -> str:
        if response.status_code == 401 and "captcha" in response.text.lower():
            return "challenged"
        if response.status_code >= 400:
            return "blocked"
        try:
            data = response.json()
            if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("_decoy"):
                return "decoy"
            if isinstance(data, dict) and data.get("_decoy"):
                return "decoy"
        except Exception:
            pass
        return "ok"

    async def run(self) -> Stats:
        start = time.time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            async for path, headers in self.requests():
                if time.time() - start > self.duration:
                    break
                self.stats.sent += 1
                try:
                    r = await client.get(self.target + path, headers=headers)
                    kind = self._classify(r)
                    if kind == "ok": self.stats.ok += 1
                    elif kind == "blocked": self.stats.blocked += 1
                    elif kind == "challenged": self.stats.challenged += 1
                    elif kind == "decoy": self.stats.decoy_suspected += 1
                except Exception:
                    self.stats.blocked += 1
                self._maybe_log()
        return self.stats

    def _maybe_log(self) -> None:
        now = time.time()
        if now - self.stats.last_log >= 2.0:
            elapsed = now - self.stats.started_at
            print(
                f"[{self.name}] t={elapsed:5.1f}s sent={self.stats.sent:4d} "
                f"ok={self.stats.ok:4d} blocked={self.stats.blocked:3d} "
                f"challenged={self.stats.challenged:3d} decoy={self.stats.decoy_suspected:3d}"
            )
            self.stats.last_log = now
