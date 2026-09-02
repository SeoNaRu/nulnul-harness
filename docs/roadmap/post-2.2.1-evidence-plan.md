# Post-2.2.1 evidence plan

## Decision question

> Does NULNUL make real coding-agent work measurably better than the same agent without NULNUL?

No single score answers this question. The frozen comparison records task correctness,
regression safety, unnecessary harness growth, repository disturbance, human
intervention, context/token proxies, runtime, resume performance, and harness cleanup.

## Frozen champion and protocol provenance

- Product version: `2.2.1`
- Git tag and commit: `v2.2.1` / `59f9799b0b15b37009e47b318e448b5790bf606c`
- Product tree: `0538de43fd4c0b8db4d34801688a8578060b1ade`
- Reproducible 38-file archive SHA-256:
  `f2d320804c5b86a7d1797c8088a36cf824a8009a6b825f19dcda8b8fa2c3388e`
- Benchmark ID: `nulnul-post-2.2.1-real-task-v1`
- Frozen manifest SHA-256:
  `847c8541570cb93274acebdfeb39a6a740de1f1f9174c731ad48f100ee5ac8a4`
- Frozen cases SHA-256:
  `ac4c662e3c4ea536209153ab6483e90575e42148c5c7fae4ce9f91136109a655`
- Frozen fixtures SHA-256:
  `d114daf36a3f30bbe68502273df29a43735e744a232b81b51eaf5b78d38daba0`
- Frozen runner SHA-256:
  `83180501008490c5c91656556cdf112ac9e5d199b30166f2178db0ec75f4337a`
- Retry budget: zero. Diagnostic repeats may not replace baseline results.

The independent benchmark freeze was written at 2026-08-26 10:12:55 KST,
before its partial baseline result file was last updated at 10:33:10 KST. The
current product worktree now contains a later, user-directed outcome-first contract
refactor. It is not part of the champion and cannot affect baseline execution:
every NULNUL arm loads the exact tagged plugin tree above. This document records
the already-frozen criteria; it does not revise them after exposure.

## 1. What NULNUL has already proved

- The shipped boundary is a skills-only plugin for Codex and Claude Code. Codex
  installs it under its plugin cache and Claude Code reports the exact `2.2.1`
  plugin in `claude plugin list --json`.
- On the original Git history, the tagged bytes reproduce the archive hash above,
  pass 15/15 product tests and 239/239 deterministic tests, produce no Codex
  documentation debt, and score 100/100 on the local Release Gate.
- Existing evidence validates bounded activation, repository-local setup,
  protected host ownership, exact checkpoint checks, stale-checkpoint rejection,
  compacted evolution state, rollback, permission boundaries, personal adaptation,
  and one narrower-scope cross-project Meta selection episode.
- Existing performance evidence supports only its named internal comparisons. In
  those fixtures, accepted fast resume reduced median input tokens from 223,911 to
  137,669, and the bounded workflow reduced median elapsed time and token usage.
- The product has retained `NO_PROMOTION` and rejected candidates when smaller
  instruction bytes or added rules did not improve measured runtime behavior.

## 2. What NULNUL has not proved

- It has not yet shown that the same current coding model completes a broad real-task
  suite more correctly with NULNUL than without it.
- It has not established a general reduction in token use, runtime, questions, or
  repository reads across ordinary product work.
- It has not established that harness cleanup is better than Vanilla while product
  correctness and user-owned configuration remain intact.
- It has not established resume advantage against a fair Vanilla new-session arm on
  the same starting repository and permission boundary.
- Two small OSS snapshots do not establish ecosystem-wide or language-wide
  generalization.
- Internal test counts, Gate scores, and prior version-to-version comparisons do not
  establish a percentage improvement in real coding work.

## 3. Claims currently supported

- NULNUL provides deterministic contracts for host ownership, checkpoint validity,
  bounded resume, evidence-gated evolution, and rollback within the published scope.
