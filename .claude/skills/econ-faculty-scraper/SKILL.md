---
name: econ-faculty-scraper
description: Extract structured biographical and publication data from economics faculty personal websites and CV PDFs into normalized relational CSVs in data/extracted/. Use this skill whenever the user wants to scrape, extract, pull, collect, or build a dataset from economics faculty pages or CVs — triggers include "run the scraper", "extract faculty data", "pull coauthors for Harvard", "build the publications dataset", "process the MIT roster", "populate data/extracted", or any request referencing a file in data/faculty_directory/. Also trigger when the user asks to harvest papers, coauthors, advisors, PhD info, employment history, students, presentations, or referee journals from econ faculty sources. Prefer this skill over ad-hoc scraping so outputs stay consistent across departments.
---

# Econ Faculty Scraper

## What this does

Reads a department roster CSV (e.g., `data/faculty_directory/harvard_econ_faculty.csv`). For each professor, visits the personal website, locates and reads the CV (PDF preferred over on-site HTML), and extracts structured biographical and publication data into normalized relational CSVs in `data/extracted/`.

The goal is a cross-department dataset for coauthorship-network research. The output CSVs append cleanly across departments — running this skill on MIT after Harvard adds to the same files, keyed by `prof_id`.

## Invocation

The user provides a department roster path:

> "run econ-faculty-scraper on data/faculty_directory/harvard_econ_faculty.csv"

If no path is given, ask which department to process. If the user names a specific professor, run the per-professor workflow for just that person.

Roster CSVs have columns `Name, Position, <website-column>`. The website column is named `Personal Website` on some rosters and `Website` on others — detect it by matching any header containing "website" (case-insensitive).

## Output directory and schemas

At the start of a run, initialize the output directory:

```bash
python3 .claude/skills/econ-faculty-scraper/scripts/init_extracted.py
```

This creates `data/extracted/` and seeds the empty CSVs below with correct headers. It's a no-op if they already exist.

### professors.csv
`prof_id, name, department, current_position, personal_website, cv_url, main_fields, phd_institution, phd_year, job_market_paper, sex, source_url`

### advisors.csv
`prof_id, advisor_name, source_url, source_snippet`

### papers.csv
`prof_id, paper_id, title, venue, year, paper_type, source_url, source_snippet`
- `paper_type` is `published` or `working`
- `venue` is the journal for published papers; blank for working papers

### coauthors.csv
`paper_id, coauthor_name` — one row per coauthor of each paper (exclude the subject professor)

### employment.csv
`prof_id, institution, position, start_year, end_year, source_url, source_snippet`

### presentations.csv
`prof_id, conference_name, year, paper_presented, source_url, source_snippet`
These are talks the professor **gave** — "Presentations", "Invited Talks", "Seminars Presented", "Conference Presentations". Do NOT include sections like "Conferences Attended".

### referee_journals.csv
`prof_id, journal, source_url, source_snippet`

### students.csv
`prof_id, student_name, year_graduated, first_placement, source_url, source_snippet`

### _processed.csv
One column: `prof_id`. Profs listed here are skipped on subsequent runs.

## ID conventions

`prof_id` = `<department>_<lastname>_<firstname>`, lowercase, ASCII-folded, punctuation stripped, spaces as underscores.
- "Pol Antràs" at Harvard → `harvard_antras_pol`
- "N. Gregory Mankiw" → `harvard_mankiw_n_gregory` (drop periods; multi-part first names joined with `_`)
- "Gita Gopinath" → `harvard_gopinath_gita`

`paper_id` = `<prof_id>_<paper_type>_<3-digit-seq>`, with `seq` starting at `001` per (prof, paper_type), counting in the order the source lists them.
- `harvard_antras_pol_published_001`
- `harvard_antras_pol_working_001`

## No-fabrication guardrail — READ THIS

This is the single most important rule in this skill. A coauthorship-network dataset is worthless if it contains hallucinated papers, coauthors, or advisors.

**Only emit a row if the data for that row is explicitly present in the source you just read.** If the CV doesn't state a year, leave `year` blank. If the website doesn't list advisors, don't add rows to `advisors.csv`. Never guess a coauthor from a title. Never fill in a PhD year from memory because "I'm pretty sure Shleifer got his PhD in 1986."

