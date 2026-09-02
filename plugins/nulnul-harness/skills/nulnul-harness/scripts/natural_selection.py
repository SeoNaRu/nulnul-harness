#!/usr/bin/env python3
"""Evaluate and transactionally evolve one project capability ecosystem."""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import capability_contract
import capability_pack
import foundation_runtime as runtime
from sync_host_entry import atomic_batch_write


SCHEMA_VERSION = 1
CAPABILITY_TYPES = {"SKILL", "AGENT", "TOOL", "VERIFICATION"}
RESULTS = {
    "KEEP", "UPGRADE_CANDIDATE", "RETIRE_CANDIDATE", "REPLACE_CANDIDATE",
    "MERGE_CANDIDATE", "CREATE_CANDIDATE", "MORE_EXPERIENCE_REQUIRED", "NO_ACTION",
}
OPERATIONS = {"KEEP", "UPGRADE", "RETIRE", "REPLACE", "MERGE", "CREATE"}
SIGNALS = {
    "success-only", "skill-contract-gap", "obsolete-job", "replacement-advantage",
    "strong-overlap", "recurring-uncovered-job", "conflict", "insufficient", "none",
}
MAX_SOURCE_EXPERIENCES = 20
MAX_BODY_BYTES = 64 * 1024


def canonical_digest(payload):
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def body_path(root, identity):
    capability_contract.canonical_logical_target(identity)
    return Path(root).resolve() / ".agents/skills" / identity / "SKILL.md"


def body_digest(root, identity):
    path, _ = capability_pack.body_source(root, "codex", identity)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _all_experiences(store):
    index = runtime.load_index(store)
    rows = []
    for identity in index.get("experiences", [])[-runtime.MAX_SEARCH_ITEMS_PER_TYPE:]:
        row = runtime.read_json(store.experiences / f"{identity}.json")
        if row:
            rows.append(row)
    return rows


def _decision_capabilities(row, known_ids):
    explicit = row.get("natural_selection", {}).get("affected_capability_ids", [])
    return sorted(set(explicit or [identity for identity in known_ids if identity in row.get("decision", "")]))


def _relation(rows, experiences, minimum_repeat=2):
    current = [row for row in rows if row["accepted_current"]]
    output = []
    for index, left in enumerate(current):
        for right in current[index + 1:]:
            pair = {left["capability_id"], right["capability_id"]}
            co_selected = sum(pair <= set(row.get("active_capability_ids", [])) for row in experiences)
            same_job = left["job"].strip().lower() == right["job"].strip().lower()
            same_check = left["project_check_identity"] == right["project_check_identity"]
            if co_selected >= minimum_repeat and (same_job or same_check):
                overlap = "STRONG_OVERLAP"
            elif co_selected or same_job or same_check:
                overlap = "PARTIAL_OVERLAP"
            else:
                overlap = "NO_OVERLAP"
            output.append({
                "capability_ids": sorted(pair),
                "overlap": overlap,
                "signals": {
                    "co_selection_count": co_selected,
                    "same_job": same_job,
                    "same_project_check": same_check,
                },
            })
    return output


