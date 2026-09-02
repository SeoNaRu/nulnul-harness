# Post-2.2.1 Project-Fit Proof decision

Status: evidence complete; release decision **v2.3 NOT READY**.

## State recovery

The earlier Evidence-First work was resumed rather than replaced. Its independent
workspace remains at `../nulnul-benchmarks/`, Git commit
`a3599dcbba975e1696a5fd4ca68f6f822d86d572`.

| Frozen object | Identity |
| --- | --- |
| exact v2.2.1 tag | `v2.2.1` / `59f9799b0b15b37009e47b318e448b5790bf606c` |
| exact v2.2.1 archive | `f2d320804c5b86a7d1797c8088a36cf824a8009a6b825f19dcda8b8fa2c3388e` |
| original manifest | `847c8541570cb93274acebdfeb39a6a740de1f1f9174c731ad48f100ee5ac8a4` |
| Outcome-First archive | `82c09bab99f0364d5db6d9b89553397951a9e5faa47e291007be2643c946f580` |
| Project-Fit candidate archive | `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b` |
| Product North Star | `d69848a85b39ce732ba3b30eebae1a9f3faf49efa88206b89f271c583d55b034` |

The North Star and Project-Fit candidate were frozen before the Project-Fit
candidate arm and before any cleanup challenger. The six invalid original cases
and their raw results remain preserved; they were not silently edited or scored.

## North Star and project-fit model

[The frozen North Star](../product-north-star.md) defines the priority order:

1. strongest verified outcome within user, repository, safety, permission,
   compatibility, reproducibility, and reasonable-cost constraints;
2. project-fit selection based on this repository's evidence, not popularity or
   ownership;
3. lower waste only among materially equivalent outcome paths.

The user states the product result. NULNUL owns capability topology unless a real
authority boundary requires the user's decision. Novelty alone never triggers
discovery. Verified state, not raw conversation memory, owns continuity.

## Capability lifecycle contract

The existing discovery, assembly, evolution, Gate, archive, and rollback surfaces
now express six decisions without a new lifecycle engine:

- `KEEP`: a strong project-fit survivor remains active;
- `UPGRADE`: reproduced project evidence competes a bounded new version, even with
  no external replacement;
- `REPLACE`: a materially stronger winner succeeds necessary unique value and the
  defeated active capability retires;
- `MERGE`: an overlapping survivor must preserve outcome and improve routing,
  context, or ownership;
- `RETIRE`: obsolete, duplicate, unsafe, defeated, or removal-tested capability
  leaves ordinary active context;
- `CREATE`: a real recurring job remains materially uncovered by current and
  external candidates.

The 15 deterministic cases in `evals/outcome-first/cases.json` cover outcome over
minimality, equivalent-quality waste, beginner burden, no AI FOMO, local Skill
upgrade, external replacement and retirement, famous-external loss, merge,
Agent evolution, routing evolution, continuity, and inspectability. These prove
decision-contract consistency, not model-level task improvement.

## Three-way real-task result

The proof view combines 19 valid original cases with six preregistered corrected
successors. Each variant has the same 25 task contracts, starting fixtures,
permission boundary, retry budget of zero, completion checks, and host/model where
available. The original Vanilla/exact-v2.2.1 pairs were counterbalanced. The frozen
Project-Fit candidate ran later as a third arm rather than interleaved with those
pairs, so its token and runtime differences are descriptive rather than causal
paired estimates.

| Variant | Strict pass | Completion pass | Runtime | Input-token proxy | Reads | Disturbed files |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Vanilla | 21/25 | 21/25 | 889.613 s | 2,123,954 | 122 | 6 |
| exact v2.2.1 | 21/25 | 23/25 | 1,154.986 s | 2,813,285 | 144 | 11 |
| Project-Fit candidate | 21/25 | 23/25 | 1,248.134 s | 3,367,586 | 141 | 12 |

The Project-Fit candidate has no strict or completion advantage over exact v2.2.1.
Its observed total runtime is 8.1% higher and its input-token proxy is 19.7%
higher. Temporal ordering and ordinary model variance mean those signals do not
prove a causal or universal slowdown, but they prohibit an efficiency claim and
provide no promotion case.

Both NULNUL variants beat Vanilla in cases 17 and 31 and lose to it in cases 22
and 25. All variants fail the corrected duplicate-Skill cleanup and messy-harness
cleanup cases 28 and 29.

