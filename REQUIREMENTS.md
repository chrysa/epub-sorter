# REQUIREMENTS — epub-sorter

> Derived from README, `main.py`, `common.py`, `cli.py`, `gui.py`, `docs/reference`.
> A requirement is marked **IMPLEMENTED** only where verifiable in source.

## Product requirements

| ID | Requirement | Status | Evidence |
|---|---|---|---|
| REQ-PROD-001 | Group EPUBs into `Author/` directories | IMPLEMENTED | `common.py rename_author`; `cli.py` "Group By Author"; `gui.py` |
| REQ-PROD-002 | Extract EPUB metadata to CSV | IMPLEMENTED | `common.py generate_csv`; default `epub_metadata.csv` (`main.py`) |
| REQ-PROD-003 | Detect duplicates by identifier (ISBN/UUID) and move to `[duplicates]` | IMPLEMENTED | `identifier_list.count(...) > 1` in `cli.py`/`gui.py`; `common.py` |
| REQ-PROD-004 | Rename files from title metadata; collisions to `[skipped]` | IMPLEMENTED | `common.py rename_file`; `README` |
| REQ-PROD-005 | Update author/title metadata back into the file | IMPLEMENTED | `common.py update_data` → `ebookmeta.set_metadata`; `cli.py` prompts |
| REQ-PROD-006 | Remove empty folders after sorting | IMPLEMENTED | `common.py` empty-folder logic; `cli.py` "Remove Empty Folder" |
| REQ-PROD-007 | GUI front-end (Tkinter, default) | IMPLEMENTED | `gui.py`; `main.py` default branch |
| REQ-PROD-008 | CLI front-end with progress bars | IMPLEMENTED | `cli.py` `IncrementalBar` |
| REQ-PROD-009 | Configurable output folder names + CSV path | IMPLEMENTED | `main.py` argparse flags |
| REQ-PROD-010 | Windows `.exe` packaging | INFERENCE (present, not run) | `build.ps1`; `pyinstaller` build extra |
| REQ-PROD-011 | Print a run summary (counts of duplicates/failed/processed/authors) | IMPLEMENTED | `cli.py get_summary` |

## Technical requirements

| ID | Requirement | Status | Evidence |
|---|---|---|---|
| REQ-TECH-001 | Python `>=3.14` | IMPLEMENTED | `pyproject.toml requires-python` |
| REQ-TECH-002 | Runtime deps pinned: `ebookmeta==1.2.11`, `progress==1.6.1` | IMPLEMENTED | `pyproject.toml`, `requirements.txt` |
| REQ-TECH-003 | Tests via pytest; coverage floor 85% on `common.py` | IMPLEMENTED | `pyproject.toml` `--cov-fail-under=85`; `tests/test_common.py` |
| REQ-TECH-004 | Lint via ruff | IMPLEMENTED | `pyproject.toml [tool.ruff]`; `make lint` |
| REQ-TECH-005 | Tests runnable in a container | IMPLEMENTED | `Dockerfile.test`; `make docker-test` |
| REQ-TECH-006 | CI on GitHub Actions (pre-commit, lint, test, sonar) | IMPLEMENTED | `.github/workflows/ci.yml`, `sonar.yml`, `sast.yml`, `secret-scan.yml` |
| REQ-TECH-007 | Conventional commits + changelog via git-cliff | IMPLEMENTED | `cliff.toml`; `CONTRIBUTING.md`; `CHANGELOG.md` |
| REQ-TECH-008 | Generated context files (ADR D-0012) | IMPLEMENTED | `scripts/gen_context_files.py`; `llms-full.txt`, `context-map.json`, `ai-instructions.md` |
| REQ-TECH-009 | Local quality gate | IMPLEMENTED | `.quality-gate.json`; `scripts/quality_gate.py` |
| REQ-TECH-010 | Bandit security lint config | IMPLEMENTED | `pyproject.toml [tool.bandit]` |

## Non-goals / gaps (FACT from `docs/reference/github-inspiration.md`)

- No fuzzy (title/author) deduplication and no content hashing — identifier-only.
- No packaging to PyPI / no runtime container (only a test container).
