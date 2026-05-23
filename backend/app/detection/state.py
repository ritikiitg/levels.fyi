"""In-memory state shared across requests: per-IP rolling counters, verdicts."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque

# Sliding windows of timestamps per IP.
_rate_window: dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=500))
# Per-IP path history (entropy + traversal pattern).
_path_window: dict[str, Deque[str]] = defaultdict(lambda: deque(maxlen=100))
# JS-execution evidence: client beacon proves a browser is running.
_js_seen: dict[str, float] = {}
# Confirmed-bot set with reason and timestamp.
_confirmed: dict[str, dict] = {}
# Recent challenge results.
_challenge_passed: dict[str, float] = {}

_lock = Lock()

# First-seen timestamp per IP (session duration proxy).
_first_seen: dict[str, float] = {}
# Cumulative interaction signals from beacon.
_beacon_stats: dict[str, dict] = defaultdict(lambda: {"mouse": 0, "scroll": 0, "key": 0, "beacons": 0})
# Cohort tracking: many IPs sharing the same fingerprint = distributed bot.
# fingerprint -> dict(ip -> last_seen_ts)
_cohorts: dict[str, dict[str, float]] = defaultdict(dict)


def record_request(ip: str, path: str) -> None:
    now = time.time()
    with _lock:
        _rate_window[ip].append(now)
        _path_window[ip].append(path)
        _first_seen.setdefault(ip, now)


def session_seconds(ip: str) -> float:
    with _lock:
        first = _first_seen.get(ip)
    return (time.time() - first) if first else 0.0


def record_beacon(ip: str, mouse: int, scroll: int, key: int) -> None:
    with _lock:
        s = _beacon_stats[ip]
        s["mouse"] += mouse
        s["scroll"] += scroll
        s["key"] += key
        s["beacons"] += 1


def beacon_stats(ip: str) -> dict:
    with _lock:
        return dict(_beacon_stats[ip])


def record_cohort(fingerprint: str, ip: str) -> None:
    with _lock:
        _cohorts[fingerprint][ip] = time.time()


def cohort_size(fingerprint: str, within_seconds: float = 60.0) -> int:
    """Count distinct IPs sharing this fingerprint in the recent window."""
    cutoff = time.time() - within_seconds
    with _lock:
        ips = _cohorts.get(fingerprint, {})
        return sum(1 for ts in ips.values() if ts >= cutoff)


def rate(ip: str, seconds: float = 10.0) -> int:
    cutoff = time.time() - seconds
    with _lock:
        return sum(1 for ts in _rate_window[ip] if ts >= cutoff)


def path_history(ip: str) -> list[str]:
    with _lock:
        return list(_path_window[ip])


def mark_js_seen(ip: str) -> None:
    with _lock:
        _js_seen[ip] = time.time()


def js_seen_recently(ip: str, within_seconds: float = 300.0) -> bool:
    with _lock:
        ts = _js_seen.get(ip)
    return ts is not None and (time.time() - ts) < within_seconds


CONFIRMED_BOT_TTL_SECONDS = 600  # 10 minutes — bots get a chance to redeem themselves


def mark_confirmed_bot(ip: str, reason: str) -> None:
    with _lock:
        _confirmed[ip] = {"reason": reason, "ts": time.time()}


def is_confirmed_bot(ip: str) -> dict | None:
    with _lock:
        rec = _confirmed.get(ip)
        if rec and (time.time() - rec["ts"]) > CONFIRMED_BOT_TTL_SECONDS:
            _confirmed.pop(ip, None)
            return None
        return rec


def clear_ip(ip: str) -> bool:
    """Operator override — clear a specific IP's confirmed-bot mark + rolling counters."""
    with _lock:
        was = _confirmed.pop(ip, None) is not None
        _rate_window.pop(ip, None)
        _path_window.pop(ip, None)
        _js_seen.pop(ip, None)
        _first_seen.pop(ip, None)
        _beacon_stats.pop(ip, None)
        _challenge_passed.pop(ip, None)
    return was


def clear_all() -> int:
    """Nuclear reset — clear ALL state. Returns count of cleared IPs."""
    with _lock:
        n = len(_confirmed)
        _confirmed.clear()
        _rate_window.clear()
        _path_window.clear()
        _js_seen.clear()
        _first_seen.clear()
        _beacon_stats.clear()
        _challenge_passed.clear()
        _cohorts.clear()
    return n


def mark_challenge_passed(ip: str) -> None:
    with _lock:
        _challenge_passed[ip] = time.time()


def challenge_passed_recently(ip: str, within_seconds: float = 600.0) -> bool:
    with _lock:
        ts = _challenge_passed.get(ip)
    return ts is not None and (time.time() - ts) < within_seconds
