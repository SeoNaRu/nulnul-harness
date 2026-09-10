# Submission checklist

This checklist targets the verified public 3.2.0 package. Historical 3.1.0 evidence is preserved separately.

## Release preparation

- [x] Skills-only product; no new MCP server, app, hook, authentication, or external service
- [x] Matching `3.2.0` product manifests, marketplace metadata, and active submission pointers
- [x] Preserve historical public adoption, casebook, failed candidates, and closed instruction evaluation
- [x] Pack the final product and verify archive reproducibility and installed-source equality
- [x] Pass all 481 repository checks and the active-host documentation-debt check on the publication candidate
- [x] Publish the non-main candidate and watch its CI to green
- [x] Capture fresh exact-public Claude adoption and deterministic Meta adoption
- [x] Require `public_release_gate.py` to report `release_ready=true`
Final/latest publication requires a successful main CI run. The [GitHub release](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.2.0) records that run and publication state.

## Separate OpenAI directory submission

- [x] Public project identity: `nulnul harness`, publisher `SeoNaRu`, MIT license
- [x] Public repository and support, privacy, and terms URLs
- [ ] Confirm the publisher's verified identity and required portal permissions
- [ ] Prepare the Skills-only directory draft with the certified package and evidence
- [ ] Obtain explicit approval before Submit for Review
- [ ] After directory approval, obtain explicit approval before Publish
- [ ] Verify the exact public listing and installation in a clean user environment

GitHub release approval does not by itself authorize a separate directory submission or publication.
