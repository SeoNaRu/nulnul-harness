# nulnul harness working agreement

This repository builds `plugins/nulnul-harness/`, a Codex plugin that finds proven capabilities, assembles the smallest useful project-local agent system, completes the user's work, and evolves it from measured outcomes without requiring users to operate a harness.

- Treat `plugins/nulnul-harness/` as the only shipped product boundary.
- Keep the plugin skills-only until a real workflow proves that an MCP server, hook, app, or external service is necessary.
- Inspect a target repository before asking questions. Ask only for product decisions or constraints that cannot be discovered safely. A request to set the harness up on a repository that already has work is never one of those questions.
- Detect the host surface before writing setup files, and enumerate its installed skills, plugins, and agents before claiming a job is covered.
- Upgrade an existing agent roster in place. Classify every existing role as kept, upgraded, merged, or removed; never recreate one that already exists.
- Search installed, official, curated, and reputable public capabilities before creating a project-local substitute. Verify fit, provenance, compatibility, maintenance, permissions, and license; popularity alone is not verification.
- Continue the user's original task after setup; setup alone is not task completion.
- Add every necessary, non-overlapping capability, but activate only what the current task needs.
- Prefer direct or single-agent execution. Add roles only from concrete independent work or verification boundaries, with one synthesis owner.
- Never register global tools, use credentials, deploy, or publish without explicit user approval.
- Keep generated setup removable. Accept an evolution only when a reproducible before/after check improves the primary outcome without violating guardrails, and observe one live cycle after promotion with an executable automatic rollback threshold; schema-v3 states must run the shipped rollback executor before final validation.
- Give durable projects one validated concise resume checkpoint; keep stable setup evidence outside the host-loaded entry, and convert every reproducible nonpass verdict into Coach feedback and one bounded proposal in the same run.
- Allow fast resume only from an explicitly verified checkpoint; machine-link every nonpass verdict to its feedback and proposal, and migrate legacy durable contracts without creating a second live-state writer.
- Give every state file one writing process, keep `unknown` distinct from `verified` and `failed`, persist cursors on empty cycles, and prove each validity check against a negative control.
- Update the harness documents in the same change as the code they describe.

Validate product changes with:

```bash
python3 scripts/pack_plugin.py
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/check_doc_debt.py .
```
