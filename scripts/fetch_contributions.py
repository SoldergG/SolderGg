#!/usr/bin/env python3
"""Scrape the public (no-auth) GitHub contributions HTML fragment and write data/contributions.json."""
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "SoldergG"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

TOOLTIP_RE = re.compile(r"(No|\d+)\s+contributions?\s+on", re.IGNORECASE)


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tooltips_by_id = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        if target:
            tooltips_by_id[target] = tip.get_text(strip=True)

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        level = int(td.get("data-level", 0))
        tip_text = tooltips_by_id.get(td.get("id"), "")
        m = TOOLTIP_RE.search(tip_text)
        if m:
            count = 0 if m.group(1).lower() == "no" else int(m.group(1))
        else:
            count = 0
        days.append({"date": d, "level": level, "count": count})

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days):
    longest = current = 0
    running = 0
    for day in days:
        if day["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    for day in reversed(days):
        if day["count"] > 0:
            current += 1
        else:
            if day["date"] != days[-1]["date"] or current > 0:
                break
            # today can be a zero-count day in progress; skip it, don't break the streak
            if day["date"] == date.today().isoformat():
                continue
            break

    best_day = max(days, key=lambda x: x["count"], default=None)

    monthly = defaultdict(int)
    for day in days:
        monthly[day["date"][:7]] += day["count"]

    return {
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
    }


def main():
    days = fetch_days()
    if not days:
        print("No contribution days parsed — GitHub markup may have changed.", file=sys.stderr)
        sys.exit(1)

    total = sum(d["count"] for d in days)
    payload = {
        "username": USERNAME,
        "total_last_year": total,
        "days": days,
        "stats": compute_stats(days),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT_PATH} — {total} contributions across {len(days)} days")


if __name__ == "__main__":
    main()
