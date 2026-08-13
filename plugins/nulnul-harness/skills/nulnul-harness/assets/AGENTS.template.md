# Repository working agreement

This is the Codex-owned root entry. Shared stable setup belongs in `docs/nulnul/project.md`; Claude Code owns `CLAUDE.md` if that host is later used.

## What

- Product outcome: {outcome}
- Canonical paths: {paths}

## Why

- {durable reason or constraint}

## How

- Build: `{build_command}`
- Test: `{test_command}`
- Verify: `{verification_command}`
- Resume checkpoint: validate `docs/nulnul/checkpoint.json` before any repository-wide inspection; when `fast_path_ready` is true, read only it and task files
- Detailed project setup: `docs/nulnul/project.md` (full workflow only)
