# Architecture — epub-sorter

## Purpose

`epub-sorter` organizes and deduplicates EPUB ebook libraries. It reads EPUB
metadata (author, title, identifier) and can group files by author, extract a
metadata CSV, find duplicates by identifier (ISBN/UUID) and move them aside, and
rename files from their title metadata. Files are routed into output folders:
`[processed]`, `[duplicates]`, `[failed]`, `[skipped]`. Two front-ends share one
engine: a Tkinter GUI (default) and a progress-bar CLI.

## Stack

- Python `>=3.14` (`pyproject.toml`); Docker test image uses `python:3.14-slim`.
- Packaging: setuptools (`build-system`, `pyproject.toml`); single-source version `0.1.0`.
- Runtime deps: `ebookmeta==1.2.11` (EPUB metadata), `progress==1.6.1` (CLI progress bar).
- GUI: `tkinter` (standard library).
- Dev/test: `pytest`, `pytest-cov`, `pytest-mock`; `ruff` (lint + format), `mypy` (typecheck).
- Build (optional): `pyinstaller==6.22.0` (`--onefile` executable).
- CI badge references GitHub Actions `ci.yml` (`.github/`).

## Layout

- `main.py` — argparse entrypoint; dispatches to CLI or GUI.
- `common.py` — `Common` dataclass: the shared engine (metadata read, CSV, dedup,
  grouping, folder moves, empty-folder cleanup). Sole coverage source.
- `cli.py` — `Cli` front-end (progress-bar driven).
- `gui.py` — `Gui` Tkinter front-end (default).
- `tests/test_common.py` — unit tests for the engine.
- `scripts/` — `gen_context_files.py`, `quality_gate.py` (repo tooling, not app code).
- `docs/` — additional documentation.
- Config: `pyproject.toml`, `Makefile`, `Dockerfile.test`, `.pre-commit-config.yaml`,
  `.quality-gate.json`, `sonar-project.properties`, `cliff.toml`, `GitVersion.yml`.

## Entrypoints

- `python main.py --epub-path <folder>` — launches the GUI (default).
- `python main.py --cli --epub-path <folder> [--rename-file] [--update-author]
  [--update-title] [--update-all]` — CLI mode.
- Flags configure output folders (`--processed-folder`, `--duplicate-folder`,
  `--skipped-folder`, `--failed-folder`) and `--output-csv`; see `main.py --help`.
- `make run-gui` / `make run-cli` wrap these.

## Data / External deps

- Input: a folder of `.epub` files (default: current working directory).
- Output: `epub_metadata.csv` plus the four bracketed folders, created relative to
  the working directory.
- External libraries only: `ebookmeta` (parses EPUB metadata), `progress` (CLI UI).
  No network, database, or service dependencies.

## Build & test

Real commands (Makefile / `pyproject.toml` / `Dockerfile.test`):

```bash
make install          # pip install -r requirements.txt
make install-dev      # deps + ruff + mypy
make lint             # ruff check .
make format           # ruff format .
make typecheck        # mypy . --ignore-missing-imports
make test             # pytest tests/ -v
make test-cov         # pytest with coverage (fail-under 85, source=common.py)
make docker-test      # build Dockerfile.test and run pytest in-container
make build            # pyinstaller --onefile main.py
make ci               # lint + typecheck + test
```

Note (docs vs. manifest): `README.md` shows `pip install -e .`, while the
`Makefile` `install` target runs `pip install -r requirements.txt`; both install
the same runtime dependencies. Coverage floor is 85% (`--cov-fail-under=85`),
scoped to `common.py`; `gui.py`, `main.py`, `cli.py` are omitted from coverage.
