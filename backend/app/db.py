"""SQLite layer. Holds salary data + a rolling request log for analytics."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "this1.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS salaries (
    uuid TEXT PRIMARY KEY,
    company TEXT NOT NULL,
    company_slug TEXT NOT NULL,
    title TEXT NOT NULL,
    job_family TEXT NOT NULL,
    level TEXT,
    years_of_experience REAL,
    years_at_company REAL,
    location TEXT,
    base_salary REAL,
    total_compensation REAL,
    currency TEXT,
    offer_date TEXT,
    raw_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_company_slug ON salaries(company_slug);
CREATE INDEX IF NOT EXISTS idx_job_family ON salaries(job_family);
CREATE INDEX IF NOT EXISTS idx_level ON salaries(level);

CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    ip TEXT NOT NULL,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    user_agent TEXT,
    status INTEGER,
    suspicion REAL,
    verdict TEXT,
    action TEXT,
    signals_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_requests_ts ON requests(ts);
CREATE INDEX IF NOT EXISTS idx_requests_ip ON requests(ip);
CREATE INDEX IF NOT EXISTS idx_requests_verdict ON requests(verdict);

CREATE TABLE IF NOT EXISTS feedback (
    request_id INTEGER PRIMARY KEY,
    truth TEXT NOT NULL,
    ts REAL NOT NULL
);
"""


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def insert_salary(row: dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO salaries
            (uuid, company, company_slug, title, job_family, level,
             years_of_experience, years_at_company, location,
             base_salary, total_compensation, currency, offer_date, raw_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                row["uuid"],
                row["company"],
                row.get("companyInfo", {}).get("slug", row["company"].lower()),
                row["title"],
                row["jobFamily"],
                row.get("level"),
                row.get("yearsOfExperience"),
                row.get("yearsAtCompany"),
                row.get("location"),
                row.get("baseSalary"),
                row.get("totalCompensation"),
                row.get("baseSalaryCurrency"),
                row.get("offerDate"),
                json.dumps(row),
            ),
        )


def log_request(entry: dict[str, Any]) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO requests
            (ts, ip, method, path, user_agent, status, suspicion, verdict, action, signals_json)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                entry["ts"],
                entry["ip"],
                entry["method"],
                entry["path"],
                entry.get("user_agent"),
                entry.get("status"),
                entry.get("suspicion"),
                entry.get("verdict"),
                entry.get("action"),
                json.dumps(entry.get("signals", {})),
            ),
        )
        return cur.lastrowid


def list_salaries(
    company_slug: str | None = None,
    job_family: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    sql = "SELECT raw_json FROM salaries WHERE 1=1"
    params: list[Any] = []
    if company_slug:
        sql += " AND company_slug = ?"
        params.append(company_slug)
    if job_family:
        sql += " AND job_family = ?"
        params.append(job_family)
    sql += " ORDER BY offer_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [json.loads(r["raw_json"]) for r in rows]


def get_salary(uuid: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT raw_json FROM salaries WHERE uuid = ?", (uuid,)
        ).fetchone()
    return json.loads(row["raw_json"]) if row else None


def list_companies() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT company, company_slug, COUNT(*) AS submissions,
                      AVG(total_compensation) AS avg_tc
               FROM salaries GROUP BY company_slug
               ORDER BY submissions DESC"""
        ).fetchall()
    return [dict(r) for r in rows]


def recent_requests(limit: int = 200) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM requests ORDER BY ts DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def verdict_counts(since_seconds: float = 3600) -> dict[str, int]:
    import time
    cutoff = time.time() - since_seconds
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT verdict, COUNT(*) AS n FROM requests WHERE ts >= ? GROUP BY verdict",
            (cutoff,),
        ).fetchall()
    return {r["verdict"]: r["n"] for r in rows if r["verdict"]}
