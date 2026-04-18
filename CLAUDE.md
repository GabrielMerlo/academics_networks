# academics_networks

Research project studying coauthorship networks among academic economists: how collaboration networks form and evolve, and how a researcher's position in the network relates to publication outcomes and career success.

## Scope

The current focus is economics faculty at the top 20 US economics departments (per RePEc, March 2026). The project collects faculty rosters from department websites, will link authors to their publication records, and build coauthorship graphs from those records to analyze network structure over time.

## Current state

_Last refreshed: 2026-04-18 (evening)._

- **Rosters collected**: all 20 top-20 departments. Faculty-list collection phase is done; scraping is the remaining data-collection step.
- **Scraped** (in `data/extracted/`): Harvard only (54 profs). 7 flagged as manual-review — no parseable CV (Diamond, Gonczarowski, Nagel, Pallais, Rabin, Stantcheva, Singh). 2 partial (Graves, Shengwu Li).
- **Dataset fields**: professors, papers, coauthors, employment, advisors, presentations, referee journals, students. `professors.csv` has `bachelor_institution / bachelor_year / nationality / nationality_source` columns; all blank on the existing 54 rows until re-scraped. `main_fields` populated for only 8/54 — heuristic is strict on purpose.
- **Coauthor-to-paper ratio** is 1.25 across the Harvard set — suspiciously low for economics; a sample spot-check is queued.
- **Skills** under `.claude/skills/` are local per-user artifacts (gitignored), not in the repo. Same for `session_log.md`.
- **Research question in play**: brain drain vs. brain circulation — do foreign-trained US-based economists maintain coauthorship ties to their undergrad country? The dataset is a good fit once bachelor's info is populated.
- **Next**: pick between (a) running the scraper on the 19 remaining departments, (b) back-filling nationality/bachelor for the 54 Harvard rows, (c) sampling Harvard coauthors for a data-quality check. Princeton's roster (87 rows) is unusually large — worth reviewing against the active-faculty-only rule before scraping.

## Working notes

- "Top 20" is scoped to **US** economics departments specifically — the RePEc global ranking was filtered to US-only.
- Faculty lists are a starting point. The next step is resolving each faculty member to an author identifier (e.g., RePEc/IDEAS handle, ORCID, Google Scholar) so publication and coauthorship data can be pulled.
