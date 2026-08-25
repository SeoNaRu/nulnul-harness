#!/usr/bin/env python3
"""Run sanitized paired constraint-reconciliation decisions."""

import argparse
import hashlib
import json
import os
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CALL_TIMEOUT_SECONDS = 600


def tree_sha256(root):
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        name = path.relative_to(root).as_posix().encode()
        content = path.read_bytes()
        digest.update(len(name).to_bytes(4, "big"))
        digest.update(name)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def snapshot(root, excluded=()):
    excluded = {Path(name) for name in excluded}
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root) not in excluded
    }


def event_values(stdout, wanted):
    values = []

    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in wanted and isinstance(item, str):
                    values.append(item)
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
        if event.get("type") == "item.completed":
            visit(event)
    return values


def usage_from(stdout):
    for line in reversed(stdout.splitlines()):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            return event["usage"]
    return {}


def errors_from(stdout):
    messages = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") in {"error", "turn.failed"}:
            value = event.get("message") or event.get("error")
            messages.append(value if isinstance(value, str) else json.dumps(value))
    return "; ".join(messages[-3:])


def run_once(case_ids, skill_dir, arm, round_index, model, schema, eval_dir):
    with (
        tempfile.TemporaryDirectory(prefix="nulnul-constraint-") as raw,
        tempfile.TemporaryDirectory(prefix=".nulnul-constraint-codex-", dir=ROOT) as codex_raw,
    ):
        project = Path(raw)
        codex_home = Path(codex_raw)
        auth = Path.home() / ".codex/auth.json"
        if auth.is_file():
            shutil.copyfile(auth, codex_home / "auth.json")
        shutil.copytree(skill_dir, project / ".agents/skills/nulnul-harness")
        cases = json.loads((eval_dir / "cases.json").read_text(encoding="utf-8"))
        prompts = []
        for case_id in case_ids:
            base = project / "cases" / case_id
            for name, content in cases[case_id]["files"].items():
                target = base / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            prompts.append(
                f"Case {case_id}. Read only cases/{case_id}/state.json and directly named task files. "
                f"{cases[case_id]['prompt']}"
            )
        (project / "AGENTS.md").write_text(
            "Load and follow `.agents/skills/nulnul-harness/SKILL.md`. "
            "For each named case, reconcile the current request with stored constraints before execution. "
            "Do not use the network, change files, execute the requested work, or invent permission. "
            "Return one decision per case as schema-valid JSON and nothing else.\n",
            encoding="utf-8",
        )
        output = project / "decision.json"
        before = snapshot(project)
        prompt = "\n\n".join(prompts) + "\nKeep each brief_reason to one sentence."
        command = [
            "codex", "exec", "--json", "--ignore-user-config", "--ephemeral",
            "--sandbox", "workspace-write", "--skip-git-repo-check", "--model", model,
            "-c", 'model_reasoning_effort="high"', "--output-schema", str(schema),
            "--output-last-message", str(output), "--cd", str(project), prompt,
        ]
        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command, text=True, capture_output=True, env=env, timeout=CALL_TIMEOUT_SECONDS
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(f"{arm} round {round_index} exceeded {CALL_TIMEOUT_SECONDS}s") from error
        elapsed = round(time.monotonic() - started, 2)
        if completed.returncode:
            details = errors_from(completed.stdout) or completed.stderr[-1000:] or "no diagnostic"
            raise RuntimeError(f"{arm} round {round_index} exited {completed.returncode}: {details}")
        if snapshot(project, ("decision.json",)) != before:
            raise RuntimeError(f"{arm} round {round_index} changed an evaluation fixture")
        decisions = json.loads(output.read_text(encoding="utf-8"))["decisions"]
        commands = event_values(completed.stdout, {"cmd", "command"})
        activated = any(
            "/nulnul-harness/SKILL.md" in value or "\\nulnul-harness\\SKILL.md" in value
            for value in commands
        )
        return decisions, activated, elapsed, usage_from(completed.stdout), len(commands)


def score(case_id, decision, cases):
    expected = cases[case_id]["expected"]
    checks = {
        key: decision.get(key) == value
        for key, value in expected.items()
    }
    checks["brief_reason"] = bool(
        isinstance(decision.get("brief_reason"), str)
        and decision["brief_reason"].strip()
    )
    return checks


