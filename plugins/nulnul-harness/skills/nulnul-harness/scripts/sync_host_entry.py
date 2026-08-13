#!/usr/bin/env python3
"""Synchronize only the active host's root NULNUL session entry."""

import argparse
import json
import os
import re
import stat
import tempfile
from pathlib import Path


HOST_ENTRIES = {"codex": "AGENTS.md", "claude": "CLAUDE.md"}
START = "<!-- nulnul:session-entry:start -->"
END = "<!-- nulnul:session-entry:end -->"


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


def managed_block(host, state):
    entry = HOST_ENTRIES[host]
    other = HOST_ENTRIES["claude" if host == "codex" else "codex"]
    label = "Codex" if host == "codex" else "Claude Code"
    if state.name == "checkpoint.json":
        resume = (
            f"Validate `{state.as_posix()}` before repository-wide inspection; when "
            "`fast_path_ready` is true, read only it and directly needed task files."
        )
    else:
        resume = (
            f"Validate `{state.as_posix()}` before relying on its checkpoint, then resume "
            "from its recorded next action."
        )
    return (
        f"{START}\n"
        "## NULNUL session entry\n\n"
        f"This is the {label}-owned root entry (`{entry}`). During a {label} run, do not "
        f"create or modify `{other}`.\n\n"
        f"{resume} Use `docs/nulnul/project.md` for stable shared setup. Both hosts share "
        "the existing `docs/nulnul/` state; do not create a second live-state writer.\n"
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
            block,
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


def sync(root, host):
    if host not in HOST_ENTRIES:
        raise ValueError("unsupported host")
    root = Path(root)
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
    return {
        "status": status,
        "host": host,
        "entry": HOST_ENTRIES[host],
        "shared_state": state.as_posix(),
        "other_host_entry_touched": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", choices=sorted(HOST_ENTRIES))
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        result = sync(args.root, args.host)
        failed = False
    except (OSError, UnicodeError, ValueError) as error:
        result = {"status": "failed", "error": str(error)}
        failed = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
