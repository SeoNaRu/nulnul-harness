#!/usr/bin/env python3
"""Three-arm Champion evidence collection for Experiment 16."""

import argparse
import datetime as dt
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTOCOL = HERE / "protocol.json"
CHAMPION_FREEZE = HERE / "champion-freeze.json"
PREREGISTRATION = HERE / "preregistration.md"
PRIOR_RUNNER = ROOT / "evals/final-pack-foundation-repair-live-proof/run.py"
FOUNDATION_FREEZE = ROOT / "evals/final-pack-foundation-repair-live-proof/foundation-freeze.json"

spec = importlib.util.spec_from_file_location("e16_prior_runner", PRIOR_RUNNER)
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)
base = proof.base


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, value):
    base.atomic_json(path, value)


def copy_tree(source, destination, *, overwrite=False):
    for item in sorted(Path(source).rglob("*")):
        if not item.is_file():
            continue
        target = Path(destination) / item.relative_to(source)
        if target.exists() and not overwrite:
            raise ValueError(f"fixture collision: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def verify_protocol(protocol):
    if len(protocol["arms"]) != 3 or len({row["arm_id"] for row in protocol["arms"]}) != 3:
        raise ValueError("Experiment 16 must contain exactly three fresh Champion arms")
    if protocol["retries"] != 0 or protocol["max_candidates"] != 1 or protocol["max_generations"] != 1:
        raise ValueError("bounded evolution budget changed")
    expected = {
        "base_fixture": base.util.scientific_tree_sha256(ROOT / protocol["base_fixture"]["path"]),
        "current_state_overlay": base.util.scientific_tree_sha256(ROOT / protocol["current_state_overlay"]["path"]),
    }
    for key, actual in expected.items():
        if actual != protocol[key]["sha256"]:
            raise ValueError(f"{key} changed after freeze")
    tasks = {}
    for name, task in protocol["tasks"].items():
        task_sha = base.digest(task["prompt"])
        overlay_sha = base.util.scientific_tree_sha256(ROOT / task["overlay"])
        if task_sha != task["task_sha256"] or overlay_sha != task["overlay_sha256"]:
            raise ValueError(f"fresh task changed after freeze: {name}")
        tasks[name] = {"task_sha256": task_sha, "overlay_sha256": overlay_sha}
    return tasks


def verify_prior_evidence(prior, freeze):
    manifest = prior / "manifest.json"
    receipt = prior / "manifest.receipt"
    if base.sha(manifest) != freeze["prior_evidence_manifest_sha256"]:
        raise ValueError("prior Foundation evidence manifest mismatch")
    if receipt.read_text(encoding="utf-8").strip() != base.sha(manifest):
        raise ValueError("prior Foundation evidence receipt mismatch")
    entries = load(manifest)
    prefix = "arms/FINAL-NEXT-SESSION-FOUNDATION/foundation-state/"
    checked = 0
    for relative, expected in entries.items():
        if not relative.startswith(prefix):
            continue
        target = prior / relative
        if not target.is_file() or base.sha(target) != expected:
            raise ValueError(f"prior Foundation state mismatch: {relative}")
        checked += 1
    experience = prior / (
        prefix + "memory/experiences/" + freeze["required_initial_experience_id"] + ".json"
    )
    if base.sha(experience) != freeze["required_initial_experience_sha256"]:
        raise ValueError("required initial Experience mismatch")
    return {"manifest_sha256": base.sha(manifest), "state_files_verified": checked}


def prepare_workspace(runtime, foundation, prior, protocol):
    workspace = runtime / "workspace"
    base_fixture = ROOT / protocol["base_fixture"]["path"]
    base.util.prepare_workspace(base_fixture, foundation, "foundation", workspace, sync_entry=True)
    copy_tree(ROOT / protocol["current_state_overlay"]["path"], workspace, overwrite=True)
    prior_state = prior / "arms/FINAL-NEXT-SESSION-FOUNDATION/foundation-state"
    memory = workspace / "docs/nulnul/memory"
    if memory.exists():
        shutil.rmtree(memory)
    shutil.copytree(prior_state / "memory", memory)
    local = workspace / "docs/nulnul/.runtime"
    local.mkdir(parents=True, exist_ok=True)
    for name in ("events", "capability-packs", "work-starts", "pack-checks"):
        shutil.copytree(prior_state / name, local / name)
    base.util.git(workspace, "init", "-q")
    base.util.git(workspace, "config", "user.email", "experiment16@example.invalid")
    base.util.git(workspace, "config", "user.name", "NULNUL Experiment 16")
    exclude = workspace / ".git/info/exclude"
    with exclude.open("a", encoding="utf-8") as handle:
        handle.write("\n**/__pycache__/\n*.pyc\n**/.pytest_cache/\ndocs/nulnul/.runtime/\n")
    base.util.git(workspace, "add", "-A")
    base.util.git(workspace, "commit", "-qm", "freeze E16 Champion and prior Foundation state")
    initial = base.util.check_result("python3 -m unittest -q && python3 tools/verify_error_catalog.py", workspace)
    if initial["result"] != "pass":
        raise ValueError("recovered Champion project state does not pass its canonical check")
    return workspace


def capability_record(workspace):
    result = base.run([
        "python3", ".agents/skills/nulnul-harness/scripts/capability_contract.py",
        "get", "docs/nulnul/project.md", "--id", "project-api-validation",
    ], workspace)
    payload = base.parse_payload(result.stdout)
    if result.returncode or not isinstance(payload, dict) or not isinstance(payload.get("capability"), dict):
        raise ValueError("canonical capability lookup failed")
    return payload["capability"]


def evolution_query(workspace, *, job=None):
    arguments = ["evolution-query", "--capability", "project-api-validation", "--limit", "20"]
    if job:
        arguments.extend(["--job", job])
    return base.runtime_call(workspace, *arguments)


def selection_preflight(foundation, workspace, protocol):
    script = foundation / "skills/nulnul-harness/scripts/capability_pack.py"
    sys.path.insert(0, str(script.parent))
    module_spec = importlib.util.spec_from_file_location("e16_pack_selection", script)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    rows = {}
    for name, task in protocol["tasks"].items():
        candidates = module.candidates(workspace / "docs/nulnul/project.md", {
            "goal": task["prompt"], "job": task["job"], "tags": [], "modules": [],
            "context_pack": {"items": []},
        })
        if not candidates or candidates[0]["capability_id"] != "project-api-validation" or candidates[0]["score"] < 2:
            raise ValueError(f"{name} is not a strong bounded Skill-A task")
        if len(candidates) > 3:
            raise ValueError(f"{name} exceeds the bounded candidate set")
        rows[name] = candidates
    return rows


def preflight(runtime, foundation, prior):
    protocol = load(PROTOCOL)
    freeze = load(CHAMPION_FREEZE)
    if runtime.exists() and any(runtime.iterdir()):
        raise ValueError("runtime root must be fresh and empty")
    runtime.mkdir(parents=True, exist_ok=True)
    evidence = runtime / "evidence"
    evidence.mkdir()
    task_freeze = verify_protocol(protocol)
    frozen_at = dt.datetime.fromisoformat(freeze["frozen_at"].replace("Z", "+00:00")).timestamp()
    fresh_task_files = [
        path
        for task in protocol["tasks"].values()
        for path in (ROOT / task["overlay"]).rglob("*")
        if path.is_file()
    ]
    if not fresh_task_files or any(path.stat().st_mtime <= frozen_at for path in fresh_task_files):
        raise ValueError("fresh tasks were not created after the Champion freeze")
    product = base.verify_product(foundation, protocol, load(FOUNDATION_FREEZE))
    prior_verification = verify_prior_evidence(prior, freeze)
    workspace = prepare_workspace(runtime, foundation, prior, protocol)
    champion = capability_record(workspace)
    body = workspace / ".agents/skills/project-api-validation/SKILL.md"
    if base.sha(body) != freeze["body_sha256"]:
        raise ValueError("Champion body digest mismatch")
    for key in (
        "capability_id", "job", "activation_trigger", "project_check_identity",
        "logical_load_target", "accepted_current",
    ):
        if champion.get(key) != freeze[key]:
            raise ValueError(f"Champion contract mismatch: {key}")
    if champion.get("version_or_digest") != freeze["version_or_digest"]:
        raise ValueError("Champion current digest mismatch")
    initial_query = evolution_query(
        workspace,
        job="public API request validation and structured error-catalog invariants for job submission",
    )
    initial_ids = [row["experience_id"] for row in initial_query["experiences"]]
    if freeze["required_initial_experience_id"] not in initial_ids:
        raise ValueError("real Foundation query omitted the required initial Experience")
    if any(
        row.get("body_digest") != freeze["body_sha256"]
        or row.get("quality") != "VERIFIED"
        or row.get("result") != "SUCCESS"
        for row in initial_query["experiences"]
    ):
        raise ValueError("initial Evolution evidence is not success-only current-digest evidence")
    lineage = base.runtime_call(workspace, "validate-lineage")
    if not lineage.get("valid"):
        raise ValueError("recovered Foundation lineage is invalid")
    selection = selection_preflight(foundation, workspace, protocol)
    codex_home = base.create_codex_home(runtime / "codex-home")
    runner_inputs = {
        "runner_sha256": base.sha(__file__),
        "protocol_sha256": base.sha(PROTOCOL),
        "champion_freeze_sha256": base.sha(CHAMPION_FREEZE),
        "preregistration_sha256": base.sha(PREREGISTRATION),
    }
    record = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "status": "pass",
        "planned_fresh_arms": 3,
        "retries": 0,
        "product": product,
        "champion": champion | {"body_sha256": base.sha(body)},
        "prior_evidence": prior_verification,
        "initial_evolution_query": initial_query,
        "initial_experience_ids": initial_ids,
        "preliminary_decision": "MORE_EXPERIENCE_REQUIRED",
        "preliminary_reason": "only verified successes; no demonstrated Skill weakness",
        "raw_transcript_used_as_evolution_input": False,
        "task_freeze": task_freeze,
        "fresh_tasks_created_after_champion_freeze": True,
        "fresh_task_files": [path.relative_to(ROOT).as_posix() for path in fresh_task_files],
        "selection_preflight": selection,
        "lineage": lineage,
        "codex_home": codex_home,
        "runner_inputs": runner_inputs,
    }
    for source, target in (
        (PROTOCOL, evidence / "protocol.json"),
        (CHAMPION_FREEZE, evidence / "champion-freeze.json"),
        (PREREGISTRATION, evidence / "preregistration.md"),
        (Path(__file__), evidence / "run.py"),
    ):
        base.util.atomic_write(target, source.read_bytes())
    atomic_json(evidence / "initial-evolution-query.json", initial_query)
    atomic_json(evidence / "preflight.json", record)
    print(json.dumps({"phase": "preflight", "status": "pass", "runtime_root": str(runtime)}), flush=True)
    return record


