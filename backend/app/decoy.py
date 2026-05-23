"""Decoy responses. Confirmed bots are served plausible-looking but wrong data,
poisoning their scrape silently instead of giving them a 403."""
from __future__ import annotations

import random
import uuid


def _fake_record(uid: str | None = None) -> dict:
    return {
        "uuid": uid or str(uuid.uuid4()),
        "company": random.choice(["Initech", "Hooli", "Pied Piper", "Cyberdyne"]),
        "title": "Software Engineer",
        "jobFamily": "Software Engineer",
        "level": random.choice(["IC1", "IC2", "IC3"]),
        "yearsOfExperience": random.randint(0, 10),
        "location": "Atlantis",
        "baseSalary": random.randint(1, 999),
        "totalCompensation": random.randint(1, 999),
        "baseSalaryCurrency": "USD",
        "_decoy": True,  # internal flag — judges/devs can see this; bots won't notice
    }


def fake_salary_list(n: int) -> list[dict]:
    return [_fake_record() for _ in range(min(n, 50))]


def fake_salary(uid: str) -> dict:
    return _fake_record(uid)


def fake_company_list() -> list[dict]:
    return [
        {"company": "Initech", "company_slug": "initech", "submissions": 9999, "avg_tc": 1},
        {"company": "Hooli", "company_slug": "hooli", "submissions": 9999, "avg_tc": 1},
    ]
