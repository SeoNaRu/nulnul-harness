#!/usr/bin/env python3
"""Evidence-gated evolution of declarative Harness controls above a guarded Kernel."""

import argparse
import json
import os
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import foundation_runtime as runtime
import harness_control
from sync_host_entry import atomic_batch_write


SCHEMA_VERSION = 1
MAX_SOURCE_EXPERIENCES = 20
RESULTS = {
    "KEEP", "TUNE_CANDIDATE", "REPLACE_CANDIDATE", "RETIRE_CANDIDATE",
    "CREATE_CANDIDATE", "MORE_EXPERIENCE_REQUIRED", "NO_ACTION",
}
OPERATIONS = {"KEEP", "TUNE", "REPLACE", "RETIRE", "CREATE"}
SIGNALS = {
    "success-only", "selection-false-positive", "selection-false-negative",
    "unnecessary-selector", "context-retrieval-miss", "context-bloat",
    "unnecessary-agent-topology", "missing-agent-specialization",
    "verification-orchestration-failure", "memory-policy-failure",
    "lifecycle-churn", "discovery-waste", "user-intervention",
    "replacement-advantage", "control-subsumed", "uncovered-control",
    "insufficient", "none",
}
DIAGNOSIS_FIELDS = (
    "observed_weakness", "why_harness_control_contributed", "generalizable_repair",
    "expected_benefit", "quality_risk", "cost_risk", "safety_risk",
    "what_must_not_change",
)
PRIMARY_FIELDS = (
    "strict", "authoritative_checks", "correct_capability_choice",
    "correct_agent_topology", "correct_memory_retrieval",
)
COST_FIELDS = (
    "input_tokens", "model_calls", "runtime_ms", "repository_reads",
    "context_bytes", "pack_bytes", "user_interventions", "fixed_direct_bytes",
    "extra_tool_calls", "persistent_state_bytes", "maintenance_units",
)


def canonical_digest(payload):
    return harness_control.canonical_digest(payload)


def paths(root):
    root = Path(root).resolve()
    local = root / "docs/nulnul/.runtime/harness-evolution"
    return {
        **harness_control.paths(root),
        "challengers": local / "challengers",
        "safety": local / "safety",
        "competitions": local / "competitions",
    }


def _all_experiences(root):
    store = runtime.Store(root)
    index = runtime.load_index(store)
    return [
        row for identity in index.get("experiences", [])[-runtime.MAX_SEARCH_ITEMS_PER_TYPE:]
        if (row := runtime.read_json(store.experiences / f"{identity}.json"))
    ]


def evolution_query(root, control_id=None, limit=20):
    """Return bounded verified control-attributed Foundation records, never raw evidence."""
    if not isinstance(limit, int) or not 1 <= limit <= 50:
        raise ValueError("Harness Evolution query limit must be between 1 and 50")
    rows = [
        row for row in _all_experiences(root)
        if row.get("status") == "ACTIVE"
        and row.get("quality") == "VERIFIED"
        and row.get("harness_evolution_eligible")
        and (not control_id or row.get("control_id") == control_id)
    ]
    rows.sort(key=lambda row: row["created_at"])
    return {
        "schema_version": SCHEMA_VERSION,
        "filters": {"control_id": control_id, "limit": limit},
        "records": rows[-limit:],
        "count": min(len(rows), limit),
        "raw_transcripts_returned": False,
    }


def champion_snapshot(root):
    registry = harness_control.current_registry(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_digest": registry["registry_digest"],
        "kernel_digest": registry["kernel_digest"],
        "controls": [
            {
                "control_id": row["control_id"],
                "current_version": row["current_version"],
                "current_digest": row["current_digest"],
                "status": row["status"],
                "policy": row["policy"],
            }
            for row in registry["controls"] if row["status"] == "CURRENT"
        ],
    }


def _current_by_id(root):
    return {
        row["control_id"]: row for row in harness_control.current_registry(root)["controls"]
        if row["status"] == "CURRENT"
    }


