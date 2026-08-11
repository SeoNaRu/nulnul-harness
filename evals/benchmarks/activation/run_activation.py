#!/usr/bin/env python3
"""Measure activation precision: does the skill stay out of work that does not need it?

Over-activation is the measured cost of this harness, so the number that matters is
how often the skill loads on work an existing contract already covers, and whether
it still loads when the repository genuinely has nothing to work from.
"""

import argparse
import collections
import json
import shlex
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
MIN_ROUNDS = 3

CASES = {
    "single-file-edit": {
        "category": "covered-task",
        "expect_activation": False,
        "files": {"app.py": "def total(rows):\n    return sum(rows)\n"},
        "prompt": "In app.py, rename the function `total` to `subtotal` and update nothing else.",
    },
    "read-only-question": {
        "category": "read-only",
        "expect_activation": False,
        "files": {"app.py": "def head(rows):\n    return rows[0]\n"},
        "prompt": "Why does head() raise on an empty list? Answer in one sentence. Change no files.",
    },
    "covered-by-tests": {
        "category": "covered-task",
        "expect_activation": False,
        "files": {
            "app.py": "def add(a, b):\n    return a - b\n",
            "test_app.py": "from app import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n",
            "AGENTS.md": "# Working agreement\n\nRun `python3 -m pytest -q` before finishing.\n",
        },
        "prompt": "The test suite fails. Fix the code so it passes.",
    },
    "explicit-task-contract": {
        "category": "covered-task",
        "expect_activation": False,
        "files": {
            "TASK.md": (
                "# Task\nInput: `names.txt`. Output: `names.json`. Keep order and remove blank lines.\n"
                "Constraint: standard library only. Check: `python3 -m unittest -q`.\n"
            ),
            "names.txt": "Ada\n\nGrace\n",
        },
        "prompt": "Implement TASK.md completely and run its check.",
    },
    "coherent-project-contract": {
        "category": "covered-task",
        "expect_activation": False,
        "files": {
            "AGENTS.md": (
                "# Contract\nGoal: maintain this Python module. Use the standard library. "
                "Run `python3 -m unittest -q` before finishing.\n"
            ),
            "slug.py": "def slug(value):\n    return value.lower().replace(' ', '-')\n",
        },
        "prompt": "Explain how slug() handles spaces. Change no files.",
    },
    "ambiguous-empty-repository": {
        "category": "new-setup",
        "expect_activation": True,
        "files": {},
        "prompt": "Build me a harness that collects new job postings every week and keeps only reviewed ones.",
    },
    "adopt-existing-project": {
        "category": "adopt-upgrade",
        "expect_activation": True,
        "files": {
            "package.json": '{"scripts":{"test":"node --test"}}\n',
            "app.js": "export const ready = true;\n",
        },
        "prompt": "Set up the harness for this existing project without changing product code.",
    },
    "recurring-workflow": {
        "category": "new-setup",
        "expect_activation": True,
        "files": {"README.md": "# Weekly paper queue\n"},
        "prompt": "Set up a recurring workflow that finds new papers, deduplicates them, and keeps a review queue.",
    },
    "capability-selection": {
        "category": "capability-discovery",
        "expect_activation": True,
        "files": {"README.md": "# Small Python CLI\n"},
        "prompt": "Inspect this project and set up only the skills or plugins that its work actually needs.",
    },
    "verified-checkpoint-fast-path": {
        "category": "fast-path",
        "expect_activation": True,
        "files": {
            "AGENTS.md": (
                "Load `.agents/skills/nulnul-harness/SKILL.md`. Validate "
                "`docs/nulnul/checkpoint.json` before repository-wide inspection; when "
                "`fast_path_ready` is true, read only it and task files.\n"
            ),
            "docs/nulnul/checkpoint.json": json.dumps({
                "schema_version": 2,
                "goal": "Maintain the arithmetic module",
                "milestone": "Fix the covered add behavior",
                "completion_check": "python3 -m unittest -q",
                "verification_status": "verified",
                "last_verified": "1 test passed",
                "next_action": "Fix the next bounded arithmetic request",
                "permission_constraints": ["local files only"],
                "approved_permissions": [],
                "blockers": [],
            }, indent=2) + "\n",
            "docs/nulnul/project.md": "FULL_SETUP_CONTRACT_SENTINEL\n",
            "app.py": "def add(a, b):\n    return a - b\n",
            "test_app.py": (
                "import unittest\nfrom app import add\n\n"
                "class AddTests(unittest.TestCase):\n"
                "    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n"
            ),
        },
        "prompt": "Fix add(), run the recorded check once, and refresh only stale checkpoint fields.",
        "required_reads": ("docs/nulnul/checkpoint.json",),
        "forbidden_reads": ("docs/nulnul/project.md", "/references/", "rg --files", "find "),
        "completion_check": "python3 -m unittest -q",
    },
}


