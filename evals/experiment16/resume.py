#!/usr/bin/env python3
"""Resume E16 after the frozen runner stopped before its second model arm."""

import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run.py"
spec = importlib.util.spec_from_file_location("e16_frozen_runner", RUNNER)
e16 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e16)
base = e16.base
proof = e16.proof


def selection_evidence(preflight, task_name):
    rows = preflight["selection_preflight"][task_name]
    selected = rows[0]
    if selected["capability_id"] != "project-api-validation" or selected["score"] < 2:
        raise ValueError("bounded selector lacks a strong Skill-A candidate")
    if any(row["score"] >= 2 for row in rows[1:]):
        raise ValueError("bounded selector has more than one strong candidate")
    contrast = ", ".join(f"{row['capability_id']}={row['score']}" for row in rows)
    return f"bounded P3 selector chose the only strong task match ({contrast})"


def state_from_bootstrap(workspace, task, protocol, preflight, task_name, active=None):
    if active is None:
        revision = base.util.git(workspace, "rev-parse", "HEAD").stdout.strip()
        active = base.runtime_call(
            workspace, "session-start", "--goal", task["prompt"],
            "--host", "codex", "--host-version", base.codex_version(),
            "--model", protocol["model"],
            "--nulnul-revision", protocol["foundation"]["product_tree_sha256"],
            "--project-revision", revision, "--host-trust", "not-required",
            "--admission-state", "PRE_SESSION_CAPABILITY_PACK",
        )
        task_record = base.runtime_call(
            workspace, "task-start", "--goal", task["prompt"], "--job", task["job"],
        )
    else:
        task_record = active["tasks"][0]
    evidence = selection_evidence(preflight, task_name)
    bootstrap = proof.pack_call(
        workspace, "bootstrap", "docs/nulnul/project.md",
        "--task-id", task_record["task_id"], "--host", "codex",
        "--select", "project-api-validation", "--evidence", evidence,
    )
    if bootstrap.get("status") != "WORK_SESSION_READY":
        raise ValueError("bounded selector did not produce a ready work session")
    capabilities = bootstrap.get("model_context", {}).get("capabilities", [])
    memory_items = task_record.get("context_pack", {}).get("items", [])
    sections = ["[Automatic bounded NULNUL context; already bound before product work.]\n"]
    if memory_items:
        sections.append(
            "Relevant verified project memory:\n"
            + json.dumps(memory_items, ensure_ascii=False, separators=(",", ":")) + "\n"
        )
    for capability in capabilities:
        sections.append(
            "Selected project capability " + capability["capability_id"]
            + " (body digest " + capability["body_digest"] + "):\n"
            + capability["content"].rstrip() + "\n"
        )
    sections.append("[User task]\n")
    preamble = "".join(sections)
    return {
        "session": active,
        "task": task_record,
        "context_pack": task_record["context_pack"],
        "bootstrap": base.bounded_payload(bootstrap),
        "bootstrap_completed_before_model": True,
        "bootstrap_completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "effective_prompt": preamble + task["prompt"],
        "host_context_bytes": len(preamble.encode()),
        "pack_context_bytes": sum(len(row["content"].encode()) for row in capabilities),
        "memory_injected_bytes": len(
            json.dumps(memory_items, ensure_ascii=False, separators=(",", ":")).encode()
        ) if memory_items else 0,
        "pack_schema_injected_bytes": 0,
        "effective_prompt_sha256": base.digest(preamble + task["prompt"]),
        "selection_recovery": {"method": "BOUNDED_P3", "evidence": evidence},
    }


