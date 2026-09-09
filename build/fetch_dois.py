"""
Resolve a DOI and the IEEE Xplore landing page for every paper, via Crossref.

The advance programs carry no DOIs. Crossref's free REST API indexes the
ISSCC and VLSI Symposium proceedings, and its `resource.primary.URL` is the
publisher's landing page (https://ieeexplore.ieee.org/document/<n>/), so one
bibliographic query per paper is enough. A candidate is accepted only when

  * its DOI belongs to the right proceedings family (10.1109/ISSCC..., or
    10.1109|10.23919/VLSI...),
  * its year equals the paper's year, and
  * its title equals the program title after normalisation, extends it
    (program titles are often cut mid-phrase), or is at least 85% similar
    over the shared opening.

Results are cached in data/dois.json (committed) so the build never needs
the network; re-running only queries papers that are not in the cache.

Usage:
    python build/fetch_dois.py              # resolve papers missing a DOI
    python build/fetch_dois.py --retry      # also re-query earlier misses
    python build/fetch_dois.py --limit 20   # smoke test

Reads data/papers.json, so run build/build.py first (and again afterwards
to fold the new links into the site data).
"""

import argparse
import html
import io
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scope  # noqa: E402
from build import strip_latex  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BUILD_DIR)
DATA_DIR = os.path.join(REPO_DIR, "data")
PAPERS_PATH = os.path.join(DATA_DIR, "papers.json")
CACHE_PATH = os.path.join(DATA_DIR, "dois.json")

API = "https://api.crossref.org/works"
MAILTO = "hyunwonch@gmail.com"          # Crossref "polite pool" contact
USER_AGENT = "PaperHistory/1.0 (https://github.com/hyunwonch/Personal.Paper_history; mailto:%s)" % MAILTO

DOI_FAMILY = {
    "ISSCC": re.compile(r"^10\.1109/isscc", re.I),
    "VLSI": re.compile(r"^10\.(1109|23919)/vlsi", re.I),
}
# Second-pass hint when the plain bibliographic query misses.
CONTAINER_HINT = {
    "ISSCC": "IEEE International Solid-State Circuits Conference",
    "VLSI": "Symposium on VLSI Circuits",
}
MIN_PREFIX_LEN = 30
FUZZY_MIN = 0.85
_TAG = re.compile(r"<[^>]+>")


def clean_crossref_title(title):
    """Crossref titles keep the publisher's markup: 'Xeon<sup>®</sup>',
    double-escaped entities ('&amp;#x2013;'), newlines and TeX ('\\boldsymbol{210}\\times')."""
    t = html.unescape(html.unescape(title or ""))
    t = _TAG.sub("", t)
    t = strip_latex(t)
    return re.sub(r"\s+", " ", t).strip()


def norm(title):
    t = scope.fold(title or "").lower()
    return re.sub(r"[^a-z0-9]+", "", t)


