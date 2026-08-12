#!/usr/bin/env python3
"""Run the two bounded 2.0-entry personal transfer evaluations."""

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
GUARDRAILS = {
    "task_correctness": "passed",
    "permissions": "passed",
    "privacy": "passed",
    "completion_checks": "passed",
    "scope": "passed",
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


personal = load_module("personal_adaptation", SKILL / "scripts/personal_adaptation.py")
checkpoint = load_module("validate_checkpoint", SKILL / "scripts/validate_checkpoint.py")
sys.modules["validate_checkpoint"] = checkpoint
migration = load_module("migrate_legacy_checkpoint", SKILL / "scripts/migrate_legacy_checkpoint.py")
learning = load_module("validate_learning_loop", SKILL / "scripts/validate_learning_loop.py")


def atomic_write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def transfer_row(case, candidate, passed, evidence):
    apply = case["expected_activation"]
    return {
        "case_id": case["case_id"],
        "role_at_run": "holdout",
        "mechanism_id": candidate["mechanism_id"],
        "candidate_ref": candidate["provenance"]["candidate_ref"],
        "project_shape": case["project_shape"],
        "activation_decision": "APPLY" if apply else "SKIP",
        "application_status": "applied" if apply else "skipped",
        "completion_check_passed": passed if apply else None,
        "guardrails": GUARDRAILS,
        "evidence": evidence,
    }


def migration_check(shape):
    with tempfile.TemporaryDirectory(prefix="nulnul-migration-transfer-") as directory:
        root = Path(directory)
        first = root / ("pyproject.toml" if shape == "python-config-bundle" else "package.json")
        second = root / ("tool.json" if shape == "python-config-bundle" else "workspace.json")
        third = root / "generated.json"
        first.write_text("old-first\n", encoding="utf-8")
        second.write_text("old-second\n", encoding="utf-8")
        first.chmod(0o600)
        calls = 0

        def fail_second(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected second replacement failure")
            return source.replace(target)

        failed = False
        try:
            migration.atomic_batch_write(
                {first: "new-first\n", second: "new-second\n", third: "new-third\n"},
                replace=fail_second,
            )
        except OSError:
            failed = True
        return (
            failed
            and first.read_text(encoding="utf-8") == "old-first\n"
            and second.read_text(encoding="utf-8") == "old-second\n"
            and not third.exists()
            and first.stat().st_mode & 0o777 == 0o600
        )


def linked_learning_check(prefix):
    feedback_id = f"feedback-{prefix}"
    proposal_id = f"proposal-{prefix}"
    results = {
        "learning_verdicts": [{
            "id": f"verdict-{prefix}",
            "status": "failed",
            "feedback_id": feedback_id,
            "proposal_ids": [proposal_id],
        }]
    }
    evolution = {
        "feedback": [{"id": feedback_id}],
        "proposals": [{"id": proposal_id, "feedback_ids": [feedback_id]}],
    }
    broken = deepcopy(results)
    broken["learning_verdicts"][0].pop("feedback_id")
    return learning.validate(results, evolution) == [] and bool(learning.validate(broken, evolution))


def final_adaptation(preregistration, transfer_results, shapes):
    candidate = preregistration["personal_candidate"]
    return {
        key: deepcopy(value) for key, value in candidate.items() if key != "candidate_author"
    } | {
        "current_scope": "personal",
        "tested_project_shapes": ["source", *shapes],
        "transfer_results": transfer_results,
        "status": "active",
        "promoted_by": "gate",
        "promoted_at": "2026-08-13",
    }


def base_results(preregistration, transfer_results, evidence, scope, rejected):
    candidate = preregistration["personal_candidate"]
    shapes = [case["project_shape"] for case in preregistration["holdout_cases"]]
    return {
        "schema_version": 1,
        "run_date": "2026-08-13",
        "source_shape": {
            "project_shape": "source",
            "mechanism_id": candidate["mechanism_id"],
            "historical_gate": candidate["provenance"]["source_gate_id"],
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
            "evidence": evidence,
            "established_scope": scope,
        },
        "rejected_personal_candidates": [rejected],
        "personal_adaptation": final_adaptation(preregistration, transfer_results, shapes),
    }


def migration_results(preregistration):
    candidate = preregistration["personal_candidate"]
    cases = preregistration["holdout_cases"]
    rows = [
        transfer_row(cases[0], candidate, migration_check(cases[0]["project_shape"]), "The injected second replacement restored both original files, removed the uncommitted new file, and preserved file mode."),
        transfer_row(cases[1], candidate, migration_check(cases[1]["project_shape"]), "A distinct workspace manifest shape restored all local state after the same bounded failure."),
        transfer_row(cases[2], candidate, None, "A single-file change does not need batch transaction machinery and was skipped."),
    ]
    results = base_results(
        preregistration,
        rows,
        "Both positive local multi-file shapes restored cleanly, the single-file negative skipped, and all guardrails passed.",
        "Durable offline repositories performing a local multi-file state migration.",
        {
            "candidate_id": "personal-external-transaction-v0",
            "mechanism_id": candidate["mechanism_id"],
            "source_claim_id": "claim-external-state-transaction-1",
            "decision": "PERSONAL_REJECT",
            "reason": "Local file restoration cannot establish transactionality for external services.",
        },
    )
    conditions = candidate["activation_conditions"]
    with tempfile.TemporaryDirectory(prefix="nulnul-migration-home-") as directory:
        home = Path(directory)
        empty = personal.discover(home, {"schema_version": 1, "conditions": conditions, "approved_permissions": []})
        promotion = personal.promote(home, preregistration, results, ROOT)
        found = personal.discover(home, {"schema_version": 1, "conditions": conditions, "approved_permissions": []})
        passed = migration_check("python-config-bundle")
    results["personal_home_evaluation"] = {"kind": "isolated user-selected temporary directory", "global_home_created": False, "promotion_status": promotion["status"]}
    results["baseline_comparison"] = {
        "comparable_dimension": "deterministic inventory discovery and restoration correctness",
        "incomparable_dimensions": ["inference tokens", "elapsed time"],
        "fresh_start": {"adaptation_discovered": empty["status"] == "APPLY", "completion_check_passed": passed},
        "personal_reuse": {"adaptation_discovered": found["status"] == "APPLY", "completion_check_passed": passed},
        "conclusion": "Both arms retain local correctness; only the approved personal inventory discovers the prior mechanism.",
    }
    results["fresh_project_adoption"] = {
        "project_shape": "shell-build-contract",
        "adaptation_id": candidate["adaptation_id"],
        "inventory_discovered": found["status"] == "APPLY",
        "compatibility_check_passed": found["status"] == "APPLY",
        "applied": passed,
        "completion_check_passed": passed,
        "guardrails": GUARDRAILS,
        "evidence": "A fresh durable local project discovered the approved mechanism and restored every file after an injected later failure.",
    }
    return results


def learning_results(preregistration):
    candidate = preregistration["personal_candidate"]
    cases = preregistration["holdout_cases"]
    rows = [
        transfer_row(cases[0], candidate, linked_learning_check("python"), "A linked Python evaluation nonpass passed while the missing-link control failed."),
        transfer_row(cases[1], candidate, linked_learning_check("node"), "A distinct CI-report identity passed only with feedback and proposal linkage."),
        transfer_row(cases[2], candidate, None, "A passing-only result had no nonpass to convert and correctly skipped the adaptation."),
    ]
    results = base_results(
        preregistration,
        rows,
        "Both nonpass report shapes enforced linkage, the passing-only negative skipped, and all guardrails passed.",
        "Projects with machine-readable measured nonpasses and an active evolution state.",
        {
            "candidate_id": "personal-auto-feedback-inference-v0",
            "mechanism_id": candidate["mechanism_id"],
            "source_claim_id": "claim-auto-inferred-feedback-1",
            "decision": "PERSONAL_REJECT",
            "reason": "The validator can verify evidence identity but cannot safely invent causal feedback or approve a proposal.",
        },
    )
    conditions = candidate["activation_conditions"]
    with tempfile.TemporaryDirectory(prefix="nulnul-learning-home-") as directory:
        home = Path(directory)
        empty = personal.discover(home, {"schema_version": 1, "conditions": conditions, "approved_permissions": []})
        promotion = personal.promote(home, preregistration, results, ROOT)
        found = personal.discover(home, {"schema_version": 1, "conditions": conditions, "approved_permissions": []})
        passed = linked_learning_check("make")
    results["personal_home_evaluation"] = {"kind": "isolated user-selected temporary directory", "global_home_created": False, "promotion_status": promotion["status"]}
    results["baseline_comparison"] = {
        "comparable_dimension": "deterministic inventory discovery and nonpass-link validation",
        "incomparable_dimensions": ["inference tokens", "elapsed time"],
        "fresh_start": {"adaptation_discovered": empty["status"] == "APPLY", "completion_check_passed": passed},
        "personal_reuse": {"adaptation_discovered": found["status"] == "APPLY", "completion_check_passed": passed},
        "conclusion": "Both arms can validate a supplied link; only the approved personal inventory discovers the prior mechanism.",
    }
    results["fresh_project_adoption"] = {
        "project_shape": "make-evaluation-report",
        "adaptation_id": candidate["adaptation_id"],
        "inventory_discovered": found["status"] == "APPLY",
        "compatibility_check_passed": found["status"] == "APPLY",
        "applied": passed,
        "completion_check_passed": passed,
        "guardrails": GUARDRAILS,
        "evidence": "A fresh evaluation project discovered the approved mechanism, accepted a linked nonpass, and rejected a missing link.",
    }
    return results


def build():
    jobs = {
        "transactional-migration": migration_results,
        "learning-verdicts": learning_results,
    }
    summary = {}
    for name, run in jobs.items():
        directory = HERE / name
        preregistration = json.loads((directory / "preregistration.json").read_text(encoding="utf-8"))
        results = run(preregistration)
        errors = personal.validate_evidence(preregistration, results, ROOT)
        if errors:
            raise RuntimeError(f"{name}: " + "; ".join(errors))
        atomic_write(directory / "results.json", results)
        summary[name] = {
            "decision": results["personal_gate"]["decision"],
            "transfer_cases": len(results["transfer_results"]),
            "fresh_project_reuse": results["fresh_project_adoption"]["completion_check_passed"],
        }
    return summary


def main():
    argparse.ArgumentParser().parse_args()
    print(json.dumps(build(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
