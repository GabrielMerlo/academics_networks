#!/usr/bin/env python3
"""Initialize data/extracted/ with empty CSVs using the expected schemas.

No-op for files that already exist. Safe to run repeatedly.
"""
import csv
from pathlib import Path

SCHEMAS = {
    "professors.csv": [
        "prof_id", "name", "department", "current_position",
        "personal_website", "cv_url", "main_fields",
        "bachelor_institution", "bachelor_year",
        "phd_institution", "phd_year", "job_market_paper",
        "sex", "nationality", "nationality_source", "source_url",
    ],
    "advisors.csv": ["prof_id", "advisor_name", "source_url", "source_snippet"],
    "papers.csv": [
        "prof_id", "paper_id", "title", "venue", "year",
        "paper_type", "source_url", "source_snippet",
    ],
    "coauthors.csv": ["paper_id", "coauthor_name"],
    "employment.csv": [
        "prof_id", "institution", "position",
        "start_year", "end_year", "source_url", "source_snippet",
    ],
    "presentations.csv": [
        "prof_id", "conference_name", "year",
        "paper_presented", "source_url", "source_snippet",
    ],
    "referee_journals.csv": ["prof_id", "journal", "source_url", "source_snippet"],
    "students.csv": [
        "prof_id", "student_name", "year_graduated",
        "first_placement", "source_url", "source_snippet",
    ],
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def main() -> None:
    out_dir = project_root() / "data" / "extracted"
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, headers in SCHEMAS.items():
        path = out_dir / name
        if path.exists():
            print(f"exists   {path.relative_to(project_root())}")
            continue
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(headers)
        print(f"created  {path.relative_to(project_root())}")

    processed = out_dir / "_processed.csv"
    if processed.exists():
        print(f"exists   {processed.relative_to(project_root())}")
    else:
        with open(processed, "w", encoding="utf-8") as f:
            f.write("prof_id\n")
        print(f"created  {processed.relative_to(project_root())}")


if __name__ == "__main__":
    main()
