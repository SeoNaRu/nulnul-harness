# Installed-copy and live-use validation — 2026-09-10

The user requested three steps: verify the actual installation, complete a small task and interrupted-check recovery, then repair observed problems and check again. These are bounded local development trials using fresh Codex sessions with the configured `gpt-6-astra` model. They are not a comparative model benchmark, public adoption, or evidence of general runtime savings.

## Installation

The enabled plugin already pointed to this local checkout, but its cached copy had 62 files and a 4,726-word entry. Fourteen shared files differed and three new files were missing. Reinstalling the existing local plugin with `codex plugin add nulnul-harness@nulnul-harness --json` refreshed the cache. All 65 product files then matched the source byte-for-byte.

Registration and version alone did not establish which instructions ran. The work session actually read the installed entry; its command output matched SHA-256 `f99575808be46caf1f296a8f93e2acf41d10a9f4ffa81b1ff5cb06455f45532e`, the retained 1,007-word entry. This does not prove an already-open parent session refreshed its previously loaded instructions.

## Observed work

| Step | Execution evidence | Result |
| --- | --- | --- |
| Small code correction | A fresh session edited the real checkpoint validator and its regression test in an isolated working copy | Integer receipt version `1` remains valid; `true`, `1.0` and other malformed values are rejected. The installed runner executed the recorded completion command once; all 12 tests passed. The reviewed two-file patch was applied to the source. |
| Forced interruption | The same recorded check was started with a controlled pause, then its dedicated process group was terminated | Both checkpoint and receipt remained `unknown`, so previous success could not authorize fast resume. |
| Fresh-session recovery | Another session read the stored state and used the installed runner | One completion-check execution, all 12 tests passed, checkpoint and receipt returned to `verified`. No implementation repair was needed. |

The check journal contains three starts and two completed passes: initial work, one deliberately interrupted attempt, and recovery. Each model session completed without waiting for user input. Both used noninteractive approval policy; interactive approval behavior was not measured. Raw local event logs, session identifiers and filesystem paths were not copied into this repository.

## Routing limitation in the initial trials

Both sessions issued one repository file-listing command before checkpoint validation. The implementation task succeeded, but this did not satisfy the instruction to validate the named checkpoint before repository-wide inspection.

After the first observation, the fast-resume section was moved ahead of general task routing and the runner invocation was spelled out. The recovery session still listed files first. Because the tasks differed, these two executions cannot estimate a causal cost change; they do show that the reorder did not eliminate the observed behavior. The reorder was restored to the preceding entry. No routing improvement or governed promotion is claimed, and another wording-only retry was not launched. The unresolved inspection order needs a separate root-cause investigation before claiming fast-resume conformance.

## Validation and retained changes

- Retained the receipt-schema type fix and its nine malformed-value negative cases plus the valid integer control.
- Documented how to refresh an already registered local development copy and verify fresh-session body loading.
- Local checks: checkpoint suite 12/12, trace compatibility 1/1, product suite 17/17, and valid skill format. After the documentation update, packaging passed with 65 files, all installed product files matched the source, the product suite passed again, and active Codex documentation debt was empty.
- Historical release counts, the closed instruction-routing A/B episode and public-adoption records remain unchanged. These trials grant no Release Gate points or publication authority.

## Follow-up: all three requested upgrades

The next bounded task repaired the actual resume entry, completed installed-copy comparison, and exercised documentation, bug repair and existing-project adoption. Five fresh Codex sessions ran against disposable synthetic utility projects: four planned cases and one conditional adoption repair. These are development observations, not customer deployments, sealed holdouts or a causal A/B comparison. The earlier closed experiment remains closed.

### Changes retained

- The managed host entry now emits shell-quoted validator and completion-runner commands from the executing installed skill. They run from the target project without requiring copied scripts or repository discovery. The previous handwritten trial entry did not exercise this shipped setup path; its literal project-relative validator command was unavailable. Foundation pre-session behavior is now conditional on an integrating host actually supplying a Pack.
- Explicit installed-copy inspection compares every shipped file, including references and assets, and reports `same`, `stale` or `unknown` with native refresh guidance in English and Korean. Comparison is bounded to 4,096 entries, 1 MiB per file and 16 MiB per tree. Unsafe or incomplete comparisons cannot establish a match; ordinary status does not traverse the product tree. Existing component fields remain compatible.
- Setup now distinguishes a first durable contract (`new-setup`, including populated repositories) from an existing NULNUL contract (`adopt-upgrade`). A local-only Codex roster must not invoke a potentially remote inventory command. The native unfiltered JSON listing attempted a remote catalog lookup in the first adoption trial; JSON output alone did not make it offline.

The skill description remains 244 characters; the entry is now 1,026 words. All five sessions read the same installed entry, SHA-256 `06be606666d52af8cf14fc026c65d56345baad131f4242eabb0767865ff89c6d`. Installed-body observation does not prove that an already-open parent thread reloaded its catalog.

### Actual outcomes

