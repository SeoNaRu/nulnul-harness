# nulnul harness working agreement

This repository builds `plugins/nulnul-harness/`, a Codex plugin that selects the strongest justified project-local capability system for the requested outcome, verifies the user's work, removes non-contributing setup, and evolves from measured outcomes without requiring users to operate a harness. Simplicity breaks ties between materially equivalent outcome paths; agent, skill, plugin, context, and infrastructure counts are never primary goals.

- Treat `plugins/nulnul-harness/` as the only shipped product boundary.
- Keep the plugin skills-only until a real workflow proves that an MCP server, hook, app, or external service is necessary.
- Inspect a target repository before asking questions. Ask only for product decisions or constraints that cannot be discovered safely. A request to set the harness up on a repository that already has work is never one of those questions.
- Continue the user's original task after setup; setup alone is not task completion.
- Select the non-overlapping capability set expected to produce the strongest verified task outcome. Among materially equivalent paths, choose the one with lower context, coordination, runtime, maintenance, and permission cost; activate only what the current task needs.
- Use direct or single-agent execution when it is outcome-competitive. Add as many bounded roles as materially improve specialization, context isolation, parallel work, or independent verification; agent count has no target and one owner keeps final synthesis.
- Never register global tools, use credentials, deploy, or publish without explicit user approval.
- Give every state file one writing process, keep `unknown` distinct from `verified` and `failed`, persist cursors on empty cycles, and prove each validity check against a negative control.
- Update the harness documents, exact evidence counts, and locale-parity claims in the same change as the code or release evidence they describe.

## Read only when the work needs it

For ordinary development, inspect the relevant files, make the requested change, execute the applicable checks, and fix attributable failures. Reuse current passing results; repeat a check only after its inputs change, it fails, or a concrete concern remains. Documentation cleanup does not require a new model experiment or reopen a closed one.

Before changing a subsystem, read its section in [the development contract](docs/development-contract.md):

| Change | Section |
| --- | --- |
| Setup, host entries, roster or capability adoption | [Setup](docs/development-contract.md#setup-and-capability-adoption) |
| Checkpoint, resume, state writers or migration | [State](docs/development-contract.md#state-and-checkpoints) |
| Producer/consumer checks or status/Trace evidence | [Workflow and trace](docs/development-contract.md#workflow-and-trace-evidence) |
| Governed evolution, evaluators or comparative claims | [Evolution](docs/development-contract.md#governed-evolution-and-comparisons) |
| Personal or cross-project transfer | [Reuse](docs/development-contract.md#personal-and-cross-project-reuse) |
| Release evidence, casebooks or publication | [Release](docs/development-contract.md#release-and-publication) |

## Validation

Validate product changes with:

The documentation-debt check uses Git commit order for tracked documents and only falls back to a repository modification-time scan when Git history is unavailable.

```bash
python3 scripts/pack_plugin.py
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/check_doc_debt.py . --host codex
```

`pack_plugin.py` must normalize archive timestamps and permissions so identical plugin trees produce byte-identical archives. Release fixtures must derive the current version from the plugin manifest instead of duplicating it. CI must pack the manifest's current version before archive checks, then run the full suite, the active Codex documentation-debt check, and Release Gate.

For release-evidence changes, also run the full `test_*.py` suite and `python3 scripts/release_gate.py`.

## Durable lessons

- After a test, rejection, promotion, or user correction produces a durable reusable lesson, read `.nulnul.local.json`; when its approved `obsidian_wiki_root` exists, follow that vault's `00_위키-작업규칙.md`, read `index.md` first, update the relevant `projects/nulnul-harness/` pages and links, then append one entry to `log.md`. Skip routine passing runs and never copy raw transcripts, secrets, personal data, or code facts that the repository already owns. Treat this as the user's standing approval only for that configured vault path.
