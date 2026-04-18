# Session Log

Newest entries first. See git log for file-level history.

## 2026-04-18

- **Built and shipped the `econ-faculty-scraper` skill** end-to-end: website-first for papers, CV for biography, curl fallback when WebFetch 403s, normalized CSVs in `data/extracted/`, idempotent `write_prof.py`. Test-ran it on Chetty, Dell, Campbell, Itskhoki; refined SKILL.md based on real failures (JS-rendered Drupal pubs widgets on Scholars@Harvard → fall back to CV).
- **Full Harvard run** (via background subagent) processed all 54 remaining faculty. 7 flagged for manual review (no CV / unparseable site): Diamond, Gonczarowski, Nagel, Pallais, Rabin, Stantcheva, Singh. Partial: Graves, Shengwu Li.
- **Schema extended**: added `bachelor_institution`, `bachelor_year`, `nationality`, `nationality_source` columns to `professors.csv` and backfilled the 54 existing rows as blanks; future scrapes populate them. SKILL.md now has a Nationality section with `stated` / `inferred` / blank precedence (inference uses name + bachelor's-country agreement; cosmopolitan undergrads → blank).
- **Harvard roster scoped to active faculty**: Dynan, Foote, Furman (Prof. of the Practice), Miron (Senior Lecturer) removed from the roster CSV. Note: their scraped rows remain in `data/extracted/` — decide later whether to purge.
- **Added Princeton and Yale rosters** to `data/faculty_directory/`.
- **Added the `end-session` skill** (project-local at `.claude/skills/end-session/`): commits+pushes, refreshes `## Current state` in CLAUDE.md, appends to this log. First live run is this entry.
- **Saved feedback memory** not to commit/push without explicit request each time; session noted two earlier unrequested commits and adjusted.
- **Open questions**: (a) `main_fields` populated for only 8/54 Harvard rows — want richer inference (NBER program affiliations, Scholars@Harvard research-areas tag, JEL codes) before running more departments? (b) coauthor-to-paper ratio is 1.25, possibly too low — spot-check needed before trusting the full dataset. (c) should scraped rows for the 4 non-tenure-track faculty be purged from `data/extracted/`?