def ecosystem_snapshot(root):
    """Return one bounded, read-only view over existing Foundation state."""
    root = Path(root).resolve()
    project = root / "docs/nulnul/project.md"
    rows = capability_contract.load(project, require_canonical=True)
    store = runtime.Store(root)
    experiences = _all_experiences(store)
    decisions = runtime.read_jsonl(store.decisions)
    known_ids = {row["capability_id"] for row in rows}
    capabilities = []
    for row in rows:
        evidence = runtime.evolution_query(
            root, capability_id=row["capability_id"], limit=20
        )["experiences"]
        history = [
            item["decision_id"] for item in decisions
            if row["capability_id"] in _decision_capabilities(item, known_ids)
        ][-20:]
        capabilities.append({
            **row,
            "capability_type": "SKILL",
            "body_digest": body_digest(root, row["capability_id"]),
            "recent_eligible_experience_ids": [item["experience_id"] for item in evidence],
            "selection_count": sum(bool(item.get("pack_id")) for item in evidence),
            "success_count": sum(item.get("result") == "SUCCESS" for item in evidence),
            "failure_count": sum(item.get("result") == "FAILURE" for item in evidence),
            "lifecycle_decision_ids": history,
        })
    digest_source = [
        {
            key: row[key]
            for key in (
                "capability_id", "capability_type", "job", "activation_trigger",
                "project_check_identity", "status", "version_or_digest",
                "logical_load_target", "body_digest",
            )
        }
        for row in capabilities
    ]
    maintenance_policy, _ = runtime.harness_policy(root, "control-maintenance-trigger", {
        "minimum_repeat_count": 2, "shortlist_limit": 3,
    })
    return {
        "schema_version": SCHEMA_VERSION,
        "ecosystem_digest": canonical_digest(digest_source),
        "capabilities": capabilities,
        "relations": _relation(rows, experiences, maintenance_policy["minimum_repeat_count"]),
        "decision_ids": [row["decision_id"] for row in decisions[-20:]],
        "evidence_count": sum(len(row["recent_eligible_experience_ids"]) for row in capabilities),
    }


def _source_experiences(root, identities):
    identities = list(dict.fromkeys(identities or []))
    if not identities or len(identities) > MAX_SOURCE_EXPERIENCES:
        raise ValueError("Natural Selection requires 1-20 source Experience IDs")
    store = runtime.Store(root)
    rows = {row["experience_id"]: row for row in _all_experiences(store)}
    missing = [identity for identity in identities if identity not in rows]
    if missing:
        raise ValueError("unknown source Experience: " + ", ".join(missing))
    selected = [rows[identity] for identity in identities]
    if any(row.get("status") != "ACTIVE" or row.get("quality") != "VERIFIED" for row in selected):
        raise ValueError("Natural Selection accepts only active VERIFIED Experiences")
    return selected


def _covered_by_decision(root, affected, source_ids):
    store = runtime.Store(root)
    known = {row["capability_id"] for row in capability_contract.load(store.nulnul / "project.md", require_canonical=True)}
    for row in reversed(runtime.read_jsonl(store.decisions)):
        if row.get("status") != "ACTIVE" or not set(affected) <= set(_decision_capabilities(row, known)):
            continue
        prior = set(row.get("natural_selection", {}).get("source_experience_ids", row.get("evidence", [])))
        if set(source_ids) <= prior:
            return row["decision_id"]
    return None