def verify_frozen_inputs(preflight_record, foundation):
    expected = preflight_record["runner_inputs"]
    actual = {
        "runner_sha256": base.sha(__file__),
        "protocol_sha256": base.sha(PROTOCOL),
        "champion_freeze_sha256": base.sha(CHAMPION_FREEZE),
        "preregistration_sha256": base.sha(PREREGISTRATION),
    }
    if actual != expected:
        raise ValueError("Experiment 16 input changed after preflight")
    verify_protocol(load(PROTOCOL))
    base.verify_product(foundation, load(PROTOCOL), load(FOUNDATION_FREEZE))


def prepare_task(workspace, task, arm_id, first):
    if not first:
        base.util.git(workspace, "add", "-A")
        base.util.git(workspace, "commit", "-qm", "freeze prior E16 outcome and Foundation memory")
    copy_tree(ROOT / task["overlay"], workspace)
    base.util.git(workspace, "add", "-A")
    base.util.git(workspace, "commit", "-qm", f"freeze fresh {arm_id} task")
    initial = base.util.check_result(task["strict_command"], workspace)
    base.util.clean_runtime_files(workspace)
    if base.util.git(workspace, "status", "--porcelain").stdout.strip():
        raise ValueError(f"{arm_id} precheck changed its baseline")
    if initial["result"] != "fail":
        raise ValueError(f"{arm_id} fixture does not expose a fresh product gap")
    return {
        "initial_strict": initial,
        "initial_workspace_sha256": base.util.scientific_tree_sha256(workspace),
        "project_revision": base.util.git(workspace, "rev-parse", "HEAD").stdout.strip(),
    }


