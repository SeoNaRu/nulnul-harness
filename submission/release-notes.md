# nulnul harness 1.3.5

This patch closes the last weighted Release Gate gap. In unattended Claude Code sessions, `.claude/**` is now classified read-only before roster inspection; even a denied write-tool call is a failed setup rather than an acceptable fallback.

A failed isolated run reproduced two protected agent-profile write attempts. After the guard changed, a fresh run made zero protected-path write calls, kept and contract-upgraded both existing agents through `CLAUDE.md`, enumerated the installed capability roster, and left a valid schema-v2 fast-resume checkpoint.

The repository test, project-contract validator, checkpoint validator, and documentation-debt check all passed, bringing the weighted Release Gate to 100/100. The plugin remains skills-only with no server, hook, daemon, authentication, external service, or new permission.

The plugin remains skills-only with no service, authentication, telemetry, hook, UI, or background process. Git-based marketplace installation and repeatable Codex and Claude Code update commands are documented in both README locales.