- The v2.2.1 tagged product is reproducibly packaged and locally validated.
- Existing evidence justifies narrower claims about the named fixtures and versions,
  including accepted and rejected candidates.
- NULNUL is designed to reuse existing capability when it is outcome-competitive
  for this project, investigate concrete material gaps, and avoid unsupported
  additions; whether that produces a measurable advantage over Vanilla is the
  question this benchmark must answer.

## 4. Claims not yet allowed

- “NULNUL makes coding agents better” without limiting the claim to a published suite.
- A universal correctness, speed, token, context, or cost improvement.
- Better results on hosts, models, languages, repository sizes, or third-party
  harnesses not represented by evidence.
- A task-success claim derived from internal contract tests alone.
- A win derived by excluding a losing, failed, timed-out, or non-activating arm.

## 5. Frozen benchmark hypotheses

1. Product-task correctness and regression safety are at least equal to Vanilla.
2. For ordinary tasks already covered by repository instructions, NULNUL activates
   no unnecessary setup and leaves harness entropy unchanged.
3. For duplicate or messy AI setup, NULNUL preserves product completion while adding
   fewer harness files or reducing duplicate roles.
4. NULNUL preserves the inactive host entry and does not expand permissions.
5. A valid checkpoint reduces bounded reads/context without reducing task success.
6. Stale files, changed tasks, and changed permissions reject fast resume.
7. Named-file fast path stays inside its declared read set; insufficient files cause
   full-workflow fallthrough.
8. Existing capabilities are reused when outcome-competitive for the project; a
   merely adequate installed candidate does not block a justified better path, and
   no duplicate Skill or Agent is created merely to demonstrate the harness.
9. Any added context/runtime cost is visible and can outweigh an otherwise equal
   result.

## 6. Areas frozen against change

Until the complete untuned baseline is recorded, do not change the tagged plugin,
manifest, cases, fixtures, task prompts, completion checks, model/config, order,
timeout, permission boundary, retry budget, scoring, failure taxonomy, or promotion
criteria. Do not inspect hidden expected patches through an agent prompt. Do not
replace a failed arm or edit an exposed case to improve a result.

After baseline, preserve host ownership, permission boundaries, checkpoint truth,
independent Gates, rollback, evidence exposure, privacy rules, and the skills-only
product boundary. No new Agent role, Gate, state schema, daemon, vector database,
hosted control plane, memory architecture, or speculative infrastructure is in scope.

## 7. Promotion criteria

Classify each fair pair as `ADVANTAGE`, `NO_ADVANTAGE`, `REGRESSION`, or `INVALID`.

Promote a bounded challenger only when a reproducible failure family exists and
either:

- task success improves meaningfully; or
- task success and regression safety are at least equal while one measured cost
  (unnecessary additions, disturbance, resume reads/context, intervention, or
  context/token cost) improves meaningfully.

Every promotion must also have no regression increase, protected-host-file
violation, permission expansion, fake verification, hidden-test leakage, benchmark
contamination, or selective result exclusion. Complexity, context, runtime, new
state, maintenance burden, failure surface, and rollback cost count against the
candidate. Equal outcomes retain v2.2.1 as `NO_ADVANTAGE`; worse outcomes are
`REGRESSION`. No reproducible loss means no product change.

## North Star clarification frozen before Project-Fit tuning

The original champion, prompts, scorers, and promotion rules above remain frozen.
The later user-directed [Product North Star](../product-north-star.md) clarifies the
metric priority without changing exposed outcomes after seeing results:

1. verified project outcome and relevant quality;
2. project fit, calm user burden, continuity, evolution response, and inspectability;
3. waste, context, runtime, coordination, maintenance, state, and permission cost.

Tier 3 never defeats a materially stronger Tier-1 result. Global popularity,
novelty, and capability counts are not primary metrics. A local Skill or Agent may
upgrade from reproduced project evidence without an external replacement; a
stronger external candidate may replace it; a defeated or duplicate capability may
retire. These are lifecycle decisions in the existing evolution contract, not a new
engine or a post-result scoring formula.
