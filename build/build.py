"""
Build the website data for Personal.Paper_history.

Reads the merged paper index that the Personal.Python workspace produces
(paper_search/index.json: ISSCC 2010-2026 and VLSI 2010-2025 programs, with
IEEE full titles / DOIs where available), keeps only the digital /
architecture / accelerator sessions, tags every paper by topic, and writes:

    data/papers.json   - the dataset (also used by scripts / notebooks)
    data/papers.js     - the same object as window.PAPER_DATA, so index.html
                         works from file:// as well as from GitHub Pages
    build/report.txt   - every session decision and per-paper decision, plus
                         the papers that no tag rule matched; read this after
                         editing scope.py / tags.py / overrides.json

Usage:
    python build/build.py                      # source = ../Personal.Python
    python build/build.py --source D:/path/to/Personal.Python
    python build/build.py --index path/to/index.json

Abstracts and local PDF paths from the source index are deliberately not
published; only program metadata (title, authors, affiliations, session)
and public links (DOI / IEEE Xplore) go to the site.
"""

import argparse
import collections
import datetime
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scope  # noqa: E402
import tags as tagdefs  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BUILD_DIR)
DATA_DIR = os.path.join(REPO_DIR, "data")
OVERRIDES_PATH = os.path.join(BUILD_DIR, "overrides.json")
REPORT_PATH = os.path.join(BUILD_DIR, "report.txt")

DEFAULT_SOURCE = os.path.join(os.path.dirname(REPO_DIR), "Personal.Python")
INDEX_REL = os.path.join("paper_search", "index.json")

TRUNCATED_TAIL = re.compile(
    r"\b(for|with|and|of|in|to|a|an|the|using|by|on|at|from|via|through|"
    r"supporting|featuring|enabling|achieving|based|towards?|under|over|"
    r"between|into|without|within)$", re.I)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def natural_key(text):
    key = []
    for part in re.split(r"(\d+)", text or ""):
        if not part:
            continue
        key.append((0, "", int(part)) if part.isdigit() else (1, part.lower(), 0))
    return tuple(key)


_LATEX_CMD = re.compile(r"\\(?:mathbf|boldsymbol|mathrm|mathit|text|textbf|textit|rm|bm)\s*\{([^{}]*)\}")
_LATEX_SYM = {"\\mu": "μ", "\\times": "×", "\\alpha": "α", "\\beta": "β", "\\Delta": "Δ", "\\Sigma": "Σ",
              "\\sim": "~", "\\approx": "≈", "\\leq": "≤", "\\geq": "≥", "\\%": "%", "\\,": " ", "\\;": " "}


def strip_latex(text):
    """IEEE Xplore titles wrap units in TeX ('$\\mathbf{1.75}\\boldsymbol{\\mu}\\mathbf{J}$')."""
    if "\\" not in text and "$" not in text:
        return text
    for _ in range(3):                                  # commands nest a couple of levels
        text = _LATEX_CMD.sub(r"\1", text)
    for cmd, sym in _LATEX_SYM.items():
        text = text.replace(cmd, sym)
    text = re.sub(r"\^\{?2\}?", "2", text)
    text = re.sub(r"[{}$]", "", text)
    return text


def clean_title(title):
    """Fold ligatures, strip TeX, mend line-break hyphenation, collapse whitespace."""
    t = scope.fold(title or "").strip()
    t = strip_latex(t)
    t = re.sub(r"(?<=\w)- (?=[A-Za-z])", "-", t)      # "Multi- Chiplet" -> "Multi-Chiplet"
    t = re.sub(r"\s+", " ", t)
    t = t.strip(" ,;:-")
    return t


def display_title(paper):
    """Prefer the published full title; mark titles the program truncated."""
    base = clean_title(paper.get("title"))
    full = clean_title(paper.get("title_full"))
    if full and len(full) > len(base):
        return full, False
    truncated = bool(TRUNCATED_TAIL.search(base))
    return base, truncated


def paper_key(conf, year, pid):
    return "%s-%s-%s" % (conf, year, pid)


