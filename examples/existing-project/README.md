# Adopt an existing project without replacing it

[English](README.md) | [한국어](README.ko.md) | [All cases](../README.md)

**Status: historical live Claude adoption on a synthetic project, recorded on 2026-09-08.** This case interprets the existing sanitized evidence; no new adoption or second-session experiment was executed while writing it.

The existing record passed the shipped evidence validator again on 2026-09-09. Its 9 related validator tests also passed. This checks evidence validity, not a new live run; see the [local validation record](../validation-2026-09-09.json).

## Request and recorded result

The bounded task was to adopt an existing project using the public NULNUL plugin, preserve its instructions and agent profiles, create a verified concise checkpoint, and continue the original JavaScript label-normalization task. Labels had to trim and collapse whitespace while preserving case, with empty input handled by the target's tests. Setup alone was not completion.

| Evidence item | Recorded result |
| --- | --- |
| Public plugin | Version `3.1.0`, tag `v3.1.0`, source `github` |
| Existing roles | `collector` and `reviewer` enumerated and classified; both profiles' before/after hashes match |
| Host ownership | Active `CLAUDE.md`; inactive `AGENTS.md` hash unchanged |
| Shared state | Exactly 1 live-state writer recorded |
| Task completion | `npm test`, exit `0` |
| Setup and checkpoint | Setup validator, checkpoint validator, checkpoint completion runner, and documentation-debt check all exit `0` |
| Resume readiness | `checkpoint_fast_path_ready: true` |

The last row means the checkpoint was ready at the recorded check. **It is not evidence that a later independent session resumed successfully, or that Codex and Claude concurrently mutated the project.**

## Inspect the source, not a reconstructed transcript

[Passing sanitized record](../../evals/benchmarks/claude-adopt/release-3.1.0-r4.json)

```bash
python3 -m json.tool evals/benchmarks/claude-adopt/release-3.1.0-r4.json
```

Validate the existing record with the shipped validator:

```bash
python3 scripts/claude_adopt_evidence.py validate \
  evals/benchmarks/claude-adopt/release-3.1.0-r4.json --version 3.1.0
```

The first command displays evidence and the second validates that record. Neither replays the live run or validates a new target repository. The record retains check names and exit codes, not a self-contained copy of the original temporary target or full replay commands. Running `npm test` in this repository is not a reproduction of that target's completion check.

The public source was frozen at commit `a9fd59e8c5852e8808f6698262e90d389f39f42a`. Its archive is `nulnul-harness-3.1.0.zip`, SHA-256 `7716a8ddfeb43632b4ad836c29deb1fd2981a84d423d2f2705fb88becad9e49d`. See the [3.1.0 release](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.1.0). Reading this card downloads or installs nothing.

## Capability decision and failures

The recorded existing profiles were preserved instead of rebuilt. The roster was explicitly inspected and classified. The active host owned its entry while the inactive host's entry stayed byte-identical, with one shared-state writer. This record does not inventory every possible external candidate or establish optimal agent selection.

Earlier failed release attempts remain available in [attempt 1](../../evals/benchmarks/claude-adopt/release-3.1.0-failure.json), [attempt 2](../../evals/benchmarks/claude-adopt/release-3.1.0-r2-failure.json), and [attempt 3](../../evals/benchmarks/claude-adopt/release-3.1.0-r3-failure.json). They involved successive candidate repairs, not four independent successes with one frozen candidate. Do not omit them when describing the release history or turn exposed regression cases into fresh holdouts.

## What a real next-session case still needs

1. A user-approved disposable target, fixed task and plugin version, preserved original files, and an exact completion command stored in its checkpoint.
2. A completed first session with sanitized evidence and an unchanged inactive host entry.
3. A genuinely new session that reads only the verified checkpoint and directly needed task files, executes the checkpoint's stored completion command, and then finishes a bounded follow-up change.
4. A negative control where stale or invalid checkpoint evidence blocks fast resume instead of being silently trusted.

This is the next experiment's specification, not an executed result. Use the existing checkpoint and host-ownership machinery rather than inventing a second state writer or copying private transcripts into a public fixture. A live model run, credentials, or external installation needs explicit approval and a fixed budget.

## Measurement limits

The cited sanitized record reports outcomes, not the full timing or cost accounting; runtime, token count, and monetary cost for this casebook are `unknown`. This was a release-adoption smoke test on a synthetic utility, not a customer deployment, an independent replication, a quality A/B win, or broad cross-project transfer evidence.
