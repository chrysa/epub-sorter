# epub-sorter — Claude context

## What does this project do?

Python tool for organizing and deduplicating EPUB ebook libraries. Reads EPUB metadata (author, title, identifier) and performs:
- **Group by author**: renames/moves files into `Author/` directories
- **Extract metadata**: dumps metadata CSV/JSON for inspection
- **Find duplicates by identifier**: detects duplicate EPUBs via ISBN/UUID metadata
- **GUI mode**: Tkinter-based desktop interface (compiled to `.exe` via PyInstaller on Windows)
- **CLI mode**: `cli.py` entry point with progress bars

## Tech stack

| Layer | Tech |
|---|---|
| Language | Python 3 |
| EPUB metadata | ebookmeta 1.2.11 |
| Progress display | progress 1.6.1 |
| GUI | tkinter (stdlib) |
| Packaging | PyInstaller 6.19 (`.exe` build) |
| Linting | ruff |
| CI | GitHub Actions |
| Pre-commit | pre-commit hooks |
| Versioning | GitVersion |

## Repository structure

```
cli.py          CLI entry point (uses Common base class)
gui.py          Tkinter GUI entry point
main.py         Script entry point / arg parser
common.py       Base class: get_processed_epub, get_metadata, rename_author, extract_metadata
requirements.txt
build.ps1       PowerShell script to build .exe via PyInstaller
Makefile
GitVersion.yml
.pre-commit-config.yaml
cliff.toml      Changelog generator config
```

## Development workflow

```bash
pip install -r requirements.txt

# CLI usage
python main.py --epub-path /path/to/epub/folder <command>

# Available commands (from cli.py):
#   author_group            — group EPUBs into Author/ directories
#   extract_metadata        — dump metadata
#   find_duplicate_by_identifier  — find duplicates by ISBN/UUID

# Build Windows executable
pwsh build.ps1
```

## Key conventions

- `Common` base class in `common.py` contains all filesystem + metadata logic
- `Cli` and `Gui` classes inherit from `Common`
- Progress bars via `IncrementalBar` from the `progress` package
- `get_processed_epub()` returns filtered EPUB file list from `self.epub_path`
- `get_metadata(epub)` calls `ebookmeta.get_metadata(filepath)`
- `rename_author(epub, metadata)` builds `Author/` directory path from metadata

## Notes / known issues

- No README description yet — `README.md` has `TODO: Add description`
- Windows-only for GUI mode (win11toast not applicable here; Tkinter is used)
- PyInstaller 6.19 — check for updates before next release
- No unit tests currently
- ruff configured but no `ruff.toml` — uses tool defaults
- SonarCloud not configured