## Initial losses and candidate decisions

The untuned losses remain in
[baseline findings](post-2.2.1-baseline-findings.md). Four bounded comparisons were
preserved:

| Candidate | Result | Reason |
| --- | --- | --- |
| resume-state-preservation-v1 | `REJECT` | Target performance fell from 2/4 to 0/4. |
| resume-state-preservation-v2 | `NARROWER_SCOPE`, not promoted | Fixed case 25 twice but missed the full preregistered family criteria. |
| different-task-state-preservation-v1 | `REJECT` | Fixed case 25 but regressed the stale-instruction guardrail. |
| capability-cleanup-routing-v1 | `REJECT` | Target cleanup was 0/4; input tokens were 38.3% above parent. |

No product behavior change was promoted. The user-directed Outcome-First and
Project-Fit decision contract remains the current product direction, but this
suite does not relabel it as measured model-performance improvement.

## Killer demo and progressive evidence

The measured demo is corrected case 31, not a staged capability-evolution story.
Vanilla fixed `slug.py` and its focused test but failed the checkpoint completion
check. Exact v2.2.1 and the Project-Fit candidate fixed the same product behavior,
refreshed the verification receipt, and passed the checkpoint validator in under
one minute per arm.

The generated user view is:

```text
RESULT
✓ Repeated-whitespace slug regression fixed

VERIFY
✓ checkpoint validation passed

RESUME
✓ verification receipt refreshed for the named files
```

The expanded `HARNESS` evidence says only what occurred: an existing verified
checkpoint was used; no Agent, Skill, infrastructure, replacement, merge, or
retirement is claimed. The messy-harness cases failed, so the requested long-term
Skill/Agent evolution scene is not supported as this proof's demo.

## Evidence artifacts

The independent workspace generates these files from frozen raw results:

- `benchmark-results.json`: 75 validity-filtered run records;
- `benchmark-summary.json`: aggregate metrics, categories, wins, losses, and release
  decision;
- `benchmark-report.md`: human-readable comparison and evidence boundaries;
- `reports/killer-demo.json` and `.md`;
- `reports/run-summary.json` and `.md`;
- `scripts/report.py`: standard-library generator with `--check` drift validation.

Reproduce the lightweight layer with:

```bash
cd ../nulnul-benchmarks
python3 -m unittest scripts/test_runner.py -v
python3 scripts/validate.py --schema-only
python3 scripts/validate.py --manifest amendments/project-fit-v2/manifest.json --schema-only
python3 scripts/report.py --check
```

Full agent reruns remain manual/release work and use the frozen commands in the
benchmark README. They are not added to ordinary product CI.

## v2.3 Proof release checklist

- [x] exact v2.2.1 frozen
- [x] Vanilla frozen
- [x] current candidate frozen
- [x] North Star frozen before tuning
- [x] Project-Fit principle documented
- [x] local Skill evolution contract tested
- [x] external replacement and retirement contract tested
- [x] famous external candidate loses to project-fit evidence case tested
- [x] merge/prune contract tested
- [x] Agent evolution contract tested
- [x] harness routing evolution boundary tested
- [x] no AI FOMO and beginner burden tested
- [x] continuity and inspectability tested
- [x] real outcome quality, verification, and secondary waste measured
- [x] initial failures and rejected candidates preserved
- [x] every attempted fix traces to a reproduced failure
- [x] deterministic product suite passes on the final documentation bytes
- [x] Release Gate passes on the final documentation bytes
- [x] public claims are scoped to measured evidence
- [x] rollback exists; no challenger changed the product worktree

## Decision

The final local cycle packed 38 files reproducibly, passed product tests 16/16 and
the deterministic suite 242/242, reported no documentation debt, and scored
Release Gate 100/100 with `local_candidate_ready=true`. `release_ready=false`
because exact-byte public Claude and Meta evidence is stale and the candidate is
Unreleased. Those contract checks do not override the real-task decision.

`v2.3 NOT READY`. The Proof infrastructure and product direction are useful, but
the current candidate did not beat exact v2.2.1, measurable costs increased, and
no bounded product challenger met promotion criteria. Do not bump, tag, publish,
or begin the Research Pass. The next highest-value problem is the reproduced
capability-cleanup completion failure in cases 28 and 29, but a larger mechanism is
not justified by this failed one-rule challenger alone.
