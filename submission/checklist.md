# Submission checklist

This checklist targets the local 3.1.0 candidate. Historical 3.0.0 public adoption and installation results do not certify the candidate.

## Complete locally

- [x] Skills-only plugin with no MCP, app, hook, authentication, or external service
- [x] Strict-semver `3.1.0` manifest and production square logo
- [x] Plugin structure validator passes
- [x] Full 444-test suite passes for the repaired public-bootstrap candidate; original untracked research files remain local
- [ ] Fresh exact-public Claude and Meta adoption pass for the repaired bytes before the final Release Gate
- [ ] Fresh exact-3.1.0 public Codex/Claude host-ownership and cross-project Meta adoption pass
- [x] Ordinary project-start requests implicitly trigger `nulnul-harness`; read-only requests do not
- [ ] Exact-3.1.0 local install, removal, clean reinstall, installed-source equality, and installed-skill validation pass for `nulnul-harness`
- [x] `dist/nulnul-harness-3.1.0.zip` passes archive integrity and reproducibility validation
- [x] Privacy, terms, support, listing copy, release notes, and MIT license drafted
- [x] Exact-name public web and current Codex catalog checks find no conflicting `nulnul harness` identity as of 2026-08-14; portal validation remains authoritative

## Requires publisher action or approval

- [x] Confirm `nulnul harness`, `SeoNaRu`, and MIT as the public name, publisher, and license
- [x] Create the public `SeoNaRu/nulnul-harness` repository
- [x] Publish the prepared repository, making the website, support, privacy, and terms URLs live
- [ ] Ensure the OpenAI organization has a verified developer or business identity and **Apps Management: Write**
- [ ] Create a **Skills only** draft at <https://platform.openai.com/plugins>
- [ ] Upload `dist/nulnul-harness-3.1.0.zip`, listing copy, logo, starter prompts, `evals/cases.json`, release notes, and selected countries
- [ ] Review the policy attestations and explicitly approve **Submit for Review**
- [ ] After OpenAI approval, explicitly approve **Publish**
- [ ] Find the exact public listing and verify installation in a clean user environment
