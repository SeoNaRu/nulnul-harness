#!/usr/bin/env python3
"""Run the offline workbook A/B as interleaved pairs and append one JSONL row per trial.

Each pair runs both arms back to back with the order alternating, so drift in
model serving or machine load cancels instead of landing on one arm. The only
difference between arms is whether the harness skill exists in the workspace.
"""

import argparse
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = Path(__file__).resolve().parent / "TASK.md"
INPUT = ROOT / "examples/youtube-sheets/input.json"
EXPECTED = ROOT / "examples/youtube-sheets/expected.json"
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
SCORER = ROOT / "scripts/score_workbook_task.py"

PROMPT = "Complete the task described in TASK.md in this directory. Write build.py, run it, and leave output.json in place."


def run_trial(arm, skill, model, effort, timeout):
    workspace = Path(tempfile.mkdtemp(prefix=f"ab-{arm}-"))
    try:
        shutil.copy(TASK, workspace / "TASK.md")
        shutil.copy(INPUT, workspace / "input.json")
        if skill is not None:
            shutil.copytree(skill, workspace / ".agents/skills/nulnul-harness")
        command = [
            "codex", "exec", "--json", "--ephemeral", "--ignore-user-config",
            "--skip-git-repo-check", "-s", "workspace-write", "-C", str(workspace),
            "-m", model, "-c", f'model_reasoning_effort="{effort}"', PROMPT,
        ]
        started = time.monotonic()
        process = subprocess.run(
            command, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout
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

        output = workspace / "output.json"
        # ponytail: shells out to the published scorer so the run and the release use one judge.
        passed = output.is_file() and subprocess.run(
            ["python3", str(SCORER), str(EXPECTED), str(output)], capture_output=True
        ).returncode == 0
        return {
            "arm": arm,
            "passed": passed,
            "skill": str(skill) if skill else None,
            "elapsed_seconds": elapsed,
            "exit_code": process.returncode,
            "activated": skill is not None and "nulnul-harness" in process.stdout,
            **{key: usage.get(key) for key in
               ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")},
        }
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", type=int, default=1)
    parser.add_argument("--start-pair", type=int, default=1)
    parser.add_argument(
        "--arm", action="append", dest="arms",
        help="name=path to a skill directory, or name=none for the bare repository "
             "(default: baseline=none and harness=<shipped skill>)",
    )
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    specs = args.arms or ["baseline=none", f"harness={SKILL}"]
    arms = []
    for spec in specs:
        name, _, path = spec.partition("=")
        arms.append((name, None if path in ("", "none") else Path(path).resolve()))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    for index in range(args.start_pair, args.start_pair + args.pairs):
        # Rotate arm order every round so serving drift cancels instead of favouring one arm.
        rotated = arms[index % len(arms):] + arms[: index % len(arms)]
        for arm, skill in rotated:
            record = {"pair": index, **run_trial(arm, skill, args.model, args.effort, args.timeout)}
            with args.out.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(json.dumps(record, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
