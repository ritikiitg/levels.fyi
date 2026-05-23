"""Per-request signal extraction. Output is a flat dict of numeric features
that feeds the scorer (rule + ML)."""
from __future__ import annotations

import ipaddress
import math
import re
from collections import Counter

from . import state
from .ua import ua_score


def _is_private_or_loopback(ip: str) -> bool:
    try:
        a = ipaddress.ip_address(ip)
        return a.is_private or a.is_loopback or a.is_link_local
    except ValueError:
        return False


def client_ip(request) -> str:
    """Resolve client IP, honoring X-Forwarded-For when present.

    In production, this MUST be restricted to trusted proxies (parse only the
    last hop from a known LB). For demo + behind Render's LB, taking the
    first XFF is acceptable and lets us see distributed-attack IP rotation.
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        first = xff.split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else "unknown"

# Header completeness — these are the headers any real browser sends.
EXPECTED_HEADERS = ("accept", "accept-language", "accept-encoding", "user-agent")

# Honeypot paths — mirrors routes/honeypot.py
HONEYPOT_PATHS = {"/internal/admin", "/api/.env", "/api/__debug__", "/api/all-salaries.json"}

# Sequential ID extractor — bots scraping by incrementing ids reveal themselves.
ID_RX = re.compile(r"/(\d+)(?:/|$)")


def _entropy(items: list[str]) -> float:
    if not items:
        return 0.0
    c = Counter(items)
    total = sum(c.values())
    return -sum((n / total) * math.log2(n / total) for n in c.values())


def _path_class(path: str) -> str:
    """Bucket the path so traversal entropy isn't blown up by unique uuids."""
    if path.startswith("/api/salaries/"):
        return "/api/salaries/:id"
    if path.startswith("/api/companies"):
        return "/api/companies"
    if path.startswith("/api/salaries"):
        return "/api/salaries"
    if path.startswith("/_defender"):
        return "/_defender"
    return path


def extract(request) -> dict:
    ip = client_ip(request)
    headers = {k.lower(): v for k, v in request.headers.items()}
    ua = headers.get("user-agent")
    path = request.url.path

    state.record_request(ip, _path_class(path))

    rate_10 = state.rate(ip, 10.0)
    rate_60 = state.rate(ip, 60.0)
    hist = state.path_history(ip)
    path_entropy = _entropy(hist)

    header_completeness = sum(1 for h in EXPECTED_HEADERS if h in headers) / len(EXPECTED_HEADERS)
    has_accept_language = int("accept-language" in headers)

    js_seen = int(state.js_seen_recently(ip))

    # sequential ID streak: count how many of the recent paths had numeric ids
    seq_hits = sum(1 for p in hist[-20:] if ID_RX.search(p))

    honeypot_hit = int(path in HONEYPOT_PATHS)

    ua_feats = ua_score(ua)

    # Real search-engine crawlers never come from loopback/private space.
    # If a request CLAIMS to be Googlebot but comes from such an IP, it's a spoof.
    if ua_feats["ua_known_good_crawler"] and _is_private_or_loopback(ip):
        ua_feats["ua_known_good_crawler"] = 0
        ua_feats["ua_known_bot"] = 1  # demote to "bot UA" category
        ua_feats["_spoofed_crawler"] = 1
    else:
        ua_feats["_spoofed_crawler"] = 0

    # ---- Phase-4 enrichments ----
    # Session shape: how many requests per second of session age?
    sess = state.session_seconds(ip)
    req_per_sec = (len(hist) / sess) if sess > 0.5 else 0.0

    # Navigation depth: unique buckets visited vs total. Bots hammer a few; humans wander.
    unique_paths = len(set(hist)) if hist else 0
    nav_diversity = (unique_paths / len(hist)) if hist else 0.0

    # Beacon-derived interaction (zeros if scraper).
    bstats = state.beacon_stats(ip)
    interaction_score = bstats["mouse"] + bstats["scroll"] * 2 + bstats["key"] * 3

    # TLS / header consistency proxy:
    # Real Chrome sends Accept-Language + sec-fetch-* + a sec-ch-ua hint.
    # Scrapers that spoof a Chrome UA usually miss these.
    claims_chrome = ua_feats["ua_has_browser_token"] and "chrome" in (ua or "").lower()
    has_sec_fetch = int(any(h.startswith("sec-fetch-") for h in headers))
    has_sec_ch_ua = int("sec-ch-ua" in headers)
    tls_inconsistency = int(claims_chrome and not (has_sec_fetch and has_sec_ch_ua))

    # Cohort fingerprint: many IPs sharing the same UA + sparse-header pattern
    # is a distributed-attack tell. We track {fingerprint -> set(IPs)} so we
    # can score cohort SIZE as a signal even when each individual IP looks fine.
    fp = f"{ua or '-'}|al={has_accept_language}|sf={has_sec_fetch}|sc={has_sec_ch_ua}"
    state.record_cohort(fp, ip)
    cohort = state.cohort_size(fp, within_seconds=60)

    out = {
        "rate_10s": rate_10,
        "rate_60s": rate_60,
        "path_entropy": round(path_entropy, 4),
        "path_history_len": len(hist),
        "header_completeness": round(header_completeness, 3),
        "has_accept_language": has_accept_language,
        "js_seen_recently": js_seen,
        "seq_id_streak": seq_hits,
        "honeypot_hit": honeypot_hit,
        "req_per_sec": round(req_per_sec, 3),
        "nav_diversity": round(nav_diversity, 3),
        "interaction_score": interaction_score,
        "tls_inconsistency": tls_inconsistency,
        "spoofed_crawler": ua_feats.pop("_spoofed_crawler", 0),
        "cohort_size": cohort,
        **{k: v for k, v in ua_feats.items() if k != "ua_label"},
    }
    out["_ua_label"] = ua_feats["ua_label"]
    out["_ip"] = ip
    out["_path"] = path
    out["_ua"] = ua or ""
    return out
