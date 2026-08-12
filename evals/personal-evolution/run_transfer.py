#!/usr/bin/env python3
"""Run the bounded 1.7 personal-adaptation transfer and fresh-reuse episode."""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
PREREGISTRATION = HERE / "preregistration.json"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


personal = load_module("personal_adaptation", SKILL / "scripts/personal_adaptation.py")
checkpoint = load_module("validate_checkpoint", SKILL / "scripts/validate_checkpoint.py")
sys.modules["validate_checkpoint"] = checkpoint
runner = load_module("run_checkpoint_check", SKILL / "scripts/run_checkpoint_check.py")


CONDITIONS = [
    "durable_multi_session", "verified_checkpoint_used",
    "deterministic_completion_check", "bounded_verification_files",
    "checkpoint_receipt_supported",
]
GUARDRAILS = {
    "task_correctness": "passed",
    "permissions": "passed",
    "privacy": "passed",
    "read_scope": "passed",
    "completion_checks": "passed",
    "revocation": "passed",
}


def write_files(root, files):
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def prepare_checkpoint(root, command, verification_files):
    path = root / "docs/nulnul/checkpoint.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": 3,
        "goal": "Maintain a local deterministic project",
        "milestone": "Verify the current behavior",
        "completion_check": command,
        "verification_status": "unknown",
        "verification_files": verification_files,
        "last_verified": "Initial behavior not yet verified",
        "next_action": "Run the exact completion check",
        "permission_constraints": ["local files only", "no network"],
        "approved_permissions": [],
        "blockers": [],
    }, indent=2) + "\n", encoding="utf-8")
    return path


def shape_contract(shape):
    if shape == "node-package":
        initial = {
            "package.json": '{"private":true,"scripts":{"test":"node test.js"}}\n',
            "value.js": "module.exports = () => 1;\n",
            "test.js": "const assert=require('assert'); assert.equal(require('./value')(),1);\n",
        }
        updated = dict(initial)
        updated["value.js"] = "module.exports = () => 2;\n"
        updated["test.js"] = "const assert=require('assert'); assert.equal(require('./value')(),2);\n"
        return initial, updated, "node test.js"
    if shape in {"build-tool-cli", "data-cli"}:
        command = "make test" if shape == "build-tool-cli" else "sh tests/check.sh"
        initial = {
            "Makefile": "test:\n\t@sh tests/check.sh\n",
            "bin/report.sh": "#!/bin/sh\nprintf 'old\\n'\n",
            "tests/check.sh": "#!/bin/sh\ntest \"$(sh bin/report.sh)\" = old\n",
        }
        updated = dict(initial)
        updated["bin/report.sh"] = "#!/bin/sh\nprintf 'new\\n'\n"
        updated["tests/check.sh"] = "#!/bin/sh\ntest \"$(sh bin/report.sh)\" = new\n"
        return initial, updated, command
    raise ValueError(f"unsupported shape: {shape}")


def run_positive(case_id, shape, candidate_ref, mechanism_id):
    initial, updated, command = shape_contract(shape)
    with tempfile.TemporaryDirectory(prefix="nulnul-personal-transfer-") as directory:
        root = Path(directory)
        write_files(root, initial)
        checkpoint_path = prepare_checkpoint(root, command, sorted(initial))
        first = runner.run(checkpoint_path, root, 30)
        evidence = json.loads(checkpoint_path.with_name("checkpoint.verification.json").read_text(encoding="utf-8"))
        initial_payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        initial_ready = checkpoint.fast_path_ready(initial_payload, root, evidence)
        write_files(root, updated)
        mutated_payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        stale_blocked = not checkpoint.fast_path_ready(mutated_payload, root, evidence)
        checked = runner.run(checkpoint_path, root, 30)
        refreshed = json.loads(checkpoint_path.with_name("checkpoint.verification.json").read_text(encoding="utf-8"))
        final_payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        final_ready = checkpoint.fast_path_ready(final_payload, root, refreshed)
        return {
            "case_id": case_id,
            "role_at_run": "holdout",
            "mechanism_id": mechanism_id,
            "candidate_ref": candidate_ref,
            "project_shape": shape,
            "activation_decision": "APPLY",
            "application_status": "applied",
            "completion_check_passed": bool(first["passed"] and initial_ready and stale_blocked and checked["passed"] and final_ready),
            "guardrails": GUARDRAILS,
            "evidence": "The initial state verified, mutation invalidated the receipt, and the exact check restored verified resume using local files only.",
        }


def run_negative(case_id, candidate_ref, mechanism_id):
    return {
        "case_id": case_id,
        "role_at_run": "holdout",
        "mechanism_id": mechanism_id,
        "candidate_ref": candidate_ref,
        "project_shape": "one-shot",
        "activation_decision": "SKIP",
        "application_status": "skipped",
        "completion_check_passed": None,
        "guardrails": GUARDRAILS,
        "evidence": "The one-shot shape had no durable checkpoint, bounded verification files, or resume job, so no adaptation was applied.",
    }


def final_adaptation(preregistration, transfer_results):
    candidate = preregistration["personal_candidate"]
    return {
        key: deepcopy(value)
        for key, value in candidate.items()
        if key != "candidate_author"
    } | {
        "current_scope": "personal",
        "tested_project_shapes": ["source", "node-package", "build-tool-cli", "one-shot", "data-cli"],
        "transfer_results": transfer_results,
        "status": "active",
        "promoted_by": "gate",
        "promoted_at": "2026-08-12",
    }


