"""Generate realistic mock salary submissions modeled on sample.json.

We do NOT call levels.fyi (per given.txt). All data is synthetic and based
on the field schema in problem1_additionalfiles/sample.json.
"""
from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from .db import init_db, insert_salary

SAMPLE_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "problem1_additionalfiles"
    / "sample.json"
)

COMPANIES = [
    ("Google", "google", "https://img.logo.dev/google.com?token="),
    ("Meta", "meta", "https://img.logo.dev/meta.com?token="),
    ("Amazon", "amazon", "https://img.logo.dev/amazon.com?token="),
    ("Microsoft", "microsoft", "https://img.logo.dev/microsoft.com?token="),
    ("Apple", "apple", "https://img.logo.dev/apple.com?token="),
    ("Netflix", "netflix", "https://img.logo.dev/netflix.com?token="),
    ("ServiceNow", "servicenow", "https://img.logo.dev/servicenow.com?token="),
    ("Stripe", "stripe", "https://img.logo.dev/stripe.com?token="),
    ("Uber", "uber", "https://img.logo.dev/uber.com?token="),
    ("Airbnb", "airbnb", "https://img.logo.dev/airbnb.com?token="),
]

ROLES = [
    ("Software Engineer", "software-engineer"),
    ("Product Manager", "product-manager"),
    ("Data Scientist", "data-scientist"),
    ("Hardware Engineer", "hardware-engineer"),
    ("Designer", "designer"),
]

LEVELS_BY_YOE = [
    ("IC1", 0, 2),
    ("IC2", 1, 4),
    ("IC3", 3, 6),
    ("IC4", 5, 10),
    ("IC5", 8, 15),
    ("IC6", 12, 25),
]

LOCATIONS = [
    ("Mountain View, CA, United States", "mountain-view-usa", 84, "USD", 1.0),
    ("Seattle, WA, United States", "seattle-usa", 80, "USD", 1.0),
    ("New York, NY, United States", "new-york-usa", 100, "USD", 1.0),
    ("London, England, United Kingdom", "london-uk", 75, "GBP", 1.27),
    ("Pune, MH, India", "pune-ind", 25, "INR", 0.012),
    ("Bangalore, KA, India", "bangalore-ind", 30, "INR", 0.012),
    ("Toronto, ON, Canada", "toronto-can", 70, "CAD", 0.73),
    ("Berlin, Germany", "berlin-deu", 65, "EUR", 1.08),
]

ARRANGEMENTS = ["remote", "hybrid", "in-person"]


def synth_row() -> dict:
    company, slug, icon = random.choice(COMPANIES)
    title, family_slug = random.choice(ROLES)
    level, min_yoe, max_yoe = random.choice(LEVELS_BY_YOE)
    yoe = random.randint(min_yoe, max_yoe)
    yac = random.randint(0, min(yoe, 6))
    loc, loc_slug, loc_factor, currency, fx = random.choice(LOCATIONS)
    arrangement = random.choice(ARRANGEMENTS)

    # base salary in USD-equivalent then localize
    base_usd = random.randint(80_000, 280_000) + (
        ["IC1", "IC2", "IC3", "IC4", "IC5", "IC6"].index(level) * 30_000
    )
    base_usd = int(base_usd * (loc_factor / 80))  # adjust by region
    base = int(base_usd / fx) if fx else base_usd

    stock_usd = random.choice([0, 0, 20_000, 60_000, 120_000, 240_000])
    bonus = int((base * random.uniform(0.05, 0.20)))
    tc_usd = base_usd + int(stock_usd / 4) + int(bonus * fx)

    offer_dt = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))

    return {
        "uuid": str(uuid.uuid4()),
        "company": company,
        "title": title,
        "jobFamily": title,
        "jobFamilySlug": family_slug,
        "level": level,
        "focusTag": title,
        "yearsOfExperience": yoe,
        "yearsAtCompany": yac,
        "yearsAtLevel": None,
        "offerDate": offer_dt.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
        "location": loc,
        "locationSlug": loc_slug,
        "workArrangement": arrangement,
        "compPerspective": random.choice(["offer", "employee"]),
        "cityId": random.randint(10000, 99999),
        "dmaId": random.randint(10000, 19999),
        "countryId": random.randint(1, 250),
        "exchangeRate": round(1 / fx, 2) if fx else 1.0,
        "baseSalary": base,
        "baseSalaryCurrency": currency,
        "salaryFormat": None,
        "employmentType": None,
        "totalCompensation": int(tc_usd / fx) if fx else tc_usd,
        "firstYearTotalCompensation": int(tc_usd / fx * 1.1) if fx else int(tc_usd * 1.1),
        "avgAnnualStockGrantValue": int(stock_usd / 4),
        "firstYearStockGrantValue": int(stock_usd / 4),
        "totalStockGrantValue": stock_usd,
        "stockGrantCurrency": "USD",
        "avgAnnualBonusValue": bonus,
        "firstYearBonusValue": int(bonus * 1.2),
        "bonusCurrency": currency,
        "salesComp": None,
        "negotiatedAmount": None,
        "gender": None,
        "ethnicity": None,
        "education": None,
        "otherDetails": None,
        "companyInfo": {
            "registered": True,
            "icon": icon,
            "name": company,
            "slug": slug,
        },
        "vestingSchedule": [
            {"percent": 25, "occurrences": 1},
            {"percent": 25, "occurrences": 4},
            {"percent": 25, "occurrences": 4},
            {"percent": 25, "occurrences": 4},
        ],
        "tags": None,
        "stockType": "stock",
        "avgAnnualOptionsGranted": None,
        "totalOptionsGranted": None,
        "optionStrikePrice": None,
        "optionPreferredPrice": None,
        "totalOutstandingShares": None,
        "latestCompanyValuation": None,
        "companySize": None,
        "fundingStage": None,
        "annualTargetBonusValue": int(bonus * 0.5),
        "annualTargetBonusPercentage": None,
        "additionalBonuses": [],
        "userCurrency": "USD",
        "userExchangeRate": None,
        "commentsAndRepliesCount": None,
        "threadId": None,
    }


def seed(n: int = 250) -> None:
    init_db()
    # Insert the provided sample first so it's always present.
    if SAMPLE_PATH.exists():
        with SAMPLE_PATH.open() as f:
            insert_salary(json.load(f))
    for _ in range(n):
        insert_salary(synth_row())
    print(f"Seeded {n + (1 if SAMPLE_PATH.exists() else 0)} salary records.")


if __name__ == "__main__":
    seed()