def complete_arm(runtime, preflight, foundation, arm, prepared, state, recovery_reason):
    protocol = e16.load(e16.PROTOCOL)
    workspace = runtime / "workspace"
    evidence = runtime / "evidence"
    task = protocol["tasks"][arm["task"]]
    arm_dir = evidence / "arms" / arm["arm_id"]
    arm_dir.mkdir(parents=True, exist_ok=True)
    if any(arm_dir.iterdir()):
        raise ValueError(f"recovery arm evidence is not empty: {arm['arm_id']}")
    body = workspace / ".agents/skills/project-api-validation/SKILL.md"
    body_before = base.sha(body)
    source_before = base.source_snapshot(foundation)
    overlay_before = base.util.scientific_tree_sha256(e16.ROOT / task["overlay"])
    transcript = arm_dir / "transcript.jsonl"
    stderr_path = arm_dir / "stderr.txt"
    print(json.dumps({"phase": "arm-start", "arm_id": arm["arm_id"], "resumed": True}), flush=True)
    execution = base.execute_model(
        protocol, workspace, state["effective_prompt"], transcript, stderr_path,
        Path(preflight["codex_home"]["path"]),
    )
    trace = base.util.parse_transcript(transcript, dict(task), workspace)
    commands = base.transcript_commands(transcript)
    strict, completion = base.independent_checks(task, workspace)
    base.copy_raw_local(workspace, transcript, arm["arm_id"])
    architecture = proof.pack_evidence(
        workspace, task, state["task"]["task_id"], trace, commands, state["session"]["session_id"],
    )
    pre_finish_writes = base.changed_files(workspace)
    finish = e16.finish_pack_task(workspace, architecture)
    architecture = proof.pack_evidence(
        workspace, task, state["task"]["task_id"], trace, commands, state["session"]["session_id"],
    )
    lineage = base.runtime_call(workspace, "validate-lineage")
    query = e16.evolution_query(workspace)
    experience = finish.get("experience") or {}
    query_ids = [row["experience_id"] for row in query["experiences"]]
    writes = base.changed_files(workspace)
    unauthorized = sorted(path for path in writes if not base.allowed_path(task, path))
    missing = sorted(path for path in task["required_writes"] if path not in writes)
    patch = base.util.git(workspace, "diff", "--binary", "HEAD", check=False).stdout.encode()
    patch_hash = base.util.atomic_write(arm_dir / "patch.diff", patch)
    snapshot = base.snapshot_foundation_state(workspace, arm_dir / "foundation-state")
    source_after = base.source_snapshot(foundation)
    overlay_after = base.util.scientific_tree_sha256(e16.ROOT / task["overlay"])
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
    if experience.get("experience_id") not in query_ids:
        infrastructure_errors.append("product_experience_missing_from_real_query")
    pack = architecture.get("pack") or {}
    ref = architecture.get("expected_ref") or {}
    check = architecture.get("check") or {}
    mechanism_gate = bool(
        pack.get("selection_method") == "bounded-semantic"
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
        "infrastructure_recovery": recovery_reason,
    }
    e16.atomic_json(arm_dir / "evolution-query.json", query)
    e16.atomic_json(arm_dir / "record.json", record)
    print(json.dumps({
        "phase": "arm-complete", "arm_id": arm["arm_id"], "resumed": True,
        "strict": strict["result"], "check": check.get("result"),
        "experience_id": experience.get("experience_id"),
        "evolution_eligible": experience.get("evolution_eligible"),
        "evidence_committed": record["evidence_committed"],
    }), flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--foundation", type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime
    foundation = args.foundation.resolve()
    preflight = e16.load(runtime / "evidence/preflight.json")
    e16.verify_frozen_inputs(preflight, foundation)
    normal = e16.load(runtime / "evidence/arms/E16-CHAMPION-NORMAL/record.json")
    if not normal.get("evidence_committed"):
        raise ValueError("first Champion arm lacks committed evidence")
    if (runtime / "evidence/arms/E16-CHAMPION-BOUNDARY/transcript.jsonl").exists():
        raise ValueError("second model arm already started; recovery would be a retry")
    protocol = e16.load(e16.PROTOCOL)
    workspace = runtime / "workspace"
    active = base.runtime_call(workspace, "inspect", "current-session")
    if active["tasks"][0]["task_id"] != "tsk-20260901T062433Z-b35369b71265":
        raise ValueError("unexpected active task at the recovery boundary")
    boundary_task = protocol["tasks"]["boundary"]
    prepared = {
        "initial_strict": base.util.check_result(boundary_task["strict_command"], workspace),
        "project_revision": base.util.git(workspace, "rev-parse", "HEAD").stdout.strip(),
        "recovered_after_session_start": True,
    }
    boundary_state = state_from_bootstrap(
        workspace, boundary_task, protocol, preflight, "boundary", active,
    )
    boundary = complete_arm(
        runtime, preflight, foundation, protocol["arms"][1], prepared, boundary_state,
        "frozen runner omitted the supported bounded P3 selection branch; no model arm had started",
    )
    if not boundary["evidence_committed"]:
        raise ValueError("boundary arm evidence did not commit")
    different_task = protocol["tasks"]["different_surface"]
    prepared = e16.prepare_task(workspace, different_task, protocol["arms"][2]["arm_id"], False)
    different_state = state_from_bootstrap(
        workspace, different_task, protocol, preflight, "different_surface",
    )
    different = complete_arm(
        runtime, preflight, foundation, protocol["arms"][2], prepared, different_state,
        "bounded P3 selection used the frozen candidate scores; no extra selector model call",
    )
    base.util.atomic_write(runtime / "evidence/resume.py", Path(__file__).read_bytes())
    report = e16.finalize(runtime, preflight, [normal, boundary, different])
    report["infrastructure_recovery"] = {
        "classification": "RUNNER_SELECTOR_BRANCH_OMISSION",
        "second_model_arm_started_before_recovery": False,
        "model_retries": 0,
        "extra_model_calls": 0,
        "task_or_champion_mutation": False,
        "bounded_selection": "only score>=2 candidate selected; score-1 incidental candidate rejected",
    }
    e16.atomic_json(runtime / "evidence/final-report.json", report)
    manifest = base.artifact_manifest(runtime / "evidence")
    e16.atomic_json(runtime / "evidence/manifest.json", manifest)
    base.util.atomic_write(
        runtime / "evidence/manifest.receipt",
        (base.sha(runtime / "evidence/manifest.json") + "\n").encode(),
    )
    print(json.dumps({
        "phase": "recovery-complete", "primary_result": report["primary_result"],
        "decision": report["decision"], "evidence_root": str(runtime / "evidence"),
    }), flush=True)


if __name__ == "__main__":
    main()
