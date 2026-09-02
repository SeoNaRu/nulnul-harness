#!/usr/bin/env python3
"""Validate bounded Governed authority; capability activation uses pre-work packs."""

import argparse
import hashlib
import json
from pathlib import Path


from sync_host_entry import SETUP_AUTHORITY, governed_setup_receipt


HOST_SURFACES = {"codex": (".agents", "AGENTS.md"), "claude": (".claude", "CLAUDE.md")}
STAGE_AUTHORITY = {
    "new-setup": (),
    "adopt-upgrade": (),
    "host-repair": ("{entry}",),
    "continuity": ("docs/nulnul/checkpoint.json", "docs/nulnul/checkpoint.verification.json"),
    "permission-transition": ("docs/nulnul/project.md",),
    "evolution": ("docs/nulnul/evolution.json", "docs/nulnul/evolution.archive.json"),
}


def canonical_digest(payload):
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def governed_stage(script, root, stage, host):
    if stage not in STAGE_AUTHORITY:
        raise ValueError("unknown governed stage")
    root = Path(root).resolve()
    project = root / "docs/nulnul/project.md"
    checkpoint = root / "docs/nulnul/checkpoint.json"
    receipt = root / "docs/nulnul/checkpoint.verification.json"
    evolution = root / "docs/nulnul/evolution.json"
    states = [path for path in (checkpoint, evolution) if path.is_file() and not path.is_symlink()]
    surface, entry_name = HOST_SURFACES[host]
    entry = root / entry_name
    entry_text = entry.read_text(encoding="utf-8") if entry.is_file() and not entry.is_symlink() else ""
    if stage == "new-setup" and (project.exists() or states):
        raise ValueError("new-setup is not eligible when durable setup already exists")
    if stage == "adopt-upgrade" and not project.is_file():
        raise ValueError("adopt-upgrade requires an existing project contract")
    if stage == "host-repair" and (
        len(states) != 1
        or (states[0].relative_to(root).as_posix() in entry_text and "nulnul:session-entry:start" in entry_text)
    ):
        raise ValueError("host-repair requires one live state and a missing or stale active entry")
    if stage == "continuity" and not (checkpoint.is_file() and receipt.is_file()):
        raise ValueError("continuity requires checkpoint and verification receipt surfaces")
    if stage == "permission-transition" and not project.is_file():
        raise ValueError("permission-transition requires an existing project contract")
    if stage == "evolution" and not evolution.is_file():
        raise ValueError("evolution requires the existing evolution state")
    load_target = root / surface / "skills/nulnul-harness/SKILL.md"
    if load_target.is_symlink() or not load_target.is_file() or not load_target.resolve().is_relative_to(root):
        raise ValueError("governed stage contract is unavailable")
    if stage in {"new-setup", "adopt-upgrade"}:
        values = SETUP_AUTHORITY if host == "codex" else (
            "CLAUDE.md",
            "docs/nulnul/project.md",
            "docs/nulnul/checkpoint.json",
            "docs/nulnul/checkpoint.verification.json",
        )
    else:
        values = STAGE_AUTHORITY[stage]
    authority = [value.format(entry=entry_name) for value in values]
    source = {"activation": "GOVERNED", "stage": stage, "host": host, "authority": authority}
    receipt_value = (
        governed_setup_receipt(stage)
        if host == "codex" and stage in {"new-setup", "adopt-upgrade"}
        else canonical_digest(source)
    )
    return {
        "status": "activated",
        "activation": "GOVERNED",
        "sequence": ["STAGE_REQUESTED", "STAGE_VALIDATED", "GOVERNED_ACTIVATED"],
        "stage": stage,
        "host": host,
        "load_target": load_target.relative_to(root).as_posix(),
        "authority": authority,
        "activation_receipt": receipt_value,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("govern",))
    parser.add_argument("stage")
    parser.add_argument("--host", choices=sorted(HOST_SURFACES), required=True)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        payload = governed_stage(Path(__file__), args.root, args.stage, args.host)
        failed = False
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        payload = {"status": "unavailable", "reason": str(error)}
        failed = True
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