def _source_experiences(root, identities, *, target=None, allow_unowned=False):
    identities = list(dict.fromkeys(identities or []))
    if not identities or len(identities) > MAX_SOURCE_EXPERIENCES:
        raise ValueError("Harness Evolution requires 1-20 source Experience IDs")
    available = {row["experience_id"]: row for row in _all_experiences(root)}
    if any(identity not in available for identity in identities):
        raise ValueError("Harness Evolution source Experience is unknown")
    rows = [available[identity] for identity in identities]
    if any(
        row.get("status") != "ACTIVE" or row.get("quality") != "VERIFIED"
        or not row.get("harness_evolution_eligible")
        for row in rows
    ):
        raise ValueError("Harness Evolution accepts only active VERIFIED Harness-attributed Experiences")
    if target and not allow_unowned:
        control = harness_control.current_control(root, target)
        if any(
            row.get("control_id") != target
            or row.get("control_digest") != control["current_digest"]
            or row.get("harness_attribution_class") != control["attribution_class"]
            for row in rows
        ):
            raise ValueError("Harness Experience does not attribute the current target control")
    return rows


def _covered_by_decision(root, control_id, sources):
    for decision in reversed(runtime.read_jsonl(runtime.Store(root).decisions)):
        evolution = decision.get("harness_evolution", {})
        if (
            decision.get("status") == "ACTIVE"
            and control_id in evolution.get("affected_control_ids", [])
            and set(sources) <= set(evolution.get("source_experience_ids", []))
        ):
            return decision["decision_id"]
    return None


def evaluate(root, review):
    """Return one bounded non-mutating Harness lifecycle result."""
    if not isinstance(review, dict) or review.get("signal") not in SIGNALS:
        raise ValueError("invalid bounded Harness Evolution signal")
    signal = review["signal"]
    target = str(review.get("target_control_id", "")).strip()
    current = _current_by_id(root)
    create = signal == "uncovered-control"
    if signal not in {"none", "insufficient"} and not target:
        raise ValueError("Harness Evolution signal requires a target CONTROL_ID")
    if create:
        if target in current or not re.fullmatch(r"control-[a-z0-9][a-z0-9-]{1,63}", target):
            raise ValueError("CREATE requires one new bounded CONTROL_ID")
    elif target and target not in current:
        raise ValueError("Harness Evolution target is not current")
    sources = list(dict.fromkeys(review.get("source_experience_ids", [])))
    experiences = _source_experiences(root, sources, target=target, allow_unowned=create) if sources else []
    if signal not in {"none", "insufficient"} and not experiences:
        raise ValueError("evidence-bearing Harness signals require source Experiences")
    result, reason = "MORE_EXPERIENCE_REQUIRED", "bounded evidence does not justify Harness mutation"
    if signal == "none":
        result, reason = "NO_ACTION", "no material Harness Evolution trigger is present"
    elif signal == "insufficient":
        result, reason = "MORE_EXPERIENCE_REQUIRED", "current evidence is not Harness-attributable"
    elif signal == "success-only":
        if any(row.get("result") != "SUCCESS" or row.get("expected_effect") != row.get("actual_effect") for row in experiences):
            result, reason = "MORE_EXPERIENCE_REQUIRED", "success review contains unresolved Harness-effect evidence"
        elif _covered_by_decision(root, target, sources):
            result, reason = "NO_ACTION", "an active Harness Decision already covers this evidence"
        elif review.get("trigger") == "explicit-maintenance":
            result, reason = "KEEP", "verified Harness Experience supports the current control"
        else:
            result, reason = "NO_ACTION", "additional success alone does not reopen Harness Evolution"
    else:
        weaknesses = [row for row in experiences if row.get("expected_effect") != row.get("actual_effect")]
        if len(weaknesses) < 2:
            result, reason = "MORE_EXPERIENCE_REQUIRED", "Harness mutation requires repeated attributable weakness"
        elif signal == "replacement-advantage":
            result, reason = "REPLACE_CANDIDATE", "repeated evidence supports competition with one distinct control strategy"
        elif signal == "control-subsumed" and review.get("subsumed_by_control_id") in current:
            result, reason = "RETIRE_CANDIDATE", "another current control completely covers this responsibility"
        elif signal == "uncovered-control":
            result, reason = "CREATE_CANDIDATE", "repeated Harness evidence exposes one unowned control responsibility"
        else:
            result, reason = "TUNE_CANDIDATE", "repeated Harness evidence supports one bounded policy adjustment"
    if result.endswith("_CANDIDATE"):
        for field in DIAGNOSIS_FIELDS:
            if not isinstance(review.get(field), str) or not review[field].strip():
                raise ValueError(f"{result} requires {field}")
    snapshot = champion_snapshot(root)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "result": result,
        "reason": reason,
        "champion_digest": snapshot["registry_digest"],
        "kernel_digest": snapshot["kernel_digest"],
        "target_control_id": target or None,
        "target_control_digest": current.get(target, {}).get("current_digest"),
        "source_experience_ids": sources,
        "diagnosis": {field: review.get(field, "") for field in DIAGNOSIS_FIELDS},
        "subsumed_by_control_id": review.get("subsumed_by_control_id"),
    }
    payload["evaluation_digest"] = canonical_digest(payload)
    return payload


