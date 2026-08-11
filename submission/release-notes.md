# nulnul harness 1.3.5

This patch makes the 100/100 Release Gate mechanically defensible. Its Claude adoption case now depends on a sanitized structured artifact instead of trusting a hand-edited `passed` status; the validator rejects any protected-path write, changed agent hash, stale plugin version, non-GitHub source, missing session entry, or failed check.

The final E2E used the GitHub-marketplace-installed 1.3.5 plugin with no local plugin override. It made zero `.claude/**` write calls, preserved both existing agent hashes, enumerated and classified the roster, and left a valid fast-resume checkpoint and session entry.

Checkpoint completion checks must now be exact commands. The shipped runner executed the generated `npm test` command successfully; prose descriptions fail validation and cannot enter fast resume. Five E2E checks and all 66 repository tests pass. The plugin remains skills-only with no server, hook, daemon, authentication, external service, or new permission.

The plugin remains skills-only with no service, authentication, telemetry, hook, UI, or background process. Git-based marketplace installation and repeatable Codex and Claude Code update commands are documented in both README locales.
