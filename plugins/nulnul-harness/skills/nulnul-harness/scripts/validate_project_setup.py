#!/usr/bin/env python3
"""Validate the durable nulnul project setup contract."""

import argparse
import json
import re
from pathlib import Path


REQUIRED_HEADINGS = {
    "Goal",
    "Current milestone",
    "Constraints and permissions",
    "Inspected roster",
    "Capability requirements",
    "Candidate evidence",
    "Capability routing",
    "Setup decisions",
    "Agent topology",
    "Evolution baseline",
    "Continuity",
}
REQUIRED_LABELS = (
    "Observable completion check:",
    "- Host surface:",
    "- Skills:",
    "- Plugins:",
    "- Agents:",
    "- Reuse now:",
    "- Add now:",
    "- Needs approval:",
    "- Skip:",
)
PLACEHOLDER = re.compile(r"\{[^{}\n]+\}")


def validate(text):
    errors = []
    headings = set(re.findall(r"^## (.+?)\s*$", text, re.MULTILINE))
    for heading in sorted(REQUIRED_HEADINGS - headings):
        errors.append(f"missing heading: {heading}")
    for label in REQUIRED_LABELS:
        match = re.search(rf"^{re.escape(label)}\s*(.*)$", text, re.MULTILINE)
        if match is None:
            errors.append(f"missing field: {label}")
        elif not match.group(1).strip() or PLACEHOLDER.search(match.group(1)):
            errors.append(f"unfinished field: {label}")
    if PLACEHOLDER.search(text):
        errors.append("contract contains template placeholders")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()
    errors = validate(args.contract.read_text(encoding="utf-8"))
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
