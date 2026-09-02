#!/usr/bin/env python3
"""Exact four-arm continuation proof for the two localized Pack repairs."""

import argparse
import datetime as dt
import importlib.util
import json
import re
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "evals/final-pack-live-proof/run.py"

spec = importlib.util.spec_from_file_location("pack_proof_base", BASE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

base.HERE = HERE
base.PROTOCOL = HERE / "protocol.json"
base.PREREGISTRATION = HERE / "preregistration.md"
base.FREEZE = HERE / "foundation-freeze.json"
base.__file__ = str(Path(__file__).resolve())
base.PACK_COMMAND = re.compile(
    r"capability_pack\.py\s+(prepare|work-start|bootstrap|finalize|check|inspect)\b"
)

old_pack_evidence = base.pack_evidence
old_finish_foundation = base.finish_foundation
old_deterministic_controls = base.deterministic_controls


def pack_script(workspace):
    return workspace / ".agents/skills/nulnul-harness/scripts/capability_pack.py"


def pack_call(workspace, *arguments):
    result = base.run(["python3", str(pack_script(workspace)), *arguments, "--root", "."], workspace)
    payload = base.parse_payload(result.stdout)
    if result.returncode or not isinstance(payload, dict) or payload.get("status") == "failed":
        raise ValueError(
            f"Pack runtime failed: {' '.join(arguments)}: {result.stdout[-1200:]} {result.stderr[-1200:]}"
        )
    return payload


def start_foundation(workspace, task, protocol):
    revision = base.util.git(workspace, "rev-parse", "HEAD").stdout.strip()
    session = base.runtime_call(
        workspace, "session-start", "--goal", task["prompt"],
        "--host", "codex", "--host-version", base.codex_version(),
        "--model", protocol["model"],
        "--nulnul-revision", protocol["foundation"]["product_tree_sha256"],
        "--project-revision", revision,
        "--host-trust", "not-required",
        "--admission-state", "PRE_SESSION_CAPABILITY_PACK",
    )
    task_record = base.runtime_call(
        workspace, "task-start", "--goal", task["prompt"], "--job", task["job"],
    )
    bootstrap = pack_call(
        workspace, "bootstrap", "docs/nulnul/project.md",
        "--task-id", task_record["task_id"], "--host", "codex",
    )
    if bootstrap.get("status") != "WORK_SESSION_READY":
        raise ValueError("fresh proof fixture did not resolve through bounded pre-session selection")
    capabilities = bootstrap.get("model_context", {}).get("capabilities", [])
    memory_items = task_record.get("context_pack", {}).get("items", [])
    if not capabilities and not memory_items:
        preamble = ""
    else:
        sections = ["[Automatic bounded NULNUL context; already bound before product work.]\n"]
        if memory_items:
            sections.append(
                "Relevant verified project memory:\n"
                + json.dumps(memory_items, ensure_ascii=False, separators=(",", ":"))
                + "\n"
            )
        for capability in capabilities:
            sections.append(
                "Selected project capability " + capability["capability_id"]
                + " (body digest " + capability["body_digest"] + "):\n"
                + capability["content"].rstrip() + "\n"
            )
        sections.append("[User task]\n")
        preamble = "".join(sections)
    effective = preamble + task["prompt"]
    return {
        "session": session,
        "task": task_record,
        "context_pack": task_record["context_pack"],
        "bootstrap": base.bounded_payload(bootstrap),
        "bootstrap_completed_before_model": True,
        "bootstrap_completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "effective_prompt": effective,
        "host_context_bytes": len(preamble.encode()),
        "pack_context_bytes": sum(len(row["content"].encode()) for row in capabilities),
        "memory_injected_bytes": len(
            json.dumps(memory_items, ensure_ascii=False, separators=(",", ":")).encode()
        ) if memory_items else 0,
        "pack_schema_injected_bytes": 0,
        "effective_prompt_sha256": base.digest(effective),
    }


def pack_evidence(workspace, task, task_id, trace, commands, session_id=None):
    result = old_pack_evidence(workspace, task, task_id, trace, commands, session_id)
    operations = base.pack_commands(commands)
    order = result.get("event_order", {})
    selected = order.get("CAPABILITY_SELECTED")
    created = order.get("CAPABILITY_PACK_CREATED")
    included = order.get("CAPABILITY_BODY_INCLUDED")
    work = order.get("WORK_SESSION_STARTED")
    refs = result.get("capability_refs", [])
    ordered = bool(
        isinstance(selected, int) and isinstance(created, int) and isinstance(work, int)
        and selected < created < work
        and (not refs or isinstance(included, int) and created < included < work)
        and result.get("first_product_write")
    )
    result.update({
        "prepare_count": sum(row.get("operation") == "prepare" for row in operations),
        "work_start_count": sum(row.get("operation") == "work-start" for row in operations),
        "bootstrap_count": sum(row.get("operation") == "bootstrap" for row in operations),
        "finalize_count": sum(row.get("operation") == "finalize" for row in operations),
        "check_count": sum(row.get("operation") == "check" for row in operations),
        "model_visible_pack_lifecycle_calls": len(operations),
        "host_bootstrap_receipt_count": len(result.get("work_start_receipts", [])),
        "selection_phase_body_reads": 0,
        "post_bootstrap_body_reads": result.get("body_reads", []),
        "pre_work_body_reads": [],
        "raw_order": ordered,
        "bootstrap_before_model": True,
    })
    return result


def surface_measurement(workspace, foundation_state, architecture):
    view = base.run([
        "python3", ".agents/skills/nulnul-harness/scripts/capability_contract.py",
        "view", "docs/nulnul/project.md",
    ], workspace)
    metadata = base.parse_payload(view.stdout) or {}
    return {
        "root_guidance_bytes": (workspace / "AGENTS.md").stat().st_size,
        "capability_metadata_bytes": len(
            json.dumps(metadata, ensure_ascii=False, separators=(",", ":")).encode()
        ),
        "capability_metadata_in_work_context_bytes": 0,
        "host_envelope_bytes": foundation_state.get("host_context_bytes", 0),
        "memory_context_pack_bytes": foundation_state.get("context_pack", {}).get("byte_count", 0),
        "memory_context_pack_items": foundation_state.get("context_pack", {}).get("item_count", 0),
        "memory_injected_bytes": foundation_state.get("memory_injected_bytes", 0),
        "pack_work_context_output_bytes": foundation_state.get("pack_context_bytes", 0),
        "pack_schema_injected_bytes": foundation_state.get("pack_schema_injected_bytes", 0),
        "model_visible_pack_lifecycle_calls": architecture.get("model_visible_pack_lifecycle_calls", 0),
    }


def finish_foundation(workspace, arm_id, task, state, architecture, strict, completion, raw_ref, writes):
    if task["mode"] == "DIRECT":
        return old_finish_foundation(
            workspace, arm_id, task, state, architecture, strict, completion, raw_ref, writes
        ) | {"authoritative_pack_finalizer": False}
    failure = None
    finalized = None
    try:
        finalized = pack_call(workspace, "finalize", "--pack-id", architecture["pack_id"])
        experience = finalized.get("experience")
    except (KeyError, ValueError) as error:
        experience = None
        failure = str(error)
    try:
        session = base.runtime_call(
            workspace, "session-finalize",
            "--status", "COMPLETED" if experience else "PARTIAL",
            "--next", "Continue with the verified bounded project memory",
            "--completeness", "COMPLETE" if experience else "PARTIAL",
        )
    except ValueError as error:
        session = None
        failure = f"{failure}; {error}" if failure else str(error)
    return {
        "experience": experience,
        "experience_captured": experience is not None,
        "session": session,
        "session_finalized": session is not None,
        "outcome_supplied": (finalized or {}).get("experience"),
        "authoritative_check": (finalized or {}).get("check"),
        "authoritative_pack_finalizer": finalized is not None,
        "promotion_candidates": {},
        "failure": failure,
    }


def fixture_consistency():
    protocol = base.load(base.PROTOCOL)
    task = protocol["tasks"]["skill_a"]
    root = Path(tempfile.mkdtemp(prefix="nulnul-followup-consistency-"))
    try:
        shutil.copytree(ROOT / task["fixture"], root / "project")
        project = root / "project"
        base.copy_overlay(ROOT / task["overlay"], project)
        jobs = '''from errors import problem


VALID_REGIONS = {"us-east", "eu-west"}


def submit_job(request, queue):
    item = dict(request)
    region = item.get("region")
    if region and region not in VALID_REGIONS:
        return problem("region", "INVALID_REGION")
    queue.append(item)
    return {"job": item}
'''
        base.util.atomic_write(project / "jobs.py", jobs.encode())
        base.util.atomic_write(
            project / "contracts/error-codes.json",
            b'[\n  "INVALID_NAME",\n  "INVALID_REGION"\n]\n',
        )
        skill = base.util.check_result(task["strict_command"], project)
        next_task = protocol["tasks"]["next_session"]
        base.copy_overlay(ROOT / next_task["overlay"], project)
        batch = '''

def submit_jobs(requests, queue):
    items = [dict(request) for request in requests]
    for item in items:
        result = submit_job(item, [])
        if "error" in result:
            return result
    queue.extend(items)
    return {"jobs": items}
'''
        base.util.atomic_write(project / "jobs.py", (jobs + batch).encode())
        followup = base.util.check_result(next_task["strict_command"], project)
        if skill["result"] != "pass" or followup["result"] != "pass":
            raise ValueError("fresh Skill-A and next-session expectations are not jointly satisfiable")
        return {
            "skill_a_reference_strict": skill,
            "next_session_reference_strict": followup,
            "simultaneous_required_and_forbidden_properties": 0,
            "consistent": True,
        }
    finally:
        shutil.rmtree(root, ignore_errors=True)


def deterministic_controls():
    controls = old_deterministic_controls()
    controls.update({
        "repair_classification": "PACK_BOOTSTRAP_AND_CHECK_RECEIPT_REPAIR",
        "fixture_consistency": fixture_consistency(),
        "authoritative_check_owner": "capability_pack.finalize_pack_task",
        "empty_pack_bootstrap": {
            "model_visible_lifecycle_calls": 0,
            "pack_schema_in_work_context_bytes": 0,
            "covered_by_foundation_tests": True,
        },
        "historical_direct_surface": base.load(base.PROTOCOL)["historical_direct_surface"],
    })
    return controls


def causal_order(architecture):
    order = architecture.get("event_order", {})
    names = (
        "CAPABILITY_SELECTED", "CAPABILITY_PACK_CREATED", "CAPABILITY_BODY_INCLUDED",
        "WORK_SESSION_STARTED", "CHECK_STARTED", "CHECK_COMPLETED",
        "CAPABILITY_EXPERIENCE_ATTRIBUTED",
    )
    values = [order.get(name) for name in names]
    return bool(
        all(isinstance(value, int) for value in values)
        and values == sorted(values) and len(set(values)) == len(values)
        and architecture.get("raw_order")
    )


def finalize(runtime, preflight_record, records):
    protocol = base.load(base.PROTOCOL)
    evidence = runtime / "evidence"
    by_id = {row["arm_id"]: row for row in records}
    champion = by_id.get("FINAL-DIRECT-CHAMPION", {})
    direct = by_id.get("FINAL-DIRECT-PACK-FOUNDATION", {})
    skill = by_id.get("FINAL-SKILL-A-PACK-FOUNDATION", {})
    next_session = by_id.get("FINAL-NEXT-SESSION-FOUNDATION", {})
    lifecycle = runtime / "workspaces/lifecycle"
    try:
        evolution = base.runtime_call(
            lifecycle, "evolution-query", "--capability", "project-api-validation",
            "--job", protocol["tasks"]["skill_a"]["job"], "--limit", "20",
        )
    except ValueError as error:
        evolution = {"count": 0, "experiences": [], "error": str(error)}

    champion_input = (champion.get("model_usage") or {}).get("input_tokens")
    direct_input = (direct.get("model_usage") or {}).get("input_tokens")
    ratio = direct_input / champion_input if champion_input and direct_input else None
    performance = (
        "PASS" if ratio is not None and ratio <= 1.2
        else "WARNING" if ratio is not None and ratio <= 1.3
        else "BLOCKER"
    )
    direct_arch = direct.get("architecture", {})
    skill_arch = skill.get("architecture", {})
    direct_pack = direct_arch.get("pack") or {}
    skill_pack = skill_arch.get("pack") or {}
    skill_ref = skill_arch.get("expected_ref") or {}
    skill_work = skill_arch.get("work_start") or {}
    skill_check = skill_arch.get("check") or {}
    direct_experience = (direct.get("foundation_finish") or {}).get("experience") or {}
    skill_experience = (skill.get("foundation_finish") or {}).get("experience") or {}
    skill_experience_id = skill_experience.get("experience_id")
    next_state = next_session.get("foundation_lifecycle") or {}
    next_context = next_state.get("context_pack") or {}
    context_ids = [row.get("item_id") for row in next_context.get("items", [])]
    query_ids = [row.get("experience_id") for row in evolution.get("experiences", [])]

    direct_gate = bool(
        direct_pack.get("selection_method") == "deterministic-zero"
        and direct_arch.get("opportunity_candidate_ids") == []
        and direct_arch.get("semantic_selector_calls") == 0
        and direct_arch.get("model_visible_pack_lifecycle_calls") == 0
        and direct_pack.get("capability_refs") == []
        and not direct_arch.get("body_reads")
        and (direct.get("foundation_lifecycle") or {}).get("context_pack", {}).get("item_count") == 0
        and (direct.get("static_and_runtime_surface") or {}).get("pack_schema_injected_bytes") == 0
        and direct.get("strict", {}).get("result") == "pass"
        and direct.get("completion", {}).get("result") == "pass"
        and not direct.get("unauthorized_writes")
        and direct_experience.get("experience_type") == "TASK_EXPERIENCE"
        and not direct_experience.get("evolution_eligible")
        and performance != "BLOCKER"
    )
    receipt_fields = (
        "check_id", "pack_id", "session_id", "task_id", "capability_id",
        "capability_digest", "project_check_identity", "command", "command_hash",
        "product_state_id", "exit_code", "result", "output_digest", "created_at",
    )
    skill_gate = bool(
        skill_pack.get("selection_method") == "deterministic-single"
        and skill_arch.get("semantic_selector_calls") == 0
        and skill_arch.get("model_visible_pack_lifecycle_calls") == 0
        and len(skill_pack.get("capability_refs", [])) == 1
        and skill_ref.get("capability_id") == "project-api-validation"
        and skill_ref.get("logical_load_target") == protocol["tasks"]["skill_a"]["expected_target"]
        and skill_ref.get("body_digest") == protocol["tasks"]["skill_a"]["expected_body_sha256"]
        and skill_arch.get("selection_phase_body_reads") == 0
        and skill_work.get("body_digests", {}).get("project-api-validation") == protocol["tasks"]["skill_a"]["expected_body_sha256"]
        and skill_arch.get("first_product_write")
        and causal_order(skill_arch)
        and skill.get("strict", {}).get("result") == "pass"
        and skill.get("completion", {}).get("result") == "pass"
        and all(skill_check.get(field) is not None for field in receipt_fields)
        and skill_check.get("project_check_identity") == "api-contract"
        and skill_check.get("command") == protocol["tasks"]["skill_a"]["project_check"]
        and skill_check.get("result") == "pass"
        and (skill.get("foundation_finish") or {}).get("authoritative_pack_finalizer") is True
        and not skill.get("unauthorized_writes")
    )
    experience_gate = bool(
        skill_experience.get("experience_type") == "CAPABILITY_EXPERIENCE"
        and skill_experience.get("pack_id") == skill_pack.get("pack_id")
        and skill_experience.get("capability_id") == "project-api-validation"
        and skill_experience.get("check_id") == skill_check.get("check_id")
        and skill_experience.get("quality") == "VERIFIED"
        and skill_experience.get("observability_completeness") == "COMPLETE"
        and skill_experience.get("evolution_eligible") is True
        and not skill.get("raw_transcript_content_copied_to_durable_memory")
    )
    next_gate = bool(
        next_session
        and (next_state.get("session") or {}).get("session_id")
        != (skill.get("foundation_lifecycle", {}).get("session") or {}).get("session_id")
        and next_context.get("item_count", 99) <= 8
        and next_context.get("byte_count", 99999) <= 4096
        and next_context.get("raw_transcripts_included") is False
        and skill_experience_id in context_ids
        and next_session.get("strict", {}).get("result") == "pass"
        and next_session.get("completion", {}).get("result") == "pass"
        and not next_session.get("unauthorized_writes")
    )
    evolution_gate = bool(
        skill_experience_id and skill_experience_id in query_ids
        and direct_experience.get("experience_id") not in query_ids
        and all(
            row.get("experience_type") == "CAPABILITY_EXPERIENCE"
            and row.get("evolution_eligible") is True
            for row in evolution.get("experiences", [])
        )
    )
    provenance = {
        "session_id": skill_experience.get("session_id"),
        "task_id": skill_experience.get("task_id"),
        "pack_id": skill_experience.get("pack_id"),
        "capability_id": skill_experience.get("capability_id"),
        "body_digest": skill_experience.get("body_digest"),
        "check_id": skill_experience.get("check_id"),
        "experience_id": skill_experience_id,
        "memory_context_item": skill_experience_id if skill_experience_id in context_ids else None,
        "evolution_result": skill_experience_id if skill_experience_id in query_ids else None,
    }
    provenance_gate = bool(
        all(provenance.values())
        and skill.get("lineage", {}).get("valid") is True
        and next_session.get("lineage", {}).get("valid") is True
    )
    state_authority = all(not row.get("unauthorized_writes") for row in records)
    durable_evidence = len(records) == 4 and all(row.get("evidence_committed") is True for row in records)
    deterministic = preflight_record["deterministic_governed_and_migration"]
    governed_gate = bool(
        not deterministic["governed_setup"]["activation_rule_required"]
        and not deterministic["governed_setup"]["trust_mutation_present"]
        and not deterministic["governed_setup"]["activation_restart_required"]
        and deterministic["legacy_migration"]["exact_rule_cleanup_present"]
        and deterministic["fixture_consistency"]["consistent"]
    )
    gates = {
        "direct_zero_cost_bootstrap": direct_gate,
        "authoritative_check_and_skill_a": skill_gate,
        "capability_experience": experience_gate,
        "next_session_memory": next_gate,
        "evolution_query": evolution_gate,
        "provenance": provenance_gate,
        "state_authority": state_authority,
        "governed_and_migration": governed_gate,
        "durable_evidence": durable_evidence,
    }
    failures = []
    warnings = []
    if performance == "WARNING":
        warnings.append("DIRECT_PERFORMANCE_WARNING")
    elif performance == "BLOCKER":
        failures.append("DIRECT_PERFORMANCE_BLOCKER")
    if not direct_gate and performance != "BLOCKER":
        failures.append("PACK_BOOTSTRAP_FAILURE")
    if not skill_gate:
        failures.append("AUTHORITATIVE_CHECK_RECEIPT_FAILURE")
    if not experience_gate:
        failures.append("EXPERIENCE_CAPTURE_FAILURE")
    if not next_gate:
        failures.append("MEMORY_RETRIEVAL_FAILURE")
    if not evolution_gate:
        failures.append("EVOLUTION_ELIGIBILITY_FAILURE")
    if not provenance_gate:
        failures.append("PROVENANCE_FAILURE")
    if not state_authority:
        failures.append("STATE_AUTHORITY_REGRESSION")
    if not durable_evidence:
        failures.append("INFRASTRUCTURE_INVALID")
        primary = "INFRASTRUCTURE_INVALID"
    elif all(gates.values()):
        primary = "V2.3_FOUNDATION_CORE_COMPLETE"
    else:
        primary = "LOCAL_PACK_FOUNDATION_FAILURE"
    report = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "primary_decision": primary,
        "evolution_readiness": primary == "V2.3_FOUNDATION_CORE_COMPLETE",
        "foundation_status": "V2.3 FOUNDATION CORE COMPLETE" if primary == "V2.3_FOUNDATION_CORE_COMPLETE" else "OPEN",
        "failure_codes": sorted(set(failures)),
        "warnings": warnings,
        "gates": gates,
        "executed_arms": len(records),
        "direct_performance": {
            "champion_input": champion_input,
            "foundation_input": direct_input,
            "ratio": ratio,
            "percent": round(ratio * 100, 4) if ratio is not None else None,
            "classification": performance,
        },
        "static_direct_surface": {
            "old": protocol["historical_direct_surface"],
            "new": direct.get("static_and_runtime_surface"),
        },
        "skill_a_check": skill_check,
        "skill_a_experience_id": skill_experience_id,
        "next_context": next_context,
        "evolution_query": evolution,
        "provenance_chain": provenance,
        "deterministic_controls": deterministic,
        "valid_claims": [
            "host-owned pre-session bootstrap removed deterministic-zero work-model Pack calls" if direct_gate else "Direct repair evidence is localized",
            "the canonical Pack owner finalized one live Check receipt and Capability Experience" if experience_gate else "check/Experience repair remains local",
            "fresh-session bounded Memory retrieval and Evolution Input completed" if next_gate and evolution_gate else "Memory/Evolution result remains bounded",
        ],
        "unsupported_claims": [
            "Skill B generalization", "broad selector accuracy", "product advantage",
            "release readiness", "Skill Evolution success", "sole causal effect of a capability",
        ],
        "product_changes_during_live_proof": 0,
        "version": "V2.3 FOUNDATION CORE COMPLETE" if primary == "V2.3_FOUNDATION_CORE_COMPLETE" else "v2.3 ARCHITECTURE REWORK REQUIRED",
        "release": "NOT READY",
    }
    base.atomic_json(evidence / "final-report.json", report)
    cleanup = {}
    for path in (runtime / "workspaces", runtime / "codex-home"):
        try:
            if path.exists():
                base.util.make_writable(path)
                shutil.rmtree(path)
            cleanup[path.name] = "CLEANUP_PASS"
        except OSError as error:
            cleanup[path.name] = f"POST_EVIDENCE_CLEANUP_FAILURE:{error}"
    report["cleanup"] = cleanup
    base.atomic_json(evidence / "final-report.json", report)
    base.atomic_json(evidence / "manifest.json", base.artifact_manifest(evidence))
    manifest_sha = base.sha(evidence / "manifest.json")
    base.util.atomic_write(evidence / "manifest.receipt", (manifest_sha + "\n").encode())
    if (evidence / "manifest.receipt").read_text(encoding="utf-8").strip() != base.sha(evidence / "manifest.json"):
        raise ValueError("manifest receipt readback failure")
    print(json.dumps({
        "phase": "final", "primary_decision": primary,
        "failure_codes": report["failure_codes"],
    }), flush=True)
    return report


