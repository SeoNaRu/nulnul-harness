#!/usr/bin/env python3
"""Migrate a legacy project contract to one safe concise checkpoint."""

import argparse
import json
import os
import re
import stat
import tempfile
from pathlib import Path

import validate_checkpoint


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
        "schema_version": 2,
        "goal": goal,
        "milestone": milestone,
        "completion_check": completion.group(1).strip(),
        "verification_status": "unknown",
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


def temporary_file(path, text, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.chmod(mode)
    return temporary


def atomic_write(path, text):
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    temporary = temporary_file(path, text, mode)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_batch_write(updates, replace=os.replace):
    originals = {
        path: (path.read_text(encoding="utf-8"), stat.S_IMODE(path.stat().st_mode))
        if path.exists() else None
        for path in updates
    }
    temporaries = {}
    try:
        for path, text in updates.items():
            temporaries[path] = temporary_file(
                path, text, originals[path][1] if originals[path] else 0o644
            )
    except OSError:
        for temporary in temporaries.values():
            temporary.unlink(missing_ok=True)
        raise
    replaced = []
    try:
        for path, temporary in temporaries.items():
            replace(temporary, path)
            replaced.append(path)
    except OSError:
        for path in reversed(replaced):
            original = originals[path]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, original[0])
                path.chmod(original[1])
        raise
    finally:
        for temporary in temporaries.values():
            temporary.unlink(missing_ok=True)


def migrate(contract_path, guidance_path):
    checkpoint_path = contract_path.with_name("checkpoint.json")
    evolution_path = contract_path.with_name("evolution.json")
    if evolution_path.exists():
        return {"status": "skipped", "reason": "evolution.json already owns live state"}
    if ".claude" in guidance_path.parts:
        raise ValueError("host-protected .claude paths are read-only")

    contract = contract_path.read_text(encoding="utf-8")
    guidance = guidance_path.read_text(encoding="utf-8")
    entry = (
        "Resume from `docs/nulnul/checkpoint.json`; use the fast path only when "
        "`verification_status` is `verified`."
    )
    updated_guidance = guidance if "docs/nulnul/checkpoint.json" in guidance else guidance.rstrip() + "\n\n" + entry + "\n"
    if checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if not isinstance(checkpoint, dict) or checkpoint.get("schema_version") not in {1, 2}:
            raise ValueError("existing checkpoint is not a supported schema-version-1-or-2 object")
        if checkpoint["schema_version"] == 2:
            errors = validate_checkpoint.validate(checkpoint)
            if errors:
                raise ValueError("existing schema-version-2 checkpoint is invalid: " + "; ".join(errors))
            return {"status": "skipped", "reason": "checkpoint.json is already current"}
        checkpoint["schema_version"] = 2
        checkpoint.setdefault("verification_status", "unknown")
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