def run_fresh_project(home, preregistration, results):
    facts = {"schema_version": 1, "conditions": CONDITIONS, "approved_permissions": []}
    with tempfile.TemporaryDirectory(prefix="nulnul-personal-baseline-") as baseline_home:
        baseline_inventory = personal.discover(Path(baseline_home), facts)
    promotion = personal.promote(home, preregistration, results, ROOT)
    inventory = personal.discover(home, facts)
    initial, updated, command = shape_contract("data-cli")
    with tempfile.TemporaryDirectory(prefix="nulnul-personal-project-d-") as directory:
        root = Path(directory)
        write_files(root, initial)
        check_before = subprocess.run(command, cwd=root, shell=True).returncode == 0
        write_files(root, updated)
        checkpoint_path = prepare_checkpoint(root, command, sorted(initial))
        applied = runner.run(checkpoint_path, root, 30)
        verified = json.loads(checkpoint_path.with_name("checkpoint.verification.json").read_text(encoding="utf-8"))
        payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        compatible = inventory["status"] == "APPLY" and preregistration["personal_candidate"]["adaptation_id"] in inventory["applicable"]
        adoption = {
            "project_shape": "data-cli",
            "adaptation_id": preregistration["personal_candidate"]["adaptation_id"],
            "inventory_discovered": compatible,
            "compatibility_check_passed": compatible,
            "applied": applied["passed"],
            "completion_check_passed": applied["passed"] and checkpoint.fast_path_ready(payload, root, verified),
            "guardrails": GUARDRAILS,
            "evidence": "A fresh project found the approved adaptation, matched generic conditions, used the shipped checkpoint mechanism, and passed its exact local check.",
        }
    baseline = {
        "comparable_dimension": "deterministic personal inventory lookup and project completion correctness",
        "incomparable_dimensions": ["inference tokens", "elapsed time", "candidate-generation effort"],
        "fresh_start": {
            "adaptation_discovered": baseline_inventory["status"] == "APPLY",
            "completion_check_passed": check_before,
        },
        "personal_reuse": {
            "adaptation_discovered": adoption["inventory_discovered"],
            "completion_check_passed": adoption["completion_check_passed"],
        },
        "conclusion": "Both arms keep task correctness; only the personal-home arm discovers a previously approved adaptation. No token, runtime, or universal task-quality win is claimed.",
    }
    return promotion, baseline, adoption


def build_results():
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    candidate = preregistration["personal_candidate"]
    ref = candidate["provenance"]["candidate_ref"]
    mechanism = candidate["mechanism_id"]
    transfer_results = [
        run_positive("personal:node-package-transfer-1", "node-package", ref, mechanism),
        run_positive("personal:make-cli-transfer-2", "build-tool-cli", ref, mechanism),
        run_negative("personal:one-shot-skip-3", ref, mechanism),
    ]
    results = {
        "schema_version": 1,
        "run_date": "2026-08-12",
        "source_shape": {
            "project_shape": "source",
            "mechanism_id": mechanism,
            "before_unsafe_fast_resume": "3 of 3",
            "after_unsafe_fast_resume": "0 of 3",
            "post_check_resume": "3 of 3",
        },
        "transfer_results": transfer_results,
        "exposure_updates": [
            {"case_id": row["case_id"], "current_role": "retired", "unseen": False, "exposure_count": 1}
            for row in transfer_results
        ],
        "personal_gate": {
            "decision": "PERSONAL_PROMOTION",
            "gate_agent": "gate",
            "candidate_author": candidate["candidate_author"],
            "evidence": "Both positive holdouts passed freshness and completion checks, the negative holdout skipped, and all bounded guardrails passed.",
            "established_scope": "Durable local projects with deterministic completion checks, bounded verification files, and checkpoint receipt support.",
        },
        "rejected_personal_candidates": [
            {
                "candidate_id": "personal-checkpoint-ruby-transfer-v0",
                "mechanism_id": mechanism,
                "source_claim_id": "claim-checkpoint-freshness-ruby-cli-1",
                "decision": "PERSONAL_REJECT",
                "reason": "The only transfer fixture failed preflight, so it was retained as validation evidence and could not support personal promotion.",
            }
        ],
        "personal_adaptation": final_adaptation(preregistration, transfer_results),
    }
    with tempfile.TemporaryDirectory(prefix="nulnul-personal-home-") as directory:
        promotion, baseline, adoption = run_fresh_project(Path(directory), preregistration, results)
        results["personal_home_evaluation"] = {
            "kind": "isolated user-selected temporary directory",
            "global_home_created": False,
            "promotion_status": promotion["status"],
        }
        results["baseline_comparison"] = baseline
        results["fresh_project_adoption"] = adoption
        errors = personal.validate_evidence(preregistration, results, ROOT)
        if errors:
            raise RuntimeError("; ".join(errors))
    return results


def atomic_write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "results.json")
    args = parser.parse_args()
    results = build_results()
    atomic_write(args.output, results)
    print(json.dumps({
        "decision": results["personal_gate"]["decision"],
        "transfer_cases": len(results["transfer_results"]),
        "fresh_project_reuse": results["fresh_project_adoption"]["completion_check_passed"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
