# Baseline kernel

Keep these invariants active on every setup or adopt-and-upgrade run. They are the small base that is cheaper than rediscovering a broken project. A fast-path task may satisfy them from repository evidence without creating a file.

1. **Repository truth** — inspect the host surface, repository instructions, code, checks, and installed skills, plugins, and agents. Keep `unknown` distinct from verified or failed.
2. **Observable outcome** — preserve the user's original request and name one runnable completion check. Put live continuation fields in one concise checkpoint instead of duplicating the full setup contract. Harness setup alone is not completion.
3. **Before state** — run the smallest existing check before changing the harness, or add one focused reproduction when no useful check exists.
4. **Capability decisions** — map each job to inspected evidence and report **reuse now**, **add now**, **needs approval**, or **skip**. Create a local substitute only after adequate candidates fail.
5. **Permission boundary** — never expand credentials, cost, global configuration, external writes, deployment, or publication without explicit approval.
6. **Continue the work** — after setup, resume the original project outcome and verify the user-visible result.
7. **Governed evolution** — keep the last accepted version active while an independent Gate reproduces the change and checks guardrails. Mark a passing candidate provisional, then confirm its version only after one healthy live cycle or roll it back when the executable threshold fires.

## Add infrastructure only when its signal appears

| Candidate | Add when |
| --- | --- |
| Persistent memory | work spans sessions, verified state is lost, or agent-specific learning must accumulate |
| Performance tracking | a named outcome needs before/after comparison |
| Dashboard | repeated human decisions need trends that the existing concise report cannot show |
| Multiple agents | independent work, context isolation, parallel branches, or independent verification outweigh coordination cost |
| Multi-stage verification | a risky change needs staged reproduction, regression, live observation, and rollback |
| Single-writer lock | concurrent or long-running processes can mutate the same state |
| MCP server | an uncovered recurring job requires a tool or service boundary that native, installed, or simpler capabilities cannot supply |
| Project-local skill | a recurring workflow remains uncovered after adequate existing candidates were inspected and rejected |

MCP registration, downloads, authentication, global installation, and external writes still require explicit approval. Record an omitted candidate only when its job was evaluated; do not copy this whole table into every project.

## Durable setup check

When a run creates or materially upgrades `docs/nulnul/project.md`, start from `assets/project-contract.template.md` and run:

```bash
python3 <nulnul-skill-directory>/scripts/validate_project_setup.py docs/nulnul/project.md
```

Run the copy belonging to the currently loaded NULNUL skill; do not persist its machine-specific absolute path in the project contract. The check verifies that the durable contract contains a goal, runnable completion check, inspected roster, capability evidence and routing, plain-language setup decisions, permissions, topology, baseline, and continuity without unfinished template placeholders. It does not require a durable contract on the fast path.
