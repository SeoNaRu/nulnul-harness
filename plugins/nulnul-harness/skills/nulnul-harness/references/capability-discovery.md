# Capability discovery

Reuse mature work before creating a local substitute.

## Map the job

For each required capability, state:

- the exact input and output
- the user-visible or mechanical quality check
- whether it reads local, public, private, or regulated data
- whether it writes files, changes external state, requires authentication, or adds recurring cost
- whether the job recurs enough to justify a durable capability
- how much context the capability spends per use, and whether it reduces context cost elsewhere

Do not search for vague categories such as “all useful tools.”

Skip the outward search when the inspected roster already has an adequate capability for every required job and a runnable completion check. Skipping the search never means skipping step 1 below: the installed roster is enumerated every time, because “adequate” is a claim about capabilities that were actually read. Search outward only for uncovered jobs. Stop when each uncovered job has one adequate verified candidate; compare more candidates only when the first has a concrete fit, safety, compatibility, or maintenance gap.

## Recurring jobs that hosts usually leave uncovered

Check these against the roster on every setup or adoption run, because a repository rarely names them and they stay uncovered by default:

- **Context economy** — a capability that shortens model output, compresses tool output, or suppresses over-building. It pays for itself in every later session, so an uncovered context-economy job is a real gap, not a nicety.
- **Session continuity** — resuming from the last verified checkpoint instead of re-deriving it.
- **Independent verification** — a reviewer or Gate that the proposal author cannot act as.

## Search in trust order

1. Native tools and already installed skills, plugins, agents, and connectors visible in the current session. Enumerate them; do not assume. Read the session's own skill and agent listings, then the host's capability directories from the surface map in `project-files.md` — for example `.claude/skills/`, `.claude/agents/`, and installed plugin caches on Claude Code, or `.agents/skills/` on Codex. Record the roster before judging coverage.
2. Repository-local capabilities already used successfully by the project.
3. First-party or curated skills and plugins available to the user's surface, from the host vendor or its official marketplace.
4. Maintained public skills or plugins from identifiable publishers and source repositories. Use `capability-registry.md` for where to look; it names the host marketplace, the sources this machine already trusts, and known candidates for the recurring jobs above.

Use the available skill or plugin catalog first. Installed or catalog-listed means available, not verified. Inspect the local `SKILL.md`, plugin manifest, declared dependencies, and source metadata for each serious candidate. Use read-only web or repository search for current public maintenance, adoption, license, and issue evidence when those claims affect selection. If a source or dimension cannot be checked, label the candidate provisional and report the gap instead of inventing availability, adoption, or verification.

## Verify candidates

Record evidence for each serious candidate:

| Dimension | Acceptable evidence |
| --- | --- |
| Job fit | documented workflow matches the required input, output, and check |
| Provenance | identifiable publisher and inspectable source or official listing |
| Compatibility | the host's current skill, plugin, and agent structure and supported surface |
| Context cost | per-use context spend is proportionate to the job, and any claimed saving is measured rather than asserted |
| Maintenance | recent meaningful updates, resolved issues, or an intentionally stable scope |
| Adoption | credible installs, users, references, stars, or project history; use only as supporting evidence |
| Quality | focused instructions, examples, tests, evals, or repeatable demonstrations |
| Permissions | least privilege, explicit external writes, and no hidden credential handling |
| License | permits the intended installation, use, or adaptation |

Popularity does not override a security, permission, compatibility, or job-fit failure. A successful local smoke test proves only the exercised behavior, not publisher trust or broad quality. Do not copy third-party content when the license is missing or incompatible.

## Select and acquire

- Prefer an adequate verified installed capability over a marginally better new dependency. Use a provisional installed capability only for a reversible, bounded run whose missing evidence is disclosed and whose permissions remain safe.
- Select the fewest non-overlapping candidates that cover the complete workflow.
- Explain what will be installed, from where, for which job, and at what scope.
- Obtain explicit approval before downloads, global installs, plugin or MCP registration, authentication, or external writes.
- After approval, use the host's plugin installer or `$skill-installer` when available instead of inventing a parallel installation mechanism.
- Reinspect installed content before relying on it. Pin or record the source revision when reproducibility matters.

Create a project-local skill only when no adequate candidate remains. Record the candidates checked, rejection reasons, the new skill's narrow job, and its removal condition.