def evaluate(root, review):
    """Map a bounded semantic review to a non-mutating lifecycle candidate."""
    if not isinstance(review, dict) or review.get("signal") not in SIGNALS:
        raise ValueError("invalid bounded Natural Selection signal")
    snapshot = ecosystem_snapshot(root)
    maintenance_policy, _ = runtime.harness_policy(root, "control-maintenance-trigger", {
        "minimum_repeat_count": 2, "shortlist_limit": 3,
    })
    current = {
        row["capability_id"]: row for row in snapshot["capabilities"] if row["accepted_current"]
    }
    affected = list(dict.fromkeys(review.get("affected_capability_ids", [])))
    unknown = sorted(set(affected) - set(current))
    signal = review["signal"]
    if unknown and signal != "recurring-uncovered-job":
        raise ValueError("unknown or noncurrent affected capability: " + ", ".join(unknown))
    source_ids = list(dict.fromkeys(review.get("source_experience_ids", [])))
    experiences = _source_experiences(root, source_ids) if source_ids else []
    if signal not in {"none", "insufficient"} and not experiences:
        raise ValueError("evidence-bearing Natural Selection signals require source Experiences")
    result, reason = "MORE_EXPERIENCE_REQUIRED", "the bounded evidence does not justify mutation"
    if signal == "none":
        result, reason = "NO_ACTION", "no material Natural Selection trigger is present"
    elif signal == "insufficient":
        result, reason = "MORE_EXPERIENCE_REQUIRED", "the signal has no evidence-supported lifecycle resolution"
    elif signal == "conflict":
        conflict = review.get("conflict", {})
        required = ("capability_a", "capability_b", "conflicting_invariant", "affected_jobs", "risk")
        if (
            not isinstance(conflict, dict)
            or any(not conflict.get(field) for field in required)
            or {conflict.get("capability_a"), conflict.get("capability_b")} != set(affected)
        ):
            raise ValueError("conflict signal requires one bounded current-capability conflict record")
        result, reason = "MORE_EXPERIENCE_REQUIRED", "the conflict is recorded but does not determine MERGE, UPGRADE, RETIRE, or REPLACE"
    elif signal == "success-only":
        if any(row.get("result") != "SUCCESS" or not row.get("evolution_eligible") for row in experiences):
            result, reason = "MORE_EXPERIENCE_REQUIRED", "success-only review contains ineligible or non-success evidence"
        elif _covered_by_decision(root, affected, source_ids):
            result, reason = "NO_ACTION", "an active lifecycle decision already covers this evidence"
        elif review.get("trigger") == "explicit-maintenance":
            result, reason = "KEEP", "verified success evidence supports the current ecosystem"
        else:
            result, reason = "NO_ACTION", "additional successes alone do not reopen lifecycle evolution"
    elif signal == "skill-contract-gap":
        failures = [
            row for row in experiences
            if row.get("result") == "FAILURE" and row.get("evolution_eligible")
            and row.get("capability_id") in affected
        ]
        if failures:
            result, reason = "UPGRADE_CANDIDATE", "verified attributable failure supports one same-identity challenger"
    elif signal == "obsolete-job":
        if len(affected) == 1 and (
            review.get("job_no_longer_exists") is True
            or review.get("replacement_coverage_id") in set(current) - {affected[0]}
        ):
            result, reason = "RETIRE_CANDIDATE", "verified evidence supports removing this capability from ordinary Packs"
    elif signal == "replacement-advantage":
        if len(affected) == 1 and review.get("replacement_capability_id") not in {None, affected[0]}:
            result, reason = "REPLACE_CANDIDATE", "a distinct project-local challenger may compete for this job"
    elif signal == "strong-overlap":
        pair = sorted(affected)
        relation = next((row for row in snapshot["relations"] if row["capability_ids"] == pair), None)
        if len(pair) == 2 and relation and relation["overlap"] == "STRONG_OVERLAP":
            result, reason = "MERGE_CANDIDATE", "repeated evidence-backed overlap supports a merged ecosystem challenger"
    elif signal == "recurring-uncovered-job":
        jobs = {str(row.get("task_job", "")).strip().lower() for row in experiences}
        if len(experiences) >= maintenance_policy["minimum_repeat_count"] and len(jobs) == 1 and all(not row.get("capability_id") for row in experiences):
            result, reason = "CREATE_CANDIDATE", "repeated verified uncovered work supports one new capability challenger"
    if result.endswith("_CANDIDATE"):
        for field in ("diagnosis", "what_must_not_change", "risk_analysis", "rollback_plan"):
            if not str(review.get(field, "")).strip():
                raise ValueError(f"{result} requires {field}")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "result": result,
        "reason": reason,
        "champion_digest": snapshot["ecosystem_digest"],
        "affected_capability_ids": affected,
        "source_experience_ids": source_ids,
        "diagnosis": review.get("diagnosis", ""),
        "what_must_not_change": review.get("what_must_not_change", ""),
        "risk_analysis": review.get("risk_analysis", ""),
        "rollback_plan": review.get("rollback_plan", ""),
        "candidate_hint": {
            key: review[key]
            for key in ("replacement_capability_id", "replacement_coverage_id", "uncovered_job")
            if key in review
        },
        "conflict_record": review.get("conflict") if signal == "conflict" else None,
    }
    payload["evaluation_digest"] = canonical_digest(payload)
    return payload


