# ARCHITECTURE — epub-sorter

> Docs-only artefact. Tags: **FACT** (verified in-repo), **INFERENCE** (reasoned from
> evidence), **UNKNOWN** (not determinable from the repo). No source was modified.

## Purpose (FACT)

`epub-sorter` is a Python tool that organises and deduplicates an EPUB ebook library by
reading each file's embedded metadata (author, title, identifier) via the `ebookmeta`
library. Source: `README.md`, `docs/reference/github-inspiration.md`, `common.py`.

## Component map (FACT)

| File | Role |
|---|---|
| `main.py` | Entry point. `argparse` CLI; dispatches to `Cli` (`--cli`) or `Gui` (default). |
| `common.py` | `Common` dataclass — shared engine: EPUB detection, metadata extraction, CSV export, author grouping, file renaming, duplicate detection helpers, empty-folder cleanup. |
| `cli.py` | `Cli(Common)` — progress-bar front-end using `IncrementalBar` (`progress` package). |
| `gui.py` | `Gui(Common)` — Tkinter desktop front-end (`tkinter`, stdlib). |
| `build.ps1` | PowerShell script; builds a Windows `.exe` via PyInstaller. (FACT: file present; contents not re-read here — INFERENCE from `README`/`CLAUDE.md`.) |
| `tests/test_common.py` | pytest suite targeting `common.py`. |
| `scripts/gen_context_files.py` | Generates `llms-full.txt`, `context-map.json`, `ai-instructions.md` (ADR D-0012). |
| `scripts/quality_gate.py` | Local quality-gate runner (`.quality-gate.json`). |

## Inheritance model (FACT)

`Common` is the base dataclass holding all filesystem + metadata logic. `Cli` and `Gui`
both inherit from it and add a presentation loop. Confirmed in `cli.py` (`class Cli(Common)`)
and `gui.py` (`class Gui(Common)`).

## Data flow (INFERENCE from `common.py` / `cli.py` / `gui.py`)

1. `detect_epubs()` — `rglob("*.epub")` under `epub_path`, filtered against the managed
   output folders.
2. `extract_metadata(epub)` — calls `ebookmeta.get_metadata(path)`; moves the file to the
   `[processed]` folder on success or `[failed]` on exception; appends a record to
   `self.data` (dict with `metadata`, `path`, `is_duplicate`, `is_failed`, ...).
3. `generate_csv()` — writes `epub_metadata.csv` from `self.data`.
4. Author grouping — `rename_author()` builds an `Author/` sub-directory from
   `metadata.author_list` and moves the file there.
5. Duplicate detection — identifiers accumulate in `identifier_list`; any identifier with
   `count > 1` marks the extra copies as duplicates, moved to `[duplicates]`.
6. Rename — `rename_file()` renames processed EPUBs from title metadata; collisions go to
   `[skipped]`.
7. Metadata update — `update_data()` can call `ebookmeta.set_metadata(...)` to rewrite
   author/title back into the file (CLI prompts `y/N`).

## Output folders (FACT — defaults from `main.py`)

`[processed]`, `[duplicates]`, `[skipped]`, `[failed]`, plus CSV `epub_metadata.csv`. All
overridable via flags.

## Coupling constraints (FACT)

- Coverage is measured only on `common.py`; `gui.py`, `main.py`, `cli.py` are omitted
  (`pyproject.toml [tool.coverage.run].omit`). The engine is the tested unit; front-ends
  are thin.
- Duplicate detection is by exact `metadata.identifier` only — no fuzzy title/author match,
  no content hashing (FACT: `docs/reference/github-inspiration.md` calls this the weakest
  point vs. state of the art).

## Deployment (FACT / INFERENCE)

- Run directly with Python `>=3.14` (`pyproject.toml requires-python`).
- Windows `.exe` packaging via PyInstaller `build` extra (`pyinstaller==6.22.0`).
- `Dockerfile.test` (multi-stage: `deps` → `test`, non-root `appuser`, `python:3.14-slim`)
  runs the test suite in a container. No runtime/production Dockerfile or compose file is
  present (FACT).

## Unknowns

- **UNKNOWN**: whether the GUI has been validated on non-Windows platforms (Tkinter is
  cross-platform, but no evidence either way).
- **UNKNOWN**: exact behaviour of `build.ps1` beyond "build .exe" (file not re-read here).
