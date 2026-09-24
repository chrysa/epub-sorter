---
name: gen-tests-cli-gui
description: 'Generate pytest tests for cli.py and gui.py in epub-sorter. Use when the user explicitly asks to add tests for the CLI or GUI, or to close the coverage gap on cli.py/gui.py.'
disable-model-invocation: true
---

# Generate tests for cli.py / gui.py

## When to invoke

User-only: an explicit "add tests for cli.py / gui.py" or "close the coverage gap" request.
Not auto-invoked — this is a targeted action, not background knowledge.

## Context

- `tests/test_common.py` exists; `cli.py` and `gui.py` have no dedicated test file yet.
- Repo gate: `pytest --cov-fail-under=85`.
- Both `Cli` (cli.py) and `Gui` (gui.py) subclass `Common` (common.py) — reuse
  `Common`'s tested behavior, only test what `Cli`/`Gui` add or override.

## Approach

1. Create `tests/test_cli.py` and `tests/test_gui.py`, mirroring `test_common.py`'s style
   (fixtures, naming, assertions).
2. Mock all I/O and third-party calls with `pytest-mock` (`mocker`):
   - `ebookmeta` calls (metadata read) — never touch a real file.
   - `progress.bar.IncrementalBar` — mock or disable.
   - `tkinter.filedialog` / `tkinter.messagebox` in `gui.py` — mock, GUI tests never
     open a real window.
3. Cover: argument parsing branches in `cli.py`, each `Gui` callback/handler, error paths
   (missing metadata, empty folder).
4. Run `pytest --cov=cli --cov=gui --cov-report=term-missing` locally before finishing;
   target the repo's 85% gate.

## Pitfalls

- Tkinter widgets require a display — always mock `tkinter` objects, never instantiate
  a real `Tk()` root in CI.
- `ebookmeta` raises on malformed EPUBs — test both the happy path and that exception path.
