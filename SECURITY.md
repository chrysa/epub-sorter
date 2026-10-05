# SECURITY — epub-sorter

> Docs-only review. No code was changed. Findings are for the owner to action.

## Secret scan (FACT)

A grep for hardcoded credentials/keys/tokens across `*.py`, `*.toml`, `*.json`, `*.md`
returned **no findings**. The only matches were rule text ("no hardcoded secrets",
"ne jamais coder en dur un secret") and the `secret-scanner` hook itself. **No secrets are
committed.**

## Controls present (FACT)

- `.github/workflows/secret-scan.yml` — secret scanning in CI.
- `.github/workflows/sast.yml` — static application security testing in CI.
- `pyproject.toml [tool.bandit]` — Bandit config (excludes tests/build/.venv/.claude).
- `.claude/hooks/secret-scanner.cjs` and `.claude/hooks/check-no-env-files.cjs` — local
  pre-tool guards.
- `Dockerfile.test` runs as a non-root `appuser`.

## Threat surface (INFERENCE)

This is a local, single-user desktop/CLI file-management tool. It has **no network I/O, no
auth, no DB, no user-supplied web input**. The principal risks are filesystem-level:

| Risk | Severity | Notes |
|---|---|---|
| Path handling when moving/renaming files from untrusted EPUB metadata | LOW–MEDIUM (INFERENCE) | Titles/authors from `ebookmeta` become path segments. A crafted `title`/`author` containing path separators or traversal (`../`) could in principle place files outside the intended folder. Not verified against the sanitisation in `common.py rename_author`/`rename_file`; owner should confirm segments are sanitised. |
| Destructive moves without dry-run | LOW (INFERENCE) | The tool moves files between folders; a mis-targeted `--epub-path` reorganises real libraries. Mitigated by dedicated `[failed]`/`[skipped]` folders, but there is no obvious dry-run/undo. |
| Parsing untrusted EPUB (zip) files via `ebookmeta` | LOW (INFERENCE) | Third-party parser on attacker-supplied archives; risk inherited from `ebookmeta==1.2.11`. |

**No HIGH/CRITICAL findings.** The MEDIUM item (metadata → path) is a hardening
suggestion, not a confirmed vulnerability — the owner should verify sanitisation in
`common.py`.

## Recommendations (PROPOSAL — owner decides)

1. Confirm/enforce sanitisation of author & title before using them as path segments
   (strip `/`, `\`, `..`, control chars) — verify existing behaviour in `common.py`.
2. Consider a `--dry-run` flag for the move/rename operations.
3. Keep `ebookmeta` on the dependency-audit radar (`dependabot.yml` is present).
