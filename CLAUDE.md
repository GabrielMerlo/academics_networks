# academics_networks

Research project studying coauthorship networks among academic economists: how collaboration networks form and evolve, and how a researcher's position in the network relates to publication outcomes and career success.

## Scope

The current focus is economics faculty at the top 20 US economics departments (per RePEc, March 2026). The project collects faculty rosters from department websites, will link authors to their publication records, and build coauthorship graphs from those records to analyze network structure over time.

## Current state

_Last refreshed: 2026-04-18 (late evening)._

- **Rosters collected**: all 20 top-20 departments. Scraping is the remaining data-collection step.
- **Scraped** (Harvard only, 54 profs): raw tables in `data/extracted/` — professors, papers, coauthors, employment, advisors, presentations, referee journals, students. 7 flagged manual-review, 2 partial. `bachelor_*` and `nationality*` columns still blank on existing rows until re-scraped; `main_fields` populated for 8/54.
- **Two-layer schema now in place**. Raw layer is the audit trail (never edit in place). Derived / network-ready layer — `authors.csv`, `papers_canonical.csv`, `paper_authors.csv` — is rebuilt from scratch on every prof commit by `build_canonical.py`. Current derived totals from Harvard: **2,501 authors (54 faculty), 4,636 canonical papers, 10,494 authorship edges** (~300 cross-prof paper dedups).
- **Canonical paper ID**: `<sorted-author-lastnames>_<year>_<title-slug>` — collapses duplicate rows when two in-roster profs coauthor the same paper. No DOI dependence (DOI column is optional, currently unused).
- **Author disambiguation is first-pass**: merges names by last-name + prefix-compatible given names. Handles "John List" vs "J. List" correctly but will false-merge two different "J. Lasts" at the top of the profession. Spot-check results before analysis.
- **Manual-review log** (`_manual_review.csv`) now tracks scraper misses by reason (`website_missing / website_unreachable / cv_not_found / pdf_parse_failed / pubs_page_unparseable / other`) so isolated faculty nodes are distinguishable from failed extractions. Empty for the existing Harvard rows — will populate on re-scrape / future departments.
- **Scraper skill** (local, gitignored under `.claude/skills/`): schema docs + usage guide + error-handling rules all updated this session. `write_prof.py` now invokes `build_canonical.py` automatically after each prof commit.
- **Research question in play**: brain drain vs. brain circulation — do foreign-trained US-based economists maintain coauthorship ties to their undergrad country? Good fit once bachelor's info is populated.
- **Next**: pick between (a) running the scraper on the 19 remaining departments, (b) back-filling nationality/bachelor for 54 Harvard rows, (c) sampling Harvard coauthors for data-quality check, (d) spot-checking the author disambiguation on the 2,501 authors currently generated. Princeton's roster (87 rows) still needs active-faculty-only review before scraping.

## Working notes

- "Top 20" is scoped to **US** economics departments specifically — the RePEc global ranking was filtered to US-only.
- Faculty lists are a starting point. The next step is resolving each faculty member to an author identifier (e.g., RePEc/IDEAS handle, ORCID, Google Scholar) so publication and coauthorship data can be pulled.
