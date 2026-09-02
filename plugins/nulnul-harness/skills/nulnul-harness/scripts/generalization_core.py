#!/usr/bin/env python3
"""Manage bounded privacy-safe cross-project Foundation knowledge."""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import foundation_runtime
import personal_adaptation


GENERALIZATION_REGISTRY = "generalizations.json"
GENERALIZATION_SCHEMA_VERSION = 1
GENERALIZATION_STATUSES = {"CANDIDATE", "TRANSFERABLE", "NARROWED", "SUPERSEDED", "RETIRED"}
PRIVACY_STATES = {
    "PROJECT_ONLY", "GENERALIZATION_CANDIDATE", "TRANSFERABLE",
    "REJECTED_SENSITIVE", "NEEDS_REDACTION",
}
GENERALIZATION_RESULTS = {
    "KEEP_PROJECT_LOCAL", "CREATE_GENERALIZATION_CANDIDATE", "PROMOTE_TRANSFERABLE",
    "NARROW_SCOPE", "SUPERSEDE", "RETIRE", "MORE_PROJECT_EVIDENCE_REQUIRED", "NO_ACTION",
}
TARGET_RESULTS = {
    "CONFIRMED", "USEFUL_BUT_PROJECT_SPECIFIC_ADAPTATION_REQUIRED",
    "NOT_APPLICABLE", "CONTRADICTED", "INSUFFICIENT_EVIDENCE",
}
GENERALIZATION_TYPES = {"CAPABILITY", "AGENT_TOPOLOGY", "HARNESS_CONTROL", "VERIFICATION", "WORKFLOW"}
MAX_SOURCE_EXPERIENCES = 20
MAX_PRIOR_ITEMS = 3
MAX_PRIOR_BYTES = 2048
DIAGNOSIS_FIELDS = {
    "source_experience_ids", "observed_reusable_pattern", "project_specific_details_removed",
    "why_pattern_may_transfer", "known_preconditions", "known_non_applicability",
    "counterevidence", "privacy_risk", "expected_target_benefit",
}
RECORD_FIELDS = {
    "schema_version", "generalization_id", "type", "status", "abstract_pattern",
    "job_problem_class", "applicability_conditions", "non_applicability_conditions",
    "source_evidence", "source_refs", "evidence_count", "independent_project_count",
    "counterevidence", "validation_history", "privacy_classification", "abstraction_digest",
    "diagnosis", "created_at", "updated_at", "supersedes", "superseded_by",
}
PROJECT_REF = re.compile(r"project:[a-f0-9]{64}")
EXPERIENCE_ID = re.compile(r"exp-[A-Za-z0-9-]+")
GENERALIZATION_ID = re.compile(r"gen-[a-f0-9]{16}")
class GeneralizationError(ValueError):
    pass


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _digest(payload):
    return hashlib.sha256(payload if isinstance(payload, bytes) else _canonical(payload)).hexdigest()


def _abstraction_payload(record):
    return {
        "type": record["type"],
        "abstract_pattern": record["abstract_pattern"].lower(),
        "job_problem_class": record["job_problem_class"].lower(),
        "applicability_conditions": sorted(record["applicability_conditions"]),
        "non_applicability_conditions": sorted(record["non_applicability_conditions"]),
    }


def _strings(value, label, *, required=True, maximum=16):
    if not isinstance(value, list) or len(value) > maximum or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise GeneralizationError(f"{label} must contain at most {maximum} non-empty strings")
    values = [item.strip() for item in value]
    if required and not values:
        raise GeneralizationError(f"{label} must not be empty")
    if len(values) != len(set(values)):
        raise GeneralizationError(f"{label} contains duplicates")
    return values


def _text(value, label, maximum=1200):
    if not isinstance(value, str) or not value.strip() or len(value.encode()) > maximum:
        raise GeneralizationError(f"{label} must be a bounded non-empty string")
    return value.strip()


