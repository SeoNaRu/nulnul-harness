# Submission checklist

This checklist targets the 3.2.0 publication candidate. Historical 3.1.0 checks and public adoption do not certify its changed bytes.

## Release preparation

- [x] Skills-only product; no new MCP server, app, hook, authentication, or external service
- [x] Matching `3.2.0` product manifests, marketplace metadata, and active submission pointers
- [x] Preserve historical public adoption, casebook, failed candidates, and closed instruction evaluation
- [ ] Pack the final product and verify archive reproducibility and installed-source equality
- [x] Pass all 481 repository checks and the active-host documentation-debt check on the publication candidate
- [ ] Publish the non-main candidate and watch its CI to green
- [ ] Capture fresh exact-public Claude adoption and deterministic Meta adoption
- [ ] Require `public_release_gate.py` to report `release_ready=true`
- [ ] Watch final main CI to green before marking the GitHub release final/latest

## Separate OpenAI directory submission

- [x] Public project identity: `nulnul harness`, publisher `SeoNaRu`, MIT license
- [x] Public repository and support, privacy, and terms URLs
- [ ] Confirm the publisher's verified identity and required portal permissions
- [ ] Prepare the Skills-only directory draft with the certified package and evidence
- [ ] Obtain explicit approval before Submit for Review
- [ ] After directory approval, obtain explicit approval before Publish
- [ ] Verify the exact public listing and installation in a clean user environment

GitHub release approval does not by itself authorize a separate directory submission or publication.
