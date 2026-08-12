#!/usr/bin/env python3
"""Measure activation precision: does the skill stay out of work that does not need it?

Over-activation is the measured cost of this harness, so the number that matters is
how often the skill loads on work an existing contract already covers, and whether
it still loads when the repository genuinely has nothing to work from.
"""

import argparse
import collections
import json
import os
import re
import shlex
import shutil
import statistics
import subprocess
import sys
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
                "schema_version": 3,
                "goal": "Maintain the arithmetic module",
                "milestone": "Rename the covered add behavior",
                "completion_check": "python3 -m unittest -q",
                "verification_status": "unknown",
                "verification_files": ["app.py", "test_app.py"],
                "last_verified": "1 test passed",
                "next_action": "Rename add to sum_values and update its test",
                "permission_constraints": ["local files only"],
                "approved_permissions": [],
                "blockers": [],
            }, indent=2) + "\n",
            "docs/nulnul/project.md": "FULL_SETUP_CONTRACT_SENTINEL\n",
            "app.py": "def add(a, b):\n    return a + b\n",
            "test_app.py": (
                "import unittest\nfrom app import add\n\n"
                "class AddTests(unittest.TestCase):\n"
                "    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n"
            ),
        },
        "prompt": "Rename add() to sum_values(), update its test, run the recorded check once, and refresh only stale checkpoint fields.",
        "required_reads": ("docs/nulnul/checkpoint.json",),
        "forbidden_reads": ("docs/nulnul/project.md", "/references/", "rg --files", "find "),
        "completion_check": "python3 -m unittest -q",
        "product_files": ("app.py", "test_app.py"),
        "prepare_verified_checkpoint": "bound",
    },
}

DIAGNOSTIC_CASES = {"verified-checkpoint-resolvable-wrapper": {
    **CASES["verified-checkpoint-fast-path"],
    "files": {
        **CASES["verified-checkpoint-fast-path"]["files"],
        "AGENTS.md": (
            "Load `.agents/skills/nulnul-harness/SKILL.md`. Validate "
            "`docs/nulnul/checkpoint.json` before repository-wide inspection; when "
            "`fast_path_ready` is true, read only it and task files.\n"
            "Available checkpoint runner: `python3 "
            ".agents/skills/nulnul-harness/scripts/run_checkpoint_check.py "
            "docs/nulnul/checkpoint.json --root .`.\n"
        ),
    },
}, "verified-checkpoint-truth-champion": {
    **CASES["verified-checkpoint-fast-path"],
    "prepare_verified_checkpoint": "legacy",
}}


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


def fresh_checkpoint_validation(workspace, timeout):
    checkpoint = workspace / "docs/nulnul/checkpoint.json"
    validator = workspace / ".agents/skills/nulnul-harness/scripts/validate_checkpoint.py"
    if not checkpoint.is_file() or not validator.is_file():
        return None
    try:
        payload = json.loads(checkpoint.read_text(encoding="utf-8"))
        process = subprocess.run(
            [sys.executable, str(validator), str(checkpoint)], cwd=workspace,
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout,
        )
        result = json.loads(process.stdout)
        evidence_path = checkpoint.with_name("checkpoint.verification.json")
        evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.is_file() else {}
    except (OSError, UnicodeError, json.JSONDecodeError, subprocess.TimeoutExpired):
        return {"valid": False, "fast_path_ready": False, "verification_status": "unknown"}
    return {
        "valid": process.returncode == 0 and result.get("valid") is True,
        "fast_path_ready": result.get("fast_path_ready") is True,
        "verification_status": payload.get("verification_status", "unknown"),
        "verified_evidence_fingerprint": evidence.get("verification_fingerprint"),
    }


def checkpoint_truth_observation(initial, current, product_mutated, telemetry):
    if initial is None or current is None:
        return None
    navigator_checks = telemetry["completion_check_invocations"]
    unverified_mutation = product_mutated and navigator_checks == 0
    return {
        "initial_fast_path_ready": initial["validation"]["fast_path_ready"],
        "product_mutated": product_mutated,
        "navigator_completion_check_invocations": navigator_checks,
        "checkpoint_changed_before_gate": initial["checkpoint"] != current["checkpoint"],
        "verified_evidence_changed_before_gate": (
            initial["validation"].get("verified_evidence_fingerprint")
            != current["validation"].get("verified_evidence_fingerprint")
        ),
        "last_verified_changed_before_gate": (
            initial["checkpoint"].get("last_verified") != current["checkpoint"].get("last_verified")
        ),
        "verification_status_before_gate": current["validation"]["verification_status"],
        "fast_path_ready_before_gate": current["validation"]["fast_path_ready"],
        "fresh_resume_accepted": current["validation"]["fast_path_ready"],
        "unverified_mutated_repository_state_accepted_for_fast_resume": (
            unverified_mutation and current["validation"]["fast_path_ready"]
        ),
    }