def _operation(result):
    return result.removesuffix("_CANDIDATE")


def validate_competition(competition):
    if not isinstance(competition, dict):
        raise ValueError("non-KEEP lifecycle mutation requires competition evidence")
    for side in ("champion", "challenger"):
        row = competition.get(side, {})
        if not all(row.get(field) is True for field in ("strict", "project_check", "completion")):
            raise ValueError(f"{side} failed a primary competition outcome")
        if row.get("unauthorized_writes") != 0:
            raise ValueError(f"{side} violated state authority")
    if competition.get("regressions") != 0 or competition.get("holdout_pass") is not True:
        raise ValueError("ecosystem Challenger has regression or holdout failure")
    outcome = competition.get("primary_outcome")
    if outcome not in {"IMPROVED", "EQUIVALENT"}:
        raise ValueError("competition must establish improved or equivalent quality")
    if outcome == "EQUIVALENT" and not str(competition.get("secondary_advantage", "")).strip():
        raise ValueError("equivalent quality requires one named secondary advantage")
    return competition


def build_candidate(specification, body):
    if not isinstance(specification, dict) or specification.get("capability_type", "SKILL") not in CAPABILITY_TYPES:
        raise ValueError("invalid capability Challenger type")
    if specification.get("capability_type", "SKILL") != "SKILL":
        raise ValueError("this phase mutates project-local Skills only")
    for field in ("capability_id", "job", "activation_trigger", "project_check_identity"):
        if not isinstance(specification.get(field), str) or not specification[field].strip():
            raise ValueError(f"Skill Challenger requires {field}")
    data = body.encode() if isinstance(body, str) else body
    if not data or len(data) > MAX_BODY_BYTES:
        raise ValueError("Skill Challenger body must be 1-65536 bytes")
    digest = hashlib.sha256(data).hexdigest()
    asserted = specification.get("version_or_digest")
    if asserted is not None and asserted != digest:
        raise ValueError("Skill Challenger digest does not match its body")
    row = capability_contract.accepted_record({
        "capability_id": specification.get("capability_id"),
        "job": specification.get("job"),
        "activation_trigger": specification.get("activation_trigger"),
        "project_check_identity": specification.get("project_check_identity"),
        "version_or_digest": digest,
        "logical_load_target": specification.get("logical_load_target"),
    })
    return {
        "capability_type": "SKILL",
        "record": row,
        "body": data.decode("utf-8"),
        "body_digest": digest,
        "candidate_digest": canonical_digest({"record": row, "body_digest": digest}),
    }


def freeze_candidate(specification, body):
    """Freeze one isolated Challenger before competition without product writes."""
    candidate = build_candidate(specification, body)
    return {
        "schema_version": SCHEMA_VERSION,
        "capability_type": candidate["capability_type"],
        "record": candidate["record"],
        "body_digest": candidate["body_digest"],
        "candidate_digest": candidate["candidate_digest"],
    }


def _candidate_for(root, operation, manifest, body, rows):
    if operation == "RETIRE":
        if manifest is not None or body is not None:
            raise ValueError("RETIRE has no capability Challenger body")
        return None
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"{operation} requires one frozen capability Challenger")
    record = manifest.get("record", {})
    identity = record.get("capability_id")
    existing = next((row for row in rows if row["capability_id"] == identity), None)
    if body is None:
        if not existing or existing["status"] != "provisional":
            raise ValueError("a non-materialized Challenger requires one existing provisional capability")
        body = body_path(root, identity).read_text(encoding="utf-8")
    candidate = build_candidate({
        "capability_type": manifest.get("capability_type"),
        **record,
    }, body)
    frozen = {key: value for key, value in candidate.items() if key != "body"}
    expected = {key: manifest.get(key) for key in ("capability_type", "record", "body_digest", "candidate_digest")}
    if frozen != expected:
        raise ValueError("frozen capability Challenger does not match its body or canonical record")
    return candidate


