# Submission checklist

## Complete locally

- [x] Skills-only plugin with no MCP, app, hook, authentication, or external service
- [x] Strict-semver `1.2.0` manifest and production square logo
- [x] Plugin structure validator passes
- [x] Six positive and three negative reviewer scenarios pass for the renamed package
- [x] Ordinary project-start requests implicitly trigger `nulnul-harness`; read-only requests do not
- [x] Local install, removal, clean reinstall, installed-source equality, and installed-skill validation pass for `nulnul-harness`
- [x] `dist/nulnul-harness-1.2.0.zip` passes archive integrity validation
- [x] Privacy, terms, support, listing copy, release notes, and MIT license drafted
- [ ] Current public checks find no conflicting `nulnul harness` listing or package identity

## Requires publisher action or approval

- [x] Confirm `nulnul harness`, `SeoNaRu`, and MIT as the public name, publisher, and license
- [x] Create the public `SeoNaRu/nulnul-harness` repository
- [x] Publish the prepared repository, making the website, support, privacy, and terms URLs live
- [ ] Ensure the OpenAI organization has a verified individual or business identity and **Apps Management: Write**
- [ ] Create a **Skills only** draft at <https://platform.openai.com/plugins>
- [ ] Upload `dist/nulnul-harness-1.2.0.zip`, listing copy, logo, starter prompts, `evals/cases.json`, release notes, and selected countries
- [ ] Review the policy attestations and explicitly approve **Submit for Review**
- [ ] After OpenAI approval, explicitly approve **Publish**
- [ ] Find the exact public listing and verify installation in a clean user environment
