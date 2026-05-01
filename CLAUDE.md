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

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **epub-sorter** (121 symbols, 230 relationships, 6 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/epub-sorter/context` | Codebase overview, check index freshness |
| `gitnexus://repo/epub-sorter/clusters` | All functional areas |
| `gitnexus://repo/epub-sorter/processes` | All execution flows |
| `gitnexus://repo/epub-sorter/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
