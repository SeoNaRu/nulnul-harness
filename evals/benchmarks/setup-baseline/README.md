# Codex setup baseline benchmark

Use two clean copies of `fixture/` with the same fresh-session prompt. One loads the prior 1.2.1 skill and one loads the 1.3.0 candidate. Compare:

- whether the existing project takes adopt-and-upgrade without asking what to build;
- whether the maintainer role is classified rather than recreated;
- whether installed skills, plugins, and agents are enumerated before capability decisions;
- whether `docs/nulnul/project.md` passes the candidate setup validator;
- whether repository tests still pass and no product code changes during setup;
- input, output, and reasoning tokens reported by Codex; and
- whether a second fresh candidate session resumes the contract and completes one small project change without redesigning the harness.

The setup prompt forbids network, credentials, external writes, global registration, deployment, and product-code changes. The continuation asks only for robotics-note routing and its focused regression test.

The 1.3.0 candidate must keep exact setup behavior while staying within 20% of the 1.2.1 input-token arm. A larger increase is a regression even when the files are correct; inspect roster discovery first because recursive cache or marketplace enumeration contributes no job evidence.

[`results.json`](results.json) records every accepted and rejected arm. Setup passed at +2.31% input tokens after the +50.89% recursive-discovery candidate was rejected. The fresh continuation passed behavior and safety checks, but it does not claim a context-cost improvement.
