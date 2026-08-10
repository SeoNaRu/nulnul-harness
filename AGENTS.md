# nulnul harness working agreement

This repository builds `plugins/nulnul-harness/`, a Codex plugin that finds proven capabilities, assembles the smallest useful project-local agent system, completes the user's work, and evolves it from measured outcomes without requiring users to operate a harness.

- Treat `plugins/nulnul-harness/` as the only shipped product boundary.
- Keep the plugin skills-only until a real workflow proves that an MCP server, hook, app, or external service is necessary.
- Inspect a target repository before asking questions. Ask only for product decisions or constraints that cannot be discovered safely.
- Search installed, official, curated, and reputable public capabilities before creating a project-local substitute. Verify fit, provenance, compatibility, maintenance, permissions, and license; popularity alone is not verification.
- Continue the user's original task after setup; setup alone is not task completion.
- Add every necessary, non-overlapping capability, but activate only what the current task needs.
- Prefer direct or single-agent execution. Add roles only from concrete independent work or verification boundaries, with one synthesis owner.
- Never register global tools, use credentials, deploy, or publish without explicit user approval.
- Keep generated setup removable. Accept an evolution only when a reproducible before/after check improves the primary outcome without violating guardrails, and observe one live cycle after promotion with an automatic rollback threshold.
- Give every state file one writing process, keep `unknown` distinct from `verified` and `failed`, persist cursors on empty cycles, and prove each validity check against a negative control.
- Update the harness documents in the same change as the code they describe.

Validate product changes with:

```bash
python3 scripts/pack_plugin.py
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/check_doc_debt.py .
```
