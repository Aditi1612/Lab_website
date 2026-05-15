#!/usr/bin/env python3
"""
Fetch Google Scholar metrics.

Strategy (in order):
  1. Semantic Scholar API — free, reliable, no bot-blocking; gives citations_all + h_index_all.
  2. Google Scholar scrape via Tor SOCKS5 — may work when Scholar allows Tor exits.
  3. Google Scholar scrape direct — last resort.

If ALL sources fail the existing scholar.json is preserved unchanged (workflow exits 0).
"""
import re
import json
import os
import sys
import time
from datetime import date

import requests

SCHOLAR_ID = "vlPM4HMAAAAJ"
SCHOLAR_URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
SS_SEARCH   = "https://api.semanticscholar.org/graph/v1/author/search"
OUTPUT      = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "scholar.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def load_existing():
    try:
        with open(OUTPUT) as f:
            return json.load(f)
    except Exception:
        return {}


def save(data):
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("Saved:", data)


def fetch_semantic_scholar():
    """Query Semantic Scholar API for Diwakar Tiwari's citation stats."""
    params = {
        "query": "Diwakar Tiwari Mizoram",
        "fields": "name,citationCount,hIndex,affiliations",
        "limit": 10,
    }
    r = requests.get(SS_SEARCH, params=params, timeout=20)
    r.raise_for_status()
    authors = r.json().get("data", [])

    # Prefer an author with "Mizoram" in affiliations
    for author in authors:
        affils = " ".join(a.get("name", "") for a in author.get("affiliations", []))
        if "mizoram" in affils.lower() or "mzu" in affils.lower():
            return author.get("citationCount"), author.get("hIndex")

    # Fallback: highest-cited author matching the name
    hits = [a for a in authors if "tiwari" in a.get("name", "").lower()]
    if hits:
        best = max(hits, key=lambda a: a.get("citationCount") or 0)
        return best.get("citationCount"), best.get("hIndex")

    return None, None


def parse_scholar_html(html):
    cells = re.findall(r'class="gsc_rsb_std">([0-9,]+)<', html)
    if len(cells) < 6:
        raise ValueError(
            f"Expected >=6 metric cells, got {len(cells)} — likely CAPTCHA"
        )
    def n(s): return int(s.replace(",", ""))
    return {
        "citations_all":   n(cells[0]),
        "citations_since": n(cells[1]),
        "h_index_all":     n(cells[2]),
        "h_index_since":   n(cells[3]),
        "i10_all":         n(cells[4]),
        "i10_since":       n(cells[5]),
    }


def fetch_scholar_scrape(proxies=None, label="direct"):
    print(f"  Scholar scrape via {label}…")
    r = requests.get(SCHOLAR_URL, headers=HEADERS, proxies=proxies, timeout=60)
    r.raise_for_status()
    return parse_scholar_html(r.text)


def main():
    existing = load_existing()

    # ── Strategy 1: Semantic Scholar API ────────────────────────────────────
    try:
        cit, h = fetch_semantic_scholar()
        if cit is not None and h is not None:
            data = dict(existing)  # preserve all existing fields
            data["citations_all"] = cit
            data["h_index_all"]   = h
            data["last_updated"]  = str(date.today())
            data.setdefault("citations_since", existing.get("citations_since", 0))
            data.setdefault("h_index_since",   existing.get("h_index_since",  0))
            data.setdefault("i10_all",         existing.get("i10_all",        0))
            data.setdefault("i10_since",       existing.get("i10_since",      0))
            save(data)
            print(f"[OK] Semantic Scholar: citations={cit}, h={h}")
            return
        print("  Semantic Scholar returned no usable data.", file=sys.stderr)
    except Exception as exc:
        print(f"  Semantic Scholar failed: {exc}", file=sys.stderr)

    # ── Strategy 2 & 3: Google Scholar scraping ──────────────────────────────
    tor = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
    for proxies, label in [(tor, "Tor SOCKS5"), (None, "direct")]:
        try:
            metrics = fetch_scholar_scrape(proxies, label)
            data = {**metrics, "last_updated": str(date.today())}
            save(data)
            print(f"[OK] Google Scholar ({label})")
            return
        except Exception as exc:
            print(f"  Failed ({label}): {exc}", file=sys.stderr)
            time.sleep(3)

    # ── All sources failed — preserve existing data ──────────────────────────
    print("All sources failed. Existing scholar.json preserved.", file=sys.stderr)
    # Exit 0 so the workflow step does not fail the job


if __name__ == "__main__":
    main()