def _decision_record(store, active, task, evaluation, operation, competition, candidate, before, after, lineage):
    source_ids = evaluation["source_experience_ids"]
    source_refs = [f"experience:{identity}" for identity in source_ids]
    decision_id = runtime.make_id("decision")
    natural = {
        "operation": operation,
        "affected_capability_ids": evaluation["affected_capability_ids"],
        "source_experience_ids": source_ids,
        "evaluation_digest": evaluation["evaluation_digest"],
        "diagnosis": evaluation.get("diagnosis", ""),
        "what_must_not_change": evaluation.get("what_must_not_change", ""),
        "risk_analysis": evaluation.get("risk_analysis", ""),
        "rollback_plan": evaluation.get("rollback_plan", ""),
        "ecosystem_champion_digest": before,
        "ecosystem_challenger_digest": after,
        "candidate_ref": ({
            "capability_id": candidate["record"]["capability_id"],
            "capability_type": candidate["capability_type"],
            "candidate_digest": candidate["candidate_digest"],
            "body_digest": candidate["body_digest"],
        } if candidate else None),
        "competition": competition,
        "lineage": lineage,
        "reconsideration_boundary": {
            "KEEP": "materially new verified Experience",
            "UPGRADE": "verified post-upgrade Experience",
            "RETIRE": "contradictory verified evidence and explicit reactivation transaction",
            "REPLACE": "contradictory verified comparison evidence",
            "MERGE": "contradictory verified comparison evidence",
            "CREATE": "verified post-create Experience",
        }[operation],
    }
    return {
        "schema_version": runtime.SCHEMA_VERSION,
        "decision_id": decision_id,
        "decision": f"{operation} " + ", ".join(evaluation["affected_capability_ids"] or [candidate["record"]["capability_id"]]),
        "why": evaluation["reason"],
        "session_id": active["session_id"],
        "task_id": task["task_id"],
        "derived_from": source_refs,
        "evidence": source_ids,
        "source_refs": source_refs,
        "created_at": runtime.utc_now(),
        "status": "ACTIVE",
        "supersedes": None,
        "superseded_by": None,
        "project_revision": active.get("project_revision", "unknown"),
        "host_fingerprint": active.get("host_fingerprint", {}).get("fingerprint_id"),
        "nulnul_revision": active.get("nulnul_revision"),
        "scope": "capability-ecosystem",
        "natural_selection": natural,
    }


def _validate_candidate_operation(root, operation, evaluation, candidate, rows):
    affected = evaluation["affected_capability_ids"]
    by_id = {row["capability_id"]: row for row in rows}
    if operation in {"UPGRADE", "RETIRE", "REPLACE"} and len(affected) != 1:
        raise ValueError(f"{operation} requires one current source capability")
    if operation == "MERGE" and len(affected) < 2:
        raise ValueError("MERGE requires at least two current source capabilities")
    if any(identity not in by_id or by_id[identity]["status"] != capability_contract.CURRENT_STATUS for identity in affected):
        raise ValueError("lifecycle source is not accepted/current")
    candidate_id = candidate["record"]["capability_id"] if candidate else None
    if operation == "UPGRADE" and candidate_id != affected[0]:
        raise ValueError("UPGRADE must preserve capability identity")
    if operation == "UPGRADE" and candidate["body_digest"] == body_digest(root, affected[0]):
        raise ValueError("UPGRADE Challenger must change the capability body")
    if operation in {"CREATE", "MERGE"} and candidate_id in by_id and by_id[candidate_id]["status"] != "provisional":
        raise ValueError(f"{operation} Challenger duplicates a canonical capability ID")
    if operation == "REPLACE" and candidate_id == affected[0]:
        raise ValueError("REPLACE requires a different capability identity")
    if operation == "REPLACE" and evaluation.get("candidate_hint", {}).get("replacement_capability_id") != candidate_id:
        raise ValueError("replacement Challenger does not match the evaluated identity")