def validate_evaluation(root, evaluation):
    if not isinstance(evaluation, dict):
        raise ValueError("Harness evaluation must be one object")
    unsigned = {key: value for key, value in evaluation.items() if key != "evaluation_digest"}
    if evaluation.get("result") not in RESULTS or evaluation.get("evaluation_digest") != canonical_digest(unsigned):
        raise ValueError("Harness evaluation identity is invalid")
    snapshot = champion_snapshot(root)
    if snapshot["registry_digest"] != evaluation.get("champion_digest"):
        raise ValueError("stale HARNESS CHAMPION digest")
    if snapshot["kernel_digest"] != evaluation.get("kernel_digest"):
        raise ValueError("Harness evaluation changed the guarded Kernel")
    sources = evaluation.get("source_experience_ids", [])
    if evaluation["result"] not in {"NO_ACTION", "MORE_EXPERIENCE_REQUIRED"} and not sources:
        raise ValueError("Harness lifecycle decision requires source Experiences")
    if sources:
        _source_experiences(
            root, sources, target=evaluation.get("target_control_id"),
            allow_unowned=evaluation["result"] == "CREATE_CANDIDATE",
        )
    return harness_control.current_registry(root)


def _operation(result):
    return result.removesuffix("_CANDIDATE")


def _new_control(specification, *, control_id=None, version=1):
    if not isinstance(specification, dict):
        raise ValueError("new Harness control specification must be one object")
    row = {
        key: specification.get(key)
        for key in harness_control.CONTROL_FIELDS
        if key not in {"current_version", "current_digest", "status"}
    }
    if control_id is not None:
        supplied = specification.get("control_id")
        if supplied not in {None, control_id}:
            raise ValueError("replacement Harness control must preserve CONTROL_ID")
        row["control_id"] = control_id
    row.update({"current_version": version, "current_digest": "", "status": "CHALLENGER"})
    row["current_digest"] = harness_control.control_digest(row)
    return harness_control.validate_control(row, statuses={"CHALLENGER"})


def _proposed_registry(root, evaluation, specification):
    champion = validate_evaluation(root, evaluation)
    operation = _operation(evaluation["result"])
    target = evaluation["target_control_id"]
    controls = [dict(row) for row in champion["controls"]]
    by_id = {row["control_id"]: row for row in controls}
    if operation == "TUNE":
        if set(specification or {}) != {"policy"} or not isinstance(specification["policy"], dict):
            raise ValueError("TUNE accepts only one declarative policy")
        tuned = dict(by_id[target])
        tuned["policy"] = dict(specification["policy"])
        tuned["current_version"] += 1
        tuned["status"] = "CHALLENGER"
        tuned["current_digest"] = harness_control.control_digest(tuned)
        harness_control.validate_control(tuned, statuses={"CHALLENGER"})
        controls = [tuned if row["control_id"] == target else row for row in controls]
    elif operation == "RETIRE":
        if specification not in ({}, None):
            raise ValueError("RETIRE has no replacement policy")
        controls = [{**row, "status": "RETIRED"} if row["control_id"] == target else row for row in controls]
    else:
        if not isinstance(specification, dict) or set(specification) != {"control"}:
            raise ValueError(f"{operation} requires one new Harness control contract")
        if operation == "REPLACE":
            candidate = _new_control(
                specification["control"], control_id=target,
                version=by_id[target]["current_version"] + 1,
            )
            controls = [candidate if row["control_id"] == target else row for row in controls]
        elif operation == "CREATE":
            candidate = _new_control(specification["control"])
            if candidate["control_id"] in by_id:
                raise ValueError("new Harness control ID already exists")
            controls.append(candidate)
        elif operation != "CREATE":
            raise ValueError("unsupported Harness control operation")
    proposed = harness_control.with_digests({
        "schema_version": SCHEMA_VERSION,
        "guarded_kernel": champion["guarded_kernel"],
        "kernel_digest": champion["kernel_digest"],
        "controls": sorted(controls, key=lambda row: row["control_id"]),
        "registry_digest": "",
    })
    return harness_control.validate_runtime_bindings(
        proposed, harness_control.shipped_registry(), allow_challenger=True
    )


