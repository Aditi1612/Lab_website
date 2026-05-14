#!/usr/bin/env python3
"""
Fetch DOI links for all publications via CrossRef API and patch publications.html.
Entries that already have a url= field are skipped.
Low-confidence matches are printed but NOT written (flagged for manual review).
"""
import re
import json
import time
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML_FILE = "docs/publications.html"
CROSSREF_URL = "https://api.crossref.org/works"
THRESHOLD = 0.60   # title similarity threshold (0-1)
MAILTO = "diwakarmzu@gmail.com"

def crossref_doi(title, author):
    query = f"{title} {author[:30]}"
    params = urllib.parse.urlencode({
        "query.bibliographic": query,
        "rows": 1,
        "select": "DOI,title,score",
        "mailto": MAILTO,
    })
    req = urllib.request.Request(
        f"{CROSSREF_URL}?{params}",
        headers={"User-Agent": f"DOI-fetcher/1.0 (mailto:{MAILTO})"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        items = data.get("message", {}).get("items", [])
        if not items:
            return None, 0
        item = items[0]
        doi = item.get("DOI", "")
        returned_title = " ".join(item.get("title", [""])).lower()
        score = item.get("score", 0)
        return doi, score, returned_title
    except Exception as e:
        print(f"  CrossRef error: {e}")
        return None, 0, ""

def title_similarity(a, b):
    """Simple token overlap similarity."""
    a_words = set(re.sub(r"[^\w\s]", "", a.lower()).split())
    b_words = set(re.sub(r"[^\w\s]", "", b.lower()).split())
    if not a_words:
        return 0
    return len(a_words & b_words) / len(a_words)

def strip_html(s):
    return re.sub(r"<[^>]+>", "", s)

def main():
    with open(HTML_FILE, encoding="utf-8") as f:
        html = f.read()

    # Match each pub object in the PUBS array
    # Pattern: {y:..., entries up to closing }
    entry_pattern = re.compile(
        r'(\{y:\d+,c:"(?:research|review|book)",t:"([^"]+)",a:"([^"]+)",[^}]*?\})',
        re.DOTALL,
    )

    matches = list(entry_pattern.finditer(html))
    print(f"Found {len(matches)} entries total.\n")

    updated_html = html
    offset = 0  # track index shift as we insert text

    flagged = []
    added = 0
    skipped_existing = 0

    for m in matches:
        full = m.group(1)
        title_raw = m.group(2)
        author_raw = m.group(3)

        # Skip if already has a url
        if 'url:"' in full or "url:'" in full:
            skipped_existing += 1
            continue

        title_clean = strip_html(title_raw)
        author_clean = strip_html(author_raw)

        result = crossref_doi(title_clean, author_clean)
        if len(result) == 3:
            doi, score, ret_title = result
        else:
            doi, score = result
            ret_title = ""

        sim = title_similarity(title_clean, ret_title)

        if not doi or sim < THRESHOLD:
            print(f"  [NO MATCH] {title_clean[:70]}")
            if doi:
                flagged.append((title_clean, doi, sim, ret_title))
            time.sleep(0.2)
            continue

        doi_url = f"https://doi.org/{doi}"
        print(f"  [OK  {sim:.2f}] {title_clean[:60]} → {doi}")

        # Insert url field before closing }
        new_full = full[:-1] + f',url:"{doi_url}"}}'
        start = m.start() + offset
        end = m.end() + offset
        updated_html = updated_html[:start] + new_full + updated_html[end:]
        offset += len(new_full) - len(full)
        added += 1
        time.sleep(0.15)  # polite rate limit

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(updated_html)

    print(f"\n✓ Added DOI links: {added}")
    print(f"  Skipped (already had url): {skipped_existing}")

    if flagged:
        print(f"\n⚠ Low-confidence matches (review manually):")
        for t, doi, sim, ret in flagged:
            print(f"  sim={sim:.2f}  https://doi.org/{doi}")
            print(f"    Our title:  {t[:80]}")
            print(f"    CrossRef:   {ret[:80]}")

if __name__ == "__main__":
    main()