def _mutated_rows(operation, evaluation, candidate, rows):
    affected = set(evaluation["affected_capability_ids"])
    candidate_id = candidate["record"]["capability_id"] if candidate else None
    output = []
    for row in rows:
        row = {key: value for key, value in row.items() if key != "accepted_current"}
        if operation == "UPGRADE" and row["capability_id"] in affected:
            row = candidate["record"]
        elif operation == "RETIRE" and row["capability_id"] in affected:
            row["status"] = "retired"
        elif operation in {"REPLACE", "MERGE"} and row["capability_id"] in affected:
            row["status"] = "superseded"
        elif candidate and row["capability_id"] == candidate_id:
            row = candidate["record"]
        output.append(row)
    if candidate and candidate_id not in {row["capability_id"] for row in output}:
        output.append(candidate["record"])
    return output


def validate_ecosystem(root):
    root = Path(root).resolve()
    project = root / "docs/nulnul/project.md"
    errors = []
    try:
        rows = capability_contract.load(project, require_canonical=True)
    except (OSError, UnicodeError, ValueError) as error:
        return [str(error)]
    for row in rows:
        if row["logical_load_target"] != capability_contract.canonical_logical_target(row["capability_id"]):
            errors.append(f"{row['capability_id']}: noncanonical target")
        try:
            digest = body_digest(root, row["capability_id"])
            if row["accepted_current"]:
                capability_pack.canonical_ref(
                    root, "codex", row, "Natural Selection validation",
                    capability_pack.configured_check(project),
                )
            if len(str(row.get("version_or_digest") or "")) == 64 and row["version_or_digest"] != digest:
                errors.append(f"{row['capability_id']}: body digest mismatch")
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(str(error))
    store = runtime.Store(root)
    experience_ids = {row["experience_id"] for row in _all_experiences(store)}
    decision_ids = set()
    known_ids = {row["capability_id"] for row in rows}
    for row in runtime.read_jsonl(store.decisions):
        identity = row.get("decision_id")
        if identity in decision_ids:
            errors.append(f"duplicate decision id: {identity}")
        decision_ids.add(identity)
        natural = row.get("natural_selection")
        if not natural:
            continue
        if natural.get("operation") not in OPERATIONS:
            errors.append(f"{identity}: invalid Natural Selection operation")
        if any(source not in experience_ids for source in natural.get("source_experience_ids", [])):
            errors.append(f"{identity}: dangling Natural Selection Experience")
        if any(capability not in known_ids for capability in natural.get("affected_capability_ids", [])):
            errors.append(f"{identity}: dangling Natural Selection capability")
        candidate = natural.get("candidate_ref")
        if natural.get("operation") not in {"KEEP", "RETIRE"}:
            if not isinstance(candidate, dict) or candidate.get("capability_id") not in known_ids:
                errors.append(f"{identity}: invalid Natural Selection candidate ref")
            elif (
                candidate.get("capability_type") not in CAPABILITY_TYPES
                or not isinstance(candidate.get("candidate_digest"), str)
                or len(candidate["candidate_digest"]) != 64
                or not isinstance(candidate.get("body_digest"), str)
                or len(candidate["body_digest"]) != 64
            ):
                errors.append(f"{identity}: invalid Natural Selection candidate identity")
        elif candidate is not None:
            errors.append(f"{identity}: {natural.get('operation')} cannot own a candidate ref")
        expected_refs = {f"experience:{source}" for source in natural.get("source_experience_ids", [])}
        if not expected_refs <= set(row.get("source_refs", [])):
            errors.append(f"{identity}: Natural Selection source provenance is incomplete")
    errors.extend(runtime.validate_lineage(root))
    return sorted(set(errors))


def _cleanup_empty(paths, root):
    root = Path(root).resolve()
    for path in sorted({path.parent for path in paths}, key=lambda item: len(item.parts), reverse=True):
        while path != root and path.is_relative_to(root):
            try:
                path.rmdir()
            except OSError:
                break
            path = path.parent