def freeze_challenger(root, evaluation, specification):
    if not evaluation.get("result", "").endswith("_CANDIDATE"):
        raise ValueError("only a mutation candidate may freeze one Harness Challenger")
    proposed = _proposed_registry(root, evaluation, specification)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "operation": _operation(evaluation["result"]),
        "target_control_id": evaluation["target_control_id"],
        "champion_digest": evaluation["champion_digest"],
        "kernel_digest": evaluation["kernel_digest"],
        "evaluation_digest": evaluation["evaluation_digest"],
        "source_experience_ids": evaluation["source_experience_ids"],
        "proposed_registry": proposed,
        "created_at": runtime.utc_now(),
        "status": "CHALLENGER",
    }
    manifest["challenger_digest"] = canonical_digest(manifest)
    path = paths(root)["challengers"] / f"{manifest['challenger_digest']}.json"
    if path.exists() and runtime.read_json(path) != manifest:
        raise ValueError("frozen Harness Challenger digest collision")
    runtime.write_json(path, manifest)
    path.chmod(0o444)
    return manifest


def load_challenger(root, digest):
    if not re.fullmatch(r"[a-f0-9]{64}", str(digest)):
        raise ValueError("invalid Harness Challenger digest")
    manifest = runtime.read_json(paths(root)["challengers"] / f"{digest}.json")
    unsigned = {key: value for key, value in (manifest or {}).items() if key != "challenger_digest"}
    if not manifest or manifest.get("challenger_digest") != canonical_digest(unsigned):
        raise ValueError("unknown or corrupt frozen Harness Challenger")
    harness_control.validate_registry(manifest["proposed_registry"])
    return manifest


def safety_gate(root, evaluation, challenger_digest):
    champion = validate_evaluation(root, evaluation)
    challenger = load_challenger(root, challenger_digest)
    if (
        challenger["evaluation_digest"] != evaluation["evaluation_digest"]
        or challenger["champion_digest"] != champion["registry_digest"]
    ):
        raise ValueError("Harness Challenger does not belong to this evaluation")
    proposed = challenger["proposed_registry"]
    champion_controls = {row["control_id"]: row for row in champion["controls"]}
    checks = {
        "kernel_unchanged": proposed["guarded_kernel"] == champion["guarded_kernel"] and proposed["kernel_digest"] == champion["kernel_digest"],
        "provenance_guarded": all("rewrite_provenance" in row["forbidden_effects"] for row in proposed["controls"]),
        "raw_transcript_guarded": all("include_raw_transcript" in row["forbidden_effects"] for row in proposed["controls"]),
        "authority_guarded": all({"broaden_authority", "mutate_host_trust"} <= set(row["forbidden_effects"]) for row in proposed["controls"]),
        "rollback_guarded": all("disable_rollback" in row["forbidden_effects"] for row in proposed["controls"]),
        "check_receipts_guarded": all("disable_authoritative_check" in row["forbidden_effects"] for row in proposed["controls"]),
        "self_promotion_blocked": all(
            row["status"] != "CURRENT"
            for row in proposed["controls"]
            if row["control_id"] not in champion_controls
            or row["current_digest"] != champion_controls[row["control_id"]]["current_digest"]
        ),
        "champion_separate": proposed["registry_digest"] != champion["registry_digest"],
    }
    result = "PASS" if all(checks.values()) else "FAIL"
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "challenger_digest": challenger_digest,
        "evaluation_digest": evaluation["evaluation_digest"],
        "kernel_digest": champion["kernel_digest"],
        "checks": checks,
        "result": result,
        "created_at": runtime.utc_now(),
    }
    receipt["safety_digest"] = canonical_digest(receipt)
    path = paths(root)["safety"] / f"{receipt['safety_digest']}.json"
    runtime.write_json(path, receipt)
    path.chmod(0o444)
    return receipt


def load_safety(root, digest):
    if not re.fullmatch(r"[a-f0-9]{64}", str(digest)):
        raise ValueError("invalid Harness safety digest")
    receipt = runtime.read_json(paths(root)["safety"] / f"{digest}.json")
    unsigned = {key: value for key, value in (receipt or {}).items() if key != "safety_digest"}
    if not receipt or receipt.get("safety_digest") != canonical_digest(unsigned):
        raise ValueError("unknown or corrupt Harness safety receipt")
    return receipt


