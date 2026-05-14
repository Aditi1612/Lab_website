#!/usr/bin/env python3
"""Fetch Google Scholar metrics by scraping the profile page directly."""
import re
import json
import os
import sys
import signal
import time
from datetime import date

import requests

SCHOLAR_ID = "vlPM4HMAAAAJ"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "scholar.json")
URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _on_timeout(signum, frame):
    print("Hard timeout reached.", file=sys.stderr)
    sys.exit(1)


def parse_metrics(html):
    # Scholar renders 6 gsc_rsb_std cells: citations_all, citations_since,
    # h_index_all, h_index_since, i10_all, i10_since
    cells = re.findall(r'class="gsc_rsb_std">([0-9,]+)<', html)
    if len(cells) < 6:
        raise ValueError(
            f"Expected >=6 metric cells, found {len(cells)} — "
            "CAPTCHA or layout change"
        )

    def n(s):
        return int(s.replace(",", ""))

    return {
        "citations_all":   n(cells[0]),
        "citations_since": n(cells[1]),
        "h_index_all":     n(cells[2]),
        "h_index_since":   n(cells[3]),
        "i10_all":         n(cells[4]),
        "i10_since":       n(cells[5]),
        "last_updated":    str(date.today()),
    }


def fetch(proxies=None, label="direct", timeout=60):
    print(f"Proxy: {label}")
    r = requests.get(URL, headers=HEADERS, proxies=proxies, timeout=timeout)
    r.raise_for_status()
    return parse_metrics(r.text)


def main():
    signal.signal(signal.SIGALRM, _on_timeout)
    signal.alarm(300)  # 5-minute hard ceiling

    tor = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

    strategies = [
        (tor,  "Tor SOCKS5"),
        (None, "direct"),
    ]

    for proxies, label in strategies:
        try:
            data = fetch(proxies, label)
            signal.alarm(0)
            os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
            with open(OUTPUT, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
            print("Saved:", data)
            return
        except Exception as exc:
            print(f"  Failed ({label}): {exc}", file=sys.stderr)
            time.sleep(3)

    print("All strategies failed.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