def _restore(originals, root):
    existing = {path: value for path, value in originals.items() if value is not None}
    if existing:
        atomic_batch_write(existing)
    created = [path for path, value in originals.items() if value is None]
    for path in created:
        path.unlink(missing_ok=True)
    _cleanup_empty(created, root)


def validate_evaluation(root, evaluation, allowed_results=RESULTS):
    """Validate one frozen Natural Selection result without mutating state."""
    if not isinstance(evaluation, dict):
        raise ValueError("Natural Selection evaluation must be one object")
    unsigned = {key: value for key, value in evaluation.items() if key != "evaluation_digest"}
    result = evaluation.get("result")
    if (
        result not in RESULTS
        or result not in set(allowed_results)
        or evaluation.get("evaluation_digest") != canonical_digest(unsigned)
    ):
        raise ValueError("Natural Selection evaluation identity is invalid")
    snapshot = ecosystem_snapshot(root)
    if snapshot["ecosystem_digest"] != evaluation.get("champion_digest"):
        raise ValueError("stale ECOSYSTEM CHAMPION digest")
    source_ids = evaluation.get("source_experience_ids", [])
    if result not in {"NO_ACTION", "MORE_EXPERIENCE_REQUIRED"} and not source_ids:
        raise ValueError("Natural Selection decision requires source Experiences")
    if source_ids:
        _source_experiences(root, source_ids)
    return snapshot