def _outcome(row, label):
    if not isinstance(row, dict) or any(not isinstance(row.get(field), bool) for field in PRIMARY_FIELDS):
        raise ValueError(f"{label} has incomplete primary outcomes")
    if any(not isinstance(row.get(field), int) or row[field] < 0 for field in ("unauthorized_writes", "regressions")):
        raise ValueError(f"{label} has invalid regression or authority evidence")
    return {field: row[field] for field in PRIMARY_FIELDS + ("unauthorized_writes", "regressions")}


def _cost(row, label):
    if not isinstance(row, dict) or any(
        not isinstance(row.get(field), (int, float)) or isinstance(row[field], bool) or row[field] < 0
        for field in COST_FIELDS
    ):
        raise ValueError(f"{label} has incomplete Harness carrying cost")
    return {field: row[field] for field in COST_FIELDS}


def freeze_competition(root, evaluation, challenger_digest, safety_digest, evidence):
    validate_evaluation(root, evaluation)
    challenger = load_challenger(root, challenger_digest)
    safety = load_safety(root, safety_digest)
    if safety.get("result") != "PASS" or safety.get("challenger_digest") != challenger_digest:
        raise ValueError("Harness competition requires a passing safety invariant gate")
    groups = evidence.get("task_groups") if isinstance(evidence, dict) else None
    if not isinstance(groups, list) or not 2 <= len(groups) <= 3:
        raise ValueError("Harness competition requires two or three bounded task groups")
    names, normalized = set(), []
    for group in groups:
        name = group.get("group")
        if name in names or name not in {"TARGET_WEAKNESS", "REGRESSION", "SEALED_HOLDOUT"}:
            raise ValueError("Harness competition groups must be unique and bounded")
        names.add(name)
        for field in ("task_hash", "fixture_hash", "project_revision"):
            if not isinstance(group.get(field), str) or not group[field]:
                raise ValueError("Harness competition freeze identity is incomplete")
        if not isinstance(group.get("check_identities"), list) or not group["check_identities"]:
            raise ValueError("Harness competition requires authoritative check identities")
        if name == "SEALED_HOLDOUT" and (
            group.get("sealed_after_challenger_digest") != challenger_digest
            or group.get("exposed_before_freeze") is not False
        ):
            raise ValueError("Harness holdout was not sealed after Challenger freeze")
        normalized.append({
            **group,
            "champion": _outcome(group.get("champion"), f"{name} Champion"),
            "challenger": _outcome(group.get("challenger"), f"{name} Challenger"),
        })
    if not {"TARGET_WEAKNESS", "SEALED_HOLDOUT"} <= names:
        raise ValueError("Harness competition requires target weakness and sealed holdout groups")
    champion_cost = _cost(evidence.get("champion_cost"), "Harness Champion")
    challenger_cost = _cost(evidence.get("challenger_cost"), "Harness Challenger")
    metric = evidence.get("control_metric")
    if not isinstance(metric, dict) or set(metric) != {"name", "direction", "champion", "challenger", "verified"}:
        raise ValueError("Harness competition requires one bounded control-specific metric")
    if metric["direction"] not in {"LOWER", "HIGHER"} or metric["verified"] is not True or any(
        not isinstance(metric[field], (int, float)) or isinstance(metric[field], bool)
        for field in ("champion", "challenger")
    ):
        raise ValueError("invalid Harness control-specific metric")
    metric_improved = (
        metric["challenger"] < metric["champion"]
        if metric["direction"] == "LOWER"
        else metric["challenger"] > metric["champion"]
    )
    def passed(row):
        return all(row[field] for field in PRIMARY_FIELDS) and row["unauthorized_writes"] == 0 and row["regressions"] == 0
    regressions = [row["group"] for row in normalized if passed(row["champion"]) and not passed(row["challenger"])]
    improvements = [row["group"] for row in normalized if not passed(row["champion"]) and passed(row["challenger"])]
    challenger_all = all(passed(row["challenger"]) for row in normalized)
    if regressions or not challenger_all:
        outcome, reason = "KEEP_CURRENT", "Harness Challenger regressed quality, safety, or the sealed holdout"
    elif improvements or metric_improved:
        outcome, reason = "PROMOTE_CHALLENGER", "Harness Challenger improved verified quality or its target control metric without regression"
    elif sum(challenger_cost.values()) < sum(champion_cost.values()):
        outcome, reason = "PROMOTE_CHALLENGER", "equivalent verified quality has lower Harness carrying cost"
    else:
        outcome, reason = "KEEP_CURRENT", "no verified quality, control-metric, or carrying-cost advantage"
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "champion_digest": evaluation["champion_digest"],
        "challenger_digest": challenger_digest,
        "evaluation_digest": evaluation["evaluation_digest"],
        "safety_digest": safety_digest,
        "task_groups": normalized,
        "control_metric": metric,
        "metric_improved": metric_improved,
        "champion_cost": champion_cost,
        "challenger_cost": challenger_cost,
        "regressions": regressions,
        "improvements": improvements,
        "outcome": outcome,
        "reason": reason,
        "created_at": runtime.utc_now(),
    }
    receipt["competition_digest"] = canonical_digest(receipt)
    path = paths(root)["competitions"] / f"{receipt['competition_digest']}.json"
    runtime.write_json(path, receipt)
    path.chmod(0o444)
    return receipt


