#!/usr/bin/env python3
"""Discover and compete frozen external capabilities behind Natural Selection."""

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import capability_pack
import foundation_runtime as runtime
import natural_selection
from sync_host_entry import atomic_batch_write


SCHEMA_VERSION = 1
SOURCE_TYPES = {"LOCAL_DIRECTORY"}
TRIGGERS = {"UPGRADE_CANDIDATE", "REPLACE_CANDIDATE", "CREATE_CANDIDATE"}
SURVIVORS = {
    "KEEP_CURRENT", "UPGRADE_LOCAL", "REPLACE_WITH_EXTERNAL",
    "CREATE_FROM_EXTERNAL", "ADAPT_EXTERNAL_AND_RETEST", "NO_SURVIVOR",
    "MORE_EVIDENCE_REQUIRED",
}
TASK_KINDS = {"TARGET_WEAKNESS", "REGRESSION", "SEALED_HOLDOUT"}
LICENSE_ALLOWLIST = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "CC0-1.0"}
QUERY_FIELDS = {
    "target_job", "weakness_summary", "required_invariant", "capability_type",
    "project_check_identity", "constraints",
}
MAX_SOURCES = 12
MAX_SHORTLIST = 3
MAX_BODY_BYTES = 64 * 1024
MAX_SOURCE_FILES = 64
MAX_SOURCE_BYTES = 1024 * 1024
MAX_QUERY_BYTES = 4096
MAX_TASKS = 3
MAX_SCORE = 100
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
SECRET_ASSIGNMENT = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*\S+"
)
EXECUTABLE_NAMES = {"setup.py", "install.sh", "postinstall", "preinstall"}
EXECUTABLE_SUFFIXES = {".exe", ".dll", ".so", ".dylib", ".bin"}
RUN_FIELDS = {
    "task_id", "contestant_id", "fixture_digest", "project_revision",
    "project_check_identity", "quality_score_identity", "disposable_workspace",
    "strict", "project_check", "completion", "unauthorized_writes",
    "regression_count", "holdout_pass", "quality_score", "writes", "result_digest",
}


def canonical_digest(payload):
    return natural_selection.canonical_digest(payload)


def _make_id(prefix):
    return f"{prefix}-{hashlib.sha256(os.urandom(32)).hexdigest()[:24]}"


def _store(root, initialize=False):
    store = runtime.Store(root)
    if initialize:
        store.initialize()
    base = store.local / "external-competition"
    return store, base


def _bounded_string(value, field, limit=1024):
    if not isinstance(value, str) or not value.strip() or len(value.encode()) > limit:
        raise ValueError(f"{field} must be one bounded nonempty string")
    if "-----BEGIN" in value or SECRET_ASSIGNMENT.search(value):
        raise ValueError(f"{field} contains structured secret-like material")
    return value.strip()


def _safe_id(value, field):
    value = _bounded_string(value, field, 128)
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"{field} has an invalid identity")
    return value


def _safe_relative(value, field):
    value = _bounded_string(value, field, 512)
    relative = Path(value)
    if relative.is_absolute() or not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError(f"{field} must be one bounded relative path")
    return relative