Every row you write to a non-professors CSV must have:
- `source_url` — the URL of the page or PDF you read the data from
- `source_snippet` — a ~100–200 character quote from that source that contains the fact

If you can't produce a real `source_snippet`, you shouldn't be writing the row.

**Examples:**
- ✅ CV says "Ph.D., Economics, MIT, 2003 (advisors: Daron Acemoglu, Simon Johnson)." → `professors.csv`: `phd_institution=MIT, phd_year=2003`; two rows in `advisors.csv` with that snippet.
- ❌ Homepage just says "MIT PhD, 2000s." → `phd_institution=MIT` is fine, but `phd_year` must stay blank.
- ❌ The professor is famous and you remember their JMP. **Do not fill it in** unless the current source says so.
- ❌ The CV is unavailable. Do NOT fall back to your prior knowledge — emit the `professors.csv` row with the roster data (`name, position, personal_website`) and leave CV-derived fields blank.

When in doubt, leave it blank. Blank beats wrong by a wide margin here.

## Source-of-truth rules

The website and the CV play different roles. Follow this split carefully:

- **Papers and coauthors → the website is the source of truth.** Professor CVs are often months or years out of date, while personal sites (publications pages, Google Scholar widgets) tend to be current. Always try the website's publications listing first. Use the CV only as a fallback or supplement.
- **Everything else → the CV is the source of truth.** Education (PhD institution/year, job market paper), advisors, employment history, presentations/invited talks, refereeing, PhD students, and main fields all live on the CV. The website rarely has these in reliable form.

When the same paper appears on both the website and the CV, keep the website version (source_url = website pubs page) — its venue/year info is more likely correct. For papers only on the CV, include them with source_url = CV URL.

## Fetching web content

Try `WebFetch` first. Some sites (notably `*.scholars.harvard.edu`) return 403 to WebFetch; when that happens, fall back to `curl` with a desktop browser user-agent and then parse the HTML with `Grep` / `Read`:

```bash
curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36" "<url>" -o /tmp/<name>.html
```

Use this same curl pattern to download CV PDFs. If WebFetch succeeds but the visible content is under ~500 chars or reads like a JavaScript placeholder ("Enable JavaScript to run this app"), treat the site as unreachable and move on with roster data only — don't fabricate anything.

## Per-professor workflow

1. **Compute `prof_id`.** Check `data/extracted/_processed.csv`. If already listed, skip (unless the user explicitly asked to re-scrape this prof).
2. **Fetch the personal website** (see "Fetching web content"). If unreachable, skip to step 7 with roster data only.
3. **Find the publications page on the website** and extract papers + coauthors from it (see "Publications: website first"). Record `source_url` = the publications page URL for each paper row. If no dedicated publications page exists, this set is empty and papers come from the CV instead.
4. **Find and download the CV** (see "CV discovery"). Prefer a PDF; download with curl and use the `anthropic-skills:pdf` skill (or the `Read` tool, which handles PDFs natively) to extract text. If no PDF exists, use the on-site CV/bio content.
5. **From the CV, extract biographical fields**: PhD institution/year, job market paper, advisors, employment, presentations, referee journals, students, main fields. Record `source_url` = CV URL (or the relevant website URL if CV is HTML) for each row.
6. **Supplement papers from the CV** — any paper on the CV whose title doesn't match a paper already pulled from the website. Compare titles case-insensitively, ignoring punctuation and leading articles.
7. **Build the JSON blob** (structure below) and save to `/tmp/prof_data.json`. If neither the website nor the CV yielded useful data, still emit a professors.csv row with the roster's name, position, and personal_website.
8. **Commit atomically**: run `python3 .claude/skills/econ-faculty-scraper/scripts/write_prof.py /tmp/prof_data.json`. The script deletes any existing rows for this `prof_id` across all tables, appends the new rows, and marks the prof as processed. Re-runs are therefore clean.
9. **Log progress**: `[12/58] harvard_antras_pol — website pubs=36, CV pubs+=4, working=8, coauthors=47, students=12`.

## Publications: website first