def finish_pack_task(workspace, architecture):
    finalized = proof.pack_call(workspace, "finalize", "--pack-id", architecture["pack_id"])
    experience = finalized.get("experience")
    status = "COMPLETED" if experience and experience.get("result") == "SUCCESS" else "PARTIAL"
    session = base.runtime_call(
        workspace, "session-finalize", "--status", status,
        "--next", "Continue collecting attributable Champion experience",
        "--completeness", "COMPLETE" if experience else "PARTIAL",
    )
    return {
        "experience": experience,
        "experience_captured": experience is not None,
        "session": session,
        "session_finalized": True,
        "authoritative_check": finalized.get("check"),
        "authoritative_pack_finalizer": True,
    }


def run_arm(runtime, preflight_record, arm, foundation, first):
    protocol = load(PROTOCOL)
    verify_frozen_inputs(preflight_record, foundation)
    workspace = runtime / "workspace"
    evidence = runtime / "evidence"
    task = protocol["tasks"][arm["task"]]
    arm_dir = evidence / "arms" / arm["arm_id"]
    arm_dir.mkdir(parents=True)
    prepared = prepare_task(workspace, task, arm["arm_id"], first)
    body = workspace / ".agents/skills/project-api-validation/SKILL.md"
    body_before = base.sha(body)
    source_before = base.source_snapshot(foundation)
    overlay_before = base.util.scientific_tree_sha256(ROOT / task["overlay"])
    state = proof.start_foundation(workspace, task, protocol)
    transcript = arm_dir / "transcript.jsonl"
    stderr_path = arm_dir / "stderr.txt"
    print(json.dumps({"phase": "arm-start", "arm_id": arm["arm_id"]}), flush=True)
    execution = base.execute_model(
        protocol, workspace, state["effective_prompt"], transcript, stderr_path,
        Path(preflight_record["codex_home"]["path"]),
    )
    trace_task = dict(task)
    trace = base.util.parse_transcript(transcript, trace_task, workspace)
    commands = base.transcript_commands(transcript)
    strict, completion = base.independent_checks(task, workspace)
    raw_ref = base.copy_raw_local(workspace, transcript, arm["arm_id"])
    architecture = proof.pack_evidence(
        workspace, task, state["task"]["task_id"], trace, commands, state["session"]["session_id"],
    )
    pre_finish_writes = base.changed_files(workspace)
    finish = finish_pack_task(workspace, architecture)
    architecture = proof.pack_evidence(
        workspace, task, state["task"]["task_id"], trace, commands, state["session"]["session_id"],
    )
    lineage = base.runtime_call(workspace, "validate-lineage")
    query = evolution_query(workspace)
    experience = finish.get("experience") or {}
    query_ids = [row["experience_id"] for row in query["experiences"]]
    writes = base.changed_files(workspace)
    unauthorized = sorted(path for path in writes if not base.allowed_path(task, path))
    missing = sorted(path for path in task["required_writes"] if path not in writes)
    patch = base.util.git(workspace, "diff", "--binary", "HEAD", check=False).stdout.encode()
    patch_hash = base.util.atomic_write(arm_dir / "patch.diff", patch)
    snapshot = base.snapshot_foundation_state(workspace, arm_dir / "foundation-state")
    source_after = base.source_snapshot(foundation)
    overlay_after = base.util.scientific_tree_sha256(ROOT / task["overlay"])
    body_after = base.sha(body)
    usage = trace.get("usage")
    infrastructure_errors = []
    if not transcript.is_file() or not trace.get("raw_complete"):
        infrastructure_errors.append("raw_transcript_missing_or_incomplete")
    if not isinstance(usage, dict) or not isinstance(usage.get("input_tokens"), int):
        infrastructure_errors.append("model_usage_missing_or_unparseable")
    if source_before != source_after or overlay_before != overlay_after:
        infrastructure_errors.append("scientific_input_mutation")
    if body_before != body_after:
        infrastructure_errors.append("champion_body_mutation")
    if base.sha(arm_dir / "patch.diff") != patch_hash:
        infrastructure_errors.append("patch_capture_corrupt")
    if experience.get("experience_id") not in query_ids:
        infrastructure_errors.append("product_experience_missing_from_real_query")
    pack = architecture.get("pack") or {}
    ref = architecture.get("expected_ref") or {}
    check = architecture.get("check") or {}
    mechanism_gate = bool(
        pack.get("selection_method") == "deterministic-single"
        and len(pack.get("capability_refs", [])) == 1
        and ref.get("capability_id") == task["expected_capability"]
        and ref.get("body_digest") == task["expected_body_sha256"]
        and ref.get("logical_load_target") == task["expected_target"]
        and architecture.get("selection_phase_body_reads") == 0
        and architecture.get("model_visible_pack_lifecycle_calls") == 0
        and check.get("check_id")
        and check.get("project_check_identity") == task["project_check_identity"]
        and experience.get("quality") == "VERIFIED"
        and experience.get("evolution_eligible") is True
        and lineage.get("valid") is True
    )
    product_pass = bool(
        strict["result"] == "pass" and completion["result"] == "pass"
        and check.get("result") == "pass" and experience.get("result") == "SUCCESS"
        and not unauthorized and not missing
    )
    record = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "arm_id": arm["arm_id"],
        "case_id": task["case_id"],
        "champion_digest": body_before,
        "task_sha256": task["task_sha256"],
        "overlay_sha256": overlay_before,
        "prepared": prepared,
        "process": execution,
        "model_usage": usage,
        "repository_reads": trace.get("repository_reads"),
        "raw_transcript": str(transcript.relative_to(evidence)),
        "raw_transcript_sha256": base.sha(transcript),
        "raw_transcript_used_as_evolution_input": False,
        "stderr": str(stderr_path.relative_to(evidence)),
        "stderr_sha256": base.sha(stderr_path),
        "patch": str((arm_dir / "patch.diff").relative_to(evidence)),
        "patch_sha256": patch_hash,
        "write_set": writes,
        "unauthorized_writes": unauthorized,
        "required_writes_missing": missing,
        "strict": strict,
        "completion": completion,
        "foundation_lifecycle": state,
        "architecture": architecture,
        "foundation_finish": finish,
        "lineage": lineage,
        "evolution_query_count": query["count"],
        "evolution_query_experience_ids": query_ids,
        "mechanism_gate": mechanism_gate,
        "product_pass": product_pass,
        "source_before": source_before,
        "source_after": source_after,
        "champion_body_before": body_before,
        "champion_body_after": body_after,
        "raw_transcript_content_copied_to_durable_memory": base.raw_copied_to_memory(workspace, transcript),
        "foundation_state": snapshot,
        "infrastructure_errors": infrastructure_errors,
        "evidence_committed": not infrastructure_errors,
        "pre_finish_writes": pre_finish_writes,
    }
    atomic_json(arm_dir / "evolution-query.json", query)
    atomic_json(arm_dir / "record.json", record)
    print(json.dumps({
        "phase": "arm-complete", "arm_id": arm["arm_id"],
        "strict": strict["result"], "check": check.get("result"),
        "experience_id": experience.get("experience_id"),
        "evolution_eligible": experience.get("evolution_eligible"),
        "evidence_committed": record["evidence_committed"],
    }), flush=True)
    return record


