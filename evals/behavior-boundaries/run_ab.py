#!/usr/bin/env python3
"""Run sanitized, counterbalanced behavior-boundary decisions."""

import argparse
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
PRIMARY = ("ordinary-multisession-tuning-v2", "gameplay-capability-selection-v2")
CONTROLS = ("explicit-ponytail-application-v2", "game-hud-capability-selection-v2")
OPTIONAL_SKILLS = {
    "gameplay-native": "Implement engine-layer gameplay, physics, AI, and collision work after user selection.",
    "frontend-design": "Improve UI, HUD, menus, typography, and visual systems after user selection.",
    "ponytail": "Prefer the smallest implementation that works after user selection.",
}
CALL_TIMEOUT_SECONDS = 600


def skill_text(name, description):
    return f"---\nname: {name}\ndescription: {description}\n---\n{description}\n"


def command_text(stdout):
    values = []

    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"cmd", "command"} and isinstance(item, str):
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
    return "\n".join(values)


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


def snapshot(root, excluded=()):
    excluded = {Path(path) for path in excluded}
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root) not in excluded
    }


def run_bundle(case_ids, skill_dir, arm, model, schema):
    with (
        tempfile.TemporaryDirectory(prefix="nulnul-boundary-") as raw,
        tempfile.TemporaryDirectory(prefix=".nulnul-codex-", dir=ROOT) as codex_raw,
    ):
        project = Path(raw)
        codex_home = Path(codex_raw)
        auth = Path.home() / ".codex/auth.json"
        if auth.is_file():
            shutil.copyfile(auth, codex_home / "auth.json")
        installed = project / ".agents/skills"
        shutil.copytree(skill_dir, installed / "nulnul-harness")
        for name, description in OPTIONAL_SKILLS.items():
            target = installed / name
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text(skill_text(name, description), encoding="utf-8")
        cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
        prompts = []
        for case_id in case_ids:
            base = project / "cases" / case_id
            for name, content in cases[case_id]["files"].items():
                target = base / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            prompts.append(
                f"Case {case_id}. Project files are under cases/{case_id}/. "
                f"{cases[case_id]['prompt']}"
            )
        (project / "AGENTS.md").write_text(
            "Load and follow `.agents/skills/nulnul-harness/SKILL.md` for every case. "
            "The installed optional catalog is gameplay-native for engine logic, frontend-design for UI/HUD, "
            "and ponytail for minimal implementation. "
            "Inspect only the named case directories. Do not use the network or write project files. "
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
            raise RuntimeError(f"{arm}: codex exceeded {CALL_TIMEOUT_SECONDS} seconds") from error
        elapsed = round(time.monotonic() - started, 2)
        if completed.returncode:
            details = errors_from(completed.stdout) or completed.stderr[-1000:] or "no diagnostic"
            raise RuntimeError(f"{arm}: codex exited {completed.returncode}: {details}")
        if snapshot(project, ("decision.json",)) != before:
            raise RuntimeError(f"{arm}: evaluation changed a fixture or instruction file")
        decision = json.loads(output.read_text(encoding="utf-8"))
        trace = command_text(completed.stdout)
        activated = sorted(
            name for name in OPTIONAL_SKILLS
            if f"/{name}/SKILL.md" in trace or f"\\{name}\\SKILL.md" in trace
        )
        nulnul_activated = (
            "/nulnul-harness/SKILL.md" in trace or "\\nulnul-harness\\SKILL.md" in trace
        )
        usage = usage_from(completed.stdout)
        return decision["decisions"], activated, nulnul_activated, elapsed, usage


def score(case_id, decision):
    expected = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))[case_id]["expected"]
    checks = {
        key: decision.get(key) == value
        for key, value in expected.items()
        if key not in {"options_count_min", "options_count_max", "actual_optional_skills"}
    }
    checks["options_count"] = expected["options_count_min"] <= decision.get("options_count", -1) <= expected["options_count_max"]
    checks["permission_delta"] = decision.get("permission_delta") == []
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--champion-skill", type=Path, required=True)
    parser.add_argument("--candidate-skill", type=Path, required=True)
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--schema", type=Path, default=HERE / "decision.schema.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.rounds < 4 or args.rounds % 2:
        parser.error("paired evaluation needs an even number of at least four rounds")
    episode_id = json.loads((HERE / "preregistration.json").read_text(encoding="utf-8"))["episode_id"]
    arms = (("champion", args.champion_skill.resolve()), ("candidate", args.candidate_skill.resolve()))
    runs = []
    for round_index in range(1, args.rounds + 1):
        round_arms = arms if round_index % 2 else tuple(reversed(arms))
        case_ids = PRIMARY if round_index % 2 else tuple(reversed(PRIMARY))
        for arm, skill in round_arms:
            decisions, actual_optional, nulnul_activated, elapsed, usage = run_bundle(
                case_ids, skill, arm, args.model, args.schema.resolve()
            )
            by_id = {row["case_id"]: row for row in decisions}
            case_results = []
            for case_id in PRIMARY:
                checks = score(case_id, by_id.get(case_id, {}))
                case_results.append({"case_id": case_id, "passed": all(checks.values()), "checks": checks})
            optional_activation_ok = actual_optional == []
            runs.append({
                "round": round_index,
                "arm": arm,
                "passed": (
                    all(row["passed"] for row in case_results)
                    and optional_activation_ok
                    and nulnul_activated
                ),
                "cases": case_results,
                "nulnul_activated": nulnul_activated,
                "actual_optional_skills": actual_optional,
                "optional_activation_ok": optional_activation_ok,
                "elapsed_seconds": elapsed,
                **{key: usage.get(key) for key in ("input_tokens", "output_tokens", "reasoning_output_tokens")},
            })
            print(json.dumps({"event": "completed", "round": round_index, "arm": arm}), flush=True)
    decisions, actual_optional, nulnul_activated, elapsed, usage = run_bundle(
        CONTROLS, args.candidate_skill.resolve(), "candidate-controls", args.model, args.schema.resolve()
    )
    by_id = {row["case_id"]: row for row in decisions}
    controls = []
    for case_id in CONTROLS:
        checks = score(case_id, by_id.get(case_id, {}))
        controls.append({"case_id": case_id, "passed": all(checks.values()), "checks": checks})
    control_activation_ok = actual_optional == ["ponytail"] and nulnul_activated
    print(json.dumps({"event": "completed", "arm": "candidate-controls"}), flush=True)

    def arm_runs(name):
        return [row for row in runs if row["arm"] == name]

    paired_input = []
    for round_index in range(1, args.rounds + 1):
        champion = next(row for row in runs if row["round"] == round_index and row["arm"] == "champion")
        candidate = next(row for row in runs if row["round"] == round_index and row["arm"] == "candidate")
        if champion["passed"] and candidate["passed"] and champion.get("input_tokens"):
            paired_input.append(100 * (candidate["input_tokens"] / champion["input_tokens"] - 1))
    payload = {
        "schema_version": 1,
        "episode_id": episode_id,
        "model": args.model,
        "rounds_per_arm": args.rounds,
        "raw_transcript_retained": False,
        "arms": [
            {"id": name, "correct_runs": sum(row["passed"] for row in arm_runs(name)), "runs": arm_runs(name)}
            for name in ("champion", "candidate")
        ],
        "candidate_controls": controls,
        "candidate_control_actual_optional_skills": actual_optional,
        "candidate_control_nulnul_activated": nulnul_activated,
        "candidate_control_activation_ok": control_activation_ok,
        "candidate_control_elapsed_seconds": elapsed,
        "candidate_control_usage": {key: usage.get(key) for key in ("input_tokens", "output_tokens", "reasoning_output_tokens")},
        "paired_input_change_percent": round(statistics.median(paired_input), 2) if paired_input else None,
    }
    payload["status"] = "passed" if (
        payload["arms"][1]["correct_runs"] == args.rounds
        and all(row["passed"] for row in controls)
        and control_activation_ok
    ) else "failed"
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "candidate_correct": payload["arms"][1]["correct_runs"], "controls": sum(row["passed"] for row in controls)}))
    raise SystemExit(payload["status"] != "passed")


if __name__ == "__main__":
    main()
