# nulnul harness 1.2.1

This patch stops `nulnul harness` from activating when a user-named local task contract already provides explicit inputs, outputs, constraints, and a runnable completion check. Project setup, capability selection, external-write planning, multi-session checkpointing, and evidence-gated evolution still activate the harness.

On the public offline workbook task, 1.2.0 and the Navigator v3 candidate both produced 3/3 exact results with no human intervention. The candidate reduced median elapsed time by 25.76%, input tokens by 25.90%, output tokens by 22.76%, and reasoning tokens by 39.34% versus 1.2.0. Two additional self-contained task types skipped activation, while an ambiguous empty project still activated and asked the required product question.

This is task-specific preliminary evidence, not a universal speed claim. The plugin remains skills-only with no service, authentication, telemetry, hook, UI, or background process.