def load_competition(root, digest):
    if not re.fullmatch(r"[a-f0-9]{64}", str(digest)):
        raise ValueError("invalid Harness competition digest")
    receipt = runtime.read_json(paths(root)["competitions"] / f"{digest}.json")
    unsigned = {key: value for key, value in (receipt or {}).items() if key != "competition_digest"}
    if not receipt or receipt.get("competition_digest") != canonical_digest(unsigned):
        raise ValueError("unknown or corrupt Harness competition")
    return receipt


def _active_task(root):
    store = runtime.Store(root)
    active = runtime.read_json(store.active)
    task = next((row for row in (active or {}).get("tasks", []) if row.get("status") == "ACTIVE"), None)
    if not active or not task:
        raise ValueError("Harness Evolution transaction requires one active Foundation Task")
    return store, active, task


def _activated_registry(challenger):
    proposed = challenger["proposed_registry"]
    controls = [
        {**row, "status": "CURRENT"} if row["status"] == "CHALLENGER" else row
        for row in proposed["controls"]
    ]
    return harness_control.with_digests({
        "schema_version": SCHEMA_VERSION,
        "guarded_kernel": proposed["guarded_kernel"],
        "kernel_digest": proposed["kernel_digest"],
        "controls": controls,
        "registry_digest": "",
    })


def _decision(active, task, evaluation, operation, before, after, safety, competition):
    sources = evaluation["source_experience_ids"]
    affected = [evaluation["target_control_id"]] if evaluation.get("target_control_id") else []
    return {
        "schema_version": runtime.SCHEMA_VERSION,
        "decision_id": runtime.make_id("decision"),
        "decision": f"{operation} Harness control " + ", ".join(affected),
        "why": evaluation["reason"],
        "session_id": active["session_id"],
        "task_id": task["task_id"],
        "derived_from": [f"experience:{identity}" for identity in sources],
        "evidence": sources,
        "source_refs": [f"experience:{identity}" for identity in sources],
        "created_at": runtime.utc_now(),
        "status": "ACTIVE",
        "supersedes": None,
        "superseded_by": None,
        "project_revision": active.get("project_revision", "unknown"),
        "host_fingerprint": active.get("host_fingerprint", {}).get("fingerprint_id"),
        "nulnul_revision": active.get("nulnul_revision"),
        "scope": "harness-control",
        "harness_evolution": {
            "operation": operation,
            "affected_control_ids": affected,
            "source_experience_ids": sources,
            "evaluation_digest": evaluation["evaluation_digest"],
            "diagnosis": evaluation["diagnosis"],
            "old_registry_digest": before["registry_digest"],
            "new_registry_digest": after["registry_digest"],
            "old_control_digest": evaluation.get("target_control_digest"),
            "new_control_digest": next((
                row["current_digest"] for row in after["controls"]
                if row["control_id"] == evaluation.get("target_control_id") and row["status"] == "CURRENT"
            ), None),
            "safety_validation": ({"digest": safety["safety_digest"], "result": safety["result"]} if safety else None),
            "competition_result": ({"digest": competition["competition_digest"], "outcome": competition["outcome"]} if competition else None),
            "cost_result": ({"champion": competition["champion_cost"], "challenger": competition["challenger_cost"]} if competition else None),
            "reconsideration_boundary": {
                "KEEP": "materially new Harness-attributable Experience",
                "TUNE": "verified post-tune Harness Experience",
                "REPLACE": "contradictory verified Harness comparison evidence",
                "RETIRE": "new evidence plus an explicit reactivation transaction",
                "CREATE": "verified post-create Harness value",
            }[operation],
        },
    }


