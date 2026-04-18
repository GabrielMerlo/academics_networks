# academics_networks

This project studies networks of economics researchers and their coauthors, how those collaboration networks evolve over time, and how network position may shape publication outcomes.

## Scope and data collection notes

_Last updated: 2026-04-18._

- **Departments**: we work with the top 20 US economics departments per the RePEc ranking (March 2026). Economists who sit in business schools, policy schools, or other departments are not included, even when they clearly do economics research.
- **Roster freshness**: faculty lists are scraped from each department's public directory and may lag current appointments. We don't systematically reconcile them against other sources.
- **Who counts as faculty**: only active faculty. We exclude lecturers, emeritus professors, and people listed only as affiliated or courtesy appointments.

## Data layout

Extracted data lives in `data/extracted/` and comes in two layers.

**Raw layer — the audit trail.** One row per (focal-prof, paper/event). Every row carries `source_url` + `source_snippet` so any claim can be traced back to the CV or website it came from. Do not hand-edit these files; re-run the scraper instead.

- `professors.csv` — one row per faculty member (`prof_id`, name, department, current_position, personal_website, cv_url, main_fields, bachelor_institution, bachelor_year, phd_institution, phd_year, job_market_paper, sex, nationality, nationality_source).
- `papers.csv` — one row per (prof, paper). Duplicates exist when two in-roster profs coauthor the same paper — dedup happens in the derived layer.
- `coauthors.csv` — one row per (paper, coauthor_name). Free-text names; canonicalization happens in the derived layer.
- `employment.csv`, `advisors.csv`, `students.csv`, `presentations.csv`, `referee_journals.csv` — per-prof biographical histories, all keyed on `prof_id`.
- `_processed.csv` — list of `prof_id`s already scraped (for resumability).
- `_manual_review.csv` — `prof_id, reason, note`. Records scraper misses so you can tell a real network isolate from a failed extraction. Reasons: `website_missing`, `website_unreachable`, `cv_not_found`, `pdf_parse_failed`, `pubs_page_unparseable`, `other`.

**Derived / network layer — rebuilt from scratch on every scraper commit.** Do not hand-edit.

- `authors.csv` — one row per disambiguated human. Columns: `author_id, display_name, name_variants, prof_id_if_faculty, is_faculty`. Joins back to `professors.csv` on `prof_id_if_faculty` when the author is in-roster faculty.
- `papers_canonical.csv` — one row per distinct paper. Columns: `canonical_paper_id, title, venue, year, paper_type, doi`. `canonical_paper_id` is `<sorted-author-lastnames>_<year>_<title-slug>` — papers that appeared on multiple in-roster profs' CVs collapse to a single row here.
- `paper_authors.csv` — bipartite edge list: `canonical_paper_id, author_id`. This is the file to read when building the coauthorship graph.

### How to use the tables

**Roster-level biographical questions** (who has a Spanish bachelor's? what fraction of Harvard faculty got their PhD at MIT?) → `professors.csv` alone.

**Individual-career histories** → join `professors.csv` with `employment.csv`, `advisors.csv`, `students.csv`, `presentations.csv`, `referee_journals.csv` on `prof_id`.

**Paper-level audit / source tracing** — "where did we learn this paper exists?" → `papers.csv` + `coauthors.csv`. These keep the `source_url` / `source_snippet` provenance and are the only place to verify that a row wasn't hallucinated.

**Coauthorship network** (the main event) → use the derived layer:
- Nodes: `authors.csv`. Filter `is_faculty == true` to restrict to top-20-department faculty.
- Bipartite edges (author ↔ paper): `paper_authors.csv`.
- Paper attributes: `papers_canonical.csv` (use for time slicing by `year` or top-5 filtering by `venue`).
- One-mode coauthor projection: self-join `paper_authors.csv` on `canonical_paper_id` to get (author_a, author_b, shared_paper_count).

**Brain-drain-style questions** (do foreign-trained US faculty coauthor with their undergrad country?) → join `authors.csv` → `professors.csv` on `prof_id_if_faculty` for attribute data (bachelor institution, nationality), then read edges from `paper_authors.csv`.

**Time-sliced networks** → filter `papers_canonical.csv` by `year`, then inner-join with `paper_authors.csv`.

**Published-only vs. working-paper networks** → filter `papers_canonical.csv` on `paper_type`.

### Caveats

- **Author disambiguation is first-pass.** Names are merged by last name + prefix-compatible given names. This handles "John List" vs. "J. List" correctly but will false-merge two genuinely different "J. Lasts" — spot-check before trusting centrality metrics.
- **`author_id` is a derived-layer key** and may shift across rebuilds when new data arrives. Do not treat it as a stable external identifier until the dataset is finalized.
- **DOI column is optional**, currently unused — working papers don't have one, and the network construction doesn't depend on it.
