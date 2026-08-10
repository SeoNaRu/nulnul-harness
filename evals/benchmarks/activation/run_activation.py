#!/usr/bin/env python3
"""Measure activation precision: does the skill stay out of work that does not need it?

Over-activation is the measured cost of this harness, so the number that matters is
how often the skill loads on work an existing contract already covers, and whether
it still loads when the repository genuinely has nothing to work from.
"""

import argparse
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"

CASES = {
    "single-file-edit": {
        "expect_activation": False,
        "files": {"app.py": "def total(rows):\n    return sum(rows)\n"},
        "prompt": "In app.py, rename the function `total` to `subtotal` and update nothing else.",
    },
    "read-only-question": {
        "expect_activation": False,
        "files": {"app.py": "def head(rows):\n    return rows[0]\n"},
        "prompt": "Why does head() raise on an empty list? Answer in one sentence. Change no files.",
    },
    "covered-by-tests": {
        "expect_activation": False,
        "files": {
            "app.py": "def add(a, b):\n    return a - b\n",
            "test_app.py": "from app import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n",
            "AGENTS.md": "# Working agreement\n\nRun `python3 -m pytest -q` before finishing.\n",
        },
        "prompt": "The test suite fails. Fix the code so it passes.",
    },
    "ambiguous-empty-repository": {
        "expect_activation": True,
        "files": {},
        "prompt": "Build me a harness that collects new job postings every week and keeps only reviewed ones.",
    },
}


def run_case(name, case, arm, skill, model, effort, timeout):
    workspace = Path(tempfile.mkdtemp(prefix=f"act-{name}-"))
    try:
        for filename, content in case["files"].items():
            (workspace / filename).write_text(content, encoding="utf-8")
        if skill is not None:
            shutil.copytree(skill, workspace / ".agents/skills/nulnul-harness")
        started = time.monotonic()
        process = subprocess.run(
            ["codex", "exec", "--json", "--ephemeral", "--ignore-user-config",
             "--skip-git-repo-check", "-s", "workspace-write", "-C", str(workspace),
             "-m", model, "-c", f'model_reasoning_effort="{effort}"', case["prompt"]],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout,
        )
        elapsed = round(time.monotonic() - started, 2)
        usage = {}
        for line in process.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                usage = event["usage"]
        # The skill is loaded by reading its SKILL.md, so its path in the transcript is the signal.
        activated = "nulnul-harness/SKILL.md" in process.stdout
        return {
            "case": name,
            "arm": arm,
            "expected_activation": case["expect_activation"],
            "activated": activated,
            "correct": activated == case["expect_activation"],
            "elapsed_seconds": elapsed,
            "created_harness_files": sorted(
                str(path.relative_to(workspace))
                for path in list(workspace.glob("docs/nulnul/*")) + list(workspace.glob("AGENTS.md"))
            ),
            **{key: usage.get(key) for key in
               ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")},
        }
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--arm", action="append", dest="arms", help="name=path to a skill directory")
    parser.add_argument("--case", action="append", dest="cases", help="limit to named cases")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    arms = []
    for spec in args.arms or [f"current={SKILL}"]:
        name, _, path = spec.partition("=")
        arms.append((name, None if path in ("", "none") else Path(path).resolve()))
    names = args.cases or list(CASES)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    for round_index in range(1, args.rounds + 1):
        for name in names:
            for arm, skill in arms:
                record = {"round": round_index,
                          **run_case(name, CASES[name], arm, skill, args.model, args.effort, args.timeout)}
                with args.out.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(json.dumps(record, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
