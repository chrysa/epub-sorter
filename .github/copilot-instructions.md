# epub-sorter — Copilot Instructions

## Project Overview

CLI tool to sort and organize `.epub` e-book files by metadata (author, title, series).

## Stack

- **Language**: Python 3.12+ (target 3.14)
- **Entry point**: `cli.py` / `main.py`
- **Quality**: pre-commit, ruff, mypy

## Key Constraints

- **Python 3.12+** — use `list[str]`, `str | None`, PEP 585/604 syntax
- **Typed** — ALL public functions must have complete type annotations
- **No `shell=True`** in subprocess calls
- `from __future__ import annotations` in every Python file
- `argv` pattern: `main(argv: Sequence[str] | None = None)`

## Development Workflow

1. Branch from `main`
2. `pre-commit run --all-files` before pushing
3. PRs require CI to pass
