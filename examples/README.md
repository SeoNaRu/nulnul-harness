# NULNUL in Action

[English](README.md) | [한국어](README.ko.md) | [Product](../README.md)

**See the work, then inspect the evidence.** These cases make NULNUL's outcome-first contract concrete without turning the number of agents, templates, or passing tests into a success metric.

## Pick a case

| Case | What you can inspect or use | Evidence status |
| --- | --- | --- |
| [Book a studio session](booking-service/README.md) | A local browser UI and JSON API, with duplicate-slot rejection | Local HTTP check and 9 Chromium checks passed on 2026-09-09; not a measured harness run |
| [Turn research into a review workbook](youtube-sheets/README.md) | Synthetic input and the published expected output: 2 leads, 3 second-review rows, 9 audit rows | Expected-output comparison and 5 tests passed on 2026-09-09; not a live research or Sheets run |
| [Adopt an existing project without replacing it](existing-project/README.md) | Sanitized 3.1.0 public Claude adoption record, preserved roles, and completion-check results | Recorded live adoption on a synthetic fixture; not a newly observed second-session resume |

This is **three case entries**, not three new verified deployments. The booking demo was added after the frozen 3.1.0 release and is not in that release archive. Product installation still consists only of `plugins/nulnul-harness/`; the casebook is repository documentation and examples.

## Start with something visible

From the repository root, with Python 3.9 or newer:

```bash
python3 examples/booking-service/app.py
```

Open `http://127.0.0.1:8765`. Choose a demo slot and book it using a fictional name. Reload to see that slot unavailable. Stopping the server clears the in-memory bookings.

The included HTTP check is separate from starting the demo:

```bash
python3 examples/booking-service/app.py --check
```

The HTTP check passed on 2026-09-09 with Python 3.12.3. It does not itself automate a browser or measure harness effectiveness. A separate Chromium run passed 9 browser checks, including stale-tab conflicts, mobile layout, keyboard booking, and safe text rendering.

[Local validation record](validation-2026-09-09.json) records source digests, the 14 passing related unit tests, historical-adoption validation, and the documentation checks. A missing favicon produced a nonblocking `404` and remains unfixed. These results validate the examples' checked behavior, not a new live adoption or an A/B performance advantage.

Publication preflight also passed all **447 repository tests**, with **0 documentation-debt items** and **Release Gate 100/100** against the unchanged 3.1.0 plugin. The booking HTTP check is now part of CI. This publication work made **0 new Claude or other model calls**; the unexecuted model-comparison draft is excluded.

## What every case discloses

- The original task, the visible result, and whether the result is recorded, expected, or unverified.
- Which existing capability was reused, which additions are only proposed, and what was deliberately not activated.
- The input, source or version reference, and exact local commands where reproduction is available.
- The acceptance conditions and at least one failure or negative-control condition.
- Measured costs and time, or `unknown` when no eligible measurement is available.
- Permissions and limitations, including whether credentials, external writes, or paid model calls are involved.

Do not relabel a reference app as a harness-generated success, a fixture as a customer deployment, or a readiness flag as an observed future session. Preserve failed attempts beside successful evidence.

## A comparison, not a victory claim

No new A/B outcome or cost advantage is claimed here. When these tasks are used for a comparison, freeze the task, starting repository, candidate version, acceptance checks, permissions, model, and budget before execution.

1. Run the default agent with the task and the same acceptance criteria.
2. Run the same agent with a concise, task-appropriate project instruction file.
3. Run the same agent with NULNUL, counting setup and capability-selection costs too.

Counterbalance execution order and keep each starting state isolated. Evaluate task results with checks fixed independently of the generated solution, including a broken input or implementation that must fail. Include unsuccessful attempts, retries, elapsed time, and token or monetary costs. Compare verified outcome quality first; compare costs among materially equivalent outcomes. A tiny task that needs no extra harness setup belongs in the case mix too.

These are proposed evaluation rules, not recorded experiments. Do not derive personal or cross-project generalization claims from these public, already exposed examples. Such claims require the repository's separate transfer and holdout gates.

## Publication boundary

No account creation, plugin installation, paid runtime, external upload, or deployment is required to read the casebook or run the local examples. Use synthetic data only. The booking server is loopback-only and unsuitable for public hosting. New external integrations or live model experiments need their own explicit approval and bounded execution plan.