def command_list(stdout, completed_only=False):
    """Return command/tool-input strings without matching text merely printed by a read."""
    commands = []

    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"cmd", "command"} and isinstance(item, str):
                    commands.append(item)
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if completed_only and event.get("type") != "item.completed":
            continue
        visit(event)
    return commands


def command_trace(stdout):
    return "\n".join(command_list(stdout))


def execution_telemetry(stdout):
    commands = command_list(stdout, completed_only=True)
    item_types = collections.Counter()
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item")
        if event.get("type") == "item.completed" and isinstance(item, dict):
            item_type = item.get("type")
            if isinstance(item_type, str):
                item_types[item_type] += 1
    reads = ("cat ", "sed ", "head ", "tail ", "rg ", "find ", "ls ", "git status", "git diff", "git show")
    return {
        "tool_calls": sum(
            count for item_type, count in item_types.items()
            if item_type not in {"agent_message", "reasoning"}
        ),
        "tool_calls_by_type": dict(sorted(item_types.items())),
        "shell_commands": len(commands),
        "read_commands": sum(any(marker in command for marker in reads) for command in commands),
        "validator_commands": sum("validate_checkpoint.py" in command for command in commands),
        "test_commands": sum(
            any(marker in command for marker in (
                "run_checkpoint_check.py", "unittest", "pytest", "npm test", "node --test"
            ))
            for command in commands
        ),
    }


def paired_comparison(records, champion, candidate):
    by_key = {(record["round"], record["case"], record["arm"]): record for record in records}
    pairs = []
    for round_index, case_name in sorted({(r["round"], r["case"]) for r in records}):
        try:
            left = by_key[(round_index, case_name, champion)]
            right = by_key[(round_index, case_name, candidate)]
        except KeyError as error:
            raise ValueError(f"missing paired arm: {error}") from error
        pairs.append((left, right))
    eligible = [(left, right) for left, right in pairs if left["correct"] and right["correct"]]
    metrics = ("elapsed_seconds", "input_tokens", "output_tokens", "reasoning_output_tokens")
    changes = {}
    for field in metrics:
        values = [
            100 * (right[field] / left[field] - 1)
            for left, right in eligible
            if isinstance(left.get(field), (int, float))
            and isinstance(right.get(field), (int, float))
            and left[field] > 0
        ]
        changes[field] = round(statistics.median(values), 2) if len(values) == len(eligible) and values else None
    return {
        "champion": champion,
        "candidate": candidate,
        "pairs": len(pairs),
        "eligible_pairs": len(eligible),
        "excluded_pairs": [
            {"round": left["round"], "case": left["case"], "reason": "behavior mismatch"}
            for left, right in pairs if not left["correct"] or not right["correct"]
        ],
        "champion_correct": sum(left["correct"] for left, _ in pairs),
        "candidate_correct": sum(right["correct"] for _, right in pairs),
        "paired_change_percent": changes,
    }


def summarize(records):
    summaries = []
    for arm in sorted({record["arm"] for record in records}):
        selected = [record for record in records if record["arm"] == arm]
        true_positive = sum(r["activated"] and r["expected_activation"] for r in selected)
        false_positive = sum(r["activated"] and not r["expected_activation"] for r in selected)
        false_negative = sum(not r["activated"] and r["expected_activation"] for r in selected)
        fast = [r for r in selected if r["category"] == "fast-path"]

        def median(field):
            values = [r[field] for r in selected if isinstance(r.get(field), (int, float))]
            return statistics.median(values) if values else None

        def telemetry_median(field):
            values = [r.get("telemetry", {}).get(field) for r in selected]
            values = [value for value in values if isinstance(value, (int, float))]
            return statistics.median(values) if values else None

        def stage_median(field):
            values = [r.get("stage_seconds", {}).get(field) for r in selected]
            values = [value for value in values if isinstance(value, (int, float))]
            return statistics.median(values) if values else None

        summaries.append({
            "arm": arm,
            "runs": len(selected),
            "correct_runs": sum(r["correct"] for r in selected),
            "accuracy": sum(r["correct"] for r in selected) / len(selected),
            "precision": true_positive / (true_positive + false_positive) if true_positive + false_positive else 1.0,
            "recall": true_positive / (true_positive + false_negative) if true_positive + false_negative else 1.0,
            "fast_path_runs": len(fast),
            "fast_path_correct_runs": sum(r["correct"] for r in fast),
            **{f"median_{field}": median(field) for field in (
                "elapsed_seconds", "input_tokens", "output_tokens", "reasoning_output_tokens"
            )},
            "median_tool_calls": telemetry_median("tool_calls"),
            "median_read_commands": telemetry_median("read_commands"),
            "median_validator_commands": telemetry_median("validator_commands"),
            "median_test_commands": telemetry_median("test_commands"),
            "median_stage_seconds": {
                field: stage_median(field) for field in ("fixture", "agent", "verification", "total")
            },
        })
    return {
        "schema_version": 1,
        "status": "passed" if records and all(record["correct"] for record in records) else "failed",
        "required_rounds": MIN_ROUNDS,
        "case_count": len(CASES),
        "arms": summaries,
    }


