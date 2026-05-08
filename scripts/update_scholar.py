#!/usr/bin/env python3
import json
import os
import sys
import signal
from datetime import date

SCHOLAR_ID = "vlPM4HMAAAAJ"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "scholar.json")
TIMEOUT_SECS = 90


def _on_timeout(signum, frame):
    print("Timed out waiting for Google Scholar — keeping existing data.", file=sys.stderr)
    sys.exit(0)


def main():
    try:
        from scholarly import scholarly, ProxyGenerator
    except ImportError:
        print("scholarly not installed", file=sys.stderr)
        sys.exit(1)

    # Hard 90-second ceiling so the job never hangs for minutes
    signal.signal(signal.SIGALRM, _on_timeout)
    signal.alarm(TIMEOUT_SECS)

    try:
        # Route through a free proxy to reduce bot-detection blocks
        pg = ProxyGenerator()
        try:
            if pg.FreeProxies():
                scholarly.use_proxy(pg)
                print("Using free proxy.")
        except Exception:
            print("Could not set up proxy — trying direct.", file=sys.stderr)

        print(f"Fetching Scholar profile for {SCHOLAR_ID} …")
        author = scholarly.fill(scholarly.search_author_id(SCHOLAR_ID))
        signal.alarm(0)  # cancel timeout on success

        data = {
            "citations_all":   author.get("citedby", 0),
            "citations_since": author.get("citedby5y", 0),
            "h_index_all":     author.get("hindex", 0),
            "h_index_since":   author.get("hindex5y", 0),
            "i10_all":         author.get("i10index", 0),
            "i10_since":       author.get("i10index5y", 0),
            "last_updated":    str(date.today()),
        }

        os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
        with open(OUTPUT, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

        print("Saved:", data)

    except Exception as exc:
        signal.alarm(0)
        print(f"Scholar fetch failed: {exc}", file=sys.stderr)
        print("Keeping existing data.", file=sys.stderr)
        sys.exit(0)  # don't mark the workflow as failed


if __name__ == "__main__":
    main()
