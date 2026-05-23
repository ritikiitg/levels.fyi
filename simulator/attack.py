"""Bot simulator CLI for this1.

Usage:
    python attack.py --scenario naive-scraper --target http://localhost:8000
    python attack.py --scenario polite-scraper --duration 30
    python attack.py --list
"""
from __future__ import annotations

import argparse
import asyncio
import sys

from scenarios import REGISTRY


def list_scenarios() -> None:
    print("Available scenarios:\n")
    for k, cls in REGISTRY.items():
        print(f"  {k:22s} -- {cls.description}")


def main() -> None:
    ap = argparse.ArgumentParser(description="this1 attack simulator")
    ap.add_argument("--scenario", "-s", help="scenario name")
    ap.add_argument("--target", "-t", default="http://localhost:8000")
    ap.add_argument("--duration", "-d", type=float, default=30.0, help="seconds")
    ap.add_argument("--qps", type=float, default=5.0, help="approximate requests/sec")
    ap.add_argument("--list", "-l", action="store_true")
    args = ap.parse_args()

    if args.list or not args.scenario:
        list_scenarios()
        if not args.scenario:
            sys.exit(0)
        sys.exit(0)

    if args.scenario not in REGISTRY:
        print(f"Unknown scenario: {args.scenario}")
        list_scenarios()
        sys.exit(2)

    cls = REGISTRY[args.scenario]
    scenario = cls(target=args.target, duration=args.duration, qps=args.qps)
    print(f"Launching: {scenario.name}")
    print(f"  -> target:   {args.target}")
    print(f"  -> duration: {args.duration}s")
    print(f"  -> qps:      ~{args.qps}\n")

    stats = asyncio.run(scenario.run())
    print("\n=== Final stats ===")
    print(f"  sent           : {stats.sent}")
    print(f"  ok             : {stats.ok}")
    print(f"  blocked        : {stats.blocked}")
    print(f"  challenged     : {stats.challenged}")
    print(f"  decoy-suspected: {stats.decoy_suspected}")
    if stats.decoy_suspected:
        print("\n[!] Some responses contained decoy (_decoy: true) records -- the")
        print("    defender confirmed bot status and poisoned the scrape.")


if __name__ == "__main__":
    main()
