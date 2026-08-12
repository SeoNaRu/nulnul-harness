#!/usr/bin/env python3
"""Aggregate the three verified families and measure 1.7 flat lookup."""

import importlib.util
import json
import os
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SCRIPT = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/cross_project_evolution.py"
SPEC = importlib.util.spec_from_file_location("cross_project_evolution", SCRIPT)
CROSS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CROSS)
SOURCES = [
    (ROOT / "evals/personal-evolution/results.json", "checkpoint-verification-freshness"),
    (ROOT / "evals/personal-evolution/transactional-migration/results.json", "local-migration-atomicity"),
    (ROOT / "evals/personal-evolution/learning-verdicts/results.json", "nonpass-learning-linkage"),
]


def atomic_write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def summarize(path, family):
    results = json.loads(path.read_text(encoding="utf-8"))
    adaptation = results["personal_adaptation"]
    transfers = adaptation["transfer_results"]
    failed = sum("failed" in row.get("reason", "").lower() for row in results.get("rejected_personal_candidates", []))
    return {
        "adaptation_id": adaptation["adaptation_id"],
        "mechanism_family": family,
        "target_job": adaptation["target_job"],
        "activation_conditions": adaptation["activation_conditions"],
        "contraindications": adaptation["contraindications"],
        "tested_project_shapes": adaptation["tested_project_shapes"],
        "positive_transfer_count": sum(row["activation_decision"] == "APPLY" and row["completion_check_passed"] is True for row in transfers),
        "negative_skip_count": sum(row["activation_decision"] == "SKIP" and row["application_status"] == "skipped" for row in transfers),
        "failed_transfer_count": failed,
        "narrowed_scope_count": int(adaptation["status"] == "narrowed"),
        "source_evidence_identity": adaptation["provenance"],
        "guardrails": adaptation["guardrails"],
        "permission_requirements": adaptation["required_permissions"],
        "privacy_class": adaptation["privacy_class"],
        "compatibility_requirements": adaptation["activation_conditions"],
        "known_conflicts": [],
        "known_complements": [],
        "cost_evaluation_summary": "No reliable cross-project token or elapsed comparison is claimed.",
        "freshness": {"evidence_status": "current", "last_verified": "2026-08-13"},
        "status": adaptation["status"],
    }


def evidence():
    adaptations = [summarize(path, family) for path, family in SOURCES]
    relations = [
        {
            "source": first["adaptation_id"],
            "target": second["adaptation_id"],
            "type": "UNKNOWN",
            "evidence": "No joint downstream episode had been run at baseline registration.",
            "reason": "Independent target jobs do not establish interaction by themselves.",
            "scope": "2.0 entry baseline",
        }
        for first, second in combinations(adaptations, 2)
    ]
    return {
        "schema_version": 1,
        "generated_at": "2026-08-13T11:00:00+09:00",
        "entry_gate": {"decision": "PASS", "independent_family_count": 3},
        "adaptations": adaptations,
        "relations": relations,
        "raw_project_data_included": False,
    }


CASES = [
    {
        "case_id": "dev:durable-nonpass-1",
        "role": "DEV",
        "conditions": [
            "durable_multi_session", "verified_checkpoint_used", "deterministic_completion_check",
            "bounded_verification_files", "checkpoint_receipt_supported",
            "machine_readable_evaluation", "measured_nonpass", "evolution_state_present",
        ],
        "expected": ["personal-checkpoint-freshness-v1", "personal-learning-verdict-linkage-v1"],
    },
    {
        "case_id": "validation:multi-file-migration-1",
        "role": "VALIDATION",
        "conditions": ["durable_multi_session", "multi_file_state_migration", "local_offline_repository"],
        "expected": ["personal-transactional-migration-v1"],
    },
    {
        "case_id": "validation:no-relevant-1",
        "role": "VALIDATION",
        "conditions": ["one_shot_task", "passing_only_run", "single_file_change"],
        "expected": [],
    },
]


def arm(payload, simple):
    rows = []
    for case in CASES:
        result = CROSS.lookup(
            payload,
            {"schema_version": 1, "conditions": case["conditions"], "approved_permissions": []},
            simple=simple,
        )
        result.update(case_id=case["case_id"], role=case["role"], correct=result["selected"] == sorted(case["expected"]))
        rows.append(result)
    return {
        "runs": rows,
        "adaptations_considered": sum(row["adaptations_considered"] for row in rows),
        "compatibility_checks_executed": sum(row["compatibility_checks_executed"] for row in rows),
        "irrelevant_compatibility_checks": sum(row["compatibility_checks_executed"] - len(row["selected"]) for row in rows),
        "correct_decisions": sum(row["correct"] for row in rows),
    }


def main():
    payload = evidence()
    errors = CROSS.validate_evidence(payload)
    if errors:
        raise RuntimeError("; ".join(errors))
    flat = arm(payload, False)
    simple = arm(payload, True)
    results = {
        "schema_version": 1,
        "run_date": "2026-08-13",
        "entry_gate": payload["entry_gate"],
        "flat_lookup": flat,
        "simple_status_permission_heuristic": simple,
        "pathology": {
            "where": "personal adaptation selection",
            "why": "Flat lookup opens a full compatibility check for every active adaptation even when bounded summary conditions can exclude it.",
            "reproduced": flat["irrelevant_compatibility_checks"] > 0,
        },
        "measurement_boundary": {
            "comparable": ["selection correctness", "full compatibility checks", "permission changes"],
            "not_comparable": ["inference tokens", "elapsed time"],
            "repository_reads": "One bounded evidence file per arm; no read reduction is claimed.",
        },
        "learning_verdicts": [{
            "id": "cross-project-flat-selection-inefficiency",
            "status": "not-established",
            "feedback_id": "feedback-cross-project-flat-selection",
            "proposal_ids": ["proposal-meta-selector-1"],
        }],
    }
    atomic_write(HERE / "cross-project-evidence.json", payload)
    atomic_write(HERE / "baseline.json", results)
    print(json.dumps({
        "entry_gate": payload["entry_gate"],
        "flat_checks": flat["compatibility_checks_executed"],
        "irrelevant_checks": flat["irrelevant_compatibility_checks"],
        "simple_checks": simple["compatibility_checks_executed"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
