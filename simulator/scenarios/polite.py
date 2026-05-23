"""Polite scraper — slow rate, spoofs a Googlebot UA. Tries to look benign.
Caught via no JS + low nav diversity + TLS/header inconsistency."""
from __future__ import annotations

import asyncio
import uuid

from .base import Scenario

GOOGLEBOT_UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"


class PoliteScraper(Scenario):
    name = "polite-scraper"
    description = "spoofs Googlebot UA, low rate. Caught via behavioral signals."

    async def requests(self):
        headers = {
            "User-Agent": GOOGLEBOT_UA,
            "Accept": "text/html",
        }
        while True:
            yield "/api/salaries?limit=50", headers
            await asyncio.sleep(2.0)
            yield "/api/companies", headers
            await asyncio.sleep(3.0)
            for _ in range(3):
                yield f"/api/salaries/{uuid.uuid4()}", headers
                await asyncio.sleep(1.0)