def shell_segments(command):
    segments = []
    for part in re.split(r"(?:&&|\|\||;|\n)", command):
        part = part.strip()
        if not part:
            continue
        try:
            tokens = shlex.split(part)
        except ValueError:
            segments.append(part)
            continue
        if tokens and os.path.basename(tokens[0]) in {"bash", "sh"}:
            for index, token in enumerate(tokens[1:], start=1):
                if token in {"-c", "-lc"} and index + 1 < len(tokens):
                    segments.extend(shell_segments(tokens[index + 1]))
                    break
            else:
                segments.append(part)
        else:
            segments.append(part)
    return segments


def executes_script(segment, script_name):
    try:
        tokens = shlex.split(segment)
    except ValueError:
        return False
    while tokens and "=" in tokens[0] and not tokens[0].startswith(("/", "./")):
        tokens.pop(0)
    if not tokens:
        return False
    executable = os.path.basename(tokens[0])
    if executable.startswith("python"):
        return any(os.path.basename(token) == script_name for token in tokens[1:])
    return executable == script_name


def completion_check_counts(commands, completion_check):
    expected = shlex.split(completion_check) if completion_check else []
    counts = {"checkpoint_runner": 0, "direct": 0}
    for command in commands:
        for segment in shell_segments(command):
            if executes_script(segment, "run_checkpoint_check.py"):
                counts["checkpoint_runner"] += 1
                continue
            try:
                actual = shlex.split(segment)
            except ValueError:
                continue
            if expected and actual[:len(expected)] == expected:
                counts["direct"] += 1
    return counts


def lifecycle_signals(stdout, completion_check, behavior_verified):
    """Reduce event order to bounded process signals; retain no command or message text."""
    items = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item")
        if event.get("type") == "item.completed" and isinstance(item, dict):
            items.append(item)

    changes = [index for index, item in enumerate(items) if item.get("type") == "file_change"]
    if not changes:
        return []
    last_change = changes[-1]
    verification = []
    for index, item in enumerate(items[last_change + 1:], start=last_change + 1):
        if item.get("type") != "command_execution":
            continue
        commands = command_list(json.dumps({"type": "item.completed", "item": item}))
        if sum(completion_check_counts(commands, completion_check).values()) or any(
            executes_script(segment, "validate_checkpoint.py")
            for command in commands for segment in shell_segments(command)
        ):
            verification.append(index)

    wrapper_observed = completion_check_counts(
        command_list(stdout, completed_only=True), completion_check
    )["checkpoint_runner"] > 0
    final_synthesis = any(
        item.get("type") == "agent_message" for item in items[last_change + 1:]
    )
    signals = []
    if behavior_verified:
        signals.append("implementation_completed")
    if verification:
        signals.append("verification_stage_entered")
    if wrapper_observed:
        signals.append("wrapper_invocation_observed")
    if final_synthesis:
        signals.append("final_synthesis_observed")
    if final_synthesis and not verification:
        signals.append("final_synthesis_without_verification")
    if verification and not wrapper_observed:
        signals.append("verification_entered_without_wrapper")
    return signals


def execution_telemetry(stdout, completion_check=None):
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
    completion_checks = completion_check_counts(commands, completion_check)
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
        "completion_check_invocations": sum(completion_checks.values()),
        "completion_check_invocations_by_kind": completion_checks,
    }


def experience_digest(run_id, case_name, category, arm, agent_seconds, verification_seconds,
                      telemetry, usage, check_exit_code, correct):
    resume_stage = "resume" if category == "fast-path" else "activation"
    completion_checks = telemetry["completion_check_invocations"]
    signals = list(telemetry.get("lifecycle_signals", ()))
    if completion_checks > 1:
        signals.append("completion_check_repeated")
    elif check_exit_code is not None and completion_checks == 0:
        signals.append("completion_check_missing")
    return {
        "schema_version": 1,
        "run_id": run_id,
        "case_id": case_name,
        "arm": arm,
        "stages": [
            {
                "stage": resume_stage,
                "owner": "navigator",
                "elapsed_ms": round(agent_seconds * 1000),
                "tool_invocations": telemetry["tool_calls"],
                "repository_reads": telemetry["read_commands"],
                "validator_invocations": telemetry["validator_commands"],
                "test_invocations": telemetry["test_commands"],
                "completion_check_invocations": telemetry["completion_check_invocations"],
            },
            {
                "stage": "verification",
                "owner": "gate",
                "elapsed_ms": round(verification_seconds * 1000),
                "tool_invocations": 1 if check_exit_code is not None else 0,
                "repository_reads": 0,
                "validator_invocations": 0,
                "test_invocations": 1 if check_exit_code is not None else 0,
                "completion_check_invocations": 1 if check_exit_code is not None else 0,
            },
        ],
        "signals": signals,
        "verification_result": "verified" if correct else "failed",
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
    }


