# Capability registry

Where to look when the installed roster does not cover a job. `capability-discovery.md` decides *whether* to search; this file says *where*, so an outward search is a lookup rather than an open-ended guess.

Nothing here is pre-verified. Every entry is a starting point to inspect against the verification table in `capability-discovery.md`. Reaching a candidate through this list still requires reading its `SKILL.md` or manifest, checking permissions and license, and getting explicit approval before installing.

## Look in this order

1. **The host's official marketplace.** Claude Code ships one and it is already configured; `claude plugin marketplace list` and `claude plugin install <name>@<marketplace>` reach it without adding anything. Codex exposes its own curated listing. Start here: an official entry clears provenance before you read a line.
2. **Marketplaces the user already added.** `claude plugin marketplace list` shows every source this machine trusts. A publisher the user already accepted needs no fresh trust decision.
3. **The named sources below**, for the recurring jobs a repository rarely names.
4. **Open search**, last. Prefer an identifiable publisher with an inspectable source repository. If provenance, license, or maintenance cannot be checked, say so and label the candidate provisional.

## Context economy

The job that pays for itself in every later session, and the one a repository never asks for. Both entries below are installed on their author's machine, which is adoption evidence, not verification.

| Capability | Source | Job | Install |
| --- | --- | --- | --- |
| `ponytail` | `github:DietrichGebert/ponytail` | Suppresses over-building: stops at the first solution that works, prefers stdlib and native platform features over new dependencies. Cuts generated code, and therefore output tokens and review time. | `claude plugin marketplace add DietrichGebert/ponytail` then `claude plugin install ponytail@ponytail` |
| `caveman` | `github:JuliusBrussee/caveman` | Compresses prose output while preserving technical substance, code, and error strings. Cuts output tokens on every response. Ships `caveman-compress` for shrinking memory files that load into every session. | `claude plugin marketplace add JuliusBrussee/caveman` then `claude plugin install caveman@caveman` |
| `rtk` | published CLI proxy, installed outside the plugin system | Filters and compresses the output of common CLI commands before it reaches the model. Cuts *input* tokens, which the two above do not touch, so it composes with them rather than overlapping. | Installed as a binary and wired through a command-rewrite hook; check `rtk --version` before assuming it is present |

The first two are style layers over the model's own output; the third trims tool output on the way in. None is a service: no server, no credential, no external write, which is why they clear the permission boundary cheaply. They cover different halves of the context budget, so covering one does not cover the other.

Measure the claim rather than repeating it. `claude plugin details <name>@<market>` gives the always-on cost, and a before/after comparison on a representative task gives the saving — the same evidence `evolution.md` demands of any other candidate.

## Reading a candidate before installing

Prefer the host's own inspection commands over cloning:

```bash
claude plugin marketplace list            # sources already trusted here
claude plugin details <name>@<market>     # component inventory and projected token cost
claude plugin validate <path> --strict    # manifest correctness before adopting a local plugin
```

`claude plugin details` reports always-on and per-invocation token cost. That number is the context-cost evidence the verification table asks for; record it rather than estimating.

## Keeping this list honest

This file is a pointer list, not a recommendation engine. Add an entry only after a real project needed the job and the candidate survived inspection. Remove one when its source stops being maintained, its permissions widen, or a native host feature covers the job. A registry that only grows stops being a shortlist.
