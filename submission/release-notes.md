# nulnul harness 1.3.3

This patch closes three integrity gaps found while testing 1.3.2. New concise checkpoints use schema version 2; version 1 remains readable for safe migration but can never enter fast resume, and unknown future versions fail closed.

Machine-readable nonpass verdict inventories are mandatory in both Product and Release Gates. Removing the complete inventory fails the release instead of silently opting out. Legacy migration prepares every target before replacement and restores earlier files when an injected later write fails.

The plugin remains skills-only. It reuses its existing standard-library validators and migrator, with no server, hook, daemon, authentication, external service, or new permission.

The plugin remains skills-only with no service, authentication, telemetry, hook, UI, or background process. Git-based marketplace installation and repeatable Codex and Claude Code update commands are documented in both README locales.
