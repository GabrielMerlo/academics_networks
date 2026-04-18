---
name: end-session
description: End-of-session close-out for this project — commit and push all uncommitted work with a drafted message, refresh the "Current state" section of CLAUDE.md with a fresh snapshot of where the project stands, and append a dated entry to session_log.md summarizing what got done. Use this skill whenever the user says "end session", "close out", "wrap up", "finish up and commit everything", "save state", "let's call it a day", "we're done for today", or any other clear signal that the user is closing the session and wants it persisted cleanly so the next session picks up without friction. Do NOT trigger on a bare "commit" / "push" / "commit the README fix" — those are normal mid-session git requests, not end-of-session flows. Only trigger when the user is signaling they're done working for now, not just asking for a single commit.
---

# End-Session

Cleanly close out a working session so the next one picks up without friction. Three steps, in order.

## 1. Git close-out

Run `git status` and `git diff --stat` to see what changed.

**If the working tree is clean** (nothing staged, nothing unstaged, nothing untracked worth committing): say so and move on to step 2. Do not create empty commits.

**If there are changes:**

1. Look at the changes (use `git diff` selectively if needed; don't flood context).
2. Summarize them in 1–2 plain-English sentences — e.g., "added MIT roster and patched the JS-pubs-page fallback in SKILL.md".
3. Run `git log --oneline -5` to match the project's existing commit-message style.
4. Draft a commit message. Always end with:
   ```
   Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
   ```
5. Show the message to the user as a preview. Invoking end-session is itself the authorization to commit, so this is for transparency — not a decision point requiring re-approval.
6. `git add` only the relevant paths. Avoid `git add -A` and `git add .` so you don't sweep in files the user didn't intend (editor backups, secrets files, accidental artifacts).
7. `git commit` with the drafted message via a HEREDOC to preserve formatting.
8. `git push`.

Never use `--no-verify`, `--amend`, or force-push. If a pre-commit hook fails, stop and report — don't retry blindly, don't amend.

If untracked files look unrelated to the session's work (e.g., `/tmp/`-adjacent scratch files that landed in the repo by accident), ask before including or skipping them rather than silently deciding.

## 2. Refresh CLAUDE.md "Current state"

`CLAUDE.md` at the project root is what a fresh session reads first. One section, `## Current state`, is owned by this skill — it gets rewritten each run so it's always current, never accumulating.

- If the section exists, replace its body.
- If it doesn't exist, add it below `## Scope` and above `## Working notes`.
- Content: 3–8 terse bullets. What's been done, what's flagged, what's queued next. Examples:
  - "54 Harvard profs scraped; 7 flagged (Diamond, Gonczarowski, Nagel, Pallais, Rabin, Stantcheva, Singh) — no parseable CV"
  - "`main_fields` populated for only 8/54 Harvard rows — heuristic is strict on purpose"
  - "Next: decide whether to re-scrape flagged profs or move on to MIT roster"

If the session didn't meaningfully change project state (just exploratory reading), leave the section alone rather than rewriting it with the same content.

Don't paste commit messages or granular file diffs here — that's what git log is for. This section is a pointer to *where we are*, not *what just changed*.

## 3. Append a session log entry

`session_log.md` at the project root. Create it if missing, seeded with:

```
# Session Log

Newest entries first. See git log for file-level history.

```

Prepend a new entry immediately below that header (so newest is always on top):

```
## YYYY-MM-DD
- <3–5 specific bullets about what got done, decisions made, open questions>
```

Use the current date. Bullets should be specific enough that a future session can pick up from them. Good vs. bad:

- ❌ "updated schema"
- ✅ "Added `nationality` and `nationality_source` columns to `professors.csv`; backfilled 54 rows with blanks; new scrapes will populate"

Include open questions or deferred decisions — those are the most valuable thing a future session can see.

If the session had genuinely no meaningful activity (read a few files, didn't decide or change anything), skip this step rather than add a thin entry.

## Wrap-up

After the three steps, run `git status` once more and give a short report:

- Whether a commit was made (short SHA + pushed?)
- Whether CLAUDE.md's Current state was refreshed
- Whether a new session_log entry was added
- Anything skipped (and why)

Keep this under 8 lines.

## Guardrails

- **Don't fabricate activity.** The log entry and CLAUDE.md status must reflect what actually happened. If you're not sure what a file change was about, keep the bullet vague ("worked on the scraper") rather than invent specifics. Better a thin entry than a fake one.
- **Don't re-scope.** If files on disk changed that clearly weren't part of this session's conversation (someone's editor backups, output from another process), surface them and ask rather than silently lump them into the commit.
- **Idempotent on a clean repo.** Running the skill twice in a row when nothing has changed since the first run should be a no-op — don't duplicate a log entry, don't rewrite Current state with identical content, don't create an empty commit.
- **Not a mid-session tool.** If the user asks "commit and push the README fix" mid-session, that's a normal git request — just do it directly. This skill is only for explicit end-of-session close-outs.

## Why this exists

The point of this skill is to make sessions *durable*. A new session needs three things to land cleanly: an up-to-date repo (git push), a pointer to where things stand (CLAUDE.md Current state), and a narrative trail of how we got here (session_log.md). When those three are in sync at the end of a session, the next one starts with zero friction. When any of them are stale, the next session starts with confusion.

Prefer thinness over fabrication. A short honest log entry is worth more than a padded one.