Find the publications page on the website — nav links like "Publications", "Research", "Papers", "Articles"; common URLs `/publications`, `/research`, `/papers`. Fetch it (same rules as the homepage). If the site uses a widget (Google Scholar embed, BibTeX-rendered list), the HTML usually still contains the titles, venues, and years.

For each paper on the page, extract:
- title
- venue (journal name for published; blank for working papers)
- year (from the citation; blank if not shown)
- paper_type (published vs. working — use the section header on the page)
- coauthors (every listed author other than the subject professor, in order)

If the website labels its list "Selected Publications" or clearly only shows a subset, **also** pull from the CV and merge. If no publications page exists at all, use the CV as the sole source.

Some publications pages (Drupal widgets on Scholars@Harvard, filterable React/Angular apps) render the list via JavaScript and never produce a parseable linear HTML list — every paper appears as a noisy card or is duplicated across pagination. If the page looks like this (lots of filter controls, unstructured duplicates, or empty `<div>` placeholders), **treat the website pubs page as unparseable and fall back to the CV** for that prof. That's a legitimate outcome; just record in your progress log that the website pubs were unavailable.

The `source_url` for a website-sourced paper is the publications page URL (not the homepage). For CV-sourced papers, source_url = CV URL.

### JSON blob shape

```json
{
  "professor": {
    "prof_id": "harvard_antras_pol",
    "name": "Pol Antràs",
    "department": "harvard",
    "current_position": "Robert G. Ory Professor of Economics",
    "personal_website": "https://antras.scholars.harvard.edu/",
    "cv_url": "https://example.com/cv.pdf",
    "main_fields": "International Trade; Multinational Firms",
    "phd_institution": "MIT",
    "phd_year": "2003",
    "job_market_paper": "Firms, Contracts, and Trade Structure",
    "sex": "male",
    "source_url": "https://example.com/cv.pdf"
  },
  "advisors": [
    {"prof_id": "...", "advisor_name": "...", "source_url": "...", "source_snippet": "..."}
  ],
  "papers": [
    {"prof_id": "...", "paper_id": "...", "title": "...", "venue": "...", "year": "...", "paper_type": "published", "source_url": "...", "source_snippet": "..."}
  ],
  "coauthors": [
    {"paper_id": "...", "coauthor_name": "..."}
  ],
  "employment": [
    {"prof_id": "...", "institution": "...", "position": "...", "start_year": "...", "end_year": "...", "source_url": "...", "source_snippet": "..."}
  ],
  "presentations": [
    {"prof_id": "...", "conference_name": "...", "year": "...", "paper_presented": "...", "source_url": "...", "source_snippet": "..."}
  ],
  "referee_journals": [
    {"prof_id": "...", "journal": "...", "source_url": "...", "source_snippet": "..."}
  ],
  "students": [
    {"prof_id": "...", "student_name": "...", "year_graduated": "...", "first_placement": "...", "source_url": "...", "source_snippet": "..."}
  ]
}
```

Any array can be empty. Any string field can be `""`. Don't include keys not listed above.

## CV discovery

Heuristics, in priority order:
1. An anchor with visible text matching `CV`, `Curriculum Vitae`, `Vita`, or `Resume`, whose href ends in `.pdf`.
2. An anchor with that text whose href points to another page; follow it and repeat step 1.
3. Any link ending in `.pdf` that has "cv" or "vita" in its filename or link text.
4. Common paths: `/cv.pdf`, `/CV.pdf`, `/files/cv.pdf`, `/assets/cv.pdf`.
5. If the site has a dedicated "CV" tab/page without a PDF, use that HTML as the CV source.

If multiple PDFs match, prefer the one most likely to be a CV (path or link text contains "cv"/"vita"), and among those prefer the most recent-looking (`cv_2025.pdf` over `cv_2018.pdf`).

If nothing matches, treat as CV-not-found.

## Extraction heuristics

**PhD institution / year**: in an "Education" section, look for `Ph.D.`, `PhD`, `D.Phil.`, `Doctor of Philosophy`. The year is usually adjacent or parenthesized. Don't confuse with postdoc, M.A., M.Sc., or B.A. listings.

