#!/usr/bin/env python3
"""Keep the frozen evaluator unchanged; require explicit public readiness to publish."""

import json
import subprocess
import sys
from pathlib import Path


def publication_exit_code(report):
    return 0 if isinstance(report, dict) and report.get("release_ready") is True else 1


def main():
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("release_gate.py"))],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    if result.returncode:
        return result.returncode
    try:
        return publication_exit_code(json.loads(result.stdout))
    except (ValueError, TypeError):
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