def clean_query(title):
    """Make the program title friendlier to a bibliographic search."""
    t = scope.fold(title or "")
    t = re.sub(r"(?<=[A-Za-z])(TM|\(TM\)|™|®)\b", "", t)   # zEnterpriseTM -> zEnterprise
    t = re.sub(r"[™®]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def strip_number(title):
    """Crossref keeps the ISSCC paper number in the title: '27.4 A 0.75-...'."""
    return re.sub(r"^\s*\d{1,2}\.\d{1,2}\s+", "", title or "")


def similarity(a, b):
    n = min(len(a), len(b))
    if n < 25:
        return 0.0
    return SequenceMatcher(None, a[:n], b[:n]).ratio()


def candidate_year(item):
    m = re.search(r"\.(20\d\d)\.", item.get("DOI", ""))
    if m:
        return int(m.group(1))
    parts = (item.get("issued") or {}).get("date-parts") or [[None]]
    return parts[0][0]


def evaluate(paper, items):
    key = norm(paper["title"])
    family = DOI_FAMILY[paper["conf"]]
    best = None
    for it in items:
        doi = it.get("DOI", "")
        if not family.search(doi):
            continue
        if candidate_year(it) != paper["year"]:
            continue
        ctitle = strip_number(clean_crossref_title((it.get("title") or [""])[0]))
        ck = norm(ctitle)
        if not ck:
            continue
        if ck == key:
            match, score = "exact", 1.0
        elif min(len(ck), len(key)) >= MIN_PREFIX_LEN and (ck.startswith(key) or key.startswith(ck)):
            match, score = "prefix", 0.99
        else:
            score = similarity(key, ck)
            if score < FUZZY_MIN:
                continue
            match = "fuzzy"
        if best is None or score > best["score"]:
            url = ((it.get("resource") or {}).get("primary") or {}).get("URL", "") or ""
            url = re.sub(r"^http://", "https://", url)
            if "ieeexplore.ieee.org" not in url:
                url = ""
            best = dict(doi=doi, url=url, title=ctitle, match=match, score=round(score, 3))
    return best


def query(title, year, hint=None, rows=5, retries=5):
    params = {
        "query.bibliographic": clean_query(title),
        "rows": rows,
        "filter": "from-pub-date:%d,until-pub-date:%d" % (year - 1, year + 1),
        "select": "DOI,title,container-title,issued,resource",
        "mailto": MAILTO,
    }
    if hint:
        params["query.container-title"] = hint
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": USER_AGENT})
    delay = 3.0
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)["message"]["items"]
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                retry_after = e.headers.get("Retry-After") if e.headers else None
                time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else delay)
                delay *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def load_cache():
    if not os.path.isfile(CACHE_PATH):
        return {}
    with open(CACHE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_cache(cache):
    ordered = {k: cache[k] for k in sorted(cache)}
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=0)
    os.replace(tmp, CACHE_PATH)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--retry", action="store_true", help="re-query papers that were not matched before")
    ap.add_argument("--limit", type=int, default=0, help="stop after N queries (smoke test)")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    if not os.path.isfile(PAPERS_PATH):
        print("data/papers.json not found; run build/build.py first")
        sys.exit(1)
    with open(PAPERS_PATH, encoding="utf-8") as f:
        papers = json.load(f)["papers"]
    cache = load_cache()

    todo = []
    for p in papers:
        if p.get("doi"):
            continue                                   # the source index already knows it
        entry = cache.get(p["key"], "missing")
        if entry == "missing" or (args.retry and entry is None):
            todo.append(p)
    if args.limit:
        todo = todo[: args.limit]
    print("[dois] %d papers, %d already have a DOI, %d cached, %d to query"
          % (len(papers), sum(1 for p in papers if p.get("doi")),
             sum(1 for p in papers if not p.get("doi") and p["key"] in cache), len(todo)))
    if not todo:
        return

    lock = threading.Lock()
    done = [0]
    matched = [0]
    errors = []

    def work(p):
        try:
            best = evaluate(p, query(p["title"], p["year"]))
            if best is None:                            # second pass: name the proceedings, look deeper
                time.sleep(0.2)
                best = evaluate(p, query(p["title"], p["year"], hint=CONTAINER_HINT[p["conf"]], rows=10))
        except Exception as e:                          # noqa: BLE001 - report, keep going
            return p, "error", str(e)
        time.sleep(0.1)                                 # stay well inside Crossref's polite-pool rate
        return p, "ok", best

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(work, p) for p in todo]
        for fut in as_completed(futures):
            p, status, result = fut.result()
            with lock:
                done[0] += 1
                if status == "error":
                    errors.append((p["key"], result))
                else:
                    cache[p["key"]] = result
                    if result:
                        matched[0] += 1
                if done[0] % 50 == 0 or done[0] == len(todo):
                    save_cache(cache)
                    print("[dois] %d/%d queried, %d matched, %d errors, %.0fs"
                          % (done[0], len(todo), matched[0], len(errors), time.time() - t0))
    save_cache(cache)

    # ---- summary -----------------------------------------------------------
    by = {}
    for p in papers:
        row = by.setdefault((p["conf"], p["year"]), [0, 0])
        row[0] += 1
        if p.get("doi") or cache.get(p["key"]):
            row[1] += 1
    print("\n[dois] papers with a direct link, per year:")
    for conf in sorted({c for c, _ in by}):
        cells = ["%d: %d/%d" % (y, by[(c, y)][1], by[(c, y)][0]) for c, y in sorted(by) if c == conf]
        print("  %s  %s" % (conf, "  ".join(cells)))
    total = sum(v[0] for v in by.values())
    linked = sum(v[1] for v in by.values())
    print("  total %d/%d (%.1f%%)" % (linked, total, 100.0 * linked / total))
    misses = [p for p in papers if not p.get("doi") and p["key"] in cache and cache[p["key"]] is None]
    if misses:
        print("\n[dois] not matched (%d); the site falls back to an Xplore search for these:" % len(misses))
        for p in misses:
            print("  %s | %s" % (p["key"], p["title"][:100]))
    if errors:
        print("\n[dois] %d requests failed (re-run to retry):" % len(errors))
        for key, err in errors[:20]:
            print("  %s: %s" % (key, err))


if __name__ == "__main__":
    main()
