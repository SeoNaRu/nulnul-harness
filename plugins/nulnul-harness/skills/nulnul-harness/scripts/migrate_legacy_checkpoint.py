#!/usr/bin/env python3
"""Migrate a legacy project contract to one safe concise checkpoint."""

import argparse
import json
import re
from pathlib import Path

import validate_checkpoint
from sync_host_entry import atomic_batch_write, managed_block, merge_entry


def section(text, heading):
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def prose(text):
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def permission_constraints(contract):
    return [
        line[2:].strip()
        for line in section(contract, "Constraints and permissions").splitlines()
        if line.startswith("- ") and line[2:].strip()
    ]


def build_checkpoint(contract):
    goal = prose(section(contract, "Goal"))
    milestone_section = section(contract, "Current milestone")
    completion = re.search(r"^Observable completion check:\s*(.+)$", milestone_section, re.MULTILINE)
    milestone = prose(re.sub(r"^Observable completion check:.*$", "", milestone_section, flags=re.MULTILINE))
    if not goal or not milestone or completion is None:
        raise ValueError("legacy contract is missing goal, milestone, or completion check")
    payload = {
        "schema_version": 3,
        "goal": goal,
        "milestone": milestone,
        "completion_check": completion.group(1).strip(),
        "verification_status": "unknown",
        "verification_files": [],
        "last_verified": "Legacy setup has no machine-readable verification result.",
        "next_action": "Run the recorded completion check, then record verified evidence.",
        "permission_constraints": permission_constraints(contract),
        "approved_permissions": [],
        "blockers": ["Re-verify this migrated checkpoint before fast resume."],
    }
    errors = validate_checkpoint.validate(payload)
    if errors:
        raise ValueError("migrated checkpoint is invalid: " + "; ".join(errors))
    return payload


def migrate(contract_path, guidance_path):
    checkpoint_path = contract_path.with_name("checkpoint.json")
    evolution_path = contract_path.with_name("evolution.json")
    if evolution_path.exists():
        return {"status": "skipped", "reason": "evolution.json already owns live state"}
    if ".claude" in guidance_path.parts:
        raise ValueError("host-protected .claude paths are read-only")

    contract = contract_path.read_text(encoding="utf-8")
    guidance = guidance_path.read_text(encoding="utf-8")
    if guidance_path.name == "AGENTS.md":
        host = "codex"
    elif guidance_path.name == "CLAUDE.md":
        host = "claude"
    else:
        raise ValueError("guidance must be the active host root AGENTS.md or CLAUDE.md")
    updated_guidance = merge_entry(
        guidance,
        managed_block(host, Path("docs/nulnul/checkpoint.json")),
    )
    if checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if not isinstance(checkpoint, dict) or checkpoint.get("schema_version") not in {1, 2, 3}:
            raise ValueError("existing checkpoint is not a supported schema-version-1-through-3 object")
        if checkpoint["schema_version"] == 3:
            errors = validate_checkpoint.validate(checkpoint)
            if errors:
                raise ValueError("existing schema-version-3 checkpoint is invalid: " + "; ".join(errors))
            return {"status": "skipped", "reason": "checkpoint.json is already current"}
        errors = validate_checkpoint.validate(checkpoint)
        if errors:
            raise ValueError("existing legacy checkpoint is invalid: " + "; ".join(errors))
        checkpoint["schema_version"] = 3
        checkpoint["verification_status"] = "unknown"
        checkpoint["verification_files"] = []
        checkpoint.setdefault("permission_constraints", permission_constraints(contract))
        blockers = checkpoint.get("blockers")
        if not isinstance(blockers, list):
            raise ValueError("existing checkpoint blockers must be an array")
        warning = "Re-verify this migrated checkpoint before fast resume."
        if warning not in blockers:
            blockers.append(warning)
        errors = validate_checkpoint.validate(checkpoint)
        if errors:
            raise ValueError("upgraded checkpoint is invalid: " + "; ".join(errors))
        atomic_batch_write({
            checkpoint_path: json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n",
            guidance_path: updated_guidance,
        })
        return {"status": "upgraded", "checkpoint": str(checkpoint_path)}

    continuity = section(contract, "Continuity")
    if "Evolution state:" not in continuity or "not needed" in continuity:
        return {"status": "skipped", "reason": "no durable legacy state to migrate"}
    checkpoint = build_checkpoint(contract)
    updated_contract = re.sub(
        r"^- Evolution state:.*$",
        "- Active checkpoint: `docs/nulnul/checkpoint.json`",
        contract,
        count=1,
        flags=re.MULTILINE,
    )
    atomic_batch_write({
        checkpoint_path: json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n",
        contract_path: updated_contract,
        guidance_path: updated_guidance,
    })
    return {"status": "created", "checkpoint": str(checkpoint_path)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("guidance", type=Path)
    args = parser.parse_args()
    try:
        result = migrate(args.contract, args.guidance)
        failed = False
    except (OSError, UnicodeError, ValueError) as error:
        result = {"status": "failed", "error": str(error)}
        failed = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
