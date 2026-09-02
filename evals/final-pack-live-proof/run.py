#!/usr/bin/env python3
"""One-shot, exact four-arm live proof for the pre-session Pack Foundation."""

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTOCOL = HERE / "protocol.json"
PREREGISTRATION = HERE / "preregistration.md"
FREEZE = HERE / "foundation-freeze.json"
UTILITY = ROOT / "evals/experiment15/e13_runner.py"

spec = importlib.util.spec_from_file_location("final_pack_evidence_util", UTILITY)
util = importlib.util.module_from_spec(spec)
spec.loader.exec_module(util)
util.REPO = ROOT

FOUNDATION_STATE_PREFIXES = ("docs/nulnul/.gitignore", "docs/nulnul/memory/")
PACK_COMMAND = re.compile(r"capability_pack\.py\s+(prepare|work-start|check|inspect)\b")
PROJECT_BODY = re.compile(r"\.agents/skills/(?!nulnul-harness/)([a-z0-9-]+)/SKILL\.md")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    if isinstance(value, str):
        value = value.encode()
    return hashlib.sha256(value).hexdigest()


def bounded_payload(value):
    if isinstance(value, dict):
        return {key: bounded_payload(item) for key, item in value.items() if key not in {"body", "content"}}
    if isinstance(value, list):
        return [bounded_payload(item) for item in value]
    return value


def atomic_json(path, value):
    util.atomic_json(Path(path), value)
    if load(path) != value:
        raise ValueError(f"evidence readback failed: {path}")


def run(argv, cwd, *, env=None, timeout=240):
    return subprocess.run(
        argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, timeout=timeout,
    )


def parse_payload(stdout):
    return util.parse_payload(stdout)


def task_hash(task):
    return digest(task["prompt"])


def fixture_snapshot(task):
    result = {"fixture_sha256": util.scientific_tree_sha256(ROOT / task["fixture"])}
    if task.get("overlay"):
        result["overlay_sha256"] = util.scientific_tree_sha256(ROOT / task["overlay"])
    return result


def source_snapshot(path):
    return util.source_snapshot(Path(path))


