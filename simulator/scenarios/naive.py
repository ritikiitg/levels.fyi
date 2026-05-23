"""Naive scraper — fast, no UA, walks sequential IDs. The dumbest possible bot."""
from __future__ import annotations

import asyncio
import uuid

from .base import Scenario


class NaiveScraper(Scenario):
    name = "naive-scraper"
    description = "high-rate, no UA, sequential id walks. Should be caught instantly."

    async def requests(self):
        i = 0
        while True:
            yield "/api/salaries?limit=100", {}
            yield "/api/companies", {}
            for _ in range(5):
                yield f"/api/salaries/{uuid.uuid4()}", {}
            # A naive crawler walks every <a href> it can find — including
            # the hidden honeypot links humans never click. Instant tell.
            if i == 0:
                yield "/internal/admin", {}
                yield "/api/.env", {}
            i += 1
            await asyncio.sleep(1 / max(self.qps, 0.1))