def load_overrides():
    if not os.path.isfile(OVERRIDES_PATH):
        return {}
    with open(OVERRIDES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def build(index_path):
    with open(index_path, encoding="utf-8") as f:
        source = json.load(f)
    overrides = load_overrides()
    tag_ids = {t["id"] for t in tagdefs.all_tags()}
    for key, ov in overrides.items():
        for field in ("tags", "add", "remove"):
            for t in ov.get(field, []):
                if t not in tag_ids:
                    raise SystemExit("overrides.json: unknown tag '%s' on %s" % (t, key))

    session_stats = collections.OrderedDict()   # (conf, year, sid) -> dict
    decisions = []                              # per-paper lines for mixed sessions
    papers = []
    used_overrides = set()

    for p in source:
        conf, year = p["conference"], int(p["year"])
        sid, sname, pid = p.get("session_id", ""), p.get("session_name", ""), p.get("paper_id", "")
        mode, rule = scope.session_mode(conf, sid, sname, pid)
        skey = (conf, year, sid)
        st = session_stats.setdefault(skey, dict(name=sname, mode=mode, rule=rule, total=0, kept=0))
        st["total"] += 1

        title, truncated = display_title(p)
        key = paper_key(conf, year, pid)
        ov = overrides.get(key, {})
        if ov:
            used_overrides.add(key)

        if "include" in ov:
            include, reason = bool(ov["include"]), "override"
        elif title.upper().startswith("WITHDRAWN"):
            include, reason = False, "withdrawn"
        elif mode == "core":
            include, reason = True, "core session"
        elif mode == "exclude":
            include, reason = False, "excluded session"
        else:
            include, reason = scope.paper_in_scope(title)
            decisions.append((conf, year, sid, sname, pid, include, reason, title))

        if not include:
            continue
        st["kept"] += 1

        folded = scope.fold(title)
        tag_list = ov.get("tags") or tagdefs.tag_title(folded, scope.fold(sname))
        for t in ov.get("add", []):
            if t not in tag_list:
                tag_list.append(t)
        tag_list = [t for t in tag_list if t not in ov.get("remove", [])] or [tagdefs.OTHER["id"]]
        if len(tag_list) > 1 and tagdefs.OTHER["id"] in tag_list:
            tag_list.remove(tagdefs.OTHER["id"])

        authors = p.get("authors_full") or p.get("authors") or []
        doi = (p.get("doi") or "").strip()
        url = (p.get("url") or "").strip()
        papers.append(dict(
            key=key,
            conf=conf,
            year=year,
            sid=sid,
            session=scope.fold(sname).strip() or "(unnamed session)",
            pid=pid,
            title=title,
            truncated=truncated,
            authors=[scope.fold(a).strip() for a in authors if a and a.strip()],
            affil=[scope.fold(a).strip() for a in (p.get("affiliations") or []) if a and a.strip()],
            tags=tag_list,
            doi=doi,
            url=url,
            scope=mode if reason != "override" else "override",
        ))

    unused = sorted(set(overrides) - used_overrides)
    if unused:
        print("  [warn] overrides never matched a paper: %s" % ", ".join(unused))

    papers.sort(key=lambda x: (-x["year"], x["conf"], natural_key(x["sid"]), natural_key(x["pid"])))
    return papers, session_stats, decisions


def write_outputs(papers, session_stats, decisions, index_path):
    os.makedirs(DATA_DIR, exist_ok=True)
    tag_defs = tagdefs.all_tags()
    counts = collections.Counter(t for p in papers for t in p["tags"])
    for t in tag_defs:
        t["count"] = counts.get(t["id"], 0)

    years = sorted({p["year"] for p in papers})
    per_conf = collections.Counter(p["conf"] for p in papers)
    payload = dict(
        generated=datetime.date.today().isoformat(),
        source=os.path.relpath(index_path, REPO_DIR).replace("\\", "/"),
        conferences=sorted(per_conf),
        years=years,
        groups=tagdefs.GROUPS,
        tags=tag_defs,
        papers=papers,
    )
    json_path = os.path.join(DATA_DIR, "papers.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    js_path = os.path.join(DATA_DIR, "papers.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.PAPER_DATA = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    # ---- report -----------------------------------------------------------
    lines = []
    lines.append("Personal.Paper_history build report  (%s)" % payload["generated"])
    lines.append("source: %s" % index_path)
    lines.append("")
    lines.append("== Papers kept per conference / year")
    by_cy = collections.Counter((p["conf"], p["year"]) for p in papers)
    for conf in payload["conferences"]:
        row = ["%s:" % conf]
        for y in years:
            row.append("%d=%d" % (y, by_cy.get((conf, y), 0)))
        lines.append("  " + " ".join(row))
    lines.append("  total: %d (%s)" % (len(papers), ", ".join("%s %d" % kv for kv in sorted(per_conf.items()))))
    lines.append("")
    lines.append("== Tag counts")
    for t in tag_defs:
        lines.append("  %-18s %4d  %s" % (t["id"], t["count"], t["label"]))
    lines.append("")
    lines.append("== Session decisions  (mode | kept/total | rule | session)")
    for (conf, year, sid), st in session_stats.items():
        lines.append("  %s %d S%-6s %-7s %3d/%-3d  [%s]  %s" % (
            conf, year, sid, st["mode"], st["kept"], st["total"], st["rule"], st["name"]))
    lines.append("")
    lines.append("== Per-paper decisions in MIXED / unnamed sessions")
    for conf, year, sid, sname, pid, include, reason, title in decisions:
        lines.append("  %s %s %d %-8s %-42s | %s" % (
            "+" if include else "-", conf, year, pid, reason[:42], title[:110]))
    lines.append("")
    lines.append("== Papers tagged 'other' (no title rule matched)")
    for p in papers:
        if p["tags"] == ["other"]:
            lines.append("  %s %d %-8s [%s] %s" % (p["conf"], p["year"], p["pid"], p["session"][:40], p["title"][:120]))
    lines.append("")
    lines.append("== Papers whose only tag came from the session name")
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return json_path, js_path, per_conf, counts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=DEFAULT_SOURCE, help="Personal.Python workspace (default: sibling folder)")
    ap.add_argument("--index", default=None, help="explicit path to paper_search/index.json")
    args = ap.parse_args()

    index_path = args.index or os.path.join(args.source, INDEX_REL)
    if not os.path.isfile(index_path):
        print("index not found: %s" % index_path)
        print("run 'python build_index.py' inside Personal.Python/paper_search first, "
              "or pass --index / --source")
        sys.exit(1)

    print("[build] reading %s" % index_path)
    papers, session_stats, decisions = build(index_path)
    json_path, js_path, per_conf, counts = write_outputs(papers, session_stats, decisions, index_path)

    print("[build] kept %d papers (%s)" % (
        len(papers), ", ".join("%s %d" % kv for kv in sorted(per_conf.items()))))
    print("[build] tagged 'other': %d" % counts.get("other", 0))
    print("[build] wrote %s (%.1f KB)" % (json_path, os.path.getsize(json_path) / 1024))
    print("[build] wrote %s" % js_path)
    print("[build] report: %s" % REPORT_PATH)


if __name__ == "__main__":
    main()
