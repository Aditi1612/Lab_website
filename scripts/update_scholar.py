#!/usr/bin/env python3
import json
import os
import sys
from datetime import date

SCHOLAR_ID = "vlPM4HMAAAAJ"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "scholar.json")

def main():
    try:
        from scholarly import scholarly
    except ImportError:
        print("scholarly not installed", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching Scholar profile for {SCHOLAR_ID}...")
    author = scholarly.fill(scholarly.search_author_id(SCHOLAR_ID))

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

if __name__ == "__main__":
    main()
