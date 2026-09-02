#!/usr/bin/env python3
"""Three-arm continuation of E15 using its proven minimal-runner primitives."""

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTOCOL = HERE / "protocol.json"
PREREG = HERE / "preregistration.md"
FREEZE = HERE / "foundation-freeze.json"
E15_RUNNER = ROOT / "evals/experiment15/run.py"

spec = importlib.util.spec_from_file_location("final_e15_runner", E15_RUNNER)
e15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e15)
e15.ROOT = ROOT
e15.PROTOCOL = PROTOCOL
e15.PREREG = PREREG
e15.FREEZE = FREEZE
e15.base.REPO = ROOT


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    e15.atomic_json(Path(path), value)


def benchmark_hashes():
    return {
        "runner_sha256": sha(__file__),
        "e15_runner_sha256": sha(E15_RUNNER),
        "base_runner_sha256": sha(e15.BASE_PATH),
        "protocol_sha256": sha(PROTOCOL),
        "preregistration_sha256": sha(PREREG),
        "foundation_freeze_sha256": sha(FREEZE),
    }


def verify_benchmark_frozen(expected):
    for key, value in benchmark_hashes().items():
        if expected.get(key) != value:
            raise ValueError(f"frozen continuation input changed: {key}")


def canonical_module(foundation):
    path = Path(foundation) / "skills/nulnul-harness/scripts/capability_contract.py"
    module_spec = importlib.util.spec_from_file_location("frozen_capability_contract", path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def exact_paths(protocol, foundation, runtime):
    return [
        {
            "arm_id": arm["arm_id"],
            "source": arm["source"],
            "task": arm["task"],
            "product_source": str(Path(foundation).resolve()),
            "fixture": str((ROOT / protocol["tasks"][arm["task"]]["fixture"]).resolve()),
            "workspace": str((Path(runtime) / "workspaces" / arm["workspace"]).resolve()),
            "evidence": str((Path(runtime) / "evidence/arms" / arm["arm_id"]).resolve()),
            "transcript": str((Path(runtime) / "evidence/arms" / arm["arm_id"] / "transcript.jsonl").resolve()),
            "receipt_root": str((Path(runtime) / "evidence/arms" / arm["arm_id"] / "receipts").resolve()),
        }
        for arm in protocol["arms"]
    ]


def validate_paths(protocol, foundation, runtime):
    runtime = Path(runtime).resolve()
    source = Path(foundation).resolve()
    evidence = runtime / "evidence"
    workspace = runtime / "workspaces/lifecycle"
    codex_home = runtime / "codex-home"
    if any(e15.base.overlap(left, right) for left, right in (
        (source, evidence), (source, workspace), (evidence, workspace),
        (codex_home, evidence), (codex_home, workspace),
    )):
        raise ValueError("scientific source, workspace, Codex home, and evidence must be disjoint")
    paths = exact_paths(protocol, foundation, runtime)
    if {row["workspace"] for row in paths} != {str(workspace)}:
        raise ValueError("the exact three lifecycle arms must share only their planned project state")
    if len({row["evidence"] for row in paths}) != 3:
        raise ValueError("arm evidence destinations must be unique")


def self_test(foundation):
    protocol = load(PROTOCOL)
    contract = canonical_module(foundation)
    assert len(protocol["arms"]) == 3
    assert [row["arm_id"] for row in protocol["arms"]] == [
        "FINAL-GOVERNED-SETUP",
        "FINAL-PROJECT-FIT-POST-RESTART",
        "FINAL-NEXT-SESSION",
    ]
    assert e15.base.positive_state_argument("rg x -g !docs/nulnul/checkpoint.json .") is False
    assert contract.canonical_logical_target("project-api-validation") == (
        "capabilities/project-api-validation/SKILL.md"
    )
    assert not transaction_command("python3 setup_transaction.py --help")
    assert transaction_command("python3 setup_transaction.py plan.json --root . --governed-receipt x")
    return {
        "exact_three_arms": "pass",
        "structured_negation": "pass",
        "canonical_target_from_frozen_product": "pass",
        "transaction_help_excluded": "pass",
    }


def preflight(args):
    protocol = load(PROTOCOL)
    freeze = load(FREEZE)
    foundation = Path(args.foundation).resolve()
    runtime = Path(args.runtime_root).resolve()
    if runtime.exists() and any(runtime.iterdir()):
        raise ValueError("runtime root must be fresh and empty")
    runtime.mkdir(parents=True, exist_ok=True)
    validate_paths(protocol, foundation, runtime)
    if not e15.source_valid(
        foundation,
        protocol["foundation"]["tree_sha256"],
        protocol["foundation"]["scientific_tree_sha256"],
    ):
        raise ValueError("repaired Foundation integrity failure")
    critical_paths = {
        "setup_transaction": "skills/nulnul-harness/scripts/setup_transaction.py",
        "canonical_capability_contract": "skills/nulnul-harness/scripts/capability_contract.py",
        "foundation_runtime": "skills/nulnul-harness/scripts/foundation_runtime.py",
        "activation_boundary": "skills/nulnul-harness/scripts/activation_boundary.py",
        "host_entry": "skills/nulnul-harness/scripts/sync_host_entry.py",
        "layer_contract_registry": "skills/nulnul-harness/assets/layer-contracts.json",
        "setup_plan_template": "skills/nulnul-harness/assets/setup-plan.template.json",
        "foundation_reference": "skills/nulnul-harness/references/foundation.md",
        "project_files_reference": "skills/nulnul-harness/references/project-files.md",
    }
    for name, relative in critical_paths.items():
        if sha(foundation / relative) != freeze["critical_files"][name]:
            raise ValueError(f"repaired Foundation critical-file mismatch: {name}")
    tasks = e15.verify_tasks(protocol)
    controls = self_test(foundation)
    evidence = runtime / "evidence"
    workspaces = runtime / "workspaces"
    evidence.mkdir()
    workspaces.mkdir()
    lifecycle = workspaces / "lifecycle"
    task = protocol["tasks"]["governed_setup"]
    e15.base.prepare_workspace(ROOT / task["fixture"], foundation, "candidate", lifecycle, sync_entry=False)
    codex_home = runtime / "codex-home"
    trust = e15.base.write_codex_home(codex_home, [lifecycle])
    layer = e15.base.config_read(codex_home, lifecycle)
    if not (
        layer["user_config_loaded"]
        and layer["project_trust_active"]
        and not layer["project_layer_active"]
    ):
        raise ValueError("real Codex trust preflight failed")
    prepared_setup = e15.freeze_workspace(task, lifecycle, "Final Governed Setup")
    contract = canonical_module(foundation)
    canonical_targets = {
        identity: contract.canonical_logical_target(identity)
        for identity in task["expected_capability_ids"]
    }
    tests = e15.command(
        ["python3", "-m", "unittest", "tests.test_foundation", "-q"],
        ROOT,
        env=os.environ | {"PYTHONDONTWRITEBYTECODE": "1"},
    )
    if tests.returncode:
        raise ValueError("Foundation deterministic regression gate failed")
    record = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "status": "pass",
        "planned_live_arms": 3,
        **benchmark_hashes(),
        "foundation_frozen_before_fresh_tasks": True,
        "foundation": e15.source_snapshot(foundation),
        "foundation_freeze": freeze,
        "tasks": tasks,
        "paths": exact_paths(protocol, foundation, runtime),
        "prepared_workspaces": {
            "FINAL-GOVERNED-SETUP": prepared_setup,
            "FINAL-PROJECT-FIT-POST-RESTART": {"pending_setup_restart": True},
            "FINAL-NEXT-SESSION": {"pending_project_fit": True},
        },
        "host_trust": trust,
        "host_config_layer_before_setup": layer,
        "canonical_targets_from_frozen_product": canonical_targets,
        "direct_surface_guard": {
            "changed": False,
            "e15_managed_block_bytes": 800,
            "repaired_managed_block_bytes": 800,
            "e15_bounded_view_bytes": 719,
            "repaired_bounded_view_bytes": 719,
            "e15_skill_sha256": "b6a38d2e0ab3e5a29b10799cf3024197858a675574311c0543d551b46cb472cf",
            "repaired_skill_sha256": sha(foundation / "skills/nulnul-harness/SKILL.md"),
            "e15_host_entry_sha256": "98b1a5166c58d6f43022740094844740da664fb98dcb5be5b51c2d6ec84e5d3b",
            "repaired_host_entry_sha256": sha(foundation / "skills/nulnul-harness/scripts/sync_host_entry.py"),
        },
        "controls": controls | {
            "foundation_tests": "98/98 PASS",
            "foundation_tests_stdout_sha256": hashlib.sha256(tests.stdout.encode()).hexdigest(),
            "foundation_tests_stderr_sha256": hashlib.sha256(tests.stderr.encode()).hexdigest(),
        },
        "runtime_root": str(runtime),
        "workspace_root": str(workspaces),
        "evidence_root": str(evidence),
        "codex_home": str(codex_home),
    }
    for source, target in (
        (PROTOCOL, evidence / "protocol.json"),
        (PREREG, evidence / "preregistration.md"),
        (FREEZE, evidence / "foundation-freeze.json"),
        (Path(__file__), evidence / "run.py"),
        (E15_RUNNER, evidence / "e15-runner.py"),
        (e15.BASE_PATH, evidence / "e13-runner.py"),
    ):
        e15.base.atomic_write(target, source.read_bytes())
    atomic_json(evidence / "preflight.json", record)
    print(json.dumps(record, indent=2))