def _json_text(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_frozen(updates):
    atomic_batch_write(updates)
    for path in updates:
        path.chmod(0o444)


def sanitize_query(root, evaluation, query):
    """Return the only project-safe metadata an adapter may receive."""
    snapshot = natural_selection.validate_evaluation(root, evaluation, TRIGGERS)
    if not isinstance(query, dict) or set(query) - QUERY_FIELDS:
        raise ValueError("external discovery query contains unsupported fields")
    affected = {
        row["capability_id"]: row for row in snapshot["capabilities"]
        if row["capability_id"] in evaluation["affected_capability_ids"]
    }
    if evaluation["result"] == "CREATE_CANDIDATE":
        target_job = evaluation.get("candidate_hint", {}).get("uncovered_job")
        check = query.get("project_check_identity")
    else:
        if len(affected) != 1:
            raise ValueError("external discovery needs one affected current capability")
        current = next(iter(affected.values()))
        target_job = current["job"]
        check = current["project_check_identity"]
    target_job = _bounded_string(target_job, "target_job")
    if query.get("target_job") not in {None, target_job}:
        raise ValueError("external query target job differs from the canonical need")
    if query.get("capability_type", "SKILL") != "SKILL":
        raise ValueError("this phase competes project-local Skills only")
    if check is None:
        raise ValueError("CREATE discovery requires a project check identity")
    check = _bounded_string(check, "project_check_identity", 256)
    if query.get("project_check_identity") not in {None, check}:
        raise ValueError("external query check differs from the canonical need")
    constraints = query.get("constraints", [])
    if not isinstance(constraints, list) or len(constraints) > 8:
        raise ValueError("external query constraints must be a bounded list")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "target_job": target_job,
        "weakness_summary": _bounded_string(query.get("weakness_summary"), "weakness_summary"),
        "required_invariant": _bounded_string(query.get("required_invariant"), "required_invariant"),
        "capability_type": "SKILL",
        "project_check_identity": check,
        "constraints": [_bounded_string(item, "constraint", 256) for item in constraints],
        "source_experience_ids": evaluation["source_experience_ids"],
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    if len(encoded) > MAX_QUERY_BYTES:
        raise ValueError("external discovery query exceeds the product bound")
    payload["query_bytes"] = len(encoded)
    payload["query_digest"] = hashlib.sha256(encoded).hexdigest()
    payload["disclosed_fields"] = sorted(set(payload) - {"query_digest", "query_bytes", "disclosed_fields"})
    return payload


def _source_files(source_root):
    files = []
    total = 0
    for path in sorted(source_root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ValueError("external source may not contain symlinks")
        if not path.is_file():
            continue
        relative = path.relative_to(source_root).as_posix()
        mode = stat.S_IMODE(path.stat().st_mode)
        if mode & 0o111 or path.name.lower() in EXECUTABLE_NAMES or path.suffix.lower() in EXECUTABLE_SUFFIXES:
            raise ValueError(f"external source contains executable or install-hook content: {relative}")
        size = path.stat().st_size
        total += size
        if len(files) >= MAX_SOURCE_FILES or total > MAX_SOURCE_BYTES:
            raise ValueError("external source exceeds bounded inspection limits")
        data = path.read_bytes()
        if len(data) != size:
            raise ValueError("external source changed during bounded inspection")
        if b"\0" in data:
            raise ValueError(f"external source contains binary content: {relative}")
        files.append({"path": relative, "digest": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    if not files:
        raise ValueError("external source contains no inspectable files")
    return files


def _policy(value):
    value = value or {}
    if not isinstance(value, dict) or set(value) - {
        "allowed_licenses", "allowed_permissions", "available_tools", "available_dependencies",
    }:
        raise ValueError("external source policy contains unsupported fields")
    result = {}
    for field, default in (
        ("allowed_licenses", sorted(LICENSE_ALLOWLIST)),
        ("allowed_permissions", []), ("available_tools", []), ("available_dependencies", []),
    ):
        items = value.get(field, default)
        if not isinstance(items, list) or len(items) > 32 or any(not isinstance(item, str) or not item for item in items):
            raise ValueError(f"external policy {field} must be one bounded string list")
        result[field] = sorted(set(items))
    return result


def _read_source(descriptor, policy):
    if not isinstance(descriptor, dict) or descriptor.get("source_type") not in SOURCE_TYPES:
        raise ValueError("unknown external capability source")
    source_id = _safe_id(descriptor.get("source_id"), "source_id")
    revision = _bounded_string(descriptor.get("source_revision"), "source_revision", 256)
    requested_location = Path(_bounded_string(descriptor.get("source_location"), "source_location", 2048))
    if requested_location.is_symlink():
        raise ValueError("external local-directory source is unavailable")
    location = requested_location.resolve()
    if not location.is_dir():
        raise ValueError("external local-directory source is unavailable")
    files = _source_files(location)
    manifest_path = location / "capability.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("external source is missing capability.json")
    try:
        source_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("external capability manifest is malformed") from error
    required = {
        "schema_version", "capability_name", "capability_id", "declared_job",
        "capability_type", "body_path", "license", "required_tools",
        "required_permissions", "dependencies", "activation_trigger",
        "project_check_identity",
    }
    if not isinstance(source_manifest, dict) or source_manifest.get("schema_version") != SCHEMA_VERSION or required - set(source_manifest):
        raise ValueError("external capability manifest is incomplete")
    if source_manifest["capability_type"] != "SKILL":
        raise ValueError("external capability type is unsupported in this phase")
    identity = _safe_id(source_manifest["capability_id"], "capability_id")
    body_relative = _safe_relative(source_manifest["body_path"], "body_path")
    body_path = location / body_relative
    if body_path.is_symlink() or not body_path.is_file() or not body_path.resolve().is_relative_to(location):
        raise ValueError("external candidate body is unavailable")
    body = body_path.read_bytes()
    if not body or len(body) > MAX_BODY_BYTES:
        raise ValueError("external candidate body exceeds the product bound")
    try:
        body_text = body.decode("utf-8")
    except UnicodeError as error:
        raise ValueError("external candidate body must be UTF-8 text") from error
    body_digest = hashlib.sha256(body).hexdigest()
    if source_manifest.get("body_digest") not in {None, body_digest}:
        raise ValueError("external candidate digest mismatch")
    source_digest = canonical_digest(files)
    fetched_digest = canonical_digest({
        "source_type": descriptor["source_type"], "source_id": source_id,
        "source_revision": revision, "source_digest": source_digest,
        "body_digest": body_digest,
    })
    license_id = _bounded_string(source_manifest["license"], "license", 128)
    reuse_mode = source_manifest.get("reuse_mode")
    if reuse_mode not in {None, "reference-only"}:
        raise ValueError("external reuse_mode is unsupported")
    if not isinstance(source_manifest.get("adaptation_required", False), bool):
        raise ValueError("external adaptation_required must be boolean")
    license_path = source_manifest.get("license_path")
    has_license_evidence = False
    license_digest = None
    if license_path:
        resolved = location / _safe_relative(license_path, "license_path")
        if resolved.is_symlink() or not resolved.is_file() or not resolved.resolve().is_relative_to(location):
            raise ValueError("external license evidence is unavailable")
        license_bytes = resolved.read_bytes()
        license_digest = hashlib.sha256(license_bytes).hexdigest()
        has_license_evidence = bool(license_bytes)
    allowed_licenses = set(policy.get("allowed_licenses", LICENSE_ALLOWLIST))
    if reuse_mode == "reference-only":
        license_state = "REFERENCE_ONLY"
    elif not isinstance(license_id, str) or not license_id.strip() or not has_license_evidence:
        license_state = "LICENSE_UNKNOWN"
    elif license_id not in allowed_licenses:
        license_state = "INCOMPATIBLE"
    else:
        license_state = "REUSE_ALLOWED"
    vectors, compatibility_reasons = {}, []
    for field, allowed_field in (
        ("required_permissions", "allowed_permissions"),
        ("required_tools", "available_tools"),
        ("dependencies", "available_dependencies"),
    ):
        values = source_manifest[field]
        if not isinstance(values, list) or len(values) > 16 or any(not isinstance(item, str) for item in values):
            raise ValueError(f"external {field} must be one bounded string list")
        vectors[field] = sorted(set(values))
        unsupported = set(values) - set(policy.get(allowed_field, []))
        if unsupported:
            compatibility_reasons.append(f"UNSUPPORTED_{field.upper()}:" + ",".join(sorted(unsupported)))
    steps = {}
    for field, default in (("setup_steps", 0), ("verification_steps", 1)):
        value = source_manifest.get(field, default)
        if not isinstance(value, int) or not 0 <= value <= 16:
            raise ValueError(f"external {field} must be an integer from 0 to 16")
        steps[field] = value
    candidate_id = "candidate-" + fetched_digest[:24]
    normalized = {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "capability_type": "SKILL",
        "capability_id": identity,
        "capability_name": _bounded_string(source_manifest["capability_name"], "capability_name", 256),
        "target_job": _bounded_string(source_manifest["declared_job"], "declared_job"),
        "activation_trigger": _bounded_string(source_manifest["activation_trigger"], "activation_trigger"),
        "project_check_identity": _bounded_string(source_manifest["project_check_identity"], "project_check_identity", 256),
        "body_digest": body_digest,
        "source_digest": source_digest,
        "fetched_digest": fetched_digest,
        "license": {"declared": license_id, "classification": license_state, "evidence_digest": license_digest},
        "required_tools": vectors["required_tools"],
        "required_permissions": vectors["required_permissions"],
        "dependencies": vectors["dependencies"],
        "adaptation_required": bool(source_manifest.get("adaptation_required", False)),
        "carrying_cost": {
            "context_bytes": len(body),
            "dependencies": len(vectors["dependencies"]),
            "tools": len(vectors["required_tools"]),
            "permissions": len(vectors["required_permissions"]),
            "setup_steps": steps["setup_steps"],
            "verification_steps": steps["verification_steps"],
        },
        "compatibility_reasons": compatibility_reasons,
    }
    normalized["normalized_digest"] = canonical_digest(normalized)
    if _source_files(location) != files:
        raise ValueError("external source changed during acquisition")
    return {
        "source": {
            "source_type": descriptor["source_type"],
            "source_id": source_id,
            "source_location": str(location),
            "source_revision": revision,
            "source_digest": source_digest,
            "fetched_at": runtime.utc_now(),
        },
        "source_manifest": source_manifest,
        "normalized": normalized,
        "body": body_text,
        "files": files,
    }


def _cooldown(root, candidate_id, evaluation_digest):
    decisions = runtime.read_jsonl(runtime.Store(root).decisions)
    for row in reversed(decisions):
        external = row.get("external_competition") or row.get("natural_selection", {}).get("competition", {}).get("external_competition")
        if not isinstance(external, dict):
            continue
        if evaluation_digest == external.get("evaluation_digest") and candidate_id in external.get("rejected_candidate_ids", []):
            return row.get("decision_id")
    return None


def discover(root, evaluation, query, sources, policy=None):
    """Read bounded metadata/body bytes into local quarantine; execute nothing."""
    root = Path(root).resolve()
    query = sanitize_query(root, evaluation, query)
    if not isinstance(sources, list) or not 1 <= len(sources) <= MAX_SOURCES:
        raise ValueError("external discovery requires 1-12 bounded sources")
    policy = _policy(policy)
    maintenance_policy, _ = runtime.harness_policy(root, "control-maintenance-trigger", {
        "minimum_repeat_count": 2, "shortlist_limit": MAX_SHORTLIST,
    })
    shortlist_limit = maintenance_policy["shortlist_limit"]
    _, base = _store(root, initialize=True)
    ranked, quarantined, filtered, seen = [], [], [], set()
    for descriptor in sources:
        try:
            candidate = _read_source(descriptor, policy)
            manifest = candidate["normalized"]
            dedupe_key = (
                candidate["source"]["source_type"], candidate["source"]["source_id"],
                candidate["source"]["source_revision"], manifest["source_digest"],
            )
            if dedupe_key in seen:
                filtered.append({"source_id": candidate["source"]["source_id"], "reason": "DUPLICATE_SOURCE_CANDIDATE"})
                continue
            seen.add(dedupe_key)
            terms = capability_pack.selection_terms(
                manifest["capability_name"], manifest["target_job"], manifest["activation_trigger"],
                manifest["project_check_identity"],
            )
            wanted = capability_pack.selection_terms(
                query["target_job"], query["weakness_summary"], query["required_invariant"],
                query["project_check_identity"], query["constraints"],
            )
            matched = sorted(terms & wanted)
            reasons = []
            if not matched:
                reasons.append("NO_PROJECT_FIT_METADATA")
            if manifest["project_check_identity"] != query["project_check_identity"]:
                reasons.append("PROJECT_CHECK_MISMATCH")
            if manifest["license"]["classification"] != "REUSE_ALLOWED":
                reasons.append(manifest["license"]["classification"])
            reasons.extend(manifest["compatibility_reasons"])
            cooldown = _cooldown(root, manifest["candidate_id"], evaluation["evaluation_digest"])
            if cooldown:
                reasons.append("REJECTED_CANDIDATE_COOLDOWN")
            record = {
                "schema_version": SCHEMA_VERSION,
                "candidate_id": manifest["candidate_id"],
                "quarantine_status": "COMPETITION_ELIGIBLE" if not reasons else "FILTERED",
                "pack_selectable": False,
                "authority": [],
                "source": candidate["source"],
                "source_files": candidate["files"],
                "competition_manifest": manifest,
                "matched_terms": matched,
                "filter_reasons": reasons,
                "evaluation_digest": evaluation["evaluation_digest"],
                "query_digest": query["query_digest"],
            }
            record["record_digest"] = canonical_digest(record)
            target = base / "quarantine" / manifest["candidate_id"]
            manifest_path = target / "manifest.json"
            body_path = target / "body.txt"
            if manifest_path.exists():
                existing = runtime.read_json(manifest_path)
                if (
                    existing.get("candidate_id") != record["candidate_id"]
                    or existing.get("competition_manifest") != record["competition_manifest"]
                    or existing.get("source", {}).get("source_revision") != record["source"]["source_revision"]
                    or hashlib.sha256(body_path.read_bytes()).hexdigest() != manifest["body_digest"]
                ):
                    raise ValueError("frozen quarantine candidate identity changed")
                record = existing
            else:
                _write_frozen({manifest_path: _json_text(record), body_path: candidate["body"]})
            quarantined.append(manifest["candidate_id"])
            if reasons:
                filtered.append({"candidate_id": manifest["candidate_id"], "reasons": reasons})
            else:
                ranked.append((len(matched), manifest["candidate_id"], manifest))
        except (OSError, UnicodeError, ValueError) as error:
            filtered.append({"source_id": descriptor.get("source_id") if isinstance(descriptor, dict) else None, "reason": str(error)})
    ranked.sort(key=lambda item: (-item[0], item[1]))
    shortlist = [manifest for _, _, manifest in ranked[:shortlist_limit]]
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "discovery_id": _make_id("discovery"),
        "evaluation_digest": evaluation["evaluation_digest"],
        "query": query,
        "source_adapter": "LOCAL_DIRECTORY",
        "source_count": len(sources),
        "quarantined_candidate_ids": quarantined,
        "shortlist_candidate_ids": [row["candidate_id"] for row in shortlist],
        "shortlist": shortlist,
        "filtered": filtered,
        "external_execution": False,
        "created_at": runtime.utc_now(),
    }
    receipt["receipt_digest"] = canonical_digest(receipt)
    path = base / "discoveries" / f"{receipt['discovery_id']}.json"
    _write_frozen({path: _json_text(receipt)})
    return receipt


def register_local_candidate(root, evaluation, specification, body, parent_candidate_id=None, adaptation_diagnosis=None):
    """Freeze one project-local Challenger; optional parent bytes remain quarantined."""
    natural_selection.validate_evaluation(root, evaluation, TRIGGERS)
    frozen = natural_selection.freeze_candidate(specification, body)
    _, base = _store(root, initialize=True)
    parent = _load_candidate(root, parent_candidate_id) if parent_candidate_id else None
    if parent and not _bounded_string(adaptation_diagnosis, "adaptation_diagnosis"):
        raise ValueError("derived local Challenger requires one adaptation diagnosis")
    candidate_id = "candidate-" + canonical_digest({
        "origin": "DERIVED_LOCAL" if parent else "PROJECT_LOCAL",
        "candidate_digest": frozen["candidate_digest"],
        "parent": parent_candidate_id,
        "evaluation_digest": evaluation["evaluation_digest"],
    })[:24]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "origin": "DERIVED_LOCAL" if parent else "PROJECT_LOCAL",
        "evaluation_digest": evaluation["evaluation_digest"],
        "natural_selection_candidate": frozen,
        "body_digest": frozen["body_digest"],
        "parent_candidate_id": parent_candidate_id,
        "parent_source_digest": parent["manifest"]["competition_manifest"].get("source_digest") if parent else None,
        "adaptation_diagnosis": adaptation_diagnosis,
        "pack_selectable": False,
        "authority": [],
        "carrying_cost": {
            "context_bytes": len(body.encode()), "dependencies": 0, "tools": 0,
            "permissions": 0, "setup_steps": 0, "verification_steps": 1,
        },
    }
    manifest["normalized_digest"] = canonical_digest(manifest)
    manifest["manifest_digest"] = canonical_digest(manifest)
    target = base / "local" / candidate_id
    manifest_path, body_path = target / "manifest.json", target / "body.txt"
    if manifest_path.exists():
        if runtime.read_json(manifest_path) != manifest or body_path.read_text(encoding="utf-8") != body:
            raise ValueError("frozen project-local Challenger identity changed")
    else:
        _write_frozen({manifest_path: _json_text(manifest), body_path: body})
    return manifest


def _load_candidate(root, candidate_id):
    _safe_id(candidate_id, "candidate_id")
    _, base = _store(root)
    for origin, relative in (("EXTERNAL", "quarantine"), ("LOCAL", "local")):
        directory = base / relative / candidate_id
        manifest_path, body_path = directory / "manifest.json", directory / "body.txt"
        if not manifest_path.exists():
            continue
        manifest = runtime.read_json(manifest_path)
        digest_field = "record_digest" if origin == "EXTERNAL" else "manifest_digest"
        if manifest.get(digest_field) != canonical_digest({key: value for key, value in manifest.items() if key != digest_field}):
            raise ValueError("frozen candidate manifest digest is invalid")
        body = body_path.read_text(encoding="utf-8")
        digest = hashlib.sha256(body.encode()).hexdigest()
        expected = manifest.get("competition_manifest", {}).get("body_digest") if origin == "EXTERNAL" else manifest.get("body_digest")
        if digest != expected:
            raise ValueError("frozen candidate body digest is invalid")
        return {"origin": origin, "manifest": manifest, "body": body}
    raise ValueError("unknown frozen competition candidate")


def _candidate_summary(candidate):
    manifest = candidate["manifest"]
    if candidate["origin"] == "EXTERNAL":
        if manifest.get("quarantine_status") != "COMPETITION_ELIGIBLE":
            raise ValueError("filtered external candidate may not enter competition")
        normalized = manifest["competition_manifest"]
        return {
            "candidate_id": normalized["candidate_id"], "contestant_id": normalized["candidate_id"], "origin": "EXTERNAL",
            "capability_id": normalized["capability_id"], "body_digest": normalized["body_digest"],
            "candidate_digest": normalized["normalized_digest"], "carrying_cost": normalized["carrying_cost"],
            "source": {
                "source_type": manifest["source"]["source_type"], "source_id": manifest["source"]["source_id"],
                "source_revision": manifest["source"]["source_revision"], "source_digest": normalized["source_digest"],
            },
            "license": normalized["license"], "adaptation_required": normalized["adaptation_required"],
        }
    frozen = manifest["natural_selection_candidate"]
    return {
        "candidate_id": manifest["candidate_id"], "contestant_id": manifest["candidate_id"], "origin": manifest["origin"],
        "capability_id": frozen["record"]["capability_id"], "body_digest": frozen["body_digest"],
        "candidate_digest": frozen["candidate_digest"], "carrying_cost": manifest["carrying_cost"],
        "source": {"parent_candidate_id": manifest.get("parent_candidate_id"), "parent_source_digest": manifest.get("parent_source_digest")},
        "license": {"classification": "PROJECT_LOCAL"}, "adaptation_required": False,
    }


def _champion_cost(root, evaluation, snapshot):
    rows = [row for row in snapshot["capabilities"] if row["capability_id"] in evaluation["affected_capability_ids"]]
    return {
        "context_bytes": sum(natural_selection.body_path(root, row["capability_id"]).stat().st_size for row in rows),
        "dependencies": 0, "tools": 0, "permissions": 0, "setup_steps": 0,
        "verification_steps": len(rows) or 1,
    }


def freeze_competition(root, evaluation, candidate_ids, tasks):
    snapshot = natural_selection.validate_evaluation(root, evaluation, TRIGGERS)
    maintenance_policy, _ = runtime.harness_policy(root, "control-maintenance-trigger", {
        "minimum_repeat_count": 2, "shortlist_limit": MAX_SHORTLIST,
    })
    if not isinstance(candidate_ids, list) or not 1 <= len(candidate_ids) <= maintenance_policy["shortlist_limit"] or len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("competition requires 1-3 unique Challengers")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= MAX_TASKS:
        raise ValueError("competition requires 1-3 frozen task groups")
    candidates = []
    for identity in candidate_ids:
        candidate = _load_candidate(root, identity)
        if candidate["manifest"].get("evaluation_digest") != evaluation["evaluation_digest"]:
            raise ValueError("competition candidate belongs to a different lifecycle need")
        candidates.append(_candidate_summary(candidate))
    kinds, revisions = set(), set()
    normalized_tasks = []
    for task in tasks:
        if not isinstance(task, dict) or task.get("kind") not in TASK_KINDS:
            raise ValueError("invalid competition task kind")
        task_id = _safe_id(task.get("task_id"), "competition task_id")
        fixture_digest = _bounded_string(task.get("fixture_digest"), "fixture_digest", 128)
        if not re.fullmatch(r"[a-f0-9]{64}", fixture_digest):
            raise ValueError("competition fixture digest must be SHA-256")
        check = _bounded_string(task.get("project_check_identity"), "project_check_identity", 256)
        quality_identity = _bounded_string(task.get("quality_score_identity"), "quality_score_identity", 256)
        revision = _bounded_string(task.get("project_revision"), "project_revision", 256)
        writes = task.get("allowed_writes", [])
        if not isinstance(writes, list) or len(writes) > 32:
            raise ValueError("competition allowed writes must be bounded")
        for value in writes:
            _safe_relative(value, "allowed_write")
        if task["kind"] == "SEALED_HOLDOUT" and task.get("sealed_after_candidate_freeze") is not True:
            raise ValueError("sealed holdout must be created after candidate freeze")
        kinds.add(task["kind"])
        revisions.add(revision)
        normalized_tasks.append({
            "task_id": task_id, "kind": task["kind"], "fixture_digest": fixture_digest,
            "project_revision": revision, "project_check_identity": check,
            "quality_score_identity": quality_identity,
            "allowed_writes": writes, "workspace": "DISPOSABLE",
            "sealed_after_candidate_freeze": task.get("sealed_after_candidate_freeze", False),
        })
    if "SEALED_HOLDOUT" not in kinds or len(revisions) != 1:
        raise ValueError("competition requires one sealed holdout on one frozen project revision")
    contestants = [{
        "contestant_id": "ECOSYSTEM_CHAMPION", "origin": "CHAMPION",
        "ecosystem_digest": snapshot["ecosystem_digest"], "carrying_cost": _champion_cost(root, evaluation, snapshot),
    }] + candidates
    payload = {
        "schema_version": SCHEMA_VERSION,
        "competition_id": _make_id("competition"),
        "evaluation_digest": evaluation["evaluation_digest"],
        "ecosystem_champion_digest": snapshot["ecosystem_digest"],
        "source_experience_ids": evaluation["source_experience_ids"],
        "lifecycle_need": evaluation["result"],
        "affected_capability_ids": evaluation["affected_capability_ids"],
        "contestants": contestants,
        "tasks": normalized_tasks,
        "criteria": ["STRICT_PRODUCT_OUTCOME", "PROJECT_CHECK", "COMPLETION", "UNAUTHORIZED_WRITES", "REGRESSION_COUNT", "CARRYING_COST_TIE_BREAK"],
        "created_at": runtime.utc_now(),
    }
    payload["competition_digest"] = canonical_digest(payload)
    _, base = _store(root, initialize=True)
    _write_frozen({base / "competitions" / f"{payload['competition_id']}.json": _json_text(payload)})
    return payload


def _load_competition(root, competition_id):
    _safe_id(competition_id, "competition_id")
    _, base = _store(root)
    payload = runtime.read_json(base / "competitions" / f"{competition_id}.json")
    if not payload or payload.get("competition_id") != competition_id:
        raise ValueError("unknown frozen competition")
    digest = payload.get("competition_digest")
    if digest != canonical_digest({key: value for key, value in payload.items() if key != "competition_digest"}):
        raise ValueError("frozen competition digest is invalid")
    return payload


def _dominates(left, right):
    keys = {"context_bytes", "dependencies", "tools", "permissions", "setup_steps", "verification_steps"}
    return all(left[key] <= right[key] for key in keys) and any(left[key] < right[key] for key in keys)


def decide(root, competition_id, results):
    competition = _load_competition(root, competition_id)
    if (
        not isinstance(results, dict) or set(results) != {"competition_id", "runs"}
        or results.get("competition_id") != competition_id or not isinstance(results.get("runs"), list)
    ):
        raise ValueError("competition results do not match the frozen competition")
    tasks = {row["task_id"]: row for row in competition["tasks"]}
    contestants = {row["contestant_id"]: row for row in competition["contestants"]}
    runs = {}
    for row in results["runs"]:
        if not isinstance(row, dict) or set(row) != RUN_FIELDS:
            raise ValueError("competition run contains unsupported evidence fields")
        key = (row.get("task_id"), row.get("contestant_id"))
        if key in runs or key[0] not in tasks or key[1] not in contestants:
            raise ValueError("competition run has unknown or duplicate identity")
        task = tasks[key[0]]
        if (
            row.get("fixture_digest") != task["fixture_digest"]
            or row.get("project_revision") != task["project_revision"]
            or row.get("project_check_identity") != task["project_check_identity"]
            or row.get("quality_score_identity") != task["quality_score_identity"]
            or row.get("disposable_workspace") is not True
        ):
            raise ValueError("competition run differs from frozen conditions")
        if not isinstance(row.get("writes", []), list) or not set(row.get("writes", [])) <= set(task["allowed_writes"]):
            raise ValueError("competition run exceeded its allowed write set")
        score = row.get("quality_score")
        if not isinstance(score, int) or not 0 <= score <= MAX_SCORE:
            raise ValueError("competition quality score must be an integer from 0 to 100")
        if not re.fullmatch(r"[a-f0-9]{64}", str(row.get("result_digest", ""))):
            raise ValueError("competition run requires one frozen result digest")
        runs[key] = row
    expected = {(task, contestant) for task in tasks for contestant in contestants}
    if set(runs) != expected:
        raise ValueError("competition results are incomplete")
    eligible, summaries = [], {}
    for contestant_id, contestant in contestants.items():
        rows = [runs[(task_id, contestant_id)] for task_id in tasks]
        passed = all(
            row.get("strict") is True and row.get("project_check") is True
            and row.get("completion") is True and row.get("unauthorized_writes") == 0
            and row.get("regression_count") == 0
            for row in rows
        ) and all(
            runs[(task_id, contestant_id)].get("holdout_pass") is True
            for task_id, task in tasks.items() if task["kind"] == "SEALED_HOLDOUT"
        )
        summary = {
            "contestant_id": contestant_id, "eligible": passed,
            "quality_score": sum(row["quality_score"] for row in rows),
            "carrying_cost": contestant["carrying_cost"],
        }
        summaries[contestant_id] = summary
        if passed:
            eligible.append(summary)
    winner, reason = None, "no contestant passed every primary condition"
    if eligible:
        best_score = max(row["quality_score"] for row in eligible)
        leaders = [row for row in eligible if row["quality_score"] == best_score]
        if len(leaders) == 1:
            winner, reason = leaders[0], "highest verified quality"
        else:
            dominators = [row for row in leaders if all(row is other or _dominates(row["carrying_cost"], other["carrying_cost"]) for other in leaders)]
            if len(dominators) == 1:
                winner, reason = dominators[0], "equivalent quality with strictly lower carrying cost"
            elif any(row["contestant_id"] == "ECOSYSTEM_CHAMPION" for row in leaders):
                winner = next(row for row in leaders if row["contestant_id"] == "ECOSYSTEM_CHAMPION")
                reason = "equivalent quality has no unique lower-cost Challenger"
    decision = "NO_SURVIVOR"
    if winner:
        if winner["contestant_id"] == "ECOSYSTEM_CHAMPION":
            decision = "KEEP_CURRENT"
        else:
            candidate = next(row for row in competition["contestants"] if row["contestant_id"] == winner["contestant_id"])
            if candidate["origin"] in {"PROJECT_LOCAL", "DERIVED_LOCAL"}:
                decision = "UPGRADE_LOCAL"
            elif candidate["adaptation_required"] or candidate["license"]["classification"] != "REUSE_ALLOWED":
                decision = "ADAPT_EXTERNAL_AND_RETEST"
            elif competition["lifecycle_need"] == "CREATE_CANDIDATE":
                decision = "CREATE_FROM_EXTERNAL"
            elif (
                competition["lifecycle_need"] == "UPGRADE_CANDIDATE"
                and candidate["capability_id"] in competition["affected_capability_ids"]
            ):
                decision = "ADAPT_EXTERNAL_AND_RETEST"
            else:
                decision = "REPLACE_WITH_EXTERNAL"
    elif eligible:
        decision, reason = "MORE_EVIDENCE_REQUIRED", "quality/cost tie has no unique survivor"
    if decision not in SURVIVORS:
        raise ValueError("invalid external competition survivor decision")
    rejected = sorted(set(contestants) - {winner["contestant_id"] if winner else None, "ECOSYSTEM_CHAMPION"})
    payload = {
        "schema_version": SCHEMA_VERSION,
        "outcome_id": _make_id("competition-outcome"),
        "competition_id": competition_id,
        "competition_digest": competition["competition_digest"],
        "evaluation_digest": competition["evaluation_digest"],
        "source_experience_ids": competition["source_experience_ids"],
        "decision": decision,
        "winner_id": winner["contestant_id"] if winner else None,
        "reason": reason,
        "summaries": summaries,
        "result_receipts": results["runs"],
        "results_digest": canonical_digest(results),
        "rejected_candidate_ids": rejected,
        "created_at": runtime.utc_now(),
    }
    payload["outcome_digest"] = canonical_digest(payload)
    _, base = _store(root, initialize=True)
    _write_frozen({base / "outcomes" / f"{payload['outcome_id']}.json": _json_text(payload)})
    return payload


def _load_outcome(root, outcome_id):
    _safe_id(outcome_id, "outcome_id")
    _, base = _store(root)
    payload = runtime.read_json(base / "outcomes" / f"{outcome_id}.json")
    if not payload or payload.get("outcome_id") != outcome_id:
        raise ValueError("unknown competition outcome")
    digest = payload.get("outcome_digest")
    if digest != canonical_digest({key: value for key, value in payload.items() if key != "outcome_digest"}):
        raise ValueError("competition outcome digest is invalid")
    return payload


def record_outcome(root, outcome_id, replace=os.replace):
    """Record a non-adoption decision in existing Foundation Memory."""
    outcome = _load_outcome(root, outcome_id)
    if outcome["decision"] in {"UPGRADE_LOCAL", "REPLACE_WITH_EXTERNAL", "CREATE_FROM_EXTERNAL"}:
        raise ValueError("a winning lifecycle mutation must use the adoption transaction")
    natural_selection._source_experiences(root, outcome["source_experience_ids"])
    store, _ = _store(root, initialize=True)
    active = runtime.read_json(store.active)
    task = next((row for row in (active or {}).get("tasks", []) if row.get("status") == "ACTIVE"), None)
    if not active or not task:
        raise ValueError("competition decision requires one active Foundation Task")
    decision_id = runtime.make_id("decision")
    source_refs = [f"experience:{identity}" for identity in outcome["source_experience_ids"]]
    competition = _load_competition(root, outcome["competition_id"])
    challengers = [row for row in competition["contestants"] if row["contestant_id"] != "ECOSYSTEM_CHAMPION"]
    extension = {
        "competition_id": outcome["competition_id"], "outcome_id": outcome_id,
        "evaluation_digest": outcome["evaluation_digest"], "decision": outcome["decision"],
        "winner_id": outcome["winner_id"], "rejected_candidate_ids": outcome["rejected_candidate_ids"],
        "competition_digest": outcome["competition_digest"],
        "candidate_provenance": challengers,
        "results_digest": outcome["results_digest"],
        "reconsideration": "new source revision or materially new verified Experience",
    }
    row = {
        "schema_version": runtime.SCHEMA_VERSION,
        "decision_id": decision_id,
        "decision": f"External capability competition: {outcome['decision']}",
        "why": outcome["reason"],
        "session_id": active["session_id"], "task_id": task["task_id"],
        "derived_from": source_refs, "evidence": outcome["source_experience_ids"],
        "source_refs": source_refs, "created_at": runtime.utc_now(), "status": "ACTIVE",
        "supersedes": None, "superseded_by": None,
        "project_revision": active.get("project_revision", "unknown"),
        "host_fingerprint": active.get("host_fingerprint", {}).get("fingerprint_id"),
        "nulnul_revision": active.get("nulnul_revision"), "scope": "external-capability-competition",
        "external_competition": extension,
    }
    decisions = runtime.read_jsonl(store.decisions) + [row]
    index = runtime.load_index(store)
    runtime._add_search(index, "decision", row)
    index["updated_at"] = runtime.utc_now()
    active = dict(active)
    active.setdefault("decision_ids", []).append(decision_id)
    updates = {
        store.decisions: "".join(json.dumps(runtime.redact(item), ensure_ascii=False, sort_keys=True) + "\n" for item in decisions),
        store.index: runtime.encoded(runtime.redact(index)),
        store.active: runtime.encoded(runtime.redact(active)),
    }
    with runtime.writer(store):
        atomic_batch_write(updates, replace=replace)
    return {"status": "RECORDED", "decision_id": decision_id, "outcome_id": outcome_id}


def _natural_competition(root, competition, outcome):
    champion = outcome["summaries"]["ECOSYSTEM_CHAMPION"]
    challenger = outcome["summaries"][outcome["winner_id"]]
    primary = "IMPROVED" if challenger["quality_score"] > champion["quality_score"] else "EQUIVALENT"
    winner = next(row for row in competition["contestants"] if row["contestant_id"] == outcome["winner_id"])
    return {
        "champion": {"strict": True, "project_check": True, "completion": True, "unauthorized_writes": 0},
        "challenger": {"strict": True, "project_check": True, "completion": True, "unauthorized_writes": 0},
        "regressions": 0, "holdout_pass": True, "primary_outcome": primary,
        "secondary_advantage": "lower carrying cost" if primary == "EQUIVALENT" else "",
        "external_competition": {
            "competition_id": competition["competition_id"], "competition_digest": competition["competition_digest"],
            "outcome_id": outcome["outcome_id"], "outcome_digest": outcome["outcome_digest"],
            "evaluation_digest": outcome["evaluation_digest"], "winner_id": outcome["winner_id"],
            "rejected_candidate_ids": outcome["rejected_candidate_ids"],
            "winner_provenance": winner,
            "results_digest": outcome["results_digest"],
        },
    }


def adopt(root, outcome_id, evaluation, replace=os.replace):
    """Delegate a verified external/local survivor to Natural Selection's transaction."""
    root = Path(root).resolve()
    outcome = _load_outcome(root, outcome_id)
    if outcome["evaluation_digest"] != evaluation.get("evaluation_digest"):
        raise ValueError("adoption evaluation differs from competition need")
    if outcome["decision"] not in {"UPGRADE_LOCAL", "REPLACE_WITH_EXTERNAL", "CREATE_FROM_EXTERNAL"}:
        raise ValueError("competition outcome has no adoptable survivor")
    competition = _load_competition(root, outcome["competition_id"])
    candidate = _load_candidate(root, outcome["winner_id"])
    summary = _candidate_summary(candidate)
    if candidate["origin"] == "EXTERNAL":
        normalized = candidate["manifest"]["competition_manifest"]
        if normalized["license"]["classification"] != "REUSE_ALLOWED" or normalized["adaptation_required"]:
            raise ValueError("external survivor requires licensed adaptation and retest")
        specification = {
            "capability_type": "SKILL", "capability_id": normalized["capability_id"],
            "job": normalized["target_job"], "activation_trigger": normalized["activation_trigger"],
            "project_check_identity": normalized["project_check_identity"],
        }
    else:
        specification = candidate["manifest"]["natural_selection_candidate"]["record"] | {"capability_type": "SKILL"}
    frozen = natural_selection.freeze_candidate(specification, candidate["body"])
    applied_evaluation = evaluation
    affected = evaluation["affected_capability_ids"]
    candidate_id = frozen["record"]["capability_id"]
    if evaluation["result"] == "UPGRADE_CANDIDATE" and candidate_id != affected[0]:
        applied_evaluation = natural_selection.evaluate(root, {
            "signal": "replacement-advantage", "affected_capability_ids": affected,
            "source_experience_ids": evaluation["source_experience_ids"],
            "replacement_capability_id": candidate_id,
            "diagnosis": evaluation["diagnosis"], "what_must_not_change": evaluation["what_must_not_change"],
            "risk_analysis": evaluation["risk_analysis"], "rollback_plan": evaluation["rollback_plan"],
        })
    natural = _natural_competition(root, competition, outcome)
    result = natural_selection.transact(
        root, applied_evaluation, natural, frozen, candidate["body"], replace=replace,
    )
    result["external_competition"] = {
        "outcome_id": outcome_id, "winner_id": outcome["winner_id"],
        "source": summary["source"], "candidate_digest": summary["candidate_digest"],
    }
    return result


def validate_state(root):
    root = Path(root).resolve()
    errors = list(natural_selection.validate_ecosystem(root))
    _, base = _store(root)
    known_candidates = set()
    for manifest_path in sorted(base.glob("quarantine/*/manifest.json")):
        try:
            record = runtime.read_json(manifest_path)
            candidate_id = manifest_path.parent.name
            known_candidates.add(candidate_id)
            if record.get("candidate_id") != candidate_id or record.get("pack_selectable") is not False or record.get("authority") != []:
                raise ValueError("quarantine authority invariant failed")
            if record.get("record_digest") != canonical_digest({key: value for key, value in record.items() if key != "record_digest"}):
                raise ValueError("quarantine record digest mismatch")
            body = (manifest_path.parent / "body.txt").read_bytes()
            if hashlib.sha256(body).hexdigest() != record.get("competition_manifest", {}).get("body_digest"):
                raise ValueError("quarantine body digest mismatch")
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(f"{manifest_path}: {error}")
    for manifest_path in sorted(base.glob("local/*/manifest.json")):
        try:
            record = runtime.read_json(manifest_path)
            known_candidates.add(manifest_path.parent.name)
            if record.get("manifest_digest") != canonical_digest({key: value for key, value in record.items() if key != "manifest_digest"}):
                raise ValueError("local Challenger manifest digest mismatch")
            body = (manifest_path.parent / "body.txt").read_bytes()
            if hashlib.sha256(body).hexdigest() != record.get("body_digest") or record.get("pack_selectable") is not False:
                raise ValueError("local Challenger identity invariant failed")
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(f"{manifest_path}: {error}")
    for kind, identity_field, digest_field in (
        ("competitions", "competition_id", "competition_digest"),
        ("outcomes", "outcome_id", "outcome_digest"),
        ("discoveries", "discovery_id", "receipt_digest"),
    ):
        for path in sorted((base / kind).glob("*.json")):
            try:
                payload = runtime.read_json(path)
                if payload.get(identity_field) != path.stem:
                    raise ValueError(f"{kind} identity mismatch")
                expected = payload.get(digest_field)
                if expected != canonical_digest({key: value for key, value in payload.items() if key != digest_field}):
                    raise ValueError(f"{kind} digest mismatch")
            except (OSError, UnicodeError, ValueError) as error:
                errors.append(f"{path}: {error}")
    for row in runtime.read_jsonl(runtime.Store(root).decisions):
        external = row.get("external_competition") or row.get("natural_selection", {}).get("competition", {}).get("external_competition")
        if not isinstance(external, dict):
            continue
        competition_id = external.get("competition_id")
        outcome_id = external.get("outcome_id")
        if not competition_id or not (base / "competitions" / f"{competition_id}.json").is_file():
            errors.append(f"{row.get('decision_id')}: dangling external competition")
        if not outcome_id or not (base / "outcomes" / f"{outcome_id}.json").is_file():
            errors.append(f"{row.get('decision_id')}: dangling external outcome")
        referenced = set(external.get("rejected_candidate_ids", []))
        winner = external.get("winner_id")
        if winner and winner != "ECOSYSTEM_CHAMPION":
            referenced.add(winner)
        if not referenced <= known_candidates:
            errors.append(f"{row.get('decision_id')}: dangling external candidate")
    return sorted(set(errors))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    sub = parser.add_subparsers(dest="command", required=True)
    discovery = sub.add_parser("discover")
    discovery.add_argument("evaluation", type=Path)
    discovery.add_argument("query", type=Path)
    discovery.add_argument("sources", type=Path)
    discovery.add_argument("--policy", type=Path)
    local = sub.add_parser("local-candidate")
    local.add_argument("evaluation", type=Path)
    local.add_argument("specification", type=Path)
    local.add_argument("body", type=Path)
    local.add_argument("--parent")
    local.add_argument("--diagnosis")
    freeze = sub.add_parser("freeze")
    freeze.add_argument("evaluation", type=Path)
    freeze.add_argument("candidates", type=Path)
    freeze.add_argument("tasks", type=Path)
    decision = sub.add_parser("decide")
    decision.add_argument("competition_id")
    decision.add_argument("results", type=Path)
    record = sub.add_parser("record")
    record.add_argument("outcome_id")
    adoption = sub.add_parser("adopt")
    adoption.add_argument("outcome_id")
    adoption.add_argument("evaluation", type=Path)
    sub.add_parser("validate")
    args = parser.parse_args()
    try:
        if args.command == "discover":
            payload = discover(
                args.root, runtime.read_json(args.evaluation), runtime.read_json(args.query),
                runtime.read_json(args.sources), runtime.read_json(args.policy) if args.policy else None,
            )
        elif args.command == "local-candidate":
            payload = register_local_candidate(
                args.root, runtime.read_json(args.evaluation), runtime.read_json(args.specification),
                args.body.read_text(encoding="utf-8"), args.parent, args.diagnosis,
            )
        elif args.command == "freeze":
            payload = freeze_competition(
                args.root, runtime.read_json(args.evaluation), runtime.read_json(args.candidates), runtime.read_json(args.tasks),
            )
        elif args.command == "decide":
            payload = decide(args.root, args.competition_id, runtime.read_json(args.results))
        elif args.command == "record":
            payload = record_outcome(args.root, args.outcome_id)
        elif args.command == "adopt":
            payload = adopt(args.root, args.outcome_id, runtime.read_json(args.evaluation))
        else:
            errors = validate_state(args.root)
            payload = {"valid": not errors, "errors": errors}
        failed = payload.get("valid") is False
    except (OSError, UnicodeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        payload, failed = {"status": "failed", "error": str(error)}, True
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
