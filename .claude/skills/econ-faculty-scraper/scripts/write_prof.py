#!/usr/bin/env python3
"""Commit one professor's extracted data to the output CSVs, idempotently.

Reads a JSON blob (schema in ../SKILL.md) and:
  1. Deletes any existing rows for this prof_id across all output CSVs
     (matched on prof_id; for coauthors.csv, matched on paper_id of this
     professor's existing papers).
  2. Appends the new rows.
  3. Marks the prof_id as processed in _processed.csv.

Re-running the same prof therefore cleanly replaces their rows.

Usage: python write_prof.py <path-to-json>
"""
import csv
import json
import sys
from pathlib import Path

# table_key -> (filename, prof_id_column, ordered fields)
TABLES = {
    "professors": (
        "professors.csv", "prof_id",
        ["prof_id", "name", "department", "current_position",
         "personal_website", "cv_url", "main_fields",
         "phd_institution", "phd_year", "job_market_paper",
         "sex", "source_url"],
    ),
    "advisors": (
        "advisors.csv", "prof_id",
        ["prof_id", "advisor_name", "source_url", "source_snippet"],
    ),
    "papers": (
        "papers.csv", "prof_id",
        ["prof_id", "paper_id", "title", "venue", "year",
         "paper_type", "source_url", "source_snippet"],
    ),
    "employment": (
        "employment.csv", "prof_id",
        ["prof_id", "institution", "position",
         "start_year", "end_year", "source_url", "source_snippet"],
    ),
    "presentations": (
        "presentations.csv", "prof_id",
        ["prof_id", "conference_name", "year",
         "paper_presented", "source_url", "source_snippet"],
    ),
    "referee_journals": (
        "referee_journals.csv", "prof_id",
        ["prof_id", "journal", "source_url", "source_snippet"],
    ),
    "students": (
        "students.csv", "prof_id",
        ["prof_id", "student_name", "year_graduated",
         "first_placement", "source_url", "source_snippet"],
    ),
}

COAUTHORS_FILE = "coauthors.csv"
COAUTHORS_FIELDS = ["paper_id", "coauthor_name"]


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def out_dir() -> Path:
    return project_root() / "data" / "extracted"


def existing_paper_ids(path: Path, prof_id: str) -> list[str]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", newline="") as f:
        return [
            row["paper_id"]
            for row in csv.DictReader(f)
            if row.get("prof_id") == prof_id
        ]


def drop_rows_by_key(path: Path, key_col: str, values: set[str]) -> None:
    if not path.exists() or not values:
        return
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        kept = [r for r in reader if r.get(key_col) not in values]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(kept)


def append_rows(path: Path, fields: list[str], rows: list[dict]) -> None:
    if not rows:
        return
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def mark_processed(prof_id: str) -> None:
    path = out_dir() / "_processed.csv"
    done: set[str] = set()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            done = {line.strip() for line in f.readlines()[1:] if line.strip()}
    if prof_id in done:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(prof_id + "\n")


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: write_prof.py <data.json>", file=sys.stderr)
        sys.exit(2)

    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    prof = data.get("professor") or {}
    prof_id = prof.get("prof_id")
    if not prof_id:
        print("professor.prof_id is required", file=sys.stderr)
        sys.exit(2)

    d = out_dir()

    # Paper IDs this prof previously had — we need them to scrub coauthors.csv.
    old_paper_ids = set(existing_paper_ids(d / "papers.csv", prof_id))

    # 1. Drop existing rows for this prof across prof-keyed tables.
    for _, (fname, key_col, _) in TABLES.items():
        drop_rows_by_key(d / fname, key_col, {prof_id})
    # Drop coauthors whose paper_id belonged to this prof.
    drop_rows_by_key(d / COAUTHORS_FILE, "paper_id", old_paper_ids)

    # 2. Append new rows.
    append_rows(d / "professors.csv", TABLES["professors"][2], [prof])
    for key, (fname, _, fields) in TABLES.items():
        if key == "professors":
            continue
        append_rows(d / fname, fields, data.get(key, []))
    append_rows(d / COAUTHORS_FILE, COAUTHORS_FIELDS, data.get("coauthors", []))

    # 3. Mark processed.
    mark_processed(prof_id)

    counts = {
        "advisors": len(data.get("advisors", [])),
        "papers": len(data.get("papers", [])),
        "coauthors": len(data.get("coauthors", [])),
        "employment": len(data.get("employment", [])),
        "presentations": len(data.get("presentations", [])),
        "referee_journals": len(data.get("referee_journals", [])),
        "students": len(data.get("students", [])),
    }
    print(f"wrote {prof_id}: " + ", ".join(f"{k}={v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
