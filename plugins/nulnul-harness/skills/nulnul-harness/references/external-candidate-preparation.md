# Prepare an inspected external skill candidate

Use only for an uncovered job or concrete material gap under `capability-discovery.md`. This offline bridge makes inspected public bytes available to the existing `LOCAL_DIRECTORY` adapter. It never fetches a repository, installs a skill, registers a plugin, executes an acquired body, or grants acceptance.

Inspect fit, maintenance, provenance, host compatibility, tools, dependencies, permissions, and license first. Acquisition retains its existing approval requirement. Keep supplied source in an approved local directory. Record the full 40-character lowercase Git revision, exact GitHub blob URL for that revision and body path, and independently observed body and license SHA-256 digests. Matching supplied bytes to declared hashes is not independent authentication of GitHub provenance; retain acquisition evidence separately.

Use the existing capability manifest fields in a preparation specification:

```json
{
  "source_id": "inspected-skill",
  "source_revision": "0123456789abcdef0123456789abcdef01234567",
  "source_url": "https://github.com/example/project/blob/0123456789abcdef0123456789abcdef01234567/skills/example/skill.md",
  "body_path": "skills/example/skill.md",
  "body_digest": "<observed sha256>",
  "license_path": "LICENSE",
  "license_digest": "<observed sha256>",
  "capability": {
    "schema_version": 1,
    "capability_id": "inspected-skill",
    "capability_name": "Inspected skill",
    "capability_type": "SKILL",
    "declared_job": "The concrete project job",
    "license": "Apache-2.0",
    "required_tools": [],
    "required_permissions": [],
    "dependencies": [],
    "activation_trigger": "The narrow task condition",
    "project_check_identity": "The authoritative project check",
    "adaptation_required": true
  }
}
```

Replace placeholders from inspection. Never erase actual tools, permissions, dependencies, or incompatibilities to pass filtering. Set `adaptation_required` explicitly; foreign host tool names, mandatory teams, model assumptions, and incompatible authority rules require adaptation. Supply the existing approved policy for needed tools or permissions. Inspect the exact license text; a permissive label alone is insufficient.

```bash
python3 <skill>/scripts/external_competition.py prepare-source inspected-source preparation.json prepared-candidate --policy approved-policy.json
```

The output is a new directory under an existing approved parent, outside host registration directories. Existing directories are never overwritten. The command checks pinned URL/revision/path agreement, digests, bounded regular non-executable files, and skill frontmatter. It writes the unchanged body bytes as uppercase `SKILL.md`, the original license, and a manifest with origin metadata, then calls the existing source validator and policy filter. Failure removes only the new preparation. Filename normalization alone does not establish host compatibility.

This bridge packages only the inspected body and license. Additional bundled resources remain unsupported: adapt a bounded self-contained challenger or leave the candidate unsupported. A reference document without skill frontmatter is rejected; use it as cited design input to an explicitly authored local candidate instead.

The returned `sources` array feeds an existing discovery specification only after Natural Selection establishes its trigger. Discovery freezes the source in quarantine and still applies sanitization, compatibility, license, permission, and project-check filters. Prepared candidates are not Pack-selectable. Derived bodies use the existing `local-candidate --parent` lineage path, not mutation of frozen source. Add `skill-acceptance.md` cases, compete against the current capability, and adopt only through the existing rollback-safe transaction. No new authority or state writer is introduced.