def run_case(name, case, arm, skill, model, effort, timeout):
    case_started = time.monotonic()
    workspace = Path(tempfile.mkdtemp(prefix=f"act-{name}-"))
    try:
        for filename, content in case["files"].items():
            path = workspace / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        if skill is not None:
            shutil.copytree(skill, workspace / ".agents/skills/nulnul-harness")
        fixture_seconds = round(time.monotonic() - case_started, 3)
        agent_started = time.monotonic()
        process = subprocess.run(
            ["codex", "exec", "--json", "--ephemeral", "--ignore-user-config",
             "--skip-git-repo-check", "-s", "workspace-write", "-C", str(workspace),
             "-m", model, "-c", f'model_reasoning_effort="{effort}"', case["prompt"]],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout,
        )
        agent_seconds = round(time.monotonic() - agent_started, 2)
        usage = {}
        for line in process.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                usage = event["usage"]
        trace = command_trace(process.stdout)
        # The skill is loaded by reading its SKILL.md, so its path in a tool command is the signal.
        activated = "nulnul-harness/SKILL.md" in trace
        missing_reads = [marker for marker in case.get("required_reads", ()) if marker not in trace]
        forbidden_reads = [marker for marker in case.get("forbidden_reads", ()) if marker in trace]
        check_exit_code = None
        verification_started = time.monotonic()
        if command := case.get("completion_check"):
            check_exit_code = subprocess.run(
                shlex.split(command), cwd=workspace, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=timeout,
            ).returncode
        verification_seconds = round(time.monotonic() - verification_started, 3)
        correct = (
            process.returncode == 0
            and activated == case["expect_activation"]
            and not missing_reads
            and not forbidden_reads
            and check_exit_code in (None, 0)
        )
        return {
            "case": name,
            "category": case["category"],
            "arm": arm,
            "expected_activation": case["expect_activation"],
            "activated": activated,
            "correct": correct,
            "agent_exit_code": process.returncode,
            "agent_error": process.stderr.strip()[-2000:] if process.returncode else "",
            "missing_required_reads": missing_reads,
            "forbidden_reads": forbidden_reads,
            "completion_check_exit_code": check_exit_code,
            "elapsed_seconds": agent_seconds,
            "stage_seconds": {
                "fixture": fixture_seconds,
                "agent": agent_seconds,
                "verification": verification_seconds,
                "total": round(time.monotonic() - case_started, 2),
            },
            "telemetry": execution_telemetry(process.stdout),
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
    parser.add_argument("--rounds", type=int, default=MIN_ROUNDS)
    parser.add_argument("--arm", action="append", dest="arms", help="name=path to a skill directory")
    parser.add_argument("--case", action="append", dest="cases", help="limit to named cases")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--champion-arm")
    parser.add_argument("--candidate-arm")
    args = parser.parse_args()

    arms = []
    for spec in args.arms or [f"current={SKILL}"]:
        name, _, path = spec.partition("=")
        arms.append((name, None if path in ("", "none") else Path(path).resolve()))
    names = args.cases or list(CASES)
    unknown = sorted(set(names) - CASES.keys())
    if unknown:
        parser.error("unknown cases: " + ", ".join(unknown))
    if args.rounds < MIN_ROUNDS:
        parser.error(f"--rounds must be at least {MIN_ROUNDS}")
    if bool(args.champion_arm) != bool(args.candidate_arm):
        parser.error("--champion-arm and --candidate-arm must be used together")
    if args.champion_arm:
        known_arms = {name for name, _ in arms}
        if {args.champion_arm, args.candidate_arm} - known_arms:
            parser.error("paired arm names must match --arm names")
        if args.rounds % 2:
            parser.error("paired runs require an even round count to counterbalance arm order")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("", encoding="utf-8")
    records = []
    for round_index in range(1, args.rounds + 1):
        for name in names:
            round_arms = arms if round_index % 2 else list(reversed(arms))
            for arm, skill in round_arms:
                record = {"round": round_index,
                          **run_case(name, CASES[name], arm, skill, args.model, args.effort, args.timeout)}
                records.append(record)
                with args.out.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(json.dumps(record, ensure_ascii=False), flush=True)
    summary = summarize(records)
    if args.champion_arm:
        comparison = paired_comparison(records, args.champion_arm, args.candidate_arm)
        summary["comparison"] = comparison
        summary["status"] = "passed" if (
            comparison["candidate_correct"] == comparison["pairs"]
            and comparison["eligible_pairs"] >= MIN_ROUNDS
        ) else "failed"
    summary_path = args.summary_out or args.out.with_suffix(".summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    raise SystemExit(summary["status"] != "passed")


if __name__ == "__main__":
    main()