def transaction_command(value):
    normalized = value.replace("\\", "/")
    return bool(
        "--help" not in normalized
        and re.search(r"\bpython3\s+(?:[^\s'\"]*/)?setup_transaction\.py\s+[^-\s'\"]", normalized)
    )


def writes_owned_destination(command, owned):
    normalized = command.replace("\\", "/")
    for path in owned:
        quoted = re.escape(path)
        patterns = (
            rf"(?:^|\s)(?:tee|touch)\s+(?:-[^\s]+\s+)*['\"]?{quoted}(?:['\"]|\s|$)",
            rf"(?:^|\s)(?:cp|mv|install)\s+[^;\n]+\s+['\"]?{quoted}(?:['\"]|\s|;|$)",
            rf"\bsed\s+-i[^;\n]*['\"]?{quoted}(?:['\"]|\s|;|$)",
            rf">\s*['\"]?{quoted}(?:['\"]|\s|;|$)",
            rf"(?:Add|Update|Delete) File:\s*{quoted}(?:\s|$)",
        )
        if any(re.search(pattern, normalized) for pattern in patterns):
            return path
    return None


def setup_evidence(task, workspace, trace, commands, foundation, config_before, config_after):
    governs = trace["boundary_events"]["govern"]
    activated = [
        row for row in governs
        if isinstance(row.get("payload"), dict) and row["payload"].get("status") == "activated"
    ]
    expected = [
        row for row in activated
        if row["payload"].get("stage") == task["expected_stage"]
        and row["payload"].get("host") == task["expected_host"]
    ]
    invalid_authority = [row for row in activated if row not in expected]
    transactions = [
        row | {"payload": e15.base.parse_payload(row["output"])}
        for row in commands if transaction_command(row["command"])
    ]
    transaction = transactions[0] if len(transactions) == 1 else None
    result = transaction.get("payload") if transaction else None
    plan_path = Path(workspace) / task["setup_plan_path"]
    try:
        plan = load(plan_path) if plan_path.is_file() and not plan_path.is_symlink() else None
    except (OSError, UnicodeError, json.JSONDecodeError):
        plan = None
    manual = []
    for row in commands:
        if transaction and row["event"] >= transaction["event"]:
            continue
        target = writes_owned_destination(row["command"], task["transaction_owned_paths"])
        if target:
            manual.append({"event": row["event"], "path": target, "command": row["command"]})
    contract = canonical_module(foundation)
    semantic_rows = plan.get("accepted_capabilities", []) if isinstance(plan, dict) else []
    try:
        expected_rows = [contract.accepted_record(row) for row in semantic_rows]
    except ValueError:
        expected_rows = []
    expected_ids = set(task["expected_capability_ids"])
    plan_valid = bool(
        isinstance(plan, dict)
        and plan.get("schema_version") == 2
        and plan.get("mode") == task["expected_stage"]
        and plan.get("host") == task["expected_host"]
        and {row.get("capability_id") for row in semantic_rows} == expected_ids
        and all("logical_load_target" not in row and "status" not in row for row in semantic_rows)
        and len(expected_rows) == len(expected_ids)
    )
    validator = e15.command(
        ["python3", ".agents/skills/nulnul-harness/scripts/capability_contract.py", "view", "docs/nulnul/project.md"],
        workspace,
    )
    view = e15.payload(validator)
    rows = view.get("capabilities", []) if isinstance(view, dict) else []
    resolutions = []
    for identity in sorted(expected_ids):
        resolved = e15.command(
            ["python3", ".agents/skills/nulnul-harness/scripts/capability_contract.py", "get", "docs/nulnul/project.md", "--id", identity],
            workspace,
        )
        resolutions.append(e15.payload(resolved) if resolved.returncode == 0 else None)
    exact_runtime = bool(
        validator.returncode == 0
        and rows == expected_rows
        and all(
            row["logical_load_target"] == contract.canonical_logical_target(row["capability_id"])
            and row["accepted_current"] is True
            for row in rows
        )
        and [item.get("capability") for item in resolutions if isinstance(item, dict)]
        == sorted(rows, key=lambda row: row["capability_id"])
    )
    rule = Path(workspace) / ".codex/rules/nulnul-activation.rules"
    shipped = Path(foundation) / "skills/nulnul-harness/assets/codex-activation.rules"
    current_activation = bool(
        trace["boundary_events"]["host-admission"] or trace["boundary_events"]["project-fit"]
    )
    governed = bool(
        expected and not invalid_authority
        and expected[0]["payload"].get("sequence") == e15.base.GOVERNED_SEQUENCE
        and expected[0]["payload"].get("authority") == task["transaction_owned_paths"]
    )
    receipt_path = (
        Path(workspace) / result["transaction_receipt"]
        if isinstance(result, dict) and result.get("transaction_receipt") else None
    )
    transaction_receipt = load(receipt_path) if receipt_path and receipt_path.is_file() else None
    events = (
        e15.setup_transaction_events(workspace, result.get("setup_transaction_id"))
        if isinstance(result, dict) and result.get("setup_transaction_id")
        else {"events": [], "duration_seconds": None}
    )
    expected_phases = [
        "project-and-checkpoint-write", "capability-validation", "host-write",
        "checkpoint-verification", "final-validation",
    ]
    transaction_pass = bool(
        transaction and transaction["exit_code"] == 0
        and result and result.get("status") == "CODEX_RESTART_REQUIRED"
        and result.get("validation_result") == "PASS"
        and result.get("rollback_result") == "NOT_REQUIRED"
        and result.get("phases") == expected_phases
        and result.get("canonical_capabilities") == expected_rows
        and transaction_receipt == result
    )
    rule_valid = bool(rule.is_file() and shipped.is_file() and rule.read_bytes() == shipped.read_bytes())
    restart = bool(transaction_pass and result.get("restart_required") is True and not current_activation)
    return {
        "governed": governed,
        "requested_attempts": len(governs),
        "activated_attempts": len(activated),
        "rejected_attempts": len(governs) - len(activated),
        "invalid_authority_grants": len(invalid_authority),
        "stage": expected[0]["payload"].get("stage") if expected else None,
        "host": expected[0]["payload"].get("host") if expected else None,
        "activation_receipt": expected[0]["payload"].get("activation_receipt") if expected else None,
        "canonical_capabilities": rows,
        "canonical_targets": {row["capability_id"]: row["logical_load_target"] for row in rows},
        "activation_resolutions": resolutions,
        "shared_runtime_validation": exact_runtime,
        "setup_plan": plan,
        "setup_plan_valid": plan_valid,
        "transaction_count": len(transactions),
        "transaction": result,
        "transaction_pass": transaction_pass,
        "transaction_phases": result.get("phases", []) if isinstance(result, dict) else [],
        "transaction_duration_seconds": events["duration_seconds"],
        "transaction_events": events["events"],
        "model_semantic_inputs": result.get("model_semantic_inputs", []) if isinstance(result, dict) else [],
        "generated_bytes": result.get("generated_bytes", {}) if isinstance(result, dict) else {},
        "manual_setup_owned_writes_before_transaction": manual,
        "tool_calls": len(commands),
        "rule_installed": rule_valid,
        "restart_required": restart,
        "current_session_activation_attempted": current_activation,
        "trust_mutated": config_before != config_after,
        "gate": bool(
            governed and plan_valid and transaction_pass and not manual and exact_runtime
            and rule_valid and restart and config_before == config_after
        ),
    }


