# epub-sorter

[![CI](https://github.com/chrysa/epub-sorter/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/epub-sorter/actions/workflows/ci.yml)

## Overview

`epub-sorter` is a Python tool for organizing and deduplicating EPUB ebook
libraries. It reads EPUB metadata (author, title, identifier) and can:

- **Group by author** — move files into `Author/` directories.
- **Extract metadata** — dump a metadata CSV for inspection.
- **Find duplicates by identifier** — detect duplicate EPUBs via their ISBN/UUID
  metadata and move them to a `[duplicates]` folder.
- **Rename files** — rename EPUBs from their title metadata (collisions go to
  `[skipped]`).

It ships two front-ends over the shared `Common` engine: a Tkinter **GUI**
(the default) and a progress-bar **CLI**.

## Usage

```bash
pip install -e .

# GUI (default)
python main.py --epub-path /path/to/epub/folder

# CLI
python main.py --cli --epub-path /path/to/epub/folder [--rename-file] \
    [--update-author] [--update-title] [--update-all]
```

Output folders (`[processed]`, `[duplicates]`, `[failed]`, `[skipped]`) and the
CSV path are configurable via flags — see `python main.py --help`.

## Development

```bash
make install-dev   # install with test extras
make test-cov      # run pytest with coverage (floor 85%)
make lint          # ruff
```