def first_divergence(left, right):
    left_stages = left.get("stages", [])
    right_stages = right.get("stages", [])
    for left_stage, right_stage in zip(left_stages, right_stages):
        if left_stage.get("stage") != right_stage.get("stage"):
            return {"status": "verified", "stage": right_stage.get("stage"), "signal": "stage_sequence"}
        if left_stage.get("completion_check_invocations") != right_stage.get("completion_check_invocations"):
            return {
                "status": "verified",
                "stage": right_stage.get("stage"),
                "signal": "completion_check_invocations",
            }
    if len(left_stages) != len(right_stages):
        extra = right_stages[len(left_stages):] or left_stages[len(right_stages):]
        stage = extra[0].get("stage") if extra else None
        return (
            {"status": "verified", "stage": stage, "signal": "stage_sequence"}
            if stage
            else {"status": "unknown", "stage": None, "signal": None}
        )
    return {"status": "unknown", "stage": None, "signal": None}


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
    divergences = [
        first_divergence(left.get("experience_digest", {}), right.get("experience_digest", {}))
        for left, right in eligible
    ]
    verified = [item for item in divergences if item["status"] == "verified"]
    stages = {item["stage"] for item in verified}
    divergence = (
        {"status": "verified", "stage": stages.pop(), "pairs": len(verified)}
        if verified and len(stages) == 1
        else {"status": "unknown", "stage": None, "pairs": len(verified)}
    )
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
        "first_divergence": divergence,
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


def run_case(name, case, arm, skill, model, effort, timeout, round_index):
    case_started = time.monotonic()
    workspace = Path(tempfile.mkdtemp(prefix=f"act-{name}-"))
    try:
        for filename, content in case["files"].items():
            path = workspace / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        if skill is not None:
            shutil.copytree(skill, workspace / ".agents/skills/nulnul-harness")
        checkpoint_path = workspace / "docs/nulnul/checkpoint.json"
        checkpoint_runner = workspace / ".agents/skills/nulnul-harness/scripts/run_checkpoint_check.py"
        preparation = case.get("prepare_verified_checkpoint")
        if preparation:
            if preparation == "legacy":
                checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
                checkpoint.update(schema_version=2, verification_status="verified")
                checkpoint.pop("verification_files")
                checkpoint.pop("verification_fingerprint", None)
                checkpoint_path.write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")
                prepare_command = shlex.split(case["completion_check"])
            else:
                prepare_command = [
                    sys.executable, str(checkpoint_runner), str(checkpoint_path), "--root", str(workspace)
                ]
            prepared = subprocess.run(
                prepare_command, cwd=workspace, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=timeout,
            )
            if prepared.returncode:
                raise RuntimeError("verified-checkpoint fixture preparation failed")
        initial_products = {
            filename: (workspace / filename).read_bytes()
            for filename in case.get("product_files", ())
        }
        initial_validation = fresh_checkpoint_validation(workspace, timeout)
        initial_checkpoint = (
            json.loads(checkpoint_path.read_text(encoding="utf-8"))
            if initial_validation is not None else None
        )
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
        telemetry = execution_telemetry(process.stdout, case.get("completion_check"))
        current_validation = fresh_checkpoint_validation(workspace, timeout)
        current_checkpoint = (
            json.loads(checkpoint_path.read_text(encoding="utf-8"))
            if current_validation is not None else None
        )
        product_mutated = bool(initial_products) and any(
            not (workspace / filename).is_file()
            or (workspace / filename).read_bytes() != content
            for filename, content in initial_products.items()
        )
        checkpoint_truth = checkpoint_truth_observation(
            {"validation": initial_validation, "checkpoint": initial_checkpoint}
            if initial_validation is not None else None,
            {"validation": current_validation, "checkpoint": current_checkpoint}
            if current_validation is not None else None,
            product_mutated,
            telemetry,
        )
        check_exit_code = None
        verification_started = time.monotonic()
        if command := case.get("completion_check"):
            gate_command = (
                [sys.executable, str(checkpoint_runner), str(checkpoint_path), "--root", str(workspace)]
                if checkpoint_truth is not None else shlex.split(command)
            )
            check_exit_code = subprocess.run(
                gate_command, cwd=workspace, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=timeout,
            ).returncode
        verification_seconds = round(time.monotonic() - verification_started, 3)
        if checkpoint_truth is not None:
            post_gate = fresh_checkpoint_validation(workspace, timeout)
            checkpoint_truth["verification_status_after_gate"] = post_gate["verification_status"]
            checkpoint_truth["fast_path_ready_after_gate"] = post_gate["fast_path_ready"]
        correct = (
            process.returncode == 0
            and activated == case["expect_activation"]
            and not missing_reads
            and not forbidden_reads
            and check_exit_code in (None, 0)
        )
        telemetry["lifecycle_signals"] = lifecycle_signals(
            process.stdout, case.get("completion_check"),
            process.returncode == 0 and check_exit_code in (None, 0),
        )
        digest = experience_digest(
            f"{name}:{arm}:r{round_index}", name, case["category"], arm,
            agent_seconds, verification_seconds, telemetry, usage, check_exit_code, correct,
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
            "telemetry": telemetry,
            "experience_digest": digest,
            "checkpoint_truth": checkpoint_truth,
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
    available_cases = {**CASES, **DIAGNOSTIC_CASES}
    names = args.cases or list(CASES)
    unknown = sorted(set(names) - available_cases.keys())
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
                          **run_case(name, available_cases[name], arm, skill, args.model, args.effort, args.timeout,
                                     round_index)}
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
