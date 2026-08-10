# nulnul harness 1.1.0

This release adds controlled personal-agent evolution and verified session continuity.

Workers can now report bounded evidence to a Coach, which proposes one targeted version change. An independent Gate compares the candidate with the last accepted version before promotion, rejection, or rollback. The same rule applies when the Coach itself is improved: no agent can approve its own upgrade. A repository-local checkpoint lets the Navigator resume the original goal from verified state instead of reconstructing it from chat.

The release includes a deterministic standard-library validator for evolution state. It rejects self-approval, invalid version transitions, unapproved permission expansion, broken references, and sensitive persisted fields. `nulnul harness` remains skills-only, with no service, authentication, telemetry, hook, UI, or background process.
