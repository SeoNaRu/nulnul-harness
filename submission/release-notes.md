# nulnul harness 2.0.1-rc.1

This patch candidate gives Codex and Claude Code separate root session-entry ownership when they are used sequentially in one repository. Codex creates or updates only `AGENTS.md`; Claude Code creates or updates only `CLAUDE.md`; both point to the existing single `docs/nulnul/checkpoint.json` or `docs/nulnul/evolution.json` writer.

The standard-library writer preserves existing user guidance outside one managed block, fails closed when shared state is missing or duplicated, and leaves the inactive host entry byte-identical. All four first-use and sequential-order cases, eight negative controls, legacy migration, and one post-freeze mixed-host cycle passed with no permission, dependency, service, or external-write change.

This release candidate does not claim simultaneous Codex and Claude Code mutation, automatic conflict merging, other host support, or global configuration management. Public 2.0.0 remains the released baseline until exact-version public adoption evidence closes the patch gate.
