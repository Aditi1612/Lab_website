#!/usr/bin/env python3
import json
import os
import sys
import signal
import time
from datetime import date

SCHOLAR_ID = "vlPM4HMAAAAJ"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "scholar.json")
MAX_RETRIES = 3
TIMEOUT_SECS = 120


def _on_timeout(signum, frame):
    print("Hard timeout reached — Scholar did not respond.", file=sys.stderr)
    sys.exit(1)


def fetch_with_tor():
    from scholarly import scholarly, ProxyGenerator
    pg = ProxyGenerator()
    pg.Tor_Internal(tor_sock_port=9050)
    scholarly.use_proxy(pg)
    print("Proxy: Tor")
    return scholarly


def fetch_with_free_proxy():
    from scholarly import scholarly, ProxyGenerator
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)
    print("Proxy: FreeProxies")
    return scholarly


def fetch_direct():
    from scholarly import scholarly
    print("Proxy: none (direct)")
    return scholarly


def get_author(scholarly_obj):
    author = scholarly_obj.fill(scholarly_obj.search_author_id(SCHOLAR_ID))
    return {
        "citations_all":   author.get("citedby", 0),
        "citations_since": author.get("citedby5y", 0),
        "h_index_all":     author.get("hindex", 0),
        "h_index_since":   author.get("hindex5y", 0),
        "i10_all":         author.get("i10index", 0),
        "i10_since":       author.get("i10index5y", 0),
        "last_updated":    str(date.today()),
    }


def main():
    signal.signal(signal.SIGALRM, _on_timeout)
    signal.alarm(TIMEOUT_SECS)

    strategies = [fetch_with_tor, fetch_with_free_proxy, fetch_direct]

    for attempt, strategy in enumerate(strategies, 1):
        try:
            print(f"\nAttempt {attempt}/{len(strategies)}: {strategy.__name__}")
            s = strategy()
            data = get_author(s)
            signal.alarm(0)

            os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
            with open(OUTPUT, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")

            print("Saved:", data)
            return

        except Exception as exc:
            print(f"  Failed: {exc}", file=sys.stderr)
            if attempt < len(strategies):
                time.sleep(5)

    print("All strategies failed.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
