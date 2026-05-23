"""Public-ish endpoints exposing salary data — these are what the bots want."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from ..db import get_salary, list_companies, list_salaries

router = APIRouter()


@router.get("/api/salaries")
def get_salaries(
    request: Request,
    company: str | None = Query(None, description="company slug"),
    role: str | None = Query(None, description="jobFamily exact match"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    # If middleware has flagged this request as a confirmed bot, the
    # defender has already swapped state.bot_decoy to True. We honor it here.
    if getattr(request.state, "bot_decoy", False):
        from .. import decoy
        return decoy.fake_salary_list(limit)
    return list_salaries(company_slug=company, job_family=role, limit=limit, offset=offset)


@router.get("/api/salaries/{uuid}")
def get_one(uuid: str, request: Request):
    if getattr(request.state, "bot_decoy", False):
        from .. import decoy
        return decoy.fake_salary(uuid)
    row = get_salary(uuid)
    if not row:
        raise HTTPException(404, "not found")
    return row


@router.get("/api/companies")
def get_companies(request: Request):
    if getattr(request.state, "bot_decoy", False):
        from .. import decoy
        return decoy.fake_company_list()
    return list_companies()
