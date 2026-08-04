# Project Harness working agreement

This repository builds `plugins/project-harness/`, a Codex plugin that prepares and evolves project-local agent setups without requiring users to understand harness terminology.

- Treat `plugins/project-harness/` as the only shipped product boundary.
- Keep the plugin skills-only until a real workflow proves that an MCP server, hook, app, or external service is necessary.
- Inspect a target repository before asking questions. Ask only for product decisions or constraints that cannot be discovered safely.
- Continue the user's original task after setup; setup alone is not task completion.
- Add every necessary, non-overlapping capability, but activate only what the current task needs.
- Choose direct, single-agent, multi-agent, or hybrid execution from concrete work boundaries rather than a fixed default.
- Never register global tools, use credentials, deploy, or publish without explicit user approval.
- Keep generated project setup removable and evolve it only from observed results, failures, tests, workarounds, and user corrections.

Validate product changes with:

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
```
