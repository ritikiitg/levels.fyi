"""Slow-and-low scraper — 1 request every ~60s, but over hours scrapes
everything. Caught via session-shape anomaly + zero interaction.

For demo we compress 'hours' into seconds via --qps override."""
from __future__ import annotations

import asyncio
import uuid

from .base import Scenario

CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0.0.0 Safari/537.36"
)


class SlowAndLow(Scenario):
    name = "slow-and-low"
    description = "one request per ~30s but never stops. Caught via session shape."

    async def requests(self):
        headers = {"User-Agent": CHROME_UA, "Accept": "text/html"}
        while True:
            yield "/api/salaries?limit=10", headers
            await asyncio.sleep(max(30.0 / max(self.qps, 0.1), 1.0))
            yield f"/api/salaries/{uuid.uuid4()}", headers
            await asyncio.sleep(max(30.0 / max(self.qps, 0.1), 1.0))