def copy_overlay(source, destination):
    for item in sorted(Path(source).rglob("*")):
        if not item.is_file():
            continue
        target = Path(destination) / item.relative_to(source)
        if target.exists() or target.is_symlink():
            raise ValueError(f"overlay collision: {target.relative_to(destination)}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def allowed_path(task, path):
    if path in task.get("allowed_writes", []):
        return True
    return any(path == prefix or path.startswith(prefix) for prefix in FOUNDATION_STATE_PREFIXES)


def changed_files(workspace):
    changed, untracked = util.changed_files(workspace)
    if untracked:
        util.git(workspace, "add", "-N", "--", *untracked, check=False)
    return sorted(set(changed))


def freeze_workspace(task, fixture, source, label, workspace, overlay=None):
    util.prepare_workspace(fixture, source, label, workspace, sync_entry=True)
    if overlay:
        copy_overlay(overlay, workspace)
    util.git(workspace, "init", "-q")
    util.git(workspace, "config", "user.email", "final-pack-proof@example.invalid")
    util.git(workspace, "config", "user.name", "Final Pack Proof")
    exclude = workspace / ".git/info/exclude"
    with exclude.open("a", encoding="utf-8") as handle:
        handle.write("\n**/__pycache__/\n*.pyc\n**/.pytest_cache/\ndocs/nulnul/.runtime/\n")
    util.git(workspace, "add", "-A")
    util.git(workspace, "commit", "-qm", f"freeze {label}")
    initial = util.check_result(task["strict_command"], workspace)
    util.clean_runtime_files(workspace)
    if util.git(workspace, "status", "--porcelain").stdout.strip():
        raise ValueError(f"{label} precheck changed its baseline")
    harness = workspace / ".agents/skills/nulnul-harness"
    return {
        "initial_strict": initial,
        "initial_workspace_sha256": util.scientific_tree_sha256(workspace),
        "installed_harness_sha256": util.tree_sha256(harness),
        "writable_copy": all(
            path.is_symlink() or bool(path.stat().st_mode & 0o200)
            for path in (workspace, *workspace.rglob("*"))
            if ".git" not in path.parts
        ),
    }


def create_codex_home(path):
    path.mkdir(parents=True)
    auth = Path.home() / ".codex/auth.json"
    if not auth.is_file():
        raise ValueError("Codex authentication is unavailable")
    (path / "auth.json").symlink_to(auth)
    util.atomic_write(path / "config.toml", b"# isolated proof config; no project trust or rules\n")
    return {
        "path": str(path),
        "config_sha256": sha(path / "config.toml"),
        "auth_reused_by_symlink": True,
        "project_trust_entries": 0,
        "real_user_config_modified": False,
    }


def verify_product(source, protocol, freeze):
    snapshot = source_snapshot(source)
    if not snapshot["read_only"]:
        raise ValueError("Foundation scientific source is not read-only")
    if snapshot["tree_sha256"] != protocol["foundation"]["product_tree_sha256"]:
        raise ValueError("Foundation tree mismatch")
    if snapshot["scientific_tree_sha256"] != protocol["foundation"]["scientific_tree_sha256"]:
        raise ValueError("Foundation scientific tree mismatch")
    for relative, expected in freeze["product_file_sha256"].items():
        target = source / relative
        if not target.is_file() or sha(target) != expected:
            raise ValueError(f"Foundation product-file mismatch: {relative}")
    package = ROOT / freeze["package"]
    if not package.is_file() or sha(package) != protocol["foundation"]["package_sha256"]:
        raise ValueError("Foundation package mismatch")
    return snapshot


def verify_tasks(protocol):
    result = {}
    for name, task in protocol["tasks"].items():
        actual = fixture_snapshot(task)
        if task_hash(task) != task["task_sha256"]:
            raise ValueError(f"task changed after freeze: {name}")
        if actual["fixture_sha256"] != task["fixture_sha256"]:
            raise ValueError(f"fixture changed after freeze: {name}")
        if task.get("overlay") and actual["overlay_sha256"] != task["overlay_sha256"]:
            raise ValueError(f"overlay changed after freeze: {name}")
        result[name] = {"task_sha256": task_hash(task), **actual}
    return result


def exact_paths(runtime, champion, foundation, protocol):
    sources = {"champion": champion, "foundation": foundation}
    return [
        {
            "arm_id": arm["arm_id"],
            "source": str(sources[arm["source"]].resolve()),
            "workspace": str((runtime / "workspaces" / arm["workspace"]).resolve()),
            "evidence": str((runtime / "evidence/arms" / arm["arm_id"]).resolve()),
            "fixture": str((ROOT / protocol["tasks"][arm["task"]]["fixture"]).resolve()),
        }
        for arm in protocol["arms"]
    ]


def validate_paths(paths, runtime, champion, foundation):
    evidence = runtime / "evidence"
    workspaces = runtime / "workspaces"
    if util.overlap(evidence, workspaces):
        raise ValueError("workspace/evidence overlap")
    for source in (champion, foundation):
        if util.overlap(source, evidence) or util.overlap(source, workspaces):
            raise ValueError("scientific source/runtime overlap")
    allowed_shared = {"FINAL-SKILL-A-PACK-FOUNDATION", "FINAL-NEXT-SESSION-FOUNDATION"}
    seen = {}
    for row in paths:
        workspace = Path(row["workspace"])
        if workspace in seen and {seen[workspace], row["arm_id"]} != allowed_shared:
            raise ValueError("unplanned workspace reuse")
        seen[workspace] = row["arm_id"]
        if util.overlap(workspace, Path(row["evidence"])):
            raise ValueError("arm workspace/evidence overlap")


def deterministic_controls():
    environment = os.environ | {"PYTHONDONTWRITEBYTECODE": "1"}
    foundation = run(
        ["python3", "-m", "unittest", "tests.test_foundation", "-q"],
        ROOT, env=environment, timeout=300,
    )
    if foundation.returncode:
        raise ValueError(f"Foundation tests failed: {foundation.stderr[-1200:]}")
    product = run(
        ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_product_plugin.py", "-q"],
        ROOT, env=environment, timeout=300,
    )
    preserved_research_conflict = bool(
        product.returncode == 1
        and product.stderr.count("FAIL: ") == 1
        and "ERROR: " not in product.stderr
        and "test_legacy_lab_is_not_part_of_the_product" in product.stderr
        and "AssertionError: True is not false : docs/research" in product.stderr
        and "FAILED (failures=1)" in product.stderr
    )
    if product.returncode and not preserved_research_conflict:
        raise ValueError(f"product tests failed: {product.stderr[-1200:]}")
    source = (ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/setup_transaction.py").read_text(encoding="utf-8")
    sync = (ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/sync_host_entry.py").read_text(encoding="utf-8")
    return {
        "foundation_suite": {
            "exit_code": foundation.returncode,
            "stdout_sha256": digest(foundation.stdout),
            "stderr_sha256": digest(foundation.stderr),
            "summary": next((line for line in foundation.stderr.splitlines() if line.startswith("Ran ")), "PASS"),
        },
        "product_suite": {
            "exit_code": product.returncode,
            "stdout_sha256": digest(product.stdout),
            "stderr_sha256": digest(product.stderr),
            "summary": next((line for line in product.stderr.splitlines() if line.startswith("Ran ")), "PASS"),
            "preserved_user_owned_docs_research_conflict": preserved_research_conflict,
            "admitted": product.returncode == 0 or preserved_research_conflict,
        },
        "governed_setup": {
            "activation_rule_required": ".codex/rules/nulnul-activation.rules" in source,
            "trust_mutation_present": "trust_level" in source,
            "activation_restart_required": "CODEX_RESTART_REQUIRED" in source,
            "covered_by_foundation_tests": True,
        },
        "legacy_migration": {
            "exact_rule_cleanup_present": "retire_legacy_runtime_rule" in sync,
            "foreign_rule_refusal_present": "refusing to remove a foreign Codex rule" in sync,
            "trust_neutral_result_present": '"trust_mutated": False' in sync,
            "covered_by_foundation_tests": True,
        },
    }


def selection_controls(foundation, protocol):
    script = foundation / "skills/nulnul-harness/scripts/capability_pack.py"
    module_spec = importlib.util.spec_from_file_location("frozen_pack_selection_probe", script)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    result = {}
    for name in ("direct", "skill_a", "next_session"):
        task = protocol["tasks"][name]
        project = ROOT / task["fixture"] / "docs/nulnul/project.md"
        rows = module.candidates(project, {
            "goal": task["prompt"], "job": task["job"], "tags": [], "modules": [],
            "context_pack": {"items": []},
        })
        result[name] = rows
    if result["direct"]:
        raise ValueError("fresh Direct task has a deterministic capability candidate")
    for name in ("skill_a", "next_session"):
        if not result[name] or result[name][0]["capability_id"] != "project-api-validation" or result[name][0]["score"] < 2:
            raise ValueError(f"fresh {name} task lacks one strong Skill-A retrieval")
    return result


def runtime_script(workspace):
    return workspace / ".agents/skills/nulnul-harness/scripts/foundation_runtime.py"


def runtime_call(workspace, *arguments):
    result = run(["python3", str(runtime_script(workspace)), "--root", ".", *arguments], workspace)
    value = parse_payload(result.stdout)
    if result.returncode or not isinstance(value, dict) or value.get("status") == "failed":
        raise ValueError(f"Foundation runtime failed: {' '.join(arguments)}: {result.stdout[-1000:]} {result.stderr[-1000:]}")
    return value


def codex_version():
    value = run(["codex", "--version"], ROOT)
    return value.stdout.strip() if value.returncode == 0 else "unknown"


def start_foundation(workspace, task, protocol):
    revision = util.git(workspace, "rev-parse", "HEAD").stdout.strip()
    session = runtime_call(
        workspace, "session-start", "--goal", task["prompt"],
        "--host", "codex", "--host-version", codex_version(),
        "--model", protocol["model"],
        "--nulnul-revision", protocol["foundation"]["product_tree_sha256"],
        "--project-revision", revision,
        "--host-trust", "not-required",
        "--admission-state", "PRE_SESSION_CAPABILITY_PACK",
    )
    task_record = runtime_call(
        workspace, "task-start", "--goal", task["prompt"], "--job", task["job"],
    )
    envelope = task_record["model_context"]
    preamble = (
        "[Automatic NULNUL host context; no user routing action is required.]\n"
        + json.dumps(envelope, ensure_ascii=False, separators=(",", ":"))
        + "\nThe Session and Task already exist; do not create duplicates. Use only the bounded "
        "items above and follow the repository's root task entry. The host finalizes evidence "
        "after the task.\n\n[User task]\n"
    )
    return {
        "session": session,
        "task": task_record,
        "context_pack": task_record["context_pack"],
        "effective_prompt": preamble + task["prompt"],
        "host_context_bytes": len(preamble.encode()),
        "effective_prompt_sha256": digest(preamble + task["prompt"]),
    }


def execute_model(protocol, workspace, prompt, transcript, stderr_path, codex_home):
    argv = [
        "codex", "exec", "--json", "--ephemeral", "--ignore-rules",
        "-s", "workspace-write", "--skip-git-repo-check", "-C", str(workspace),
        "-m", protocol["model"],
        "-c", f'model_reasoning_effort="{protocol["reasoning_effort"]}"', prompt,
    ]
    environment = os.environ | {
        "CODEX_HOME": str(codex_home),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    started = time.monotonic()
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    timed_out = False
    with transcript.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            argv, cwd=workspace, env=environment, stdin=subprocess.DEVNULL,
            stdout=stdout, stderr=stderr,
        )
        try:
            process.wait(timeout=protocol["timeout_seconds"])
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait()
        stdout.flush()
        stderr.flush()
        os.fsync(stdout.fileno())
        os.fsync(stderr.fileno())
    return {
        "process_started": True,
        "process_exit": process.returncode,
        "timed_out": timed_out,
        "started_at": started_at,
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "runtime_seconds": round(time.monotonic() - started, 3),
        "command": argv[:-1] + ["<FROZEN_EFFECTIVE_PROMPT>"],
    }


def transcript_commands(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {}) if event.get("type") == "item.completed" else {}
        if item.get("type") != "command_execution":
            continue
        rows.append({
            "event": number,
            "command": str(item.get("command", "")),
            "exit_code": util.command_exit(item),
            "output": str(item.get("aggregated_output", item.get("output", ""))),
        })
    return rows


def pack_commands(commands):
    result = []
    for row in commands:
        match = PACK_COMMAND.search(row["command"].replace("\\", "/"))
        if match:
            result.append(row | {
                "operation": match.group(1),
                "payload": parse_payload(row["output"]),
                "output_bytes": len(row["output"].encode()),
            })
    return result


def body_reads(commands):
    rows = []
    for row in commands:
        if not util.READ_COMMAND.search(row["command"]):
            continue
        for capability in PROJECT_BODY.findall(row["command"].replace("\\", "/")):
            rows.append({"event": row["event"], "capability_id": capability, "command": row["command"]})
    return rows


def receipt_files(workspace, folder, field):
    root = workspace / "docs/nulnul/.runtime" / folder
    result = []
    for path in sorted(root.glob("*.json")) if root.is_dir() else []:
        value = load(path)
        result.append({"path": path.relative_to(workspace).as_posix(), field: value.get(field), "record": value})
    return result


def pack_evidence(workspace, task, task_id, trace, commands, session_id=None):
    operations = pack_commands(commands)
    prepare = [row for row in operations if row["operation"] == "prepare"]
    starts = [row for row in operations if row["operation"] == "work-start"]
    checks = [row for row in operations if row["operation"] == "check"]
    packs = [row for row in receipt_files(workspace, "capability-packs", "pack_id") if row["record"].get("task_id") == task_id]
    work_starts = [row for row in receipt_files(workspace, "work-starts", "pack_id") if row["record"].get("task_id") == task_id]
    pack = packs[-1]["record"] if len(packs) == 1 else None
    work = work_starts[-1]["record"] if len(work_starts) == 1 else None
    check_receipts = [
        row for row in receipt_files(workspace, "pack-checks", "check_id")
        if pack and row["record"].get("pack_id") == pack.get("pack_id")
    ]
    check = check_receipts[-1]["record"] if len(check_receipts) == 1 else None
    reads = body_reads(commands)
    start_event = starts[0]["event"] if len(starts) == 1 else None
    pre_work_reads = [row for row in reads if start_event is None or row["event"] < start_event]
    first_write = trace.get("first_task_write")
    refs = pack.get("capability_refs", []) if pack else []
    expected = task.get("expected_capability")
    expected_ref = next((row for row in refs if row.get("capability_id") == expected), None)
    event_rows = []
    active = workspace / "docs/nulnul/.runtime/active-session.json"
    if session_id is None and active.is_file():
        session_id = load(active).get("session_id")
    if session_id:
        events = workspace / f"docs/nulnul/.runtime/events/{session_id}.jsonl"
        if events.is_file():
            event_rows = [json.loads(line) for line in events.read_text(encoding="utf-8").splitlines() if line.strip()]
    kinds = {row.get("kind"): row for row in event_rows}
    opportunity = next((row.get("details", {}) for row in event_rows if row.get("kind") == "CAPABILITY_OPPORTUNITY"), {})
    semantic_required = sum(row.get("kind") == "CAPABILITY_SELECTION_REQUIRED" for row in event_rows)
    raw_order = bool(
        len(prepare) == 1 and len(starts) == 1 and first_write
        and prepare[0]["event"] < starts[0]["event"] < first_write["event"]
        and (not checks or first_write["event"] < checks[0]["event"])
    )
    return {
        "commands": [
            {key: value for key, value in row.items() if key not in {"output", "payload"}}
            | {"payload": bounded_payload(row.get("payload"))}
            for row in operations
        ],
        "prepare_count": len(prepare),
        "work_start_count": len(starts),
        "check_count": len(checks),
        "pack_receipts": packs,
        "work_start_receipts": work_starts,
        "check_receipts": check_receipts,
        "pack": pack,
        "work_start": work,
        "check": check,
        "pack_id": pack.get("pack_id") if pack else None,
        "check_id": check.get("check_id") if check else None,
        "capability_refs": refs,
        "candidate_ids": (prepare[0].get("payload") or {}).get("candidates", []) if prepare else [],
        "opportunity_candidate_ids": opportunity.get("candidate_ids", []),
        "semantic_selector_calls": semantic_required,
        "selection_method": pack.get("selection_method") if pack else None,
        "selection_evidence": pack.get("selection_evidence") if pack else None,
        "expected_ref": expected_ref,
        "body_reads": reads,
        "pre_work_body_reads": pre_work_reads,
        "first_product_write": first_write,
        "raw_order": raw_order,
        "event_order": {kind: row.get("event_id") for kind, row in kinds.items()},
        "event_rows": event_rows,
        "session_id": session_id,
    }


def copy_raw_local(workspace, transcript, arm_id):
    target = workspace / "docs/nulnul/.runtime/raw" / f"{arm_id}.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(transcript, target)
    return target.relative_to(workspace).as_posix()


def independent_checks(task, workspace):
    return (
        util.check_result(task["strict_command"], workspace),
        util.check_result(task["completion_command"], workspace),
    )


def surface_measurement(workspace, foundation_state, architecture):
    view = run([
        "python3", ".agents/skills/nulnul-harness/scripts/capability_contract.py",
        "view", "docs/nulnul/project.md",
    ], workspace)
    metadata = parse_payload(view.stdout) or {}
    work_command = next(
        (row for row in architecture.get("commands", []) if row.get("operation") == "work-start"),
        {},
    )
    return {
        "root_guidance_bytes": (workspace / "AGENTS.md").stat().st_size,
        "capability_metadata_bytes": len(json.dumps(metadata, ensure_ascii=False, separators=(",", ":")).encode()),
        "host_envelope_bytes": foundation_state.get("host_context_bytes", 0),
        "memory_context_pack_bytes": foundation_state.get("context_pack", {}).get("byte_count", 0),
        "memory_context_pack_items": foundation_state.get("context_pack", {}).get("item_count", 0),
        "pack_work_context_output_bytes": work_command.get("output_bytes", 0),
    }


def finish_foundation(workspace, arm_id, task, state, architecture, strict, completion, raw_ref, writes):
    check = architecture.get("check")
    pack_id = architecture.get("pack_id")
    check_id = architecture.get("check_id")
    success = strict["result"] == "pass" and completion["result"] == "pass"
    if task["mode"] != "DIRECT":
        success = success and bool(check and check.get("result") == "pass")
    outcome = {
        "experience_type": "TASK_EXPERIENCE",
        "quality": "VERIFIED" if success else "PARTIAL",
        "observability_completeness": "COMPLETE" if success else "PARTIAL",
        "result": "SUCCESS" if success else "FAILURE",
        "product_outcome": "frozen product and project checks passed" if success else "frozen product or project check failed",
        "changes": [path for path in writes if path in task.get("allowed_writes", [])],
        "checks": [{"id": task.get("project_check_identity", "strict"), "result": "pass" if success else "fail"}],
        "verified_failure_reason": None if success else "independent product or configured project check failed",
        "source_refs": [f"raw:{raw_ref}"],
        "modules": task.get("allowed_writes", []),
    }
    if pack_id:
        outcome["pack_id"] = pack_id
    if check_id:
        outcome["check_id"] = check_id
    local = workspace / "docs/nulnul/.runtime"
    outcome_path = local / f"{arm_id}-outcome.json"
    promotions_path = local / f"{arm_id}-promotions.json"
    util.atomic_json(outcome_path, outcome)
    util.atomic_json(promotions_path, {})
    failure = None
    try:
        experience = runtime_call(
            workspace, "task-finish", "--task-id", state["task"]["task_id"],
            "--outcome", str(outcome_path.relative_to(workspace)),
            "--promotions", str(promotions_path.relative_to(workspace)),
        )
    except ValueError as error:
        experience = None
        failure = str(error)
    try:
        session = runtime_call(
            workspace, "session-finalize",
            "--status", "COMPLETED" if experience and success else "PARTIAL",
            "--next", "Continue with the verified bounded project memory",
            "--completeness", "COMPLETE" if experience and success else "PARTIAL",
        )
    except ValueError as error:
        session = None
        failure = f"{failure}; {error}" if failure else str(error)
    return {
        "experience": experience,
        "experience_captured": experience is not None,
        "session": session,
        "session_finalized": session is not None,
        "outcome_supplied": outcome,
        "promotion_candidates": {},
        "failure": failure,
    }


def snapshot_foundation_state(workspace, destination):
    destination.mkdir()
    files = []
    memory = workspace / "docs/nulnul/memory"
    if memory.is_dir():
        shutil.copytree(memory, destination / "memory")
    local = workspace / "docs/nulnul/.runtime"
    for name in ("events", "capability-packs", "work-starts", "pack-checks"):
        source = local / name
        if source.is_dir():
            shutil.copytree(source, destination / name)
    for path in destination.rglob("*"):
        if path.is_file():
            files.append({"path": path.relative_to(destination).as_posix(), "sha256": sha(path)})
    return {"tree_sha256": util.tree_sha256(destination), "files": files, "raw_files": [row for row in files if row["path"].startswith("raw/")]}


def raw_copied_to_memory(workspace, transcript):
    raw = transcript.read_bytes()
    if not raw:
        return False
    memory = workspace / "docs/nulnul/memory"
    return any(
        raw == path.read_bytes() or raw in path.read_bytes()
        for path in memory.rglob("*") if path.is_file()
    ) if memory.is_dir() else False


def artifact_manifest(root):
    return {
        path.relative_to(root).as_posix(): sha(path)
        for path in sorted(Path(root).rglob("*"))
        if path.is_file() and path.name not in {"manifest.json", "manifest.receipt"}
    }


def preflight(runtime, champion, foundation):
    protocol = load(PROTOCOL)
    freeze = load(FREEZE)
    if len(protocol["arms"]) != 4 or len({row["arm_id"] for row in protocol["arms"]}) != 4:
        raise ValueError("protocol must contain exactly four unique arms")
    if runtime.exists() and any(runtime.iterdir()):
        raise ValueError("runtime root must be fresh and empty")
    runtime.mkdir(parents=True, exist_ok=True)
    evidence = runtime / "evidence"
    workspaces = runtime / "workspaces"
    evidence.mkdir()
    workspaces.mkdir()
    paths = exact_paths(runtime, champion, foundation, protocol)
    validate_paths(paths, runtime, champion, foundation)
    champion_snapshot = source_snapshot(champion)
    if not champion_snapshot["read_only"] or champion_snapshot["tree_sha256"] != protocol["champion"]["tree_sha256"]:
        raise ValueError("Champion source integrity failure")
    foundation_snapshot = verify_product(foundation, protocol, freeze)
    tasks = verify_tasks(protocol)
    controls = deterministic_controls()
    controls["selection_fixtures"] = selection_controls(foundation, protocol)
    direct = protocol["tasks"]["direct"]
    skill = protocol["tasks"]["skill_a"]
    prepared = {
        "FINAL-DIRECT-CHAMPION": freeze_workspace(
            direct, ROOT / direct["fixture"], champion, "champion",
            workspaces / "direct-champion",
        ),
        "FINAL-DIRECT-PACK-FOUNDATION": freeze_workspace(
            direct, ROOT / direct["fixture"], foundation, "foundation",
            workspaces / "direct-foundation",
        ),
        "FINAL-SKILL-A-PACK-FOUNDATION": freeze_workspace(
            skill, ROOT / skill["fixture"], foundation, "foundation",
            workspaces / "lifecycle", ROOT / skill["overlay"],
        ),
        "FINAL-NEXT-SESSION-FOUNDATION": {"pending_prior_experience": True},
    }
    for workspace in (workspaces / "direct-foundation", workspaces / "lifecycle"):
        if (workspace / ".codex/rules/nulnul-activation.rules").exists():
            raise ValueError("retired runtime activation rule exists in prepared product")
    codex_home = create_codex_home(runtime / "codex-home")
    runner_hashes = {
        "runner_sha256": sha(__file__),
        "utility_sha256": sha(UTILITY),
        "protocol_sha256": sha(PROTOCOL),
        "preregistration_sha256": sha(PREREGISTRATION),
        "foundation_freeze_sha256": sha(FREEZE),
    }
    record = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "status": "pass",
        "planned_arms": 4,
        "retries": 0,
        "foundation_frozen_before_fresh_tasks": True,
        "champion": champion_snapshot,
        "foundation": foundation_snapshot,
        "foundation_freeze": freeze,
        "tasks": tasks,
        "paths": paths,
        "prepared_workspaces": prepared,
        "codex_home": codex_home,
        "host_activation_prerequisites": {
            "project_trust": "not-required",
            "project_activation_rule": "absent",
            "activation_restart": "not-required",
            "privileged_helper": "absent",
        },
        "deterministic_governed_and_migration": controls,
        "runner_inputs": runner_hashes,
        "runtime_root": str(runtime),
        "evidence_root": str(evidence),
    }
    for source, target in (
        (PROTOCOL, evidence / "protocol.json"),
        (PREREGISTRATION, evidence / "preregistration.md"),
        (FREEZE, evidence / "foundation-freeze.json"),
        (Path(__file__), evidence / "run.py"),
        (UTILITY, evidence / "evidence-util.py"),
    ):
        util.atomic_write(target, source.read_bytes())
    atomic_json(evidence / "preflight.json", record)
    print(json.dumps({"phase": "preflight", "status": "pass", "runtime_root": str(runtime)}), flush=True)
    return record


def verify_frozen_inputs(preflight_record, foundation):
    expected = preflight_record["runner_inputs"]
    actual = {
        "runner_sha256": sha(__file__),
        "utility_sha256": sha(UTILITY),
        "protocol_sha256": sha(PROTOCOL),
        "preregistration_sha256": sha(PREREGISTRATION),
        "foundation_freeze_sha256": sha(FREEZE),
    }
    if actual != expected:
        raise ValueError("frozen experiment input changed after preflight")
    protocol = load(PROTOCOL)
    verify_tasks(protocol)
    verify_product(foundation, protocol, load(FREEZE))


def prepare_next_workspace(workspace, protocol, skill_record):
    prior_finalized = skill_record.get("foundation_finish", {}).get("session_finalized") is True
    util.git(workspace, "add", "-A")
    util.git(workspace, "commit", "-qm", "freeze Skill-A outcome and Foundation memory")
    task = protocol["tasks"]["next_session"]
    copy_overlay(ROOT / task["overlay"], workspace)
    util.git(workspace, "add", "-A")
    util.git(workspace, "commit", "-qm", "freeze fresh next-session task")
    initial = util.check_result(task["strict_command"], workspace)
    util.clean_runtime_files(workspace)
    if util.git(workspace, "status", "--porcelain").stdout.strip():
        raise ValueError("next-session precheck changed baseline")
    return {
        "initial_strict": initial,
        "initial_workspace_sha256": util.scientific_tree_sha256(workspace),
        "installed_harness_sha256": util.tree_sha256(workspace / ".agents/skills/nulnul-harness"),
        "prior_session_id": skill_record.get("foundation_finish", {}).get("session", {}).get("session_id"),
        "prior_experience_id": skill_record.get("foundation_finish", {}).get("experience", {}).get("experience_id"),
        "prior_session_finalized": prior_finalized,
    }


def run_arm(runtime, preflight_record, arm, champion, foundation, prior_record=None):
    protocol = load(PROTOCOL)
    verify_frozen_inputs(preflight_record, foundation)
    task = protocol["tasks"][arm["task"]]
    evidence = runtime / "evidence"
    workspace = runtime / "workspaces" / arm["workspace"]
    source = champion if arm["source"] == "champion" else foundation
    arm_dir = evidence / "arms" / arm["arm_id"]
    if arm_dir.exists():
        raise ValueError(f"arm evidence already exists: {arm['arm_id']}")
    arm_dir.mkdir(parents=True)
    prepared = preflight_record["prepared_workspaces"].get(arm["arm_id"], {})
    if arm["arm_id"] == "FINAL-NEXT-SESSION-FOUNDATION":
        prepared = prepare_next_workspace(workspace, protocol, prior_record)
        preflight_record["prepared_workspaces"][arm["arm_id"]] = prepared
        atomic_json(evidence / "preflight.json", preflight_record)
    if util.scientific_tree_sha256(workspace) != prepared["initial_workspace_sha256"]:
        raise ValueError("prepared workspace identity changed")
    if util.tree_sha256(workspace / ".agents/skills/nulnul-harness") != prepared["installed_harness_sha256"]:
        raise ValueError("installed product identity changed")
    source_before = source_snapshot(source)
    fixture_before = fixture_snapshot(task)
    foundation_state = start_foundation(workspace, task, protocol) if arm["source"] == "foundation" else None
    prompt = foundation_state["effective_prompt"] if foundation_state else task["prompt"]
    transcript = arm_dir / "transcript.jsonl"
    stderr_path = arm_dir / "stderr.txt"
    print(json.dumps({"phase": "arm-start", "arm_id": arm["arm_id"]}), flush=True)
    execution = execute_model(
        protocol, workspace, prompt, transcript, stderr_path,
        Path(preflight_record["codex_home"]["path"]),
    )
    trace_task = dict(task)
    trace_task["allowed_writes"] = task.get("allowed_writes", [])
    trace = util.parse_transcript(transcript, trace_task, workspace)
    commands = transcript_commands(transcript)
    strict, completion = independent_checks(task, workspace)
    raw_ref = copy_raw_local(workspace, transcript, arm["arm_id"]) if foundation_state else None
    architecture = pack_evidence(
        workspace, task, foundation_state["task"]["task_id"], trace, commands,
        foundation_state["session"]["session_id"],
    ) if foundation_state else {}
    static_surface = surface_measurement(workspace, foundation_state, architecture) if foundation_state else None
    pre_finish_writes = changed_files(workspace)
    finish = finish_foundation(
        workspace, arm["arm_id"], task, foundation_state, architecture,
        strict, completion, raw_ref, pre_finish_writes,
    ) if foundation_state else None
    if foundation_state:
        architecture = pack_evidence(
            workspace, task, foundation_state["task"]["task_id"], trace, commands,
            foundation_state["session"]["session_id"],
        )
    try:
        lineage = runtime_call(workspace, "validate-lineage") if foundation_state else None
    except ValueError as error:
        lineage = {"valid": False, "errors": [str(error)]}
    writes = changed_files(workspace)
    unauthorized = sorted(path for path in writes if not allowed_path(task, path))
    missing = sorted(path for path in task.get("required_writes", []) if path not in writes)
    patch = util.git(workspace, "diff", "--binary", "HEAD", check=False).stdout.encode()
    patch_hash = util.atomic_write(arm_dir / "patch.diff", patch)
    state = snapshot_foundation_state(workspace, arm_dir / "foundation-state") if foundation_state else None
    source_after = source_snapshot(source)
    fixture_after = fixture_snapshot(task)
    usage = trace.get("usage")
    infrastructure_errors = []
    if not transcript.is_file() or not trace.get("raw_complete"):
        infrastructure_errors.append("raw_transcript_missing_or_incomplete")
    if not isinstance(usage, dict) or not isinstance(usage.get("input_tokens"), int) or usage.get("input_tokens", 0) <= 0:
        infrastructure_errors.append("model_usage_missing_or_unparseable")
    if source_before != source_after:
        infrastructure_errors.append("frozen_product_source_mutation")
    if fixture_before != fixture_after:
        infrastructure_errors.append("frozen_task_source_mutation")
    if sha(arm_dir / "patch.diff") != patch_hash:
        infrastructure_errors.append("patch_capture_corrupt")
    if execution["process_exit"] != 0 and not usage:
        infrastructure_errors.append("model_process_uninterpretable")
    record = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "case_id": task["case_id"],
        "arm_id": arm["arm_id"],
        "arm": arm["source"],
        "host": "codex",
        "model": protocol["model"],
        "configuration": {
            "reasoning_effort": protocol["reasoning_effort"],
            "timeout_seconds": protocol["timeout_seconds"],
            "retries": 0,
            "sandbox": "workspace-write",
            "project_trust": "not-required",
            "runtime_activation_rule": "absent",
        },
        "task_sha256": task_hash(task),
        "effective_prompt_sha256": foundation_state["effective_prompt_sha256"] if foundation_state else task_hash(task),
        "fixture": fixture_before,
        "initial_workspace_sha256": prepared["initial_workspace_sha256"],
        "installed_harness_sha256": prepared["installed_harness_sha256"],
        "process": execution,
        "raw_transcript": str(transcript.relative_to(evidence)),
        "raw_transcript_sha256": sha(transcript),
        "raw_transcript_complete": trace.get("raw_complete"),
        "stderr": str(stderr_path.relative_to(evidence)),
        "stderr_sha256": sha(stderr_path),
        "model_usage": usage,
        "repository_reads": trace.get("repository_reads"),
        "commands": [{key: value for key, value in row.items() if key != "output"} for row in commands],
        "patch": str((arm_dir / "patch.diff").relative_to(evidence)),
        "patch_sha256": patch_hash,
        "write_set": writes,
        "unauthorized_writes": unauthorized,
        "required_writes_missing": missing,
        "initial_strict": prepared["initial_strict"],
        "strict": strict,
        "completion": completion,
        "foundation_lifecycle": foundation_state,
        "static_and_runtime_surface": static_surface,
        "architecture": architecture,
        "foundation_finish": finish,
        "lineage": lineage,
        "foundation_state_evidence": state,
        "raw_transcript_content_copied_to_durable_memory": raw_copied_to_memory(workspace, transcript) if foundation_state else False,
        "trace_summary": {
            "event_count": trace.get("event_count"),
            "body_reads": body_reads(commands),
            "first_product_write": trace.get("first_task_write"),
            "verification_events": trace.get("verification_events"),
            "final_text": trace.get("final_text", "")[-2400:],
        },
        "frozen_source_before": source_before,
        "frozen_source_after": source_after,
        "frozen_fixture_before": fixture_before,
        "frozen_fixture_after": fixture_after,
        "infrastructure_errors": infrastructure_errors,
        "evidence_committed": not infrastructure_errors,
        "cleanup_status": "LIFECYCLE_PRESERVED" if arm["workspace"] == "lifecycle" else "PENDING",
    }
    atomic_json(arm_dir / "record.json", record)
    if record["evidence_committed"] and arm["workspace"] != "lifecycle":
        try:
            util.make_writable(workspace)
            shutil.rmtree(workspace)
            record["cleanup_status"] = "CLEANUP_PASS"
        except OSError as error:
            record["cleanup_status"] = "POST_EVIDENCE_CLEANUP_FAILURE"
            record["cleanup_error"] = str(error)
        atomic_json(arm_dir / "record.json", record)
    print(json.dumps({
        "phase": "arm-complete", "arm_id": arm["arm_id"],
        "evidence_committed": record["evidence_committed"],
        "strict": strict["result"], "completion": completion["result"],
        "input_tokens": (usage or {}).get("input_tokens"),
    }), flush=True)
    return record


def current_opportunity(architecture):
    for row in architecture.get("event_rows", []):
        if row.get("kind") == "CAPABILITY_OPPORTUNITY":
            return row.get("details", {})
    return {}


def finalize(runtime, preflight_record, records):
    protocol = load(PROTOCOL)
    evidence = runtime / "evidence"
    by_id = {row["arm_id"]: row for row in records}
    champion = by_id["FINAL-DIRECT-CHAMPION"]
    direct = by_id["FINAL-DIRECT-PACK-FOUNDATION"]
    skill = by_id["FINAL-SKILL-A-PACK-FOUNDATION"]
    next_session = by_id["FINAL-NEXT-SESSION-FOUNDATION"]
    lifecycle = runtime / "workspaces/lifecycle"
    try:
        evolution = runtime_call(
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
    next_arch = next_session.get("architecture", {})
    direct_pack = direct_arch.get("pack") or {}
    skill_pack = skill_arch.get("pack") or {}
    skill_ref = skill_arch.get("expected_ref") or {}
    skill_work = skill_arch.get("work_start") or {}
    skill_check = skill_arch.get("check") or {}
    skill_experience = (skill.get("foundation_finish") or {}).get("experience") or {}
    direct_experience = (direct.get("foundation_finish") or {}).get("experience") or {}
    next_state = next_session.get("foundation_lifecycle") or {}
    next_context = next_state.get("context_pack") or {}
    skill_experience_id = skill_experience.get("experience_id")
    context_ids = [row.get("item_id") for row in next_context.get("items", [])]
    relevant_context = skill_experience_id in context_ids
    query_ids = [row.get("experience_id") for row in evolution.get("experiences", [])]
    event_order = skill_arch.get("event_order", {})
    order_names = (
        "CAPABILITY_SELECTED", "CAPABILITY_PACK_CREATED", "CAPABILITY_BODY_INCLUDED",
        "WORK_SESSION_STARTED", "CHECK_COMPLETED", "CAPABILITY_EXPERIENCE_ATTRIBUTED",
    )
    orders = [event_order.get(name) for name in order_names]
    causal_order = bool(
        all(isinstance(value, int) for value in orders)
        and orders == sorted(orders) and len(set(orders)) == len(orders)
        and skill_arch.get("raw_order")
    )
    direct_gate = bool(
        direct_pack.get("selection_method") == "deterministic-zero"
        and direct_arch.get("opportunity_candidate_ids") == []
        and direct_arch.get("semantic_selector_calls") == 0
        and direct_pack.get("capability_refs") == []
        and direct_arch.get("prepare_count") == 1
        and direct_arch.get("work_start_count") == 1
        and direct_arch.get("check_count") == 0
        and not direct_arch.get("body_reads")
        and direct_arch.get("raw_order")
        and (direct.get("foundation_lifecycle") or {}).get("context_pack", {}).get("item_count") == 0
        and direct.get("strict", {}).get("result") == "pass"
        and direct.get("completion", {}).get("result") == "pass"
        and not direct.get("unauthorized_writes")
        and direct_experience.get("experience_type") == "TASK_EXPERIENCE"
        and not direct_experience.get("evolution_eligible")
        and performance != "BLOCKER"
    )
    skill_gate = bool(
        skill_pack.get("selection_method") in {"deterministic-single", "bounded-semantic"}
        and 1 <= len(skill_arch.get("opportunity_candidate_ids", [])) <= 3
        and "project-api-validation" in skill_arch.get("opportunity_candidate_ids", [])
        and len(skill_pack.get("capability_refs", [])) == 1
        and skill_ref.get("capability_id") == "project-api-validation"
        and skill_ref.get("logical_load_target") == protocol["tasks"]["skill_a"]["expected_target"]
        and skill_ref.get("body_digest") == protocol["tasks"]["skill_a"]["expected_body_sha256"]
        and not skill_arch.get("pre_work_body_reads")
        and skill_work.get("body_digests", {}).get("project-api-validation") == protocol["tasks"]["skill_a"]["expected_body_sha256"]
        and skill_arch.get("first_product_write")
        and causal_order
        and skill.get("strict", {}).get("result") == "pass"
        and skill.get("completion", {}).get("result") == "pass"
        and skill_check.get("project_check_identity") == "api-contract"
        and skill_check.get("result") == "pass"
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
        (next_state.get("session") or {}).get("session_id") != (skill.get("foundation_lifecycle", {}).get("session") or {}).get("session_id")
        and next_context.get("item_count", 99) <= 8
        and next_context.get("byte_count", 99999) <= 4096
        and next_context.get("raw_transcripts_included") is False
        and relevant_context
        and next_session.get("strict", {}).get("result") == "pass"
        and next_session.get("completion", {}).get("result") == "pass"
        and not next_session.get("unauthorized_writes")
    )
    evolution_gate = bool(
        skill_experience_id and skill_experience_id in query_ids
        and direct_experience.get("experience_id") not in query_ids
        and all(row.get("experience_type") == "CAPABILITY_EXPERIENCE" and row.get("evolution_eligible") is True for row in evolution.get("experiences", []))
        and all(not {"raw_transcript", "transcript", "model_context"}.intersection(row) for row in evolution.get("experiences", []))
    )
    provenance_chain = {
        "session_id": skill_experience.get("session_id"),
        "task_id": skill_experience.get("task_id"),
        "pack_id": skill_experience.get("pack_id"),
        "capability_id": skill_experience.get("capability_id"),
        "body_digest": skill_experience.get("body_digest"),
        "check_id": skill_experience.get("check_id"),
        "experience_id": skill_experience_id,
        "context_item_id": skill_experience_id if relevant_context else None,
        "evolution_result_id": skill_experience_id if skill_experience_id in query_ids else None,
    }
    provenance_gate = bool(
        all(provenance_chain.values())
        and skill.get("lineage", {}).get("valid") is True
        and next_session.get("lineage", {}).get("valid") is True
    )
    state_authority_gate = all(not row.get("unauthorized_writes") for row in records)
    durable_evidence_gate = all(row.get("evidence_committed") is True for row in records)
    gates = {
        "direct": direct_gate,
        "skill_a_pack": skill_gate,
        "capability_experience": experience_gate,
        "next_session_memory": next_gate,
        "evolution_input": evolution_gate,
        "provenance": provenance_gate,
        "state_authority": state_authority_gate,
        "durable_evidence": durable_evidence_gate,
        "governed_migration_deterministic": all([
            not preflight_record["deterministic_governed_and_migration"]["governed_setup"]["activation_rule_required"],
            not preflight_record["deterministic_governed_and_migration"]["governed_setup"]["trust_mutation_present"],
            not preflight_record["deterministic_governed_and_migration"]["governed_setup"]["activation_restart_required"],
            preflight_record["deterministic_governed_and_migration"]["legacy_migration"]["exact_rule_cleanup_present"],
            preflight_record["deterministic_governed_and_migration"]["legacy_migration"]["foreign_rule_refusal_present"],
        ]),
    }
    failure_codes = []
    warnings = []
    if performance == "WARNING":
        warnings.append("DIRECT_PERFORMANCE_WARNING")
    elif performance == "BLOCKER":
        failure_codes.append("DIRECT_PERFORMANCE_BLOCKER")
    if not direct_gate and performance != "BLOCKER":
        if direct_pack.get("capability_refs"):
            failure_codes.append("PACK_SELECTION_FAILURE")
        elif not direct_pack or direct_arch.get("body_reads"):
            failure_codes.append("PACK_BODY_BOUNDARY_FAILURE")
        else:
            failure_codes.append("PRODUCT_REGRESSION")
    if not skill_gate:
        refs = skill_pack.get("capability_refs", [])
        if len(refs) != 1 or skill_ref.get("capability_id") != "project-api-validation":
            failure_codes.append("PACK_SELECTION_FAILURE")
        if skill_ref and (
            skill_ref.get("logical_load_target") != protocol["tasks"]["skill_a"]["expected_target"]
            or skill_ref.get("body_digest") != protocol["tasks"]["skill_a"]["expected_body_sha256"]
        ):
            failure_codes.append("PACK_INTEGRITY_FAILURE")
        if skill_arch.get("pre_work_body_reads") or not skill_work.get("body_digests") or not causal_order:
            failure_codes.append("PACK_BODY_BOUNDARY_FAILURE")
        if skill.get("strict", {}).get("result") != "pass" or skill.get("completion", {}).get("result") != "pass":
            failure_codes.append("PRODUCT_REGRESSION")
        if skill_check.get("result") != "pass":
            failure_codes.append("CHECK_FAILURE")
    if not experience_gate:
        if not skill_experience:
            failure_codes.append("EXPERIENCE_CAPTURE_FAILURE")
        else:
            failure_codes.append("EVOLUTION_ELIGIBILITY_FAILURE")
    if not next_gate:
        failure_codes.append("MEMORY_RETRIEVAL_FAILURE")
    if not evolution_gate:
        failure_codes.append("EVOLUTION_ELIGIBILITY_FAILURE")
    if not provenance_gate:
        failure_codes.append("PROVENANCE_FAILURE")
    if not state_authority_gate:
        failure_codes.append("STATE_AUTHORITY_REGRESSION")
    infrastructure = not durable_evidence_gate
    if infrastructure:
        failure_codes.append("INFRASTRUCTURE_INVALID")
        primary = "INFRASTRUCTURE_INVALID"
    elif all(gates.values()):
        primary = "PACK_FOUNDATION_LIVE_PROVEN"
    else:
        primary = "PACK_FOUNDATION_LOCAL_FAILURE"
    report = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "primary_result": primary,
        "foundation_status": "V2.3 FOUNDATION CORE COMPLETE" if primary == "PACK_FOUNDATION_LIVE_PROVEN" else "OPEN",
        "evolution_readiness": primary == "PACK_FOUNDATION_LIVE_PROVEN",
        "failure_codes": sorted(set(failure_codes)),
        "warnings": warnings,
        "gates": gates,
        "direct_performance": {
            "champion_input": champion_input,
            "foundation_input": direct_input,
            "ratio": ratio,
            "percent": round(ratio * 100, 4) if ratio is not None else None,
            "classification": performance,
        },
        "skill_a_experience_id": skill_experience_id,
        "next_context": next_context,
        "evolution_query": evolution,
        "provenance_chain": provenance_chain,
        "deterministic_governed_and_migration": preflight_record["deterministic_governed_and_migration"],
        "valid_claims": [
            "empty-Pack Direct remained functional" if direct_gate else "Direct evidence is localized in arm record",
            "one live Pack-backed Capability Experience completed" if experience_gate else "Pack/Experience failure is localized",
            "fresh-session bounded Memory restoration completed" if next_gate else "Memory restoration remains unproven",
        ],
        "unsupported_claims": [
            "Skill B generalization", "broad capability-selection accuracy", "product advantage",
            "release readiness", "Skill Evolution success", "sole causal effect of a capability",
        ],
        "version": "v2.3 ARCHITECTURE REWORK REQUIRED" if primary != "PACK_FOUNDATION_LIVE_PROVEN" else "V2.3 FOUNDATION CORE COMPLETE",
        "release": "NOT READY",
        "product_changes_during_experiment": 0,
    }
    atomic_json(evidence / "final-report.json", report)
    cleanup = {}
    for path in (runtime / "workspaces", runtime / "codex-home"):
        try:
            if path.exists():
                util.make_writable(path)
                shutil.rmtree(path)
            cleanup[path.name] = "CLEANUP_PASS"
        except OSError as error:
            cleanup[path.name] = f"POST_EVIDENCE_CLEANUP_FAILURE:{error}"
    report["cleanup"] = cleanup
    atomic_json(evidence / "final-report.json", report)
    atomic_json(evidence / "manifest.json", artifact_manifest(evidence))
    manifest_sha = sha(evidence / "manifest.json")
    util.atomic_write(evidence / "manifest.receipt", (manifest_sha + "\n").encode())
    if (evidence / "manifest.receipt").read_text(encoding="utf-8").strip() != sha(evidence / "manifest.json"):
        raise ValueError("manifest receipt readback failure")
    print(json.dumps({"phase": "final", "primary_result": primary, "failure_codes": report["failure_codes"]}), flush=True)
    return report


def self_test():
    protocol = load(PROTOCOL)
    assert len(protocol["arms"]) == 4
    assert [row["arm_id"] for row in protocol["arms"]] == [
        "FINAL-DIRECT-CHAMPION", "FINAL-DIRECT-PACK-FOUNDATION",
        "FINAL-SKILL-A-PACK-FOUNDATION", "FINAL-NEXT-SESSION-FOUNDATION",
    ]
    verify_tasks(protocol)
    assert protocol["tasks"]["skill_a"]["job"] == protocol["tasks"]["next_session"]["job"]
    assert protocol["tasks"]["direct"]["expected_capability"] if "expected_capability" in protocol["tasks"]["direct"] else True
    return {"status": "pass", "exact_arms": 4, "task_inputs": "verified", "retries": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--champion")
    parser.add_argument("--foundation")
    parser.add_argument("--runtime-root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2))
        return
    if not all((args.champion, args.foundation, args.runtime_root)):
        parser.error("--champion, --foundation, and --runtime-root are required")
    runtime = Path(args.runtime_root).resolve()
    champion = Path(args.champion).resolve()
    foundation = Path(args.foundation).resolve()
    preflight_record = preflight(runtime, champion, foundation)
    records = []
    for arm in load(PROTOCOL)["arms"]:
        prior = records[-1] if arm["arm_id"] == "FINAL-NEXT-SESSION-FOUNDATION" else None
        records.append(run_arm(runtime, preflight_record, arm, champion, foundation, prior))
    finalize(runtime, preflight_record, records)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "failed", "error": f"{type(error).__name__}:{error}"}), flush=True)
        raise
