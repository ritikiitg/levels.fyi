"""POST-heavy scenario simulating a credential-stuffing attack against
a (hypothetical) login endpoint. Even without a login route, the request
pattern itself trips the defender."""
from __future__ import annotations

import asyncio
import random

from .base import Scenario


class CredentialStuffer(Scenario):
    name = "credential-stuffer"
    description = "rapid POSTs against /api/login. High rate, low diversity."

    async def requests(self):
        headers = {"User-Agent": "okhttp/4.9.3", "Content-Type": "application/json"}
        while True:
            for _ in range(20):
                yield "/api/login?u=test", headers
                await asyncio.sleep(0.05)
            await asyncio.sleep(0.2)