def median(runs, field):
    values = [run[field] for run in runs]
    return statistics.median(values) if values else 0


def paired_change(champion, candidate, field):
    champion_by_round = {run["round"]: run for run in champion}
    candidate_by_round = {run["round"]: run for run in candidate}
    changes = []
    for round_index in sorted(champion_by_round.keys() & candidate_by_round.keys()):
        baseline = champion_by_round[round_index][field]
        current = candidate_by_round[round_index][field]
        if baseline:
            changes.append((current - baseline) / baseline * 100)
    return round(statistics.median(changes), 2) if changes else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--champion-skill", type=Path, required=True)
    parser.add_argument("--candidate-skill", type=Path, required=True)
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate-only", action="store_true")
    parser.add_argument("--baseline-results", type=Path)
    parser.add_argument("--eval-dir", type=Path, default=HERE)
    args = parser.parse_args()
    if args.rounds != 4:
        parser.error("the frozen comparison requires exactly four rounds")
    eval_dir = args.eval_dir.resolve()
    preregistration = json.loads((eval_dir / "preregistration.json").read_text(encoding="utf-8"))
    cases = json.loads((eval_dir / "cases.json").read_text(encoding="utf-8"))
    case_ids = tuple(cases)
    all_arms = (
        ("champion", args.champion_skill.resolve()),
        ("candidate", args.candidate_skill.resolve()),
    )
    arms = all_arms[1:] if args.candidate_only else all_arms
    if args.candidate_only and args.baseline_results is None:
        parser.error("--candidate-only requires --baseline-results")
    runs = {name: [] for name, _ in arms}
    for round_index in range(1, args.rounds + 1):
        round_arms = arms if round_index % 2 else tuple(reversed(arms))
        ordered_cases = case_ids if round_index % 2 else tuple(reversed(case_ids))
        for arm, skill in round_arms:
            decisions, activated, elapsed, usage, command_count = run_once(
                ordered_cases, skill, arm, round_index, args.model,
                eval_dir / "decision.schema.json", eval_dir,
            )
            by_id = {row.get("case_id"): row for row in decisions}
            checks = {
                case_id: score(case_id, by_id.get(case_id, {}), cases)
                for case_id in case_ids
            }
            exact_cases = [case_id for case_id, values in checks.items() if values and all(values.values())]
            runs[arm].append({
                "round": round_index,
                "correct": activated and len(exact_cases) == len(case_ids),
                "activated": activated,
                "exact_cases": exact_cases,
                "failed_cases": [case_id for case_id in case_ids if case_id not in exact_cases],
                "failed_checks": {
                    case_id: [key for key, passed in checks[case_id].items() if not passed]
                    for case_id in case_ids if case_id not in exact_cases
                },
                "command_count": command_count,
                "elapsed_seconds": elapsed,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "reasoning_output_tokens": usage.get("reasoning_output_tokens", 0),
            })
    if args.candidate_only:
        baseline_payload = json.loads(args.baseline_results.read_text(encoding="utf-8"))
        champion_runs = next(
            arm["runs"] for arm in baseline_payload["arms"] if arm["id"] == "champion"
        )
    else:
        champion_runs = runs["champion"]
    payload = {
        "schema_version": 1,
        "episode_id": preregistration["episode_id"],
        "model": args.model,
        "rounds_per_arm": args.rounds,
        "raw_transcript_retained": False,
        "permission_delta": [],
        "arms": [
            {
                "id": arm,
                "skill_tree_sha256": tree_sha256(skill),
                "exact_runs": sum(run["correct"] for run in runs[arm]),
                "medians": {
                    field: median(runs[arm], field)
                    for field in ("elapsed_seconds", "input_tokens", "output_tokens", "reasoning_output_tokens")
                },
                "runs": runs[arm],
            }
            for arm, skill in arms
        ],
        "paired_input_change_percent": paired_change(
            champion_runs, runs["candidate"], "input_tokens"
        ),
    }
    if args.candidate_only:
        payload["baseline_results_sha256"] = hashlib.sha256(
            args.baseline_results.read_bytes()
        ).hexdigest()
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