**Advisors / supervisors**: CVs sometimes list them explicitly under the PhD line — `Advisors:`, `Committee:`, `Supervisors:`, `Dissertation committee:`. If not explicitly stated, leave blank. Never infer.

**Job market paper**: look for the literal header "Job Market Paper" or a labeled entry. Some professors retain the label indefinitely; others drop it after tenure. If absent, leave blank.

**Published vs. working**: section headers carry the signal. "Publications", "Published Papers", "Refereed Articles", "Journal Articles" → `paper_type=published`. "Working Papers", "Under Review", "Submitted", "Unpublished Manuscripts" → `paper_type=working`. A paper marked "forthcoming" is typically in the published section and goes in as `published` with `venue` = the forthcoming journal (no year if no year is given).

**Coauthors**: parse every author name other than the subject professor. Preserve order. If the CV uses "with X, Y, Z" phrasing, those are the coauthors. If authors are comma-listed ("Antràs, P., Helpman, E."), the subject is one of them — exclude.

**Employment**: "Academic Positions", "Appointments", "Employment", "Professional Experience". Each entry usually has institution, position, and year range. Current position often has `—present` or no end year.

**Presentations**: "Presentations", "Invited Talks", "Seminars Presented", "Conference Presentations", "Invited Seminars". Each entry typically has (venue, year) and sometimes a paper title.

**Referee journals**: "Refereeing", "Reviewer for", "Referee for", "Ad hoc reviewer". List of journal names.

**Students**: "Ph.D. Students", "Ph.D. Advisees", "Graduate Advisees", "Thesis Committees Chaired". Include `year_graduated` and `first_placement` only if stated.

**Main fields of research**: usually on the homepage ("My research interests are..." / "Fields: ..."). Store as a single string, semicolon-separated if multiple.

## Sex inference

Infer from the first name using common conventions ("David" → male, "Amanda" → female). Leave blank when the name is ambiguous ("Robin", "Pat", "Sam", "Alex", most non-English names you're unsure about). If the website has a clear profile photo and the name is ambiguous, the photo can resolve it; otherwise leave blank.

This field is for aggregate statistics. Blank is always better than a guess.

## Resumability

`_processed.csv` is the source of truth for "this prof is done". Skip any `prof_id` that appears there unless the user asks to re-scrape.

To re-scrape a single prof, the user can delete that line from `_processed.csv` and re-run. The `write_prof.py` script cleanly replaces rows on re-run.

## Error handling

Don't let one bad professor kill the run.

- Website 404 / timeout / empty: emit only the `professors.csv` row (with roster data), skip everything else, log the failure.
- PDF fails to parse: fall back to the on-site CV content.
- Roster row has a blank website: emit only the `professors.csv` row.
- Fetch the next prof. Keep going.

## Summary report

At the end of a department run, print:

```
=== Summary: harvard ===
Roster:         58
Processed now:  54
Skipped:         4  (already in _processed.csv)
CV found:       47  (39 PDF, 8 HTML)
No CV:           7
Mean per prof:  published=32, working=9, coauthors=41, presentations=18
Zero rows flagged: 3
  - harvard_xxx_yyy: website returned empty
  - harvard_zzz_www: CV not found and site had no bio content
  - harvard_aaa_bbb: PDF failed to parse
```

## Site-specific tips

- **Scholars @ Harvard** (`*.scholars.harvard.edu`): WebFetch often gets a **403** here — fall back to `curl -A <browser-UA>` immediately. "CV" is usually a top-nav link at `/biocv`; the PDF is typically at `/sites/g/files/.../..._cv_<date>.pdf`. There's also often a separate "Publications" tab that's the preferred source for papers.
- **MIT Econ** (`economics.mit.edu/people/faculty/...`): the MIT page is usually a stub that links to the professor's personal site. Follow the outbound link and treat *that* as the personal website.
- **Google Sites / Jekyll / GitHub Pages**: typically have a "CV" tab with a PDF upload. Navigation is usually explicit.
- **Custom domains** (e.g., `rajchetty.com`): vary widely. Read the nav carefully.

If WebFetch returns a JS-placeholder page (very little visible text, mentions "Enable JavaScript"), treat as CV-not-found and move on — don't fabricate content.
