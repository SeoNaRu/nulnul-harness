# nulnul harness 1.2.0

This release makes controlled personal-agent evolution faster to enter, safer across repeated upgrades, and easier to adopt internationally.

Workers can now report bounded evidence to a Coach, which proposes one targeted version change. An independent Gate compares the candidate with the last accepted version before promotion, rejection, or rollback. The same rule applies when the Coach itself is improved: no agent can approve its own upgrade. A repository-local checkpoint lets the Navigator resume the original goal from verified state instead of reconstructing it from chat.

The deterministic standard-library validator now preserves continuous multi-promotion history while still rejecting target or declared proposal-author self-approval, broken chains, invalid transitions, unapproved permission expansion, broken references, and sensitive persisted fields. This is structural validation of recorded state, not cryptographic identity proof. `nulnul harness` remains skills-only, with no service, authentication, telemetry, hook, UI, or background process.

The default GitHub documentation now provides equivalent English and Korean onboarding. Automated checks keep locale links, version badges, install commands, evidence counts, and local documentation targets consistent.

Repositories with sufficient instructions, capabilities, and completion checks now take a direct execution path. Capability discovery runs only for uncovered jobs and stops after finding one adequate verified candidate per job.
