# NULNUL EXPERIMENT 14

## Integrated Foundation End-to-End Proof

Frozen before official arm 1:

- Foundation product tree: `6466a15772673f9650593b5488fb828aee9407b41d6ac0b05f8e774052288935`
- Foundation package: `982ae1c86bb38038831b4b04d982b222d487cee4ca3457af43daa2d3fea8ca7e`
- Champion revision: `cee7b91e2a992adee1582702b7a4084c631443b6`
- Champion artifact: `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b`
- Champion tree: `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`
- Foundation freeze predates all four fresh task hashes.
- Model-arm budget: exactly five, no retries or smoke calls.

The five official arms, in order, are Direct Champion, Direct Foundation,
Governed Setup Foundation, Project-Fit Foundation after a real Codex restart,
and a fresh next-session Foundation task. The last three share one real project
lifecycle; model conversation state never crosses processes.

The runner may invoke the shipped Foundation CLI automatically at host
boundaries and supply only observable execution facts to `task-finish`. It may
not write Session, Experience, Memory, promotion, or lineage records directly.
Those records receive credit only when the frozen product runtime validates and
writes them. Raw transcripts remain local-only and are excluded from Memory,
Context Packs, and Evolution queries.

Direct hard gate: Foundation input is no more than 120% of Champion, with zero
positive activation, body exposure/read, live/evolution-state read by the model,
unrelated Memory, or raw-history replay. Context is bounded to 8 items and 4096
serialized bytes.

Setup hard gate: host-owned trust is unchanged; Governed activation precedes
setup work; one canonical accepted-capability contract passes the same runtime
parser; the exact project rule is installed; current session stops at
`CODEX_RESTART_REQUIRED`; a fresh Codex process sees the trusted project layer.

Project-Fit hard gate: exact `project-api-validation`, no pre-commit body,
exactly one post-commit body, body before product write, strict/completion/check
PASS, linked activation/check/attribution receipts, and no unauthorized writes.

Foundation loop hard gate: the frozen product runtime automatically writes one
VERIFIED evolution-eligible Capability Experience, finalizes its Session and
handoff, promotes only the preregistered Lesson when the causal experience is
valid, restores relevant bounded Memory to a new Session without raw history,
validates the entire lineage, and returns the E14 Capability Experience from a
bounded eligible query. A fresh project has no prior version/digest Experience
boundary, so the required first query uses capability + job with `since = null`;
the record itself establishes the first future boundary.

Primary results are exactly `FOUNDATION_INTEGRATED_E2E_PROVEN`,
`FOUNDATION_CORE_FAILURE`, or `INFRASTRUCTURE_INVALID`. Interpretable product
failures do not become infrastructure failures and do not stop independent arms.
