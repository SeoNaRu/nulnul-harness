#!/usr/bin/env python3
"""Parse and validate the one project capability-acceptance contract."""

import argparse
import json
import re
from pathlib import Path


HEADING = "Accepted capabilities"
COLUMNS = (
    "Capability ID",
    "Job",
    "Activate when",
    "Project check",
    "Status",
    "Version or digest",
    "Logical load target",
)
CURRENT_STATUS = "accepted/current"
STATUSES = {CURRENT_STATUS, "provisional", "rejected", "retired", "superseded"}
IDENTITY = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
CHECK_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
LOGICAL_TARGET_ROOT = "capabilities"


def canonical_logical_target(identity):
    """Return the host-independent logical address owned by one capability ID."""
    if not isinstance(identity, str) or not IDENTITY.fullmatch(identity):
        raise ValueError(f"invalid capability id: {identity or '<empty>'}")
    return f"{LOGICAL_TARGET_ROOT}/{identity}/SKILL.md"


def accepted_record(row):
    """Bind model-selected semantic metadata to deterministic acceptance fields."""
    if not isinstance(row, dict):
        raise ValueError("accepted capability must be one object")
    identity = row.get("capability_id", "")
    target = canonical_logical_target(identity)
    asserted_target = row.get("logical_load_target")
    if asserted_target is not None and asserted_target != target:
        raise ValueError(f"CAPABILITY_TARGET_MISMATCH: {identity}")
    asserted_status = row.get("status")
    if asserted_status is not None and asserted_status != CURRENT_STATUS:
        raise ValueError(f"{identity}: accepted capability status must be {CURRENT_STATUS}")
    canonical = {
        "capability_id": identity,
        "job": row.get("job", ""),
        "activation_trigger": row.get("activation_trigger", ""),
        "project_check_identity": row.get("project_check_identity", ""),
        "status": CURRENT_STATUS,
        "version_or_digest": row.get("version_or_digest"),
        "logical_load_target": target,
    }
    return parse(render([canonical]), require_canonical=True)[0]


def markdown_table(text, heading=HEADING, columns=None):
    marker = f"## {heading}"
    match = re.search(rf"^{re.escape(marker)}\s*$", text, re.MULTILINE)
    if match is None:
        return None
    section = text[match.end():].split("\n## ", 1)[0]
    lines = [line for line in section.splitlines() if line.lstrip().startswith("|")]
    if len(lines) < 2:
        raise ValueError(f"{heading} must contain a Markdown table")
    cells = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    expected = COLUMNS if columns is None and heading == HEADING else columns
    if expected is not None and tuple(cells[0]) != tuple(expected):
        raise ValueError(f"{heading} columns must be: {' | '.join(expected)}")
    if len(cells[1]) != len(cells[0]) or any(not set(cell) <= {"-", ":"} for cell in cells[1]):
        raise ValueError(f"{heading} has an invalid separator row")
    rows = []
    for number, row in enumerate(cells[2:], 1):
        if len(row) != len(cells[0]):
            raise ValueError(f"{heading} row {number} has {len(row)} fields; expected {len(cells[0])}")
        rows.append(dict(zip(cells[0], row)))
    return rows


def routing_has_rows(text):
    """Detect legacy routing rows without treating prose as accepted capability state."""
    try:
        rows = markdown_table(text, "Capability routing")
    except ValueError:
        return False
    return bool(rows)


def validate_row(row):
    errors = []
    identity = row["Capability ID"]
    if not IDENTITY.fullmatch(identity):
        errors.append(f"invalid capability id: {identity or '<empty>'}")
    for field in ("Job", "Activate when", "Project check", "Status", "Logical load target"):
        if not row[field] or re.search(r"\{[^{}\n]+\}", row[field]):
            errors.append(f"{identity or '<empty>'}: missing {field.lower()}")
    for field, value in row.items():
        if "|" in value or "\n" in value or "\r" in value:
            errors.append(f"{identity or '<empty>'}: invalid Markdown in {field.lower()}")
    if row["Status"] and row["Status"] not in STATUSES:
        errors.append(f"{identity or '<empty>'}: invalid status")
    if row["Project check"] and not CHECK_ID.fullmatch(row["Project check"]):
        errors.append(f"{identity or '<empty>'}: invalid project check identity")
    if IDENTITY.fullmatch(identity):
        expected_target = canonical_logical_target(identity)
        if row["Logical load target"] != expected_target:
            errors.append(f"CAPABILITY_TARGET_MISMATCH: {identity}")
    return errors


