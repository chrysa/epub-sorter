---
name: epub-sample-fixtures
description: 'Generate minimal sample EPUB files with controlled/malformed metadata for epub-sorter tests. Use when writing tests for metadata-driven rename/dedup logic, or when asked for EPUB test fixtures.'
---

# Generate sample EPUB fixtures

## When to invoke

Auto or user-invoked when a test needs an EPUB file with specific metadata
(author, title, identifier) — including missing or duplicate metadata cases.

## What it does

Bundled script `scripts/make_test_epub.py` builds a minimal valid EPUB (zip container
with `mimetype`, `META-INF/container.xml`, and an OPF with configurable `dc:creator`,
`dc:title`, `dc:identifier`) using stdlib `zipfile` — no real book content needed.

## Usage

```bash
python .claude/skills/epub-sample-fixtures/scripts/make_test_epub.py \
    --out tests/fixtures/sample.epub \
    --author "Jane Doe" --title "Sample Book" --identifier "urn:uuid:1234"

# Malformed cases: omit --author or --identifier, or repeat --identifier
# across two calls to produce a duplicate-identifier pair.
```

## Coverage this unlocks

- Missing author → tests `Common.rename_author` fallback behavior.
- Missing identifier → tests `find_duplicate_by_identifier` skip/warn path.
- Duplicate identifiers across two generated files → tests dedup detection itself.

## Pitfalls

- Keep generated EPUBs out of version control except as fixtures created at test
  time (use a pytest `tmp_path` fixture, not committed binary files).
