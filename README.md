<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL logo">
</p>

<h1 align="center">NULNUL</h1>

<p align="center">
  <strong>Verified capabilities. Personal agents. Controlled evolution.</strong><br>
  A skills-only Codex plugin for turning ideas into verified agent systems.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-1.2.1-111111" alt="version 1.2.1">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Harness_100-100%2F100-111111" alt="Harness 100: 100/100"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT license"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.ko.md">한국어</a>
</p>

## Why NULNUL

More tools do not make a better agent system. Unverified skills, overlapping roles, unnecessary servers, and self-declared “learning” create cost and failure points.

`NULNUL` takes the smaller path:

- inspect the repository and its completion checks before changing it;
- find and verify existing capabilities before creating new ones;
- activate only the skills and agents needed for the current job;
- finish the original task instead of stopping at setup;
- resume later sessions from repository evidence, not chat memory;
- turn reproducible feedback into agent upgrades that require an independent Gate.

## Quick start

```bash
git clone https://github.com/SeoNaRu/nulnul-harness.git
cd nulnul-harness
codex plugin marketplace add "$PWD"
codex plugin add nulnul-harness@nulnul-harness
```

Start a new Codex session and ask for the product, not the harness:

```text
Build an automation that finds finance YouTube creators, deduplicates them,
and safely writes reviewed results to Google Sheets.
```

The harness inspects the project, reuses adequate instructions and tests, checks available capabilities, asks only for decisions it cannot safely discover, and continues through implementation and verification. It does not activate for simple read-only questions or duplicate a coherent project setup.

## Product loop

```text
Discover → Verify → Assemble → Run → Checkpoint → Evolve
```

| Stage | Durable result |
| --- | --- |
| Discover | Required jobs and existing candidates |
| Verify | Provenance, compatibility, quality, permissions, and license |
| Assemble | The smallest complete capability and agent set |
| Run | The user-visible result and its completion check |
| Checkpoint | Verified state, next action, blockers, and approved permissions |
| Evolve | Reproducible feedback, version comparison, independent promotion, and rollback |

## Personal agent evolution

```text
Worker feedback ──▶ Coach proposal ──▶ independent Gate
       ▲                                      │
       └──────── Navigator resumes work ◀─────┘
```

| Responsibility | Job |
| --- | --- |
| Navigator | Own the outcome, completion check, permissions, checkpoint, and resume |
| Worker | Complete one bounded job and report observable evidence |
| Coach | Diagnose the nearest responsible layer and propose one versioned change |
| Gate | Compare the candidate with the accepted version, then promote, reject, or roll back |

These are responsibility boundaries, not four mandatory live agents. Simple work can combine roles; every promotion still separates its author from its Gate. The Coach can be upgraded from feedback, but it cannot approve its own candidate.

For multi-session work, the harness stores only bounded state in `docs/nulnul/evolution.json`. Its standard-library validator rejects target or proposal-author self-approval, contradictory records, missing evidence, invalid version transitions, sensitive persisted keys, and permission expansion without prior approval.

## Evidence, not claims

| Check | Current result |
| --- | --- |
| Automated repository tests | 29 passed |
| Harness 100 behavior and safety gate | 100/100 |
| Positive isolated scenarios | 6 passed |
| Negative safety scenarios | 3 passed |
| Independent forward evaluation | Found 3 validator gaps; all fixed and preserved as regressions |
| Offline workbook A/B (3 trials per arm) | All exact; Navigator v3 median time -25.76%, output tokens -22.76% vs 1.2.0 |

Harness 100 is a release gate, not a universal performance benchmark. It covers implicit project activation, ambiguous empty repositories, reuse of coherent setups, capability-first automation, permission boundaries, evidence-gated evolution, read-only non-activation, secret persistence, and unapproved global registration.

Reproduce the public checks:

```bash
python3 scripts/harness_100.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Inputs and decisions are published in [`evals/cases.json`](evals/cases.json) and [`evals/results.json`](evals/results.json).

## Reference workflow: YouTube → Google Sheets

The public example models a finance-creator research workflow without copying production identities or contact data. It covers channel discovery, classification, stable channel-ID deduplication, exclusion precedence, reviewer feedback, spreadsheet-formula escaping, safe upsert behavior, and run metrics.

- Synthetic example: [`examples/youtube-sheets`](examples/youtube-sheets)
- Offline quality scorer and A/B evidence: [`evals/benchmarks/youtube-sheets`](evals/benchmarks/youtube-sheets)

No real Google authentication or Sheet write is performed without explicit approval. The first isolated 3×3 comparison exposed overhead on an already-complete contract; Navigator v3 then skipped unnecessary activation and reproduced exact results with lower medians. This is task-specific preliminary evidence, not a universal performance claim.

## Trust model

- **Installed ≠ verified.** Availability is discovery evidence, not proof.
- **Popularity ≠ fitness.** Adoption cannot override provenance, permissions, license, or task fit.
- **Least privilege.** Authentication, external writes, deployment, publication, and global registration remain approval boundaries.
- **No secret persistence.** Credentials, raw conversations, and personal data do not become project memory.
- **Independent promotion.** An agent cannot approve its own upgrade.
- **Verified resume.** Checkpoints are rechecked against repository reality before use.
- **Removable setup.** Generated project state can be deleted without damaging product code.

## What ships

```text
plugins/nulnul-harness/                 # only shipped product boundary
├── .codex-plugin/plugin.json
├── assets/nulnul-harness.svg
└── skills/nulnul-harness/
    ├── SKILL.md                        # execution contract
    ├── agents/openai.yaml              # Codex UI metadata
    ├── references/                     # discovery, assembly, safety, evolution
    ├── assets/                         # removable project templates
    └── scripts/                        # deterministic state validator
```

The plugin remains skills-only. It includes no MCP server, hook, app, authentication, telemetry, hosted service, or background process. Evolution happens during normal agent work; it is not an unsupervised daemon. Gate independence is validated from declared state; it is not cryptographic identity proof.

## Removal

```bash
codex plugin remove nulnul-harness@nulnul-harness
codex plugin marketplace remove nulnul-harness
```

## Development

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/harness_100.py
```

Product decisions and experiment notes are summarized in [`CHANGELOG.md`](CHANGELOG.md). See [`SUPPORT.md`](SUPPORT.md) and the [MIT license](LICENSE).

MIT © [SeoNaRu](https://github.com/SeoNaRu)
