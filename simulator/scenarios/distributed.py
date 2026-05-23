"""Distributed scraper — rotates X-Forwarded-For across many fake IPs.
Each one looks innocent in isolation; the model still catches the cohort via
header inconsistencies + no JS."""
from __future__ import annotations

import asyncio
import random

from .base import Scenario

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0.0.0 Safari/537.36"
)


def _fake_ip() -> str:
    return f"{random.randint(2,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


class DistributedScraper(Scenario):
    name = "distributed"
    description = "rotates X-Forwarded-For. Each request looks innocent; caught at cohort level."

    async def requests(self):
        while True:
            ip = _fake_ip()
            headers = {
                "User-Agent": CHROME_UA,
                "Accept": "text/html",
                "X-Forwarded-For": ip,
                # Notice: missing sec-fetch-* and sec-ch-ua — TLS-consistency tell.
            }
            yield random.choice([
                "/api/salaries?limit=50",
                "/api/companies",
                "/api/salaries?company=google",
                "/api/salaries?role=Software%20Engineer",
            ]), headers
            await asyncio.sleep(random.uniform(0.4, 1.2))
