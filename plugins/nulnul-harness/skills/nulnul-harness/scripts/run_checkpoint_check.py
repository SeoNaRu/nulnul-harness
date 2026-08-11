#!/usr/bin/env python3
"""Run the exact completion command recorded by a concise checkpoint."""

import argparse
import json
import subprocess
from pathlib import Path

import validate_checkpoint


def run(checkpoint_path, root, timeout):
    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    errors = validate_checkpoint.validate(payload)
    if errors:
        return {"passed": False, "exit_code": None, "errors": errors}
    command = payload["completion_check"]
    try:
        result = subprocess.run(command, cwd=root, shell=True, timeout=timeout)
        return {"passed": result.returncode == 0, "exit_code": result.returncode, "errors": []}
    except subprocess.TimeoutExpired:
        return {"passed": False, "exit_code": None, "errors": ["completion_check timed out"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    try:
        result = run(args.checkpoint, args.root, args.timeout)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        result = {"passed": False, "exit_code": None, "errors": [str(error)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(not result["passed"])


if __name__ == "__main__":
    main()