def parse(text, *, require_canonical=False, current_only=False):
    rows = markdown_table(text)
    if rows is None:
        if require_canonical or routing_has_rows(text):
            raise ValueError("missing canonical Accepted capabilities table")
        return []
    errors = []
    identities = []
    for row in rows:
        errors.extend(validate_row(row))
        identities.append(row["Capability ID"])
    duplicates = sorted({identity for identity in identities if identities.count(identity) > 1})
    errors.extend(f"duplicate capability id: {identity}" for identity in duplicates)
    if errors:
        raise ValueError("; ".join(errors))
    result = [
        {
            "capability_id": row["Capability ID"],
            "job": row["Job"],
            "activation_trigger": row["Activate when"],
            "project_check_identity": row["Project check"],
            "status": row["Status"],
            "version_or_digest": None if row["Version or digest"] in {"", "-"} else row["Version or digest"],
            "logical_load_target": row["Logical load target"],
            "accepted_current": row["Status"] == CURRENT_STATUS,
        }
        for row in rows
    ]
    return [row for row in result if row["accepted_current"]] if current_only else result


def validate(text, *, require_canonical=False):
    try:
        parse(text, require_canonical=require_canonical)
    except ValueError as error:
        return [str(error)]
    return []


def load(path, *, require_canonical=False, current_only=False):
    if path.is_symlink() or not path.is_file():
        raise ValueError("project capability contract must be one regular file")
    return parse(
        path.read_text(encoding="utf-8"),
        require_canonical=require_canonical,
        current_only=current_only,
    )


def bounded_view(path):
    return load(path, require_canonical=False, current_only=True)


def selected(path, identity):
    matches = [row for row in bounded_view(path) if row["capability_id"] == identity]
    if len(matches) != 1:
        raise ValueError("selected capability is not one accepted/current identity")
    return matches[0]


def render(rows):
    canonical = []
    for row in rows:
        canonical.append({
            "Capability ID": row.get("Capability ID", row.get("capability_id", "")),
            "Job": row.get("Job", row.get("job", "")),
            "Activate when": row.get("Activate when", row.get("activation_trigger", "")),
            "Project check": row.get("Project check", row.get("project_check_identity", "")),
            "Status": row.get("Status", row.get("status", "")),
            "Version or digest": row.get("Version or digest", row.get("version_or_digest") or "-"),
            "Logical load target": row.get("Logical load target", row.get("logical_load_target", "")),
        })
    errors = [error for row in canonical for error in validate_row(row)]
    identities = [row["Capability ID"] for row in canonical]
    errors.extend(
        f"duplicate capability id: {identity}"
        for identity in sorted({value for value in identities if identities.count(value) > 1})
    )
    if errors:
        raise ValueError("; ".join(errors))
    lines = [
        f"## {HEADING}",
        "",
        "| " + " | ".join(COLUMNS) + " |",
        "| " + " | ".join("---" for _ in COLUMNS) + " |",
    ]
    lines.extend("| " + " | ".join(row[column] for column in COLUMNS) + " |" for row in canonical)
    return "\n".join(lines) + "\n"


def replace_rows(text, rows):
    section = render(rows)
    marker = f"## {HEADING}"
    match = re.search(rf"^{re.escape(marker)}\s*$", text, re.MULTILINE)
    if match:
        next_heading = re.search(r"^## ", text[match.end():], re.MULTILINE)
        end = match.end() + next_heading.start() if next_heading else len(text)
        updated = text[:match.start()] + section + "\n" + text[end:]
    else:
        routing = re.search(r"^## Capability routing\s*$", text, re.MULTILINE)
        if not routing:
            raise ValueError("project contract has no Capability routing insertion point")
        updated = text[:routing.start()] + section + "\n" + text[routing.start():]
    parse(updated, require_canonical=True)
    return updated


def write_rows(path, rows):
    from sync_host_entry import atomic_write

    if path.is_symlink() or not path.is_file():
        raise ValueError("project capability contract must be one regular file")
    updated = replace_rows(path.read_text(encoding="utf-8"), rows)
    atomic_write(path, updated)
    return load(path, require_canonical=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "view", "get", "write"))
    parser.add_argument("project", type=Path)
    parser.add_argument("--id")
    parser.add_argument("--setup", action="store_true", help="require the canonical table")
    parser.add_argument("--rows", type=Path, help="JSON array used by governed Setup/Adopt")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            errors = validate(args.project.read_text(encoding="utf-8"), require_canonical=args.setup)
            payload = {"valid": not errors, "errors": errors}
            failed = bool(errors)
        elif args.command == "view":
            payload = {"status": "ok", "capabilities": bounded_view(args.project)}
            failed = False
        elif args.command == "get":
            if not args.id:
                raise ValueError("get requires --id")
            payload = {"status": "ok", "capability": selected(args.project, args.id)}
            failed = False
        else:
            if not args.rows:
                raise ValueError("write requires --rows")
            rows = json.loads(args.rows.read_text(encoding="utf-8"))
            if not isinstance(rows, list):
                raise ValueError("capability rows must be one JSON array")
            payload = {"status": "updated", "capabilities": write_rows(args.project, rows)}
            failed = False
    except (OSError, UnicodeError, ValueError) as error:
        payload = {"status": "unavailable", "reason": str(error)}
        failed = True
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
