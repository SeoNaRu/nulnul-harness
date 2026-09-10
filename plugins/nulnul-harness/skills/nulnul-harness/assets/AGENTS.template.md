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
- Resume checkpoint: use the managed entry's executable validator before discovery; when `fast_path_ready` is true, read only the checkpoint and needed task files. Generate that block with the loaded skill's `scripts/sync_host_entry.py`; do not guess project-relative script paths.
- Detailed project setup: `docs/nulnul/project.md` (full workflow only)