| Case | Observed result | Scope of evidence |
| --- | --- | --- |
| Document resume | Corrected the README check command; 2 tests passed through one recorded completion execution | Initial checkpoint was verified; validation preceded repository discovery, and reads stayed within the checkpoint and needed task/check inputs. |
| Bug resume | Preserved label case while collapsing whitespace; added one regression; 3 tests passed through one recorded completion execution | Initial checkpoint was verified; no repository listing occurred. The separately enabled Ponytail skill was also read, so strict whole-read-set conformance is not claimed. |
| Interrupted-check recovery | A dedicated paused check was terminated; checkpoint and receipt remained `unknown`; a new session restored verified state with one completion execution and 3 passing tests | Initial validation rejected fast resume. The full workflow repaired reported documentation debt; this is recovery evidence, not a verified-fast-path read-budget case. |
| First existing-project adoption | Transaction passed, reviewer was classified `reuse`, README was corrected and final checkpoint verified | Preserved the inactive host entry and role profile, but also repaired an existing label bug and attempted the native remote installed-catalog lookup. This is not a clean local-only, documentation-scope pass. |
| Adoption repair | Started again from the original project files, with code/test preservation explicit; setup and README work completed, 2 tests passed, checkpoint verified | No remote inventory command; code, tests, inactive entry and profile remained byte-identical. The session still repeated the completion check after the transaction and found trailing whitespace in the generated entry. |

Both adoption cases used the executing installed plugin and its transaction rather than a shadow project-local skill. All five finished with one checkpoint state and fresh verification evidence. Every model session used noninteractive approval policy, so absence of a confirmation pause does not measure interactive approval behavior. Model invocations themselves used the existing configured service; the local-only boundary concerned task-side operations.

### Final repairs, checks and limits

The generator's trailing whitespace was repaired at its source and covered by a regression assertion. The setup reference now explicitly reuses a passing transaction's current receipt when command, verification inputs and result remain unchanged; descriptive checkpoint edits alone do not justify another completion run. This last reuse clarification was not given a sixth model trial. No claim that adoption has eliminated every redundant check is made.

The full repository suite passed **476/476**. After the final whitespace correction, **18/18** host-entry, migration and Direct-surface checks passed; the product suite passed **17/17** after final packaging. New coverage executes generated commands from a project with quoted installation paths, rejects unknown/stale evidence, preserves inactive-host files, detects changes outside the old component list, and rejects unsafe/oversized installation trees. Two obsolete prose assertions found during the full run were replaced with migration execution and block-ownership checks.

Final packaging contains **65 files**, the registered local cache matches every shipped file, skill format is valid, and active Codex documentation debt is empty. Release Gate remains **100/100 for the local candidate**, with `release_ready: false`: exact public Claude/Meta adoption and release publication are still outstanding. These trials add no Release Gate points and authorize no public release. Raw commands, private paths and session identifiers remain outside this document.

The five-session budget is closed. The observed repository-discovery ordering improved in these cases; a comparative speed gain, universal routing guarantee, strict whole-read-set pass for every session and complete elimination of adoption rechecks remain unproven.

## Sequential follow-up: transaction-owned check reuse

A separately approved episode reproduced the remaining adoption recheck before proceeding to an actual Trace task and release preparation. The earlier five-session history and rejected instruction-routing experiment remain closed. All three bounded model calls completed: one reproduction, one conditional repair, and one actual Trace task. No further local model retries were used.

| Observation | Recorded result |
| --- | --- |
| Initial reproduction | Two successful setup transactions executed the same recorded completion command twice after one direct baseline check. One intermediate plan was invalid. Descriptive setup rewriting re-entered the transaction's unconditional completion check; the verdict remains a redundant-completion nonpass. |
| Conditional repair verification | Two metadata-only adoption transactions added zero completion executions. The existing journal retained two starts and the prior verification receipt remained byte-identical. Eleven other files were preserved; the project contract shortened by 931 bytes and checkpoint by 151 bytes. |

The fix belongs to `setup_transaction.execute`: reuse requires a verified schema-v3 checkpoint, matching command digest and verification-file list, and current file fingerprints both before setup writes and after project/host writes. Missing, unknown, failed, stale, or command/input-changed evidence invokes the existing completion runner. A changed host or setup document included among verification inputs also forces execution. The transaction retains its rollback and single-writer boundary; reuse reports `reused: true` with `exit_code: null`, rather than claiming another execution.

Five added regression tests cover reuse, changed source and failed-check rollback, command/file-list changes, untrusted prior evidence, and checked host/setup changes. The full repository suite passed **481/481**, and independent read-only review found no blocking regression. These are a known exposed regression and its conditional repair verification, not a holdout, A/B comparison, public-adoption credit, or universal savings claim.
## Actual project: quoted verification paths in Trace

The existing NULNUL Trace working tree missed supported Python verification scripts when their literal path was quoted and contained spaces. A fresh Codex session repaired the shared classifier in an isolated snapshot of the actual current source, including existing user changes. This was an actual project repair, not a synthetic utility adoption or independent transfer benchmark.

The two-file change accepts ordinary single- and double-quoted script paths and retains the exact comparison identity. Three focused regression groups cover valid paths, wrong filenames, and unsafe composition/substitution; downstream regression comparisons also check shell wrappers and distinct arguments, quoting and paths. The new tests failed against the old code in a disposable copy. The installed runner then executed the existing `pnpm test` command once, passing four trace-core and five collector test files and their affected builds.

After review and original-file hash checks, only the classifier and its regression tests were applied to the original project. Its recorded completion command passed once more as an integration check and restored a verified checkpoint. Original-project memory guard passed against its existing active item; private memory was not copied into the snapshot. Inactive host guidance, role/skill profiles, dependencies and unrelated source were preserved. No Trace commit or publication was performed.

The worker's completion run and the supervisor's original-workspace integration run are distinct checks. These observations establish this repair and receipt-reuse case, without attributing comparative speed or general task superiority to the harness. The initial adoption nonpass remains linked to its Coach feedback and bounded proposal in [the machine-readable report](../evals/release-3.2.0-validation.json); ordinary code maintenance does not promote an agent version.
