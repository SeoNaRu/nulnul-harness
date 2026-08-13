#!/usr/bin/env python3
"""Run bounded intent/means decisions and retain only schema-valid final JSON."""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FRONTEND_SKILL = """---
name: frontend-design
description: Improve frontend visual quality.
---
Use bold gradients, generous rounding, card grouping, and expressive motion as defaults.
Treat accepted user and project direction as constraints when they are provided.
"""


def run_case(case_id, case, skill_dir, model, schema):
    with (
        tempfile.TemporaryDirectory(prefix="nulnul-intent-") as raw,
        tempfile.TemporaryDirectory(prefix="nulnul-codex-") as codex_raw,
    ):
        project = Path(raw)
        codex_home = Path(codex_raw)
        shutil.copyfile(Path.home() / ".codex/auth.json", codex_home / "auth.json")
        for name, content in case["files"].items():
            target = project / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        installed = project / ".agents/skills"
        shutil.copytree(skill_dir, installed / "nulnul-harness")
        frontend = installed / "frontend-design"
        frontend.mkdir(parents=True)
        (frontend / "SKILL.md").write_text(FRONTEND_SKILL, encoding="utf-8")
        (project / "AGENTS.md").write_text(
            "Load and follow `.agents/skills/nulnul-harness/SKILL.md` for this decision. "
            "Installed skills are nulnul-harness and frontend-design. Read only named project "
            "files and the approved personal source when the request names it. Do not use the "
            "network, write files, or ask the user. Return the decision JSON only.\n",
            encoding="utf-8",
        )
        output = project / "decision.json"
        prompt = f"Case id: {case_id}. {case['prompt']} Return the decision JSON only; brief_reason must be at most two sentences."
        command = [
            "codex", "exec", "--ignore-user-config", "--ignore-rules", "--ephemeral",
            "--sandbox", "read-only", "--skip-git-repo-check", "--model", model,
            "--output-schema", str(schema),
            "--output-last-message", str(output), "--cd", str(project), prompt,
        ]
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            env={**os.environ, "CODEX_HOME": str(codex_home)},
        )
        if completed.returncode:
            raise RuntimeError(
                f"{case_id}: codex exited {completed.returncode}: {completed.stderr[-1000:]}"
            )
        return json.loads(output.read_text(encoding="utf-8"))


def score(decision, expected):
    checks = {
        "case_id": isinstance(decision.get("case_id"), str),
        "no_unrelated_personal_reads": decision.get("unrelated_personal_reads") == 0,
        "no_permission_delta": decision.get("permission_delta") == [],
    }
    if "popularity_only" in decision:
        checks["not_popularity_only"] = decision["popularity_only"] is False
    for key in (
        "skill_used", "current_fit_assessed", "alternative_considered",
        "switching_cost_considered", "final_path", "personal_sources_read",
        "surface_radius", "visual_tone", "frontend_architecture", "backend",
    ):
        if key in expected:
            checks[key] = decision.get(key) == expected[key]
    if "direction_authority" in expected:
        checks["direction_authority"] = set(decision.get("direction_authority", [])) == set(expected["direction_authority"])
    if "forbidden_skill_role" in expected:
        checks["skill_role"] = decision.get("skill_role") != expected["forbidden_skill_role"]
    if "explicit_constraint" in expected:
        checks["explicit_constraint"] = expected["explicit_constraint"] in decision.get("explicit_constraints", [])
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True)
    parser.add_argument("--order", required=True)
    parser.add_argument("--cases", type=Path, default=HERE / "cases.json")
    parser.add_argument("--schema", type=Path, default=HERE / "decision.schema.json")
    parser.add_argument("--skill-dir", type=Path, default=ROOT / "plugins/nulnul-harness/skills/nulnul-harness")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads((HERE / "preregistration.json").read_text(encoding="utf-8"))
    amendment = json.loads((HERE / "amendment.json").read_text(encoding="utf-8"))
    orders = {**prereg, **amendment}
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    runs = []
    for index, case_id in enumerate(orders[args.order], 1):
        decision = run_case(
            case_id, cases[case_id], args.skill_dir.resolve(), args.model, args.schema.resolve()
        )
        checks = score(decision, cases[case_id]["expected"])
        retained = {
            key: value for key, value in decision.items()
            if key not in {"brief_reason", "explicit_constraints", "suggested_means"}
        }
        runs.append({
            "run": index,
            "case_id": case_id,
            "passed": all(checks.values()),
            "checks": checks,
            "decision": retained,
        })
    payload = {
        "schema_version": 1,
        "episode_id": prereg["episode_id"],
        "arm": args.arm,
        "model": args.model,
        "model_invocations": len(runs),
        "raw_transcript_retained": False,
        "runs": runs,
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"arm": args.arm, "passed": sum(row["passed"] for row in runs), "runs": len(runs)}))


if __name__ == "__main__":
    main()
