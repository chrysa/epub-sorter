# TESTING — epub-sorter

> All commands below are transcribed from `Makefile`, `pyproject.toml`, `Dockerfile.test`
> and `CONTRIBUTING.md`. They were **not executed** (docs-only task).

## Framework (FACT)

- **pytest** with `pytest-cov` and `pytest-mock` (`pyproject.toml [project.optional-dependencies].test`).
- `testpaths = ["tests"]`; `addopts = "-v --tb=short --cov-fail-under=85"`.
- Coverage source is `common.py` only; `gui.py`, `main.py`, `cli.py`, `tests/*`, `build/*`
  are omitted. Front-ends are intentionally untested by coverage.
- Single suite file: `tests/test_common.py` (contains at least `TestGetMetadata` and
  fixtures that build a `Common` instance over `tmp_path` folders).

## Commands (FACT — from `Makefile` / `CONTRIBUTING.md`)

```bash
make install-dev   # install with test extras
make test          # pytest tests/ -v
make test-cov      # pytest with coverage (term-missing + xml), floor 85%
make lint          # ruff
make docker-test   # build Dockerfile.test and run the suite in a container
pre-commit run --all-files
```

Contributor rule (FACT, `CONTRIBUTING.md`): use `make` targets, never call
`pytest`/`ruff`/`mypy` directly on the host.

## Container test run (FACT — `Dockerfile.test`)

Multi-stage (`deps` → `test`), base `python:3.14-slim`, runs as non-root `appuser`,
entrypoint runs pytest with `--cov-report=term-missing` and `--ignore=gui.py --ignore=main.py`.

## CI gates (FACT — `.github/workflows/`)

`ci.yml` runs test + coverage on Python 3.14, uploads `test-results-3.14`, and feeds a
separate `sonar` job (`chrysa/github-actions/sonar-scan-python@v1.9.0`, project-key
`chrysa_epub-sorter`). Additional workflows: `sast.yml`, `secret-scan.yml`,
`quality-gate-check.yml`.

## Notes / verification debt

- **INFERENCE**: the suite exists and is wired into CI, but this task did not run it, so a
  live green/red status is **UNKNOWN** here.
- `CLAUDE.md` still states "No unit tests currently" — this is **stale**; a suite is
  present (see `CONTRADICTIONS` in `REVIEW.md`).
