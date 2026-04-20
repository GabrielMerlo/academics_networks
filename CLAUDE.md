# academics_networks

Research project studying coauthorship networks among academic economists: how collaboration networks form and evolve, and how a researcher's position in the network relates to publication outcomes and career success.

## Scope

The current focus is economics faculty at the top 20 US economics departments (per RePEc, March 2026). The project collects faculty rosters from department websites, will link authors to their publication records, and build coauthorship graphs from those records to analyze network structure over time.

## Current state

_Last refreshed: 2026-04-19._

- **Scraped**: Harvard (54) + MIT (40) = **94 active faculty** across 2 of 20 departments. Network-layer totals: **3,675 authors (94 faculty), 6,538 canonical papers, 15,106 authorship edges**.
- **MIT data-quality caveat**: 34 of 40 MIT profs are flagged `other` in `_manual_review.csv` — the scrape agent skipped presentations/referee_journals/students to stay on context budget. Those three tables are effectively Harvard-only right now. 4 MIT profs flagged `cv_not_found` (Ball, Chernozhukov, Gibbons, Mullainathan); 2 flagged `pubs_page_unparseable` (Atkin, Prelec). Rambachan has only 1 of ~20 papers (parser miss, currently unflagged).
- **Two-layer schema** (raw + derived) in place and documented in README. `build_canonical.py` rebuilds authors/papers_canonical/paper_authors from scratch on every prof commit. Canonical paper ID = `<sorted-author-lastnames>_<year>_<title-slug>`.
- **Author disambiguation is first-pass**: merges by last-name + prefix-compatible given names. Good for rare names, false-merges risk for common East Asian names. Spot-check needed before analysis.
- **Design decisions confirmed this session**: bipartite (author×paper) is the canonical storage; weighted author-author matrices are one self-join away. Keep paper titles for deduplication. `author_id` is unstable across rebuilds. External-ID resolution (RePEc > OpenAlex > ORCID) is the upgrade path for serious disambiguation but not needed for the first pass — faculty-to-faculty edges are clean via `prof_id`.
- **CV cache**: `data/cv_cache/<department>/<slug>.txt` (gitignored). Only `.txt` extractions are kept; PDFs are transient. SKILL.md updated to enforce this. Harvard cache has 2 HTML bio pages (Campbell, Dell); MIT cache has 36 `.txt` files.
- **Research question in play**: brain drain vs. brain circulation — do foreign-trained US-based economists maintain coauthorship ties to their undergrad country? Good fit once bachelor's info is populated.
- **Next**: pick between (a) re-scraping the 34 MIT profs for presentations/referee_journals/students (CVs are cached, targeted pass), (b) fixing the 2 MIT pubs-parser misses + Rambachan, (c) continuing to the remaining 18 departments, (d) starting network analysis on the Harvard+MIT slice to validate the design end-to-end. Princeton's 87-row roster still needs active-faculty-only review before scraping.

## Working notes

- "Top 20" is scoped to **US** economics departments specifically — the RePEc global ranking was filtered to US-only.
- Faculty lists are a starting point. The next step is resolving each faculty member to an author identifier (e.g., RePEc/IDEAS handle, ORCID, Google Scholar) so publication and coauthorship data can be pulled.