def bounded_evidence(query):
    fields = (
        "experience_id", "task_job", "pack_id", "capability_id", "body_digest",
        "selection_evidence", "check_id", "check_result", "product_outcome", "result",
        "success", "project_revision", "host_fingerprint", "source_refs", "quality",
        "observability_completeness", "evolution_eligible",
    )
    return [{key: row.get(key) for key in fields} for row in query["experiences"]]


def record_keep(workspace, protocol, evidence_rows):
    source_ids = [row["experience_id"] for row in evidence_rows]
    revision = base.util.git(workspace, "rev-parse", "HEAD").stdout.strip()
    session = base.runtime_call(
        workspace, "session-start", "--goal", "Decide the project-api-validation lifecycle from verified Experiences",
        "--host", "codex", "--host-version", base.codex_version(), "--model", protocol["model"],
        "--nulnul-revision", protocol["foundation"]["product_tree_sha256"],
        "--project-revision", revision, "--host-trust", "not-required",
        "--admission-state", "PRE_SESSION_CAPABILITY_PACK",
    )
    task = base.runtime_call(
        workspace, "task-start", "--goal", "Record the evidence-gated Skill lifecycle decision",
        "--job", "project-local capability lifecycle decision",
    )
    local = workspace / "docs/nulnul/.runtime"
    outcome_path = local / "E16-keep-outcome.json"
    promotions_path = local / "E16-keep-promotions.json"
    source_refs = [f"experience:{identity}" for identity in source_ids]
    atomic_json(outcome_path, {
        "experience_type": "TASK_EXPERIENCE",
        "quality": "VERIFIED",
        "observability_completeness": "COMPLETE",
        "result": "SUCCESS",
        "product_outcome": "KEEP: no verified attributable weakness justifies Skill mutation",
        "checks": [{"id": "evolution-evidence-review", "result": "pass"}],
        "source_refs": source_refs,
        "project_revision_before": revision,
        "project_revision_after": revision,
    })
    atomic_json(promotions_path, {"decisions": [{
        "decision": "KEEP project-api-validation at digest 13ffff5d869132d68ca2554d64a4b3e425d268f6e99e938bf46cf56881cfa2b9",
        "why": f"{len(source_ids)} verified attributable successes and no demonstrated Skill weakness",
        "scope": "project",
        "source_refs": source_refs,
        "evidence": source_ids,
    }]})
    review_experience = base.runtime_call(
        workspace, "task-finish", "--task-id", task["task_id"],
        "--outcome", str(outcome_path.relative_to(workspace)),
        "--promotions", str(promotions_path.relative_to(workspace)),
    )
    finalized = base.runtime_call(
        workspace, "session-finalize", "--status", "COMPLETED",
        "--next", "Wait for materially new project-api-validation Experience",
        "--completeness", "COMPLETE",
    )
    decisions = base.runtime_call(workspace, "inspect", "decisions", "--limit", "20")["decisions"]
    decision = decisions[-1]
    lineage = base.runtime_call(workspace, "validate-lineage")
    if not lineage.get("valid") or not set(source_refs).issubset(decision.get("source_refs", [])):
        raise ValueError("KEEP decision provenance is incomplete")
    return {
        "evolution_id": decision["decision_id"],
        "decision_record": decision,
        "review_experience": review_experience,
        "session": session,
        "session_finalization": finalized,
        "source_experience_ids": source_ids,
        "lineage": lineage,
    }


