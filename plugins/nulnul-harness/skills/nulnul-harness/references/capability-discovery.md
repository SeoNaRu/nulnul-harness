# Capability discovery

Reuse mature work before creating a local substitute.

## Map the job

For each required capability, state:

- the exact input and output
- the user-visible or mechanical quality check
- whether it reads local, public, private, or regulated data
- whether it writes files, changes external state, requires authentication, or adds recurring cost
- whether the job recurs enough to justify a durable capability

Do not search for vague categories such as “all useful tools.”

## Search in trust order

1. Native tools and already installed skills, plugins, and connectors visible in the current session.
2. Repository-local capabilities already used successfully by the project.
3. OpenAI-built or curated skills and plugins available to the user's surface.
4. Maintained public skills or plugins from identifiable publishers and source repositories.

Use the available skill or plugin catalog first. Installed or catalog-listed means available, not verified. Inspect the local `SKILL.md`, plugin manifest, declared dependencies, and source metadata for each serious candidate. Use read-only web or repository search for current public maintenance, adoption, license, and issue evidence when those claims affect selection. If a source or dimension cannot be checked, label the candidate provisional and report the gap instead of inventing availability, adoption, or verification.

## Verify candidates

Record evidence for each serious candidate:

| Dimension | Acceptable evidence |
| --- | --- |
| Job fit | documented workflow matches the required input, output, and check |
| Provenance | identifiable publisher and inspectable source or official listing |
| Compatibility | current Codex skill or plugin structure and supported surface |
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