def _restore(originals):
    existing = {path: value for path, value in originals.items() if value is not None}
    if existing:
        atomic_batch_write(existing)
    for path, value in originals.items():
        if value is None:
            path.unlink(missing_ok=True)


def transact(root, evaluation, challenger_digest=None, safety_digest=None, competition_digest=None, replace=os.replace):
    """Commit one safety-gated control Decision and restore all owned bytes on failure."""
    root = Path(root).resolve()
    before = validate_evaluation(root, evaluation)
    if evaluation["result"] in {"NO_ACTION", "MORE_EXPERIENCE_REQUIRED"}:
        raise ValueError("a non-decision evaluation cannot mutate Harness state")
    operation = _operation(evaluation["result"])
    safety = competition = None
    after = before
    if operation == "KEEP":
        if any((challenger_digest, safety_digest, competition_digest)):
            raise ValueError("KEEP has no Harness Challenger competition")
    else:
        challenger = load_challenger(root, challenger_digest)
        safety = load_safety(root, safety_digest)
        competition = load_competition(root, competition_digest)
        if (
            safety.get("result") != "PASS"
            or safety.get("challenger_digest") != challenger_digest
            or competition.get("outcome") != "PROMOTE_CHALLENGER"
            or competition.get("challenger_digest") != challenger_digest
            or competition.get("safety_digest") != safety_digest
            or challenger.get("evaluation_digest") != evaluation["evaluation_digest"]
        ):
            raise ValueError("Harness promotion requires one winning frozen safety-gated competition")
        after = _activated_registry(challenger)
    store, active, task = _active_task(root)
    decision = _decision(active, task, evaluation, operation, before, after, safety, competition)
    decisions = runtime.read_jsonl(store.decisions) + [decision]
    index = runtime.load_index(store)
    runtime._add_search(index, "decision", decision)
    index["updated_at"] = runtime.utc_now()
    active = dict(active)
    active.setdefault("decision_ids", []).append(decision["decision_id"])
    event_path = store.local / "events" / f"{active['session_id']}.jsonl"
    events = runtime.read_jsonl(event_path)
    events.append({
        "event_id": len(events) + 1,
        "kind": "DECISION",
        "session_id": active["session_id"],
        "task_id": task["task_id"],
        "created_at": runtime.utc_now(),
        "details": {"decision_id": decision["decision_id"], "operation": operation, "surface": "harness-control"},
    })
    updates = {
        store.decisions: "".join(json.dumps(runtime.redact(row), ensure_ascii=False, sort_keys=True) + "\n" for row in decisions),
        store.index: runtime.encoded(runtime.redact(index)),
        store.active: runtime.encoded(runtime.redact(active)),
        event_path: "".join(json.dumps(runtime.redact(row), ensure_ascii=False, sort_keys=True) + "\n" for row in events),
    }
    if operation != "KEEP":
        updates[paths(root)["history"] / f"{before['registry_digest']}.json"] = runtime.encoded(before)
        updates[paths(root)["current"]] = runtime.encoded(after)
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else None for path in updates}
    with runtime.writer(store):
        try:
            atomic_batch_write(updates, replace=replace)
            errors = validate_state(root)
            if errors:
                raise ValueError("invalid Harness state after lifecycle mutation: " + "; ".join(errors))
        except Exception:
            _restore(originals)
            raise
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "COMMITTED",
        "operation": operation,
        "decision_id": decision["decision_id"],
        "old_registry_digest": before["registry_digest"],
        "current_registry_digest": harness_control.current_registry(root)["registry_digest"],
        "rollback": "NOT_REQUIRED",
    }


