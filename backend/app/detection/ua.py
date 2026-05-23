"""User-Agent quality scoring."""
from __future__ import annotations

import re

KNOWN_BOT_TOKENS = (
    "bot", "spider", "crawl", "scrap", "curl/", "wget/", "python-requests",
    "httpx", "go-http-client", "java/", "okhttp", "headless", "phantomjs",
    "selenium", "playwright",
)

KNOWN_GOOD_CRAWLERS = (
    "googlebot", "bingbot", "duckduckbot", "applebot",
)

BROWSER_TOKENS = ("mozilla", "chrome", "safari", "firefox", "edge", "opera")


def ua_score(ua: str | None) -> dict:
    """Return a dict of features for the classifier + a heuristic label."""
    if not ua:
        return {
            "ua_missing": 1, "ua_known_bot": 0, "ua_known_good_crawler": 0,
            "ua_has_browser_token": 0, "ua_len": 0, "ua_label": "missing",
        }
    low = ua.lower()
    is_known_bot = int(any(t in low for t in KNOWN_BOT_TOKENS))
    is_known_good = int(any(t in low for t in KNOWN_GOOD_CRAWLERS))
    has_browser = int(any(t in low for t in BROWSER_TOKENS))
    return {
        "ua_missing": 0,
        "ua_known_bot": is_known_bot,
        "ua_known_good_crawler": is_known_good,
        "ua_has_browser_token": has_browser,
        "ua_len": len(ua),
        "ua_label": "good_crawler" if is_known_good else
                    "bot" if is_known_bot else
                    "browser" if has_browser else "unknown",
    }