def _contains_redactable(value):
    if isinstance(value, dict):
        return any(
            key.lower() in {"credential", "credentials", "api_key", "token", "secret", "secrets", "email"}
            or _contains_redactable(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_redactable(item) for item in value)
    return isinstance(value, str) and bool(
        personal_adaptation.EMAIL.search(value) or personal_adaptation.CREDENTIAL.search(value)
    )


def privacy_classify(payload, requested="PROJECT_ONLY"):
    if requested not in {"PROJECT_ONLY", "GENERALIZATION_CANDIDATE", "TRANSFERABLE"}:
        raise GeneralizationError("unknown privacy classification")
    errors = []
    personal_adaptation._reject_private(payload, errors, "generalization")
    if not errors:
        return {"state": requested, "errors": []}
    return {
        "state": "NEEDS_REDACTION" if _contains_redactable(payload) else "REJECTED_SENSITIVE",
        "errors": errors,
    }


def _knowledge_path(home):
    if home is None:
        raise GeneralizationError("PERSONAL_HOME_REQUIRED")
    root = Path(home).resolve()
    if not root.is_dir():
        raise GeneralizationError("personal evolution home must already exist")
    return root / GENERALIZATION_REGISTRY


def empty_generalizations():
    return {"schema_version": GENERALIZATION_SCHEMA_VERSION, "generalizations": [], "updated_at": _now()}


def _source_refs(record):
    refs = []
    if record.get("capability_id"):
        version = record.get("body_digest") or record.get("capability_version") or "unknown"
        refs.append(f"capability:{record['capability_id']}@{version}")
    if record.get("agent_topology_id") and record.get("agent_topology_digest"):
        refs.append(f"topology:{record['agent_topology_id']}@{record['agent_topology_digest']}")
    if record.get("agent_id"):
        refs.append(f"agent:{record['agent_id']}")
    if record.get("control_id") and record.get("control_digest"):
        refs.append(f"control:{record['control_id']}@{record['control_digest']}")
    return refs


def _eligible_experience(record):
    if record.get("quality") != "VERIFIED" or record.get("observability_completeness") != "COMPLETE":
        return False
    if record.get("status") != "ACTIVE" or record.get("result") not in {"SUCCESS", "FAILURE"}:
        return False
    checks = record.get("checks", [])
    if not checks or any(str(row.get("result", "")).lower() not in {"pass", "passed", "success", "fail", "failed", "failure"} for row in checks):
        return False
    if record.get("experience_type") == "CAPABILITY_EXPERIENCE":
        return record.get("evolution_eligible") is True
    if record.get("agent_attribution_scope"):
        return record.get("agent_evolution_eligible") is True
    if record.get("harness_attribution_class"):
        return record.get("harness_evolution_eligible") is True
    return record.get("experience_type") in {"TASK_EXPERIENCE", "GOVERNED_EXPERIENCE", "RECOVERY_EXPERIENCE"}


def _session(store, session_id):
    path = store.sessions / f"{session_id}.json"
    record = foundation_runtime.read_json(path)
    if record is None:
        active = foundation_runtime.read_json(store.active)
        record = active if active and active.get("session_id") == session_id else None
    return record


def collect_source_evidence(source_projects):
    if not isinstance(source_projects, list) or not source_projects:
        raise GeneralizationError("source_projects must not be empty")
    rows = []
    for source in source_projects:
        if not isinstance(source, dict) or set(source) != {"root", "experience_ids"}:
            raise GeneralizationError("each source project needs only root and experience_ids")
        root = Path(source["root"]).resolve()
        ids = source["experience_ids"]
        if not isinstance(ids, list) or not ids:
            raise GeneralizationError("source project experience_ids must not be empty")
        lineage_errors = foundation_runtime.validate_lineage(root)
        if lineage_errors:
            raise GeneralizationError("invalid source project lineage: " + "; ".join(lineage_errors))
        store = foundation_runtime.Store(root)
        source_rows = []
        for identity in ids:
            record = foundation_runtime.read_json(store.experiences / f"{identity}.json")
            if not record or not _eligible_experience(record):
                raise GeneralizationError(f"unknown or ineligible source Experience: {identity}")
            session = _session(store, record.get("session_id"))
            if not session or identity not in session.get("experience_ids", []):
                raise GeneralizationError(f"Experience is not linked to its Session: {identity}")
            project_identity = session.get("host_fingerprint", {}).get("project_root_identity")
            if not re.fullmatch(r"[a-f0-9]{64}", str(project_identity or "")):
                raise GeneralizationError(f"Experience has no privacy-safe project identity: {identity}")
            derived = sorted({
                ref.split(":", 1)[1] for ref in record.get("source_refs", [])
                if isinstance(ref, str) and ref.startswith("generalization:")
            })
            source_rows.append({
                "project_ref": f"project:{project_identity}",
                "experience_id": identity,
                "experience_digest": _digest(record),
                "experience_type": record["experience_type"],
                "result": record["result"],
                "derived_generalization_ids": derived,
            })
        if len({row["project_ref"] for row in source_rows}) != 1:
            raise GeneralizationError("one source project cannot combine multiple project identities")
        rows.extend(source_rows)
    if len(rows) > MAX_SOURCE_EXPERIENCES:
        raise GeneralizationError(f"generalization input exceeds {MAX_SOURCE_EXPERIENCES} Experiences")
    keys = {(row["project_ref"], row["experience_id"]) for row in rows}
    if len(keys) != len(rows):
        raise GeneralizationError("duplicate source Experience")
    return rows


def build_candidate(specification):
    if not isinstance(specification, dict):
        raise GeneralizationError("generalization proposal must be an object")
    kind = specification.get("type")
    if kind not in GENERALIZATION_TYPES:
        raise GeneralizationError("generalization type is invalid")
    pattern = _text(specification.get("abstract_pattern"), "abstract_pattern")
    job = _text(specification.get("job_problem_class"), "job_problem_class", 400)
    applies = _strings(specification.get("applicability_conditions"), "applicability_conditions")
    excludes = _strings(specification.get("non_applicability_conditions"), "non_applicability_conditions", required=False)
    if set(applies) & set(excludes):
        raise GeneralizationError("applicability and non-applicability conditions overlap")
    diagnosis = specification.get("diagnosis")
    if not isinstance(diagnosis, dict) or set(diagnosis) != DIAGNOSIS_FIELDS:
        raise GeneralizationError("generalization diagnosis is incomplete")
    diagnosis = dict(diagnosis)
    for field in DIAGNOSIS_FIELDS - {"source_experience_ids", "known_preconditions", "known_non_applicability", "counterevidence"}:
        diagnosis[field] = _text(diagnosis[field], f"diagnosis.{field}")
    for field in ("source_experience_ids", "known_preconditions", "known_non_applicability", "counterevidence"):
        diagnosis[field] = _strings(diagnosis[field], f"diagnosis.{field}", required=field != "counterevidence", maximum=20)
    privacy = privacy_classify({
        "abstract_pattern": pattern, "job_problem_class": job,
        "applicability_conditions": applies, "non_applicability_conditions": excludes,
        "diagnosis": diagnosis,
    }, "GENERALIZATION_CANDIDATE")
    if privacy["state"] != "GENERALIZATION_CANDIDATE":
        raise GeneralizationError(f"generalization privacy gate: {privacy['state']}: {'; '.join(privacy['errors'])}")
    evidence = collect_source_evidence(specification.get("source_projects"))
    ids = sorted(row["experience_id"] for row in evidence)
    if sorted(diagnosis["source_experience_ids"]) != ids:
        raise GeneralizationError("diagnosis source Experiences do not match verified input")
    identity_payload = {
        "type": kind, "abstract_pattern": pattern.lower(), "job_problem_class": job.lower(),
        "applicability_conditions": sorted(applies), "non_applicability_conditions": sorted(excludes),
    }
    abstraction_digest = _digest(identity_payload)
    created = specification.get("created_at") or _now()
    independent = {row["project_ref"] for row in evidence if not row["derived_generalization_ids"]}
    refs = set()
    for source in specification["source_projects"]:
        store = foundation_runtime.Store(source["root"])
        for experience_id in source["experience_ids"]:
            refs.update(_source_refs(foundation_runtime.read_json(store.experiences / f"{experience_id}.json")))
    record = {
        "schema_version": GENERALIZATION_SCHEMA_VERSION,
        "generalization_id": f"gen-{abstraction_digest[:16]}",
        "type": kind,
        "status": "CANDIDATE",
        "abstract_pattern": pattern,
        "job_problem_class": job,
        "applicability_conditions": sorted(applies),
        "non_applicability_conditions": sorted(excludes),
        "source_evidence": sorted(evidence, key=lambda row: (row["project_ref"], row["experience_id"])),
        "source_refs": sorted(refs),
        "evidence_count": len(evidence),
        "independent_project_count": len(independent),
        "counterevidence": [],
        "validation_history": [],
        "privacy_classification": "GENERALIZATION_CANDIDATE",
        "abstraction_digest": abstraction_digest,
        "diagnosis": diagnosis,
        "created_at": created,
        "updated_at": created,
        "supersedes": None,
        "superseded_by": None,
    }
    errors = validate_record(record)
    if errors:
        raise GeneralizationError("; ".join(errors))
    return record


def validate_record(record, label="generalization"):
    errors = []
    if not isinstance(record, dict) or not RECORD_FIELDS <= set(record):
        return [f"{label} is incomplete"]
    privacy_errors = []
    personal_adaptation._reject_private(record, privacy_errors, label)
    errors.extend(privacy_errors)
    if record.get("schema_version") != GENERALIZATION_SCHEMA_VERSION:
        errors.append(f"{label}.schema_version is invalid")
    if not GENERALIZATION_ID.fullmatch(str(record.get("generalization_id", ""))):
        errors.append(f"{label}.generalization_id is invalid")
    if record.get("type") not in GENERALIZATION_TYPES:
        errors.append(f"{label}.type is invalid")
    if record.get("status") not in GENERALIZATION_STATUSES:
        errors.append(f"{label}.status is invalid")
    for field in ("abstract_pattern", "job_problem_class", "created_at", "updated_at"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f"{label}.{field} must be non-empty")
    for field in ("applicability_conditions", "non_applicability_conditions", "source_refs", "counterevidence", "validation_history"):
        if not isinstance(record.get(field), list):
            errors.append(f"{label}.{field} must be an array")
    if set(record.get("applicability_conditions", [])) & set(record.get("non_applicability_conditions", [])):
        errors.append(f"{label} applicability boundaries overlap")
    if not re.fullmatch(r"[a-f0-9]{64}", str(record.get("abstraction_digest", ""))):
        errors.append(f"{label}.abstraction_digest is invalid")
    elif record["abstraction_digest"] != _digest(_abstraction_payload(record)):
        errors.append(f"{label}.abstraction_digest does not bind the abstraction")
    expected_privacy = "GENERALIZATION_CANDIDATE" if record.get("status") == "CANDIDATE" else "TRANSFERABLE"
    if record.get("privacy_classification") != expected_privacy:
        errors.append(f"{label}.privacy_classification does not match lifecycle state")
    evidence = record.get("source_evidence")
    if not isinstance(evidence, list) or not evidence or len(evidence) > MAX_SOURCE_EXPERIENCES:
        errors.append(f"{label}.source_evidence is invalid")
        evidence = []
    seen = set()
    independent = set()
    for index, row in enumerate(evidence):
        row_label = f"{label}.source_evidence[{index}]"
        required = {"project_ref", "experience_id", "experience_digest", "experience_type", "result", "derived_generalization_ids"}
        if not isinstance(row, dict) or set(row) != required:
            errors.append(f"{row_label} is incomplete")
            continue
        key = (row["project_ref"], row["experience_id"])
        if key in seen:
            errors.append(f"{row_label} is duplicated")
        seen.add(key)
        if not PROJECT_REF.fullmatch(str(row["project_ref"])):
            errors.append(f"{row_label}.project_ref is invalid")
        if not EXPERIENCE_ID.fullmatch(str(row["experience_id"])):
            errors.append(f"{row_label}.experience_id is invalid")
        if not re.fullmatch(r"[a-f0-9]{64}", str(row["experience_digest"])):
            errors.append(f"{row_label}.experience_digest is invalid")
        derived = row["derived_generalization_ids"]
        if not isinstance(derived, list) or any(not GENERALIZATION_ID.fullmatch(str(item)) for item in derived):
            errors.append(f"{row_label}.derived_generalization_ids is invalid")
        elif record["generalization_id"] in derived:
            errors.append(f"{row_label} creates circular Generalization evidence")
        elif not derived:
            independent.add(row["project_ref"])
    if record.get("evidence_count") != len(evidence):
        errors.append(f"{label}.evidence_count is incorrect")
    if record.get("independent_project_count") != len(independent):
        errors.append(f"{label}.independent_project_count is incorrect")
    diagnosis = record.get("diagnosis")
    if not isinstance(diagnosis, dict) or set(diagnosis) != DIAGNOSIS_FIELDS:
        errors.append(f"{label}.diagnosis is incomplete")
    elif sorted(diagnosis.get("source_experience_ids", [])) != sorted(row["experience_id"] for row in evidence):
        errors.append(f"{label}.diagnosis source Experiences do not match")
    validation_keys = set()
    for index, row in enumerate(record.get("validation_history", [])):
        required = {"target_project_ref", "target_experience_id", "target_experience_digest", "result", "validated_at", "applicability_summary"}
        if not isinstance(row, dict) or set(row) != required or row.get("result") not in TARGET_RESULTS:
            errors.append(f"{label}.validation_history[{index}] is invalid")
        elif not PROJECT_REF.fullmatch(str(row.get("target_project_ref", ""))):
            errors.append(f"{label}.validation_history[{index}].target_project_ref is invalid")
        elif not EXPERIENCE_ID.fullmatch(str(row.get("target_experience_id", ""))) or not re.fullmatch(r"[a-f0-9]{64}", str(row.get("target_experience_digest", ""))):
            errors.append(f"{label}.validation_history[{index}] Experience identity is invalid")
        else:
            key = (row["target_project_ref"], row["target_experience_id"])
            if key in validation_keys:
                errors.append(f"{label}.validation_history[{index}] is duplicated")
            validation_keys.add(key)
    for index, row in enumerate(record.get("counterevidence", [])):
        if not isinstance(row, dict) or not isinstance(row.get("summary"), str) or not row["summary"].strip():
            errors.append(f"{label}.counterevidence[{index}] is invalid")
    if record.get("supersedes") == record.get("generalization_id") or record.get("superseded_by") == record.get("generalization_id"):
        errors.append(f"{label} self-supersedes")
    return errors


def validate_registry(payload):
    if not isinstance(payload, dict) or payload.get("schema_version") != GENERALIZATION_SCHEMA_VERSION:
        return ["generalization registry must be a schema-version-1 object"]
    records = payload.get("generalizations")
    if not isinstance(records, list):
        return ["generalizations must be an array"]
    errors = []
    by_id = {}
    digests = set()
    for index, record in enumerate(records):
        errors.extend(validate_record(record, f"generalizations[{index}]"))
        identity = record.get("generalization_id") if isinstance(record, dict) else None
        digest = record.get("abstraction_digest") if isinstance(record, dict) else None
        if identity in by_id:
            errors.append(f"duplicate Generalization ID: {identity}")
        if digest in digests:
            errors.append(f"duplicate Generalization abstraction: {digest}")
        by_id[identity] = record
        digests.add(digest)
    for identity, record in by_id.items():
        if not isinstance(record, dict):
            continue
        old = record.get("supersedes")
        new = record.get("superseded_by")
        if old and (old not in by_id or by_id[old].get("superseded_by") != identity):
            errors.append(f"{identity}: broken supersedes lineage")
        if new and (new not in by_id or by_id[new].get("supersedes") != identity):
            errors.append(f"{identity}: broken superseded_by lineage")
    return sorted(set(errors))


def load_generalizations(home):
    path = _knowledge_path(home)
    payload = foundation_runtime.read_json(path, empty_generalizations())
    errors = validate_registry(payload)
    if errors:
        raise GeneralizationError("; ".join(errors))
    return payload


def evaluate(candidate=None, existing=None):
    if candidate is not None:
        errors = validate_record(candidate, "candidate")
        if errors:
            raise GeneralizationError("; ".join(errors))
        if candidate["evidence_count"] < 2:
            result = "MORE_PROJECT_EVIDENCE_REQUIRED"
        else:
            result = "CREATE_GENERALIZATION_CANDIDATE"
        return {"result": result, "generalization_id": candidate["generalization_id"]}
    if existing is None:
        return {"result": "NO_ACTION", "generalization_id": None}
    errors = validate_record(existing)
    if errors:
        raise GeneralizationError("; ".join(errors))
    if existing["status"] == "CANDIDATE" and (
        existing["independent_project_count"] >= 2
        or any(row["result"] == "CONFIRMED" for row in existing["validation_history"])
    ):
        result = "PROMOTE_TRANSFERABLE"
    elif existing["status"] in {"TRANSFERABLE", "NARROWED"} and existing["counterevidence"]:
        result = "NARROW_SCOPE"
    elif existing["status"] in {"SUPERSEDED", "RETIRED"}:
        result = "NO_ACTION"
    else:
        result = "MORE_PROJECT_EVIDENCE_REQUIRED"
    return {"result": result, "generalization_id": existing["generalization_id"]}


def _write_registry(path, payload, replace=os.replace):
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.chmod(mode)
    try:
        replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def transact(home, decision, *, candidate=None, generalization_id=None, validation=None,
             applicability_conditions=None, non_applicability_conditions=None,
             supersedes=None, reason=None, target_root=None, target_experience_id=None,
             target_result=None, applicability_summary=None, equivalent_generalization_id=None,
             replace=os.replace):
    if decision not in GENERALIZATION_RESULTS | {"RECORD_TARGET_VALIDATION"}:
        raise GeneralizationError("unknown Generalization transaction decision")
    path = _knowledge_path(home)
    registry = load_generalizations(home)
    records = registry["generalizations"]
    current = next((row for row in records if row["generalization_id"] == generalization_id), None)
    now = _now()
    if decision == "CREATE_GENERALIZATION_CANDIDATE":
        if candidate is None or validate_record(candidate):
            raise GeneralizationError("transaction needs one valid frozen candidate")
        if evaluate(candidate=candidate)["result"] != "CREATE_GENERALIZATION_CANDIDATE":
            raise GeneralizationError("Candidate needs repeated verified source evidence")
        duplicate = next((row for row in records if row["abstraction_digest"] == candidate["abstraction_digest"]), None)
        if equivalent_generalization_id:
            proposed = next((row for row in records if row["generalization_id"] == equivalent_generalization_id), None)
            if not proposed:
                raise GeneralizationError("semantic-equivalence survivor is unknown")
            comparable = ("type", "job_problem_class", "applicability_conditions", "non_applicability_conditions")
            if any(proposed[field] != candidate[field] for field in comparable):
                raise GeneralizationError("semantic-equivalence proposal crosses the bounded contract")
            duplicate = proposed
        if duplicate:
            by_key = {(row["project_ref"], row["experience_id"]): row for row in duplicate["source_evidence"]}
            by_key.update({(row["project_ref"], row["experience_id"]): row for row in candidate["source_evidence"]})
            duplicate["source_evidence"] = sorted(by_key.values(), key=lambda row: (row["project_ref"], row["experience_id"]))
            duplicate["evidence_count"] = len(duplicate["source_evidence"])
            duplicate["independent_project_count"] = len({
                row["project_ref"] for row in duplicate["source_evidence"] if not row["derived_generalization_ids"]
            })
            duplicate["source_refs"] = sorted(set(duplicate["source_refs"] + candidate["source_refs"]))
            duplicate["diagnosis"]["source_experience_ids"] = sorted(row["experience_id"] for row in duplicate["source_evidence"])
            duplicate["updated_at"] = now
            generalization_id = duplicate["generalization_id"]
        else:
            records.append(candidate)
            generalization_id = candidate["generalization_id"]
    elif current is None:
        raise GeneralizationError("unknown Generalization")
    elif decision == "PROMOTE_TRANSFERABLE":
        if evaluate(existing=current)["result"] != "PROMOTE_TRANSFERABLE":
            raise GeneralizationError("Generalization lacks independent or target validation evidence")
        current.update(status="TRANSFERABLE", privacy_classification="TRANSFERABLE", updated_at=now)
    elif decision == "RECORD_TARGET_VALIDATION":
        if validation is not None:
            raise GeneralizationError("target validation facts must be derived by the transaction")
        validation = target_validation_receipt(
            home, generalization_id, target_root, target_experience_id,
            target_result, applicability_summary,
        )
        trial = dict(current)
        trial["validation_history"] = current["validation_history"] + [validation]
        if validation["result"] == "CONTRADICTED":
            trial["counterevidence"] = current["counterevidence"] + [{
                "target_project_ref": validation["target_project_ref"],
                "target_experience_id": validation["target_experience_id"],
                "summary": validation["applicability_summary"],
            }]
        trial["updated_at"] = now
        current.clear()
        current.update(trial)
    elif decision == "NARROW_SCOPE":
        if not current["counterevidence"]:
            raise GeneralizationError("scope narrowing requires counterevidence")
        new_applies = _strings(applicability_conditions, "applicability_conditions")
        new_excludes = _strings(non_applicability_conditions, "non_applicability_conditions", required=False)
        if set(new_applies) == set(current["applicability_conditions"]) and set(new_excludes) == set(current["non_applicability_conditions"]):
            raise GeneralizationError("scope narrowing must change applicability")
        current.update(
            status="NARROWED", privacy_classification="TRANSFERABLE",
            applicability_conditions=sorted(new_applies),
            non_applicability_conditions=sorted(new_excludes), updated_at=now,
        )
        current["abstraction_digest"] = _digest(_abstraction_payload(current))
    elif decision == "SUPERSEDE":
        if candidate is None or candidate.get("generalization_id") in {generalization_id, None}:
            raise GeneralizationError("supersession needs one distinct frozen candidate")
        if validate_record(candidate):
            raise GeneralizationError("invalid superseding candidate")
        if candidate["independent_project_count"] < 2:
            raise GeneralizationError("supersession needs independently supported evidence")
        if any(row["generalization_id"] == candidate["generalization_id"] for row in records):
            raise GeneralizationError("superseding Generalization already exists")
        candidate = dict(candidate)
        candidate.update(
            status="TRANSFERABLE", privacy_classification="TRANSFERABLE",
            supersedes=current["generalization_id"], updated_at=now,
        )
        current.update(status="SUPERSEDED", privacy_classification="TRANSFERABLE", superseded_by=candidate["generalization_id"], updated_at=now)
        records.append(candidate)
    elif decision == "RETIRE":
        if not isinstance(reason, str) or not reason.strip():
            raise GeneralizationError("retirement requires evidence-supported reason")
        current.update(status="RETIRED", privacy_classification="TRANSFERABLE", updated_at=now)
        current["counterevidence"] = current["counterevidence"] + [{"summary": reason.strip()}]
    elif decision in {"KEEP_PROJECT_LOCAL", "MORE_PROJECT_EVIDENCE_REQUIRED", "NO_ACTION"}:
        return {"status": decision, "generalization_id": generalization_id, "written": False}
    else:
        raise GeneralizationError("decision requires a supported transaction handler")
    registry["updated_at"] = now
    errors = validate_registry(registry)
    if errors:
        raise GeneralizationError("; ".join(errors))
    _write_registry(path, registry, replace)
    return {"status": decision, "generalization_id": generalization_id, "written": True}


def target_validation_receipt(home, generalization_id, target_root, experience_id, result, applicability_summary, validated_at=None):
    if result not in TARGET_RESULTS:
        raise GeneralizationError("target validation result is invalid")
    if target_root is None or not isinstance(experience_id, str):
        raise GeneralizationError("target validation requires project and Experience identity")
    record = next((row for row in load_generalizations(home)["generalizations"] if row["generalization_id"] == generalization_id), None)
    if not record or record["status"] not in {"CANDIDATE", "TRANSFERABLE", "NARROWED"}:
        raise GeneralizationError("target validation needs a current Candidate or Transferable record")
    evidence = collect_source_evidence([{"root": str(target_root), "experience_ids": [experience_id]}])[0]
    source = foundation_runtime.read_json(
        foundation_runtime.Store(target_root).experiences / f"{experience_id}.json"
    )
    if f"generalization:{generalization_id}" not in source.get("source_refs", []):
        raise GeneralizationError("target Experience does not reference the transferred prior")
    if evidence["project_ref"] in {row["project_ref"] for row in record["source_evidence"]}:
        raise GeneralizationError("source project cannot validate its own transfer")
    summary = _text(applicability_summary, "applicability_summary", 500)
    privacy = privacy_classify({"applicability_summary": summary}, "TRANSFERABLE")
    if privacy["state"] != "TRANSFERABLE":
        raise GeneralizationError(f"target validation privacy gate: {privacy['state']}")
    return {
        "target_project_ref": evidence["project_ref"],
        "target_experience_id": experience_id,
        "target_experience_digest": evidence["experience_digest"],
        "result": result,
        "validated_at": validated_at or _now(),
        "applicability_summary": summary,
    }


def retrieve_priors(home, target, limit=MAX_PRIOR_ITEMS, max_bytes=MAX_PRIOR_BYTES):
    if not 1 <= limit <= MAX_PRIOR_ITEMS or not 1 <= max_bytes <= MAX_PRIOR_BYTES:
        raise GeneralizationError("Target Prior Pack exceeds its bounded limits")
    if not isinstance(target, dict) or target.get("schema_version") != 1:
        raise GeneralizationError("target facts must be a schema-version-1 object")
    job = _text(target.get("job_problem_class"), "target.job_problem_class", 400)
    conditions = set(_strings(target.get("conditions"), "target.conditions", required=False))
    privacy = privacy_classify(target, "TRANSFERABLE")
    if privacy["state"] != "TRANSFERABLE":
        raise GeneralizationError(f"target facts privacy gate: {privacy['state']}")
    target_terms = set(foundation_runtime.tokens(job))
    priors = []
    used = 0
    for record in load_generalizations(home)["generalizations"]:
        if record["status"] not in {"TRANSFERABLE", "NARROWED"}:
            continue
        record_terms = set(foundation_runtime.tokens(record["job_problem_class"]))
        exact_job = record["job_problem_class"].lower() == job.lower()
        if not exact_job and len(target_terms & record_terms) < 2:
            continue
        if not set(record["applicability_conditions"]) <= conditions:
            continue
        if set(record["non_applicability_conditions"]) & conditions:
            continue
        item = {
            "generalization_id": record["generalization_id"],
            "type": record["type"],
            "abstract_pattern": record["abstract_pattern"],
            "why_relevant": "target job and all applicability conditions match",
            "applicability_conditions": record["applicability_conditions"],
            "non_applicability_conditions": record["non_applicability_conditions"],
            "independent_project_count": record["independent_project_count"],
            "evidence_strength": "target-confirmed" if any(row["result"] == "CONFIRMED" for row in record["validation_history"]) else "multi-project",
            "counterevidence_summary": [row.get("summary", "scoped contradiction") for row in record["counterevidence"]][:3],
        }
        size = len(_canonical(item))
        if len(priors) >= limit or used + size > max_bytes:
            break
        priors.append(item)
        used += size
    return {
        "schema_version": 1,
        "priors": priors,
        "item_count": len(priors),
        "byte_count": used,
        "max_items": limit,
        "max_bytes": max_bytes,
        "source_project_memory_included": False,
        "raw_transcripts_included": False,
        "target_authority_changed": False,
    }


def lifecycle_seed(record):
    owners = {
        "CAPABILITY": "NATURAL_SELECTION", "AGENT_TOPOLOGY": "AGENT_EVOLUTION",
        "HARNESS_CONTROL": "HARNESS_EVOLUTION", "VERIFICATION": "NATURAL_SELECTION",
        "WORKFLOW": "NATURAL_SELECTION",
    }
    return {
        "owner": owners[record["type"]],
        "generalization_id": record["generalization_id"],
        "status": "PRIOR_ONLY",
        "direct_mutation_authority": False,
    }


def classify_legacy(payload):
    if isinstance(payload, dict) and payload.get("schema_version") == 1 and "adaptations" in payload:
        return {
            "status": "HISTORICAL_NONCURRENT",
            "reason": "legacy personal-adaptation summaries lack Foundation Experience, privacy-state, and target-validation lineage",
        }
    if validate_registry(payload) == []:
        return {"status": "CURRENT_GENERALIZATION_REGISTRY", "reason": "current contract"}
    return {"status": "REJECTED_LEGACY", "reason": "unrecognized or unverifiable cross-project record"}


def real_review(project_roots):
    projects = 0
    eligible = 0
    seen_roots = set()
    for root in project_roots:
        root = Path(root).resolve()
        if root in seen_roots:
            continue
        seen_roots.add(root)
        store = foundation_runtime.Store(root)
        root_has_evidence = False
        for path in sorted(store.experiences.glob("*.json")):
            record = foundation_runtime.read_json(path)
            if not _eligible_experience(record):
                continue
            session = _session(store, record["session_id"])
            project = session.get("host_fingerprint", {}).get("project_root_identity") if session else None
            if re.fullmatch(r"[a-f0-9]{64}", str(project or "")):
                root_has_evidence = True
                eligible += 1
        projects += int(root_has_evidence)
    return {
        "result": "LIVE_CROSS_PROJECT_TRANSFER_PROVEN" if projects >= 2 else "MORE_REAL_PROJECT_EVIDENCE_REQUIRED",
        "independent_project_count": projects,
        "eligible_experience_count": eligible,
    }


def knowledge_main(argv):
    parser = argparse.ArgumentParser(prog="generalization_core.py")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-home")
    validate.add_argument("--home", type=Path, required=True)
    candidate = sub.add_parser("candidate")
    candidate.add_argument("specification", type=Path)
    evaluate_parser = sub.add_parser("evaluate")
    evaluate_parser.add_argument("record", type=Path)
    transaction = sub.add_parser("transact")
    transaction.add_argument("decision", choices=sorted(GENERALIZATION_RESULTS | {"RECORD_TARGET_VALIDATION"}))
    transaction.add_argument("payload", type=Path)
    transaction.add_argument("--home", type=Path, required=True)
    prior = sub.add_parser("prior")
    prior.add_argument("target", type=Path)
    prior.add_argument("--home", type=Path, required=True)
    receipt = sub.add_parser("target-receipt")
    receipt.add_argument("generalization_id")
    receipt.add_argument("target_root", type=Path)
    receipt.add_argument("experience_id")
    receipt.add_argument("result", choices=sorted(TARGET_RESULTS))
    receipt.add_argument("applicability_summary")
    receipt.add_argument("--home", type=Path, required=True)
    legacy = sub.add_parser("classify-legacy")
    legacy.add_argument("record", type=Path)
    review = sub.add_parser("real-review")
    review.add_argument("project_root", type=Path, nargs="+")
    args = parser.parse_args(argv)
    if args.command == "validate-home":
        payload = load_generalizations(args.home)
        return {"valid": True, "errors": [], "record_count": len(payload["generalizations"])}
    if args.command == "candidate":
        return build_candidate(json.loads(args.specification.read_text(encoding="utf-8")))
    if args.command == "evaluate":
        return evaluate(existing=json.loads(args.record.read_text(encoding="utf-8")))
    if args.command == "transact":
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise GeneralizationError("transaction payload must be an object")
        return transact(args.home, args.decision, **payload)
    if args.command == "prior":
        return retrieve_priors(args.home, json.loads(args.target.read_text(encoding="utf-8")))
    if args.command == "target-receipt":
        return target_validation_receipt(
            args.home, args.generalization_id, args.target_root, args.experience_id,
            args.result, args.applicability_summary,
        )
    if args.command == "classify-legacy":
        return classify_legacy(json.loads(args.record.read_text(encoding="utf-8")))
    return real_review(args.project_root)

def main():
    try:
        output = knowledge_main(sys.argv[1:])
        failed = output.get("valid") is False
    except (OSError, UnicodeError, json.JSONDecodeError, GeneralizationError, ValueError) as error:
        output = {"valid": False, "errors": [str(error)]}
        failed = True
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