def transact(root, evaluation, competition=None, candidate_manifest=None, candidate_body=None, replace=os.replace):
    """Apply one validated lifecycle decision or restore every transaction-owned file."""
    root = Path(root).resolve()
    snapshot = validate_evaluation(root, evaluation)
    if evaluation["result"] in {"NO_ACTION", "MORE_EXPERIENCE_REQUIRED"}:
        raise ValueError("a non-decision evaluation cannot mutate the ecosystem")
    operation = _operation(evaluation["result"])
    if operation != "KEEP":
        validate_competition(competition)
    elif competition is not None:
        raise ValueError("KEEP does not require a Challenger competition")
    project = root / "docs/nulnul/project.md"
    rows = capability_contract.load(project, require_canonical=True)
    candidate = _candidate_for(root, operation, candidate_manifest, candidate_body, rows) if operation != "KEEP" else None
    _validate_candidate_operation(root, operation, evaluation, candidate, rows)
    proposed = _mutated_rows(operation, evaluation, candidate, rows)
    project_text = capability_contract.replace_rows(project.read_text(encoding="utf-8"), proposed)
    after_source = []
    for row in proposed:
        identity = row["capability_id"]
        digest = candidate["body_digest"] if candidate and candidate["record"]["capability_id"] == identity else body_digest(root, identity)
        after_source.append({
            "capability_id": identity,
            "capability_type": "SKILL",
            "job": row["job"],
            "activation_trigger": row["activation_trigger"],
            "project_check_identity": row["project_check_identity"],
            "status": row["status"],
            "version_or_digest": row.get("version_or_digest"),
            "logical_load_target": row["logical_load_target"],
            "body_digest": digest,
        })
    after_digest = canonical_digest(after_source)
    lineage = {
        "old": [
            {"capability_id": row["capability_id"], "digest": body_digest(root, row["capability_id"]), "status": row["status"]}
            for row in rows if row["capability_id"] in evaluation["affected_capability_ids"]
        ],
        "new": ({
            "capability_id": candidate["record"]["capability_id"],
            "digest": candidate["body_digest"],
            "status": capability_contract.CURRENT_STATUS,
        } if candidate else None),
    }
    store = runtime.Store(root)
    active = runtime.read_json(store.active)
    task = next((row for row in (active or {}).get("tasks", []) if row.get("status") == "ACTIVE"), None)
    if not active or not task:
        raise ValueError("Natural Selection transaction requires one active Foundation Task")
    decision = _decision_record(
        store, active, task, evaluation, operation, competition, candidate,
        snapshot["ecosystem_digest"], after_digest, lineage,
    )
    decisions = runtime.read_jsonl(store.decisions) + [decision]
    index = runtime.load_index(store)
    runtime._add_search(index, "decision", decision)
    index["updated_at"] = runtime.utc_now()
    active = dict(active)
    active.setdefault("decision_ids", []).append(decision["decision_id"])
    events_path = store.local / "events" / f"{active['session_id']}.jsonl"
    events = runtime.read_jsonl(events_path)
    events.append({
        "event_id": len(events) + 1,
        "kind": "DECISION",
        "session_id": active["session_id"],
        "task_id": task["task_id"],
        "created_at": runtime.utc_now(),
        "details": {
            "decision_id": decision["decision_id"],
            "operation": operation,
            "affected_capability_ids": evaluation["affected_capability_ids"],
        },
    })
    updates = {
        project: project_text,
        store.decisions: "".join(json.dumps(runtime.redact(row), ensure_ascii=False, sort_keys=True) + "\n" for row in decisions),
        store.index: runtime.encoded(runtime.redact(index)),
        store.active: runtime.encoded(runtime.redact(active)),
        events_path: "".join(json.dumps(runtime.redact(row), ensure_ascii=False, sort_keys=True) + "\n" for row in events),
    }
    if candidate:
        target = body_path(root, candidate["record"]["capability_id"])
        updates[target] = candidate["body"]
        if operation == "UPGRADE":
            old_digest = body_digest(root, candidate["record"]["capability_id"])
            archive = target.parent / "versions" / old_digest / "SKILL.md"
            old_body = target.read_text(encoding="utf-8")
            if archive.exists() and (
                archive.is_symlink() or not archive.is_file() or archive.read_text(encoding="utf-8") != old_body
            ):
                raise ValueError("existing Skill version archive does not match the Champion body")
            updates[archive] = old_body
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else None for path in updates}
    with runtime.writer(store):
        try:
            atomic_batch_write(updates, replace=replace)
            errors = validate_ecosystem(root)
            if errors:
                raise ValueError("invalid ecosystem after lifecycle mutation: " + "; ".join(errors))
        except Exception:
            _restore(originals, root)
            raise
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "COMMITTED",
        "operation": operation,
        "decision_id": decision["decision_id"],
        "ecosystem_champion_digest": snapshot["ecosystem_digest"],
        "ecosystem_current_digest": ecosystem_snapshot(root)["ecosystem_digest"],
        "current_capability_ids": [row["capability_id"] for row in capability_contract.bounded_view(project)],
        "rollback": "NOT_REQUIRED",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot")
    review = sub.add_parser("evaluate")
    review.add_argument("review", type=Path)
    candidate = sub.add_parser("candidate")
    candidate.add_argument("specification", type=Path)
    candidate.add_argument("body", type=Path)
    apply = sub.add_parser("transact")
    apply.add_argument("evaluation", type=Path)
    apply.add_argument("--competition", type=Path)
    apply.add_argument("--candidate", type=Path)
    apply.add_argument("--candidate-body", type=Path)
    sub.add_parser("validate")
    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            payload = ecosystem_snapshot(args.root)
        elif args.command == "evaluate":
            payload = evaluate(args.root, runtime.read_json(args.review))
        elif args.command == "candidate":
            payload = freeze_candidate(
                runtime.read_json(args.specification), args.body.read_text(encoding="utf-8")
            )
        elif args.command == "transact":
            payload = transact(
                args.root,
                runtime.read_json(args.evaluation),
                runtime.read_json(args.competition) if args.competition else None,
                runtime.read_json(args.candidate) if args.candidate else None,
                args.candidate_body.read_text(encoding="utf-8") if args.candidate_body else None,
            )
        else:
            errors = validate_ecosystem(args.root)
            payload = {"valid": not errors, "errors": errors}
        failed = payload.get("valid") is False
    except (OSError, UnicodeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        payload = {"status": "failed", "error": str(error)}
        failed = True
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
