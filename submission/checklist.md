# Submission checklist

## Complete locally

- [x] Skills-only plugin with no MCP, app, hook, authentication, or external service
- [x] Strict-semver `2.0.1` manifest and production square logo
- [x] Plugin structure validator passes
- [x] Full 215-test suite and Release Gate 100/100 pass
- [x] Fresh exact-public Codex/Claude host-ownership and cross-project Meta adoption pass
- [x] Ordinary project-start requests implicitly trigger `nulnul-harness`; read-only requests do not
- [x] Local install, removal, clean reinstall, installed-source equality, and installed-skill validation pass for `nulnul-harness`
- [x] `dist/nulnul-harness-2.0.1.zip` passes archive integrity validation and matches the public release asset
- [x] Privacy, terms, support, listing copy, release notes, and MIT license drafted
- [ ] Current public checks find no conflicting `nulnul harness` listing or package identity

## Requires publisher action or approval

- [x] Confirm `nulnul harness`, `SeoNaRu`, and MIT as the public name, publisher, and license
- [x] Create the public `SeoNaRu/nulnul-harness` repository
- [x] Publish the prepared repository, making the website, support, privacy, and terms URLs live
- [ ] Ensure the OpenAI organization has a verified developer or business identity and **Apps Management: Write**
- [ ] Create a **Skills only** draft at <https://platform.openai.com/plugins>
- [ ] Upload `dist/nulnul-harness-2.0.1.zip`, listing copy, logo, starter prompts, `evals/cases.json`, release notes, and selected countries
- [ ] Review the policy attestations and explicitly approve **Submit for Review**
- [ ] After OpenAI approval, explicitly approve **Publish**
- [ ] Find the exact public listing and verify installation in a clean user environment