def finalize(runtime, preflight_record, records):
    protocol = load(PROTOCOL)
    evidence = runtime / "evidence"
    workspace = runtime / "workspace"
    final_query = evolution_query(workspace)
    evidence_rows = bounded_evidence(final_query)
    initial_ids = set(preflight_record["initial_experience_ids"])
    new_rows = [row for row in evidence_rows if row["experience_id"] not in initial_ids]
    all_success = bool(
        len(records) == 3 and len(new_rows) == 3
        and all(record["evidence_committed"] and record["mechanism_gate"] and record["product_pass"] for record in records)
        and all(
            row["quality"] == "VERIFIED" and row["result"] == "SUCCESS"
            and row["check_result"] == "pass" and row["evolution_eligible"] is True
            for row in evidence_rows
        )
    )
    decision_memory = record_keep(workspace, protocol, evidence_rows) if all_success else None
    lineage = base.runtime_call(workspace, "validate-lineage")
    source_unchanged = all(
        record["champion_body_before"] == record["champion_body_after"]
        == load(CHAMPION_FREEZE)["body_sha256"]
        for record in records
    )
    state_authority = all(not record["unauthorized_writes"] for record in records)
    infrastructure = any(not record["evidence_committed"] for record in records)
    if infrastructure:
        primary = "INFRASTRUCTURE_INVALID"
        decision = None
        failures = sorted({error for record in records for error in record["infrastructure_errors"]})
    elif all_success and decision_memory and lineage.get("valid") and source_unchanged and state_authority:
        primary = "SKILL_KEEP_PROVEN"
        decision = "KEEP"
        failures = []
    else:
        primary = "EVOLUTION_CORE_FAILURE"
        decision = None
        failures = []
        if len(new_rows) != 3:
            failures.append("INSUFFICIENT_EVOLUTION_EVIDENCE")
        if not all(record["mechanism_gate"] for record in records):
            failures.append("PROVENANCE_FAILURE")
        if any(not record["product_pass"] for record in records):
            failures.append("SKILL_WEAKNESS_NOT_ATTRIBUTABLE")
        if not source_unchanged or not state_authority:
            failures.append("STATE_AUTHORITY_REGRESSION")
        if not lineage.get("valid"):
            failures.append("PROVENANCE_FAILURE")
        failures = sorted(set(failures))
    review = []
    for row in evidence_rows:
        review.append({
            "experience_id": row["experience_id"],
            "classification": "SUCCESS" if row["result"] == "SUCCESS" and row["check_result"] == "pass" else "FAILURE",
            "task_job": row["task_job"],
            "body_digest": row["body_digest"],
            "check_id": row["check_id"],
            "check_result": row["check_result"],
            "outcome": row["product_outcome"],
        })
    report = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "foundation": {"status": "V2.3 FOUNDATION CORE COMPLETE", "evolution_readiness": True},
        "capability": preflight_record["champion"],
        "initial_evolution_query": {
            "filters": preflight_record["initial_evolution_query"]["filters"],
            "experience_ids": preflight_record["initial_experience_ids"],
            "count": preflight_record["initial_evolution_query"]["count"],
            "raw_transcript_used": False,
        },
        "experience_review": review,
        "preliminary_decision": "MORE_EXPERIENCE_REQUIRED",
        "preliminary_reason": "initial evidence was successful and contained no demonstrated weakness",
        "fresh_experience_collection": {
            "required": True,
            "planned": 3,
            "executed": len(records),
            "task_case_ids": [record["case_id"] for record in records],
            "new_experience_ids": [row["experience_id"] for row in new_rows],
        },
        "final_evidence_set": evidence_rows,
        "evolution_diagnosis": {
            "target": "project-api-validation",
            "affected_job": "public API request acceptance/rejection and structured error-catalog invariants",
            "source_experience_ids": [row["experience_id"] for row in evidence_rows],
            "weakness": None if all_success else "requires bounded attribution review",
            "attribution": "no Skill-attributable weakness observed" if all_success else "not established",
            "general_repair": None,
            "regression_risk": "unnecessary mutation of a Skill supported by all verified evidence",
        },
        "challenger": {
            "generated": False,
            "digest": None,
            "diff": None,
            "byte_delta": 0,
            "source_experiences": [],
            "evolution_id": None,
        },
        "competition": {
            "entered": False,
            "reason": "no evidence-grounded upgrade was justified" if all_success else "no candidate generated before attribution review",
            "pairs": 0,
        },
        "outcome": {
            "strict": [record["strict"]["result"] for record in records],
            "checks": [(record["foundation_finish"].get("authoritative_check") or {}).get("result") for record in records],
            "completion": [record["completion"]["result"] for record in records],
            "regressions": sum(not record["product_pass"] for record in records),
            "performance": [record.get("model_usage") for record in records],
        },
        "decision": decision,
        "evolution_transaction": {
            "executed": False,
            "old_digest": load(CHAMPION_FREEZE)["body_sha256"],
            "new_digest": None,
            "canonical_capability": "unchanged",
            "pack_resolution": source_unchanged,
            "rollback": "not required",
        },
        "evolution_memory": decision_memory,
        "future_pack": {
            "current_capability_digest": load(CHAMPION_FREEZE)["body_sha256"],
            "resolves_champion_body": source_unchanged,
        },
        "primary_result": primary,
        "failure_codes": failures,
        "valid_claims": [
            "Foundation Evolution Input supplied the evidence set",
            "the current Skill governed the evaluated fresh jobs" if all_success else "fresh Champion evidence is interpretable",
            "NULNUL recorded an evidence-grounded KEEP without mutation" if all_success else "no unsupported mutation occurred",
        ],
        "unsupported_claims": [
            "broad Skill generalization",
            "a Skill upgrade",
            "external capability superiority",
            "public release readiness",
        ],
        "lineage": lineage,
        "state_authority": state_authority,
        "raw_transcript_used_as_evolution_input": False,
        "user_routing_questions": 0,
        "foundation_status": "V2.3 FOUNDATION CORE COMPLETE",
        "next": "NORMAL PROJECT EXPERIENCE ACCUMULATION / NEXT CAPABILITY" if primary == "SKILL_KEEP_PROVEN" else "STOP — localized Evolution review",
    }
    atomic_json(evidence / "final-evolution-query.json", final_query)
    atomic_json(evidence / "final-report.json", report)
    manifest = base.artifact_manifest(evidence)
    atomic_json(evidence / "manifest.json", manifest)
    base.util.atomic_write(evidence / "manifest.receipt", (base.sha(evidence / "manifest.json") + "\n").encode())
    print(json.dumps({
        "phase": "complete", "primary_result": primary, "decision": decision,
        "new_experiences": len(new_rows), "evolution_id": (decision_memory or {}).get("evolution_id"),
        "evidence_root": str(evidence),
    }), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--foundation", type=Path, required=True)
    parser.add_argument("--prior-evidence", type=Path, required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    preflight_record = preflight(args.runtime, args.foundation.resolve(), args.prior_evidence.resolve())
    if args.preflight_only:
        return
    records = []
    for index, arm in enumerate(load(PROTOCOL)["arms"]):
        records.append(run_arm(args.runtime, preflight_record, arm, args.foundation.resolve(), index == 0))
        if "champion_body_mutation" in records[-1]["infrastructure_errors"]:
            break
    finalize(args.runtime, preflight_record, records)


if __name__ == "__main__":
    main()