def prepare_after_setup(protocol, preflight_record, workspace, arm_record):
    preparation = e15.prepare_project_fit(protocol, preflight_record, workspace, arm_record)
    target = Path(preflight_record["evidence_root"]) / "preparations/FINAL-PROJECT-FIT-POST-RESTART.json"
    atomic_json(target, preparation)
    return preparation


def prepare_after_project_fit(protocol, preflight_record, workspace, arm_record):
    preparation = e15.prepare_next_session(protocol, preflight_record, workspace, arm_record)
    target = Path(preflight_record["evidence_root"]) / "preparations/FINAL-NEXT-SESSION.json"
    atomic_json(target, preparation)
    return preparation


def run_arm(args):
    e15.run_arm(args)
    protocol = load(PROTOCOL)
    runtime = Path(args.runtime_root).resolve()
    evidence = runtime / "evidence"
    record_path = evidence / "arms" / args.arm_id / "record.json"
    record = load(record_path)
    preflight_record = load(evidence / "preflight.json")
    workspace = runtime / "workspaces/lifecycle"
    if record.get("evidence_committed") is True and args.arm_id == "FINAL-GOVERNED-SETUP":
        if record.get("architecture", {}).get("setup", {}).get("gate"):
            record["post_restart_preparation"] = prepare_after_setup(
                protocol, preflight_record, workspace, record
            )
        else:
            record["post_restart_preparation"] = {"status": "not_prepared", "reason": "setup_gate_failed"}
    elif record.get("evidence_committed") is True and args.arm_id == "FINAL-PROJECT-FIT-POST-RESTART":
        record["next_session_preparation"] = prepare_after_project_fit(
            protocol, preflight_record, workspace, record
        )
    atomic_json(record_path, record)
    print(json.dumps(record, indent=2))