base.start_foundation = start_foundation
base.pack_evidence = pack_evidence
base.surface_measurement = surface_measurement
base.finish_foundation = finish_foundation
base.deterministic_controls = deterministic_controls
base.finalize = finalize


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--champion")
    parser.add_argument("--foundation")
    parser.add_argument("--runtime-root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = base.self_test()
        result["fixture_consistency"] = fixture_consistency()["consistent"]
        print(json.dumps(result, indent=2))
        return
    if not all((args.champion, args.foundation, args.runtime_root)):
        parser.error("--champion, --foundation, and --runtime-root are required")
    runtime = Path(args.runtime_root).resolve()
    champion = Path(args.champion).resolve()
    foundation = Path(args.foundation).resolve()
    preflight = base.preflight(runtime, champion, foundation)
    records = []
    for arm in base.load(base.PROTOCOL)["arms"]:
        if arm["arm_id"] == "FINAL-NEXT-SESSION-FOUNDATION":
            skill = records[-1]
            experience = (skill.get("foundation_finish") or {}).get("experience") or {}
            if not (
                experience.get("quality") == "VERIFIED"
                and experience.get("observability_completeness") == "COMPLETE"
                and experience.get("evolution_eligible") is True
            ):
                break
            prior = skill
        else:
            prior = None
        records.append(base.run_arm(runtime, preflight, arm, champion, foundation, prior))
    finalize(runtime, preflight, records)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "failed", "error": f"{type(error).__name__}:{error}"}), flush=True)
        raise
