# REVIEW — epub-sorter (documentation pass)

> Read-only audit. Records contradictions, documentation debt, and skipped artefacts.
> No source, test, config, or CI file was modified.

## Contradictions found (FACT)

`CLAUDE.md` (the hand-written top block, above the generated standards section) is **stale**
relative to the actual repo:

1. **"No README description yet — `README.md` has `TODO: Add description`"** — false.
   `README.md` has a full Overview/Usage/Development description.
2. **"No unit tests currently"** — false. `tests/test_common.py` exists (~12 KB) and is wired
   into CI with an 85% coverage floor.
3. **"SonarCloud not configured"** — false. `.github/workflows/sonar.yml` runs
   `sonar-scan-python@v1.9.0` with `sonar-project.properties` (key `chrysa_epub-sorter`).
4. **PyInstaller version drift** — `CLAUDE.md` says `PyInstaller 6.19`; `pyproject.toml`
   pins `pyinstaller==6.22.0`.
5. **"ruff configured but no `ruff.toml` — uses tool defaults"** — misleading; ruff **is**
   configured inside `pyproject.toml` (`[tool.ruff]`, `[tool.ruff.lint]`), not defaults.
6. CLI command names differ between `CLAUDE.md` ("Available commands: `author_group`,
   `extract_metadata`, `find_duplicate_by_identifier`") and the actual flag-driven interface
   in `main.py`/`cli.py` (`--rename-file`, `--update-author`, `--update-title`,
   `--update-all`; steps labelled "Group By Author", "Search Duplicates By Identifiers"…).
   The `CLAUDE.md` list appears aspirational/inaccurate.

These were **not corrected** (CLAUDE.md hand block is outside this task's mandate to rewrite;
only a compact Documentation map pointer was added — see below). The owner should refresh the
"Notes / known issues" block of `CLAUDE.md`.

## Documentation debt

- `CLAUDE.md` "Notes / known issues" section needs a rewrite (items 1–6 above).
- No `PRD.md`/`TRD.md` existed and none was generated — this is a solo utility, not a
  product with a formal product/technical requirements split; REQUIREMENTS.md covers the
  need adequately (see skipped list).
- No runtime observability story (no logging/metrics beyond CLI prints) — see skipped
  OBSERVABILITY.

## Docs generated this pass

- `ARCHITECTURE.md` — component map, inheritance, data flow, deployment.
- `REQUIREMENTS.md` — REQ-PROD / REQ-TECH matrix (IMPLEMENTED where verifiable).
- `TESTING.md` — framework, commands, CI gates.
- `SECURITY.md` — secret-scan result + filesystem threat surface (no HIGH/CRITICAL).
- `DECISIONS.md` — preserved D-0001; appended reconstructed ADRs D-A…D-D.
- `REVIEW.md` — this file.

## Docs deliberately skipped (with reason)

| Doc | Reason skipped |
|---|---|
| PRD.md | Solo file-management utility; no distinct product-requirements layer beyond REQUIREMENTS.md. |
| TRD.md | Would duplicate ARCHITECTURE.md + REQUIREMENTS.md for a ~4-module tool. |
| CONSTRAINTS.md | Constraints are few and captured inline (Python 3.14, identifier-only dedup, Windows exe); no standalone value. |
| OBSERVABILITY.md | No logging/metrics/tracing in code — nothing verifiable to document (only CLI stdout + progress bars). Recorded as debt instead. |
| ROADMAP.md | No roadmap/backlog artefact in-repo; inventing one would violate "no fabrication". The only forward-looking note is the dedup limitation in `docs/reference/github-inspiration.md`. |
| GLOSSARY.md | Domain vocabulary is small and self-explanatory (EPUB, identifier, author group, processed/duplicates/failed/skipped folders); defined inline in ARCHITECTURE.md. |
| CONTRIBUTING.md | Already exists and is accurate — preserved, not touched. |
| CHANGELOG.md | Auto-generated from conventional commits via git-cliff — preserved, not touched. |

## Key UNKNOWNs

- Live test suite pass/fail status (not executed here).
- Exact contents/behaviour of `build.ps1`.
- Whether author/title strings are sanitised before becoming path segments (SECURITY.md).
- Formal ratification dates of reconstructed ADRs.