def validate_state(root):
    errors = []
    try:
        current = harness_control.current_registry(root)
        if current["kernel_digest"] != harness_control.shipped_registry()["kernel_digest"]:
            errors.append("current Harness registry changed the guarded Kernel")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    for path in sorted(paths(root)["history"].glob("*.json")):
        try:
            registry = harness_control.read_registry(path)
            if path.stem != registry["registry_digest"]:
                errors.append(f"{path.name}: history digest mismatch")
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path.name}: {exc}")
    experiences = {row["experience_id"]: row for row in _all_experiences(root)}
    for decision in runtime.read_jsonl(runtime.Store(root).decisions):
        evolution = decision.get("harness_evolution")
        if not evolution:
            continue
        operation = evolution.get("operation")
        if operation not in OPERATIONS:
            errors.append(f"{decision.get('decision_id')}: invalid Harness operation")
        sources = evolution.get("source_experience_ids", [])
        if any(identity not in experiences or not experiences[identity].get("harness_evolution_eligible") for identity in sources):
            errors.append(f"{decision.get('decision_id')}: invalid Harness source Experience")
        for field in ("old_registry_digest", "new_registry_digest"):
            if not re.fullmatch(r"[a-f0-9]{64}", str(evolution.get(field, ""))):
                errors.append(f"{decision.get('decision_id')}: invalid {field}")
        if operation != "KEEP" and (
            evolution.get("safety_validation", {}).get("result") != "PASS"
            or evolution.get("competition_result", {}).get("outcome") != "PROMOTE_CHALLENGER"
        ):
            errors.append(f"{decision.get('decision_id')}: mutation lacks safety-gated winning competition")
    return sorted(set(errors))


def real_review(root):
    experiences = _all_experiences(root)
    verified = [row for row in experiences if row.get("quality") == "VERIFIED"]
    eligible = [row for row in verified if row.get("harness_evolution_eligible")]
    return {
        "schema_version": SCHEMA_VERSION,
        "verified_experience_count": len(verified),
        "harness_evolution_eligible_count": len(eligible),
        "historical_fixed_controls": [
            "bounded Capability selection", "deterministic Setup", "Pre-Session Capability Pack",
            "zero-cost empty-Pack bootstrap", "authoritative check finalization",
        ],
        "mutation_justified": False,
        "decision": "NO_REAL_HARNESS_MUTATION_JUSTIFIED" if not eligible else "MORE_HARNESS_EXPERIENCE_REQUIRED",
        "reason": (
            "historical Harness weaknesses are already fixed in the current Champion and no current Harness-attributable weakness exists"
            if not eligible else "eligible Harness evidence exists but no bounded current-control diagnosis has been verified"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("snapshot")
    query_parser = commands.add_parser("query")
    query_parser.add_argument("--control-id")
    query_parser.add_argument("--limit", type=int, default=20)
    evaluate_parser = commands.add_parser("evaluate")
    evaluate_parser.add_argument("review", type=Path)
    challenger_parser = commands.add_parser("challenger")
    challenger_parser.add_argument("evaluation", type=Path)
    challenger_parser.add_argument("specification", type=Path)
    safety_parser = commands.add_parser("safety")
    safety_parser.add_argument("evaluation", type=Path)
    safety_parser.add_argument("challenger_digest")
    competition_parser = commands.add_parser("compete")
    competition_parser.add_argument("evaluation", type=Path)
    competition_parser.add_argument("challenger_digest")
    competition_parser.add_argument("safety_digest")
    competition_parser.add_argument("evidence", type=Path)
    transact_parser = commands.add_parser("transact")
    transact_parser.add_argument("evaluation", type=Path)
    transact_parser.add_argument("--challenger")
    transact_parser.add_argument("--safety")
    transact_parser.add_argument("--competition")
    commands.add_parser("validate")
    commands.add_parser("real-review")
    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            payload = champion_snapshot(args.root)
        elif args.command == "query":
            payload = evolution_query(args.root, args.control_id, args.limit)
        elif args.command == "evaluate":
            payload = evaluate(args.root, runtime.read_json(args.review))
        elif args.command == "challenger":
            payload = freeze_challenger(args.root, runtime.read_json(args.evaluation), runtime.read_json(args.specification))
        elif args.command == "safety":
            payload = safety_gate(args.root, runtime.read_json(args.evaluation), args.challenger_digest)
        elif args.command == "compete":
            payload = freeze_competition(
                args.root, runtime.read_json(args.evaluation), args.challenger_digest,
                args.safety_digest, runtime.read_json(args.evidence),
            )
        elif args.command == "transact":
            payload = transact(
                args.root, runtime.read_json(args.evaluation), args.challenger,
                args.safety, args.competition,
            )
        elif args.command == "validate":
            errors = validate_state(args.root)
            payload = {"status": "PASS" if not errors else "FAIL", "errors": errors}
        else:
            payload = real_review(args.root)
    except (OSError, UnicodeError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("status") != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
