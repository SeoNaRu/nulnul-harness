#!/usr/bin/env python3
"""Synchronize only the active host's root NULNUL session entry."""

import argparse
import hashlib
import json
import os
import re
import shlex
import stat
import sys
import tempfile
from pathlib import Path


HOST_ENTRIES = {"codex": "AGENTS.md", "claude": "CLAUDE.md"}
START = "<!-- nulnul:session-entry:start -->"
END = "<!-- nulnul:session-entry:end -->"
SETUP_AUTHORITY = (
    "AGENTS.md",
    "docs/nulnul/project.md",
    "docs/nulnul/checkpoint.json",
    "docs/nulnul/checkpoint.verification.json",
)
LEGACY_RULE = Path(".codex/rules/nulnul-activation.rules")
LEGACY_RULE_SHA256 = "9e924670b92c543c253f2aec679d30e47b012c5d53ab93756e6608beda6566ef"


sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_project_setup


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


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def governed_setup_receipt(stage):
    source = {
        "activation": "GOVERNED",
        "stage": stage,
        "host": "codex",
        "authority": list(SETUP_AUTHORITY),
    }
    return sha256_bytes(json.dumps(source, sort_keys=True, separators=(",", ":")).encode())


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


def managed_block(host, state):
    entry = HOST_ENTRIES[host]
    other = HOST_ENTRIES["claude" if host == "codex" else "codex"]
    if host == "codex":
        opportunity = (
            " If a Foundation host supplies a bound Pack, use supplied context without Pack "
            "lifecycle commands. No selected body is Direct."
        )
    else:
        opportunity = ""
    resume = ""
    if state.as_posix() == "docs/nulnul/checkpoint.json":
        scripts = Path(__file__).resolve().parent
        validator = shlex.join(["python3", str(scripts / "validate_checkpoint.py"), state.as_posix()])
        runner = shlex.join(["python3", str(scripts / "run_checkpoint_check.py"), state.as_posix()])
        resume = (
            "On checkpoint resume, before discovery, run from project root:\n"
            f"```sh\n{validator}\n```\n"
            "If `fast_path_ready` is true and scope/permissions match, read checkpoint and needed "
            "task files only; otherwise use full workflow. Then run the recorded check once:\n"
            f"```sh\n{runner}\n```\n"
        )
    return (
        f"{START}\n"
        "## NULNUL task entry\n\n"
        f"{host} owns `{entry}`; preserve `{other}`. "
        "Load NULNUL only for explicit setup, repair, continuation, or evolution."
        f"{opportunity}\n{resume}"
        f"Stable setup: `docs/nulnul/project.md`; state: `{state.as_posix()}`; one writer.\n"
        f"{END}"
    )


def merge_entry(existing, block):
    starts = existing.count(START)
    ends = existing.count(END)
    if starts != ends or starts > 1:
        raise ValueError("root guidance has an ambiguous NULNUL session-entry block")
    if starts == 1:
        return re.sub(
            rf"{re.escape(START)}.*?{re.escape(END)}",
            lambda _match: block,
            existing,
            count=1,
            flags=re.DOTALL,
        )
    prefix = existing.rstrip()
    return (prefix + "\n\n" if prefix else "") + block + "\n"


def shared_state(root):
    states = [
        path
        for path in (
            root / "docs/nulnul/checkpoint.json",
            root / "docs/nulnul/evolution.json",
        )
        if path.exists()
    ]
    if len(states) != 1:
        raise ValueError("exactly one shared checkpoint.json or evolution.json is required")
    state = states[0]
    if state.is_symlink() or not state.is_file():
        raise ValueError("shared state must be a regular repository file")
    return state.relative_to(root)


def validate_setup_for_runtime(root):
    project = root / "docs/nulnul/project.md"
    if project.is_symlink() or not project.is_file():
        raise ValueError("project setup contract is unavailable")
    text = project.read_text(encoding="utf-8")
    errors = validate_project_setup.validate(text)
    errors.extend(validate_project_setup.capability_contract.validate(text, require_canonical=True))
    errors = list(dict.fromkeys(errors))
    if errors:
        raise ValueError("setup is not runtime-valid: " + "; ".join(errors))


def retire_legacy_runtime_rule(root):
    """Remove only the exact retired rule during explicit teardown/adoption cleanup."""
    root = Path(root).resolve()
    target = root / LEGACY_RULE
    if target.is_symlink() or not target.resolve(strict=False).is_relative_to(root):
        raise ValueError("legacy Codex rule path is unsafe")
    if not target.exists():
        return {"status": "LEGACY_RUNTIME_RULE_ABSENT", "changed": False, "trust_mutated": False}
    if not target.is_file() or sha256_bytes(target.read_bytes()) != LEGACY_RULE_SHA256:
        raise ValueError("refusing to remove a foreign Codex rule")
    try:
        target.unlink()
    except OSError as error:
        return {
            "status": "LEGACY_RUNTIME_RULE_REMOVAL_REQUIRED",
            "changed": False,
            "trust_mutated": False,
            "reason": str(error),
        }
    return {"status": "LEGACY_RUNTIME_RULE_RETIRED", "changed": True, "trust_mutated": False}


def sync(root, host):
    if host not in HOST_ENTRIES:
        raise ValueError("unsupported host")
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("project root must be an existing directory")
    state = shared_state(root)
    target = root / HOST_ENTRIES[host]
    if target.is_symlink():
        raise ValueError("root guidance must not be a symlink")
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    updated = merge_entry(existing, managed_block(host, state))
    if updated == existing:
        status = "unchanged"
    else:
        atomic_write(target, updated)
        status = "updated" if existing else "created"
    result = {
        "status": status,
        "host": host,
        "entry": HOST_ENTRIES[host],
        "shared_state": state.as_posix(),
        "other_host_entry_touched": False,
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", choices=sorted(HOST_ENTRIES))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--retire-runtime-activation", action="store_true")
    args = parser.parse_args()
    try:
        if args.retire_runtime_activation:
            if args.host != "codex":
                raise ValueError("retired Codex rule cleanup requires the Codex host")
            result = retire_legacy_runtime_rule(args.root) | {"host": "codex"}
            failed = result["status"] == "LEGACY_RUNTIME_RULE_REMOVAL_REQUIRED"
        else:
            result = sync(args.root, args.host)
            failed = result.get("status") == "failed"
    except (OSError, UnicodeError, ValueError) as error:
        result = {"status": "failed", "error": str(error)}
        failed = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
