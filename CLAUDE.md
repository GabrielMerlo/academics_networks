# academics_networks

Research project studying coauthorship networks among academic economists: how collaboration networks form and evolve, and how a researcher's position in the network relates to publication outcomes and career success.

## Scope

The current focus is economics faculty at the top 20 US economics departments (per RePEc, March 2026). The project collects faculty rosters from department websites, will link authors to their publication records, and build coauthorship graphs from those records to analyze network structure over time.

## Repository layout

- `data/Top 20 Uni` — ranked list of target departments (source: RePEc, March 2026).
- `data/faculty_directory/` — per-department faculty rosters scraped from department sites. Files are named `<school>_econ_faculty.csv` with columns `Name, Position, <website-column>`. The website column name varies slightly by source (Harvard uses `Personal Website`, MIT uses `Website`); the third field holds the faculty member's personal/professional page when available and is empty otherwise.
- `reading_list/` — background literature (gitignored). Current papers:
  - Carrell, Figlio & Lusher (2022), "Clubs and the Networks in Economics Reviewing."
  - Li, Aste, Caccioli & Livan (2019), "Early coauthorship with top scientists predicts success in academic careers."
- `README.md` — one-line project description.

## Conventions

- Faculty CSVs: UTF-8, header row, one row per faculty member. Preserve diacritics in names (e.g., "Pol Antràs"). Quote fields that contain commas.
- When adding a new department, match the existing Harvard CSV schema and filename pattern.
- `reading_list/` and `.DS_Store` are gitignored; do not commit PDFs or macOS metadata.

## Working notes

- "Top 20" is scoped to **US** economics departments specifically — the RePEc global ranking was filtered to US-only.
- Faculty lists are a starting point. The next step is resolving each faculty member to an author identifier (e.g., RePEc/IDEAS handle, ORCID, Google Scholar) so publication and coauthorship data can be pulled.