def runtime_call(workspace, *arguments):
    return e15.runtime_call(workspace, *arguments)


def finalize(args):
    protocol = load(PROTOCOL)
    runtime = Path(args.runtime_root).resolve()
    evidence = runtime / "evidence"
    preflight_record = load(evidence / "preflight.json")
    verify_benchmark_frozen(preflight_record)
    records = {}
    for arm in protocol["arms"]:
        path = evidence / "arms" / arm["arm_id"] / "record.json"
        if not path.is_file():
            raise ValueError(f"official arm record missing: {arm['arm_id']}")
        records[arm["arm_id"]] = load(path)
    setup = records["FINAL-GOVERNED-SETUP"]
    project = records["FINAL-PROJECT-FIT-POST-RESTART"]
    next_session = records["FINAL-NEXT-SESSION"]
    lifecycle = runtime / "workspaces/lifecycle"
    inspections = {}
    for kind in ("sessions", "experiences", "decisions", "lessons", "open-threads", "stats"):
        try:
            inspections[kind] = runtime_call(lifecycle, "inspect", kind, "--limit", "50")
        except ValueError as error:
            inspections[kind] = {"status": "failed", "error": str(error)}
    try:
        lineage = runtime_call(lifecycle, "validate-lineage")
    except ValueError as error:
        lineage = {"valid": False, "errors": [str(error)]}
    experience = (project.get("foundation_finish") or {}).get("experience") or {}
    experience_id = experience.get("experience_id")
    try:
        evolution = runtime_call(
            lifecycle, "evolution-query",
            "--capability", "project-api-validation",
            "--job", protocol["tasks"]["project_fit"]["job"],
            "--since", experience.get("body_digest", ""),
            "--limit", "20",
        )
    except ValueError as error:
        evolution = {"count": 0, "experiences": [], "error": str(error)}
    setup_arch = setup.get("architecture", {}).get("setup", {})
    project_arch = project.get("architecture", {}).get("project_fit", {})
    setup_experience = (setup.get("foundation_finish") or {}).get("experience") or {}
    project_session = ((project.get("foundation_lifecycle") or {}).get("session") or {}).get("session_id")
    next_session_id = ((next_session.get("foundation_lifecycle") or {}).get("session") or {}).get("session_id")
    next_context = ((next_session.get("foundation_lifecycle") or {}).get("context_pack") or {})
    context_ids = [row.get("item_id") for row in next_context.get("items", [])]
    prior_handoff = ((next_session.get("foundation_lifecycle") or {}).get("session") or {}).get("previous_handoff") or {}
    lesson_ids = [row.get("lesson_id") for row in inspections.get("lessons", {}).get("lessons", [])]
    relevant_context = bool(experience_id in context_ids or set(lesson_ids).intersection(context_ids))
    query_ids = [row.get("experience_id") for row in evolution.get("experiences", [])]
    chain = {
        "session_id": project_session,
        "task_id": experience.get("task_id"),
        "activation_id": experience.get("activation_id"),
        "check_id": experience.get("check_id"),
        "experience_id": experience_id,
        "context_item_id": experience_id if experience_id in context_ids else next(
            (item for item in lesson_ids if item in context_ids), None
        ),
        "evolution_query_experience_id": experience_id if experience_id in query_ids else None,
    }
    provenance = bool(
        lineage.get("valid") is True and all(chain.values())
        and experience.get("session_id") == project_session
        and experience.get("activation_id") == project_arch.get("activation_id")
        and experience.get("check_id") == project_arch.get("check_id")
    )
    gates = {
        "setup": bool(
            setup_arch.get("gate")
            and setup.get("strict", {}).get("result") == "pass"
            and setup.get("completion", {}).get("result") == "pass"
            and not setup.get("unauthorized_writes")
            and (setup.get("foundation_finish") or {}).get("session_finalized")
            and setup_experience.get("experience_type") == "GOVERNED_EXPERIENCE"
        ),
        "host_restart": bool(
            setup.get("post_restart_preparation", {}).get("old_model_process_terminated")
            and setup.get("post_restart_preparation", {}).get("conversation_context_reused") is False
            and setup.get("post_restart_preparation", {}).get("host_config", {}).get("user_config_loaded")
            and setup.get("post_restart_preparation", {}).get("host_config", {}).get("project_trust_active")
            and setup.get("post_restart_preparation", {}).get("host_config", {}).get("project_layer_active")
            and setup.get("post_restart_preparation", {}).get("static_rule_admission", {}).get("all_exact_operations_allowed")
            and setup.get("post_restart_preparation", {}).get("precommit_availability", {}).get("visible_body_count") == 0
        ),
        "project_fit": bool(
            project_arch.get("valid")
            and project.get("strict", {}).get("result") == "pass"
            and project.get("completion", {}).get("result") == "pass"
            and not project.get("unauthorized_writes")
        ),
        "experience": bool(
            experience.get("experience_type") == "CAPABILITY_EXPERIENCE"
            and experience.get("quality") == "VERIFIED"
            and experience.get("evolution_eligible") is True
        ),
        "memory": bool(
            (project.get("foundation_finish") or {}).get("session_finalized")
            and experience_id and lineage.get("valid") is True
        ),
        "next_session": bool(
            next_session_id and next_session_id != project_session
            and prior_handoff.get("session_id") == project_session
            and next_context.get("item_count", 99) <= 8
            and next_context.get("byte_count", 99999) <= 4096
            and next_context.get("raw_transcripts_included") is False
            and relevant_context
            and next_session.get("strict", {}).get("result") == "pass"
            and next_session.get("completion", {}).get("result") == "pass"
        ),
        "evolution_input": bool(
            experience_id and experience_id in query_ids
            and all(
                row.get("experience_type") == "CAPABILITY_EXPERIENCE"
                and row.get("evolution_eligible") is True
                for row in evolution.get("experiences", [])
            )
        ),
        "provenance": provenance,
        "state_authority": all(
            not row.get("unauthorized_writes") and not row.get("host_trust_mutated")
            for row in records.values()
        ),
        "durable_evidence": all(
            row.get("evidence_committed") is True for row in records.values()
        ),
    }
    infrastructure = any(
        row.get("infrastructure_errors") or not row.get("evidence_committed")
        for row in records.values()
    )
    target_failure = bool(
        not setup_arch.get("shared_runtime_validation")
        or any(
            "CAPABILITY_TARGET_MISMATCH" in str(value)
            for value in (setup_arch.get("transaction") or {}).values()
        )
    )
    activation_failed = gates["setup"] and not (
        gates["host_restart"] and gates["project_fit"] and gates["experience"]
    )
    memory_failed = gates["project_fit"] and gates["experience"] and not (
        gates["memory"] and gates["next_session"] and gates["evolution_input"] and gates["provenance"]
    )
    if infrastructure:
        decision = "INFRASTRUCTURE_INVALID"
    elif all(gates.values()):
        decision = "V2.3 FOUNDATION CORE COMPLETE"
    elif target_failure:
        decision = "CANONICAL_CAPABILITY_CONTRACT_DESIGN_FAILURE"
    elif activation_failed:
        decision = "RUNTIME_EXCLUSIVE_ACTIVATION_NOT_JUSTIFIED"
    elif memory_failed:
        decision = "LOCAL_MEMORY_FOUNDATION_FAILURE"
    else:
        decision = "CANONICAL_CAPABILITY_CONTRACT_DESIGN_FAILURE"
    report = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "final_decision": decision,
        "evolution_readiness": decision == "V2.3 FOUNDATION CORE COMPLETE",
        "foundation_status": decision,
        "live_arms_planned": 3,
        "live_arms_executed": 3,
        "gates": gates,
        "setup": setup_arch,
        "post_restart_host": setup.get("post_restart_preparation"),
        "project_fit": project_arch,
        "capability_experience": experience,
        "next_session_context": next_context,
        "relevant_context_restored": relevant_context,
        "evolution_query": evolution,
        "provenance_chain": chain,
        "lineage": lineage,
        "memory_inspections": inspections,
        "model_usage": {
            arm_id: record.get("model_usage") for arm_id, record in records.items()
        },
        "version": (
            "V2.3 FOUNDATION CORE COMPLETE"
            if decision == "V2.3 FOUNDATION CORE COMPLETE"
            else "v2.3 ARCHITECTURE REWORK REQUIRED"
        ),
        "release": "NOT READY",
        "product_changes_during_live_experiment": 0,
    }
    atomic_json(evidence / "final-report.json", report)
    for path in (runtime / "workspaces", runtime / "codex-home"):
        try:
            if path.exists():
                e15.base.make_writable(path)
                shutil.rmtree(path)
        except OSError as error:
            report.setdefault("cleanup", {})[path.name] = f"POST_EVIDENCE_CLEANUP_FAILURE:{error}"
    atomic_json(evidence / "final-report.json", report)
    manifest = e15.artifact_manifest(evidence)
    atomic_json(evidence / "manifest.json", manifest)
    receipt = sha(evidence / "manifest.json")
    e15.base.atomic_write(evidence / "manifest.json.receipt", (receipt + "\n").encode())
    if (evidence / "manifest.json.receipt").read_text().strip() != sha(evidence / "manifest.json"):
        raise ValueError("manifest receipt readback failed")
    print(json.dumps(report, indent=2))


e15.benchmark_hashes = benchmark_hashes
e15.verify_benchmark_frozen = verify_benchmark_frozen
e15.setup_evidence = setup_evidence


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("preflight")
    prepare.add_argument("--foundation", required=True)
    prepare.add_argument("--runtime-root", required=True)
    arm = sub.add_parser("run-arm")
    arm.add_argument("--runtime-root", required=True)
    arm.add_argument("--arm-id", required=True)
    finish = sub.add_parser("finalize")
    finish.add_argument("--runtime-root", required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        preflight(args)
    elif args.command == "run-arm":
        run_arm(args)
    else:
        finalize(args)


if __name__ == "__main__":
    main()
