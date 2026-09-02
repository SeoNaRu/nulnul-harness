#!/usr/bin/env python3
from pathlib import Path

root = Path(".")
entry = (root / "AGENTS.md").read_text(encoding="utf-8")
project = (root / "docs/nulnul/project.md").read_text(encoding="utf-8")
rule = root / ".codex/rules/nulnul-activation.rules"
asset = root / ".agents/skills/nulnul-harness/assets/codex-activation.rules"
assert "Webhook delivery working agreement" in entry
assert entry.count("<!-- nulnul:session-entry:start -->") == 1
assert "## Accepted capabilities" in project
assert "project-api-validation" in project
assert "project-release-docs" in project
assert rule.is_file() and asset.is_file() and rule.read_bytes() == asset.read_bytes()
print("Foundation host setup verified")
