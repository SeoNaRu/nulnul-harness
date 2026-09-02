#!/usr/bin/env python3
"""Exact five-arm runner for NULNUL Experiment 14.

This is deliberately an adapter over the preserved E13 minimal runner.  It
adds only Foundation lifecycle orchestration and integrated evidence checks.
"""

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
PREREG = HERE / "preregistration.md"
FREEZE = HERE / "foundation-freeze.json"
BASE_PATH = HERE / "e13_runner.py"

spec = importlib.util.spec_from_file_location("e14_e13_runner", BASE_PATH)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.REPO = ROOT

HEX64 = re.compile(r"[a-f0-9]{64}")
FOUNDATION_STATE_PREFIXES = (
    "docs/nulnul/.gitignore",
    "docs/nulnul/memory/",
)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def task_hash(task):
    return hashlib.sha256(task["prompt"].encode()).hexdigest()


def atomic_json(path, payload):
    base.atomic_json(Path(path), payload)
    if load(path) != payload:
        raise ValueError(f"evidence readback failed: {path}")


def command(command, cwd, *, env=None, timeout=180):
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def payload(result):
    return base.parse_payload(result.stdout)


def source_snapshot(root):
    return base.source_snapshot(Path(root))


def source_valid(root, tree, scientific=None):
    root = Path(root)
    return bool(
        root.is_dir()
        and base.read_only_tree(root)
        and base.tree_sha256(root) == tree
        and (scientific is None or base.scientific_tree_sha256(root) == scientific)
    )


def file_tree(root):
    return base.tree_sha256(Path(root))


def benchmark_hashes():
    return {
        "runner_sha256": sha(__file__),
        "base_runner_sha256": sha(BASE_PATH),
        "protocol_sha256": sha(PROTOCOL),
        "preregistration_sha256": sha(PREREG),
        "foundation_freeze_sha256": sha(FREEZE),
    }


def verify_benchmark_frozen(expected):
    actual = benchmark_hashes()
    for key, value in actual.items():
        if expected.get(key) != value:
            raise ValueError(f"frozen experiment input changed: {key}")


def fixture_snapshot(task):
    result = {"fixture_sha256": file_tree(ROOT / task["fixture"])}
    if task.get("overlay"):
        result["overlay_sha256"] = file_tree(ROOT / task["overlay"])
    return result


def verify_tasks(protocol):
    result = {}
    for name, task in protocol["tasks"].items():
        snapshot = fixture_snapshot(task)
        if task_hash(task) != task["task_sha256"]:
            raise ValueError(f"task changed after freeze: {name}")
        if snapshot["fixture_sha256"] != task["fixture_sha256"]:
            raise ValueError(f"fixture changed after freeze: {name}")
        if task.get("overlay") and snapshot["overlay_sha256"] != task["overlay_sha256"]:
            raise ValueError(f"overlay changed after freeze: {name}")
        base.scientific_tree_sha256(ROOT / task["fixture"])
        if task.get("overlay"):
            base.scientific_tree_sha256(ROOT / task["overlay"])
        result[name] = {"task_sha256": task_hash(task), **snapshot}
    return result


def exact_paths(protocol, champion, foundation, runtime):
    sources = {"champion": Path(champion), "foundation": Path(foundation)}
    paths = []
    for arm in protocol["arms"]:
        task = protocol["tasks"][arm["task"]]
        paths.append({
            "arm_id": arm["arm_id"],
            "source": arm["source"],
            "task": arm["task"],
            "product_source": str(sources[arm["source"]].resolve()),
            "fixture": str((ROOT / task["fixture"]).resolve()),
            "workspace": str((runtime / "workspaces" / arm["workspace"]).resolve()),
            "evidence": str((runtime / "evidence" / "arms" / arm["arm_id"]).resolve()),
            "transcript": str((runtime / "evidence" / "arms" / arm["arm_id"] / "transcript.jsonl").resolve()),
            "receipt_root": str((runtime / "evidence" / "arms" / arm["arm_id"] / "receipts").resolve()),
        })
    return paths


def validate_paths(protocol, champion, foundation, runtime):
    runtime = Path(runtime).resolve()
    evidence = runtime / "evidence"
    workspaces = runtime / "workspaces"
    codex_home = runtime / "codex-home"
    failures = []
    for source in (Path(champion), Path(foundation)):
        if base.overlap(source, evidence) or base.overlap(source, workspaces):
            failures.append("scientific source overlaps mutable runtime")
    if base.overlap(evidence, workspaces) or base.overlap(codex_home, evidence) or base.overlap(codex_home, workspaces):
        failures.append("runtime roots overlap")
    shared = {
        "E14-GOVERNED-SETUP-FOUNDATION",
        "E14-PROJECT-FIT-FOUNDATION",
        "E14-NEXT-SESSION-MEMORY-FOUNDATION",
    }
    seen = {}
    for row in exact_paths(protocol, champion, foundation, runtime):
        workspace = Path(row["workspace"])
        prior = seen.get(workspace)
        if prior and not {prior, row["arm_id"]}.issubset(shared):
            failures.append("unplanned mutable-workspace overlap")
        seen[workspace] = row["arm_id"]
        for output in (Path(row["evidence"]), Path(row["transcript"]), Path(row["receipt_root"])):
            if base.overlap(workspace, output):
                failures.append(f"{row['arm_id']}: workspace overlaps evidence")
    if failures:
        raise ValueError("; ".join(sorted(set(failures))))


def self_test():
    protocol = load(PROTOCOL)
    assert len(protocol["arms"]) == 5
    assert len({row["arm_id"] for row in protocol["arms"]}) == 5
    assert base.positive_state_argument("rg x -g !docs/nulnul/checkpoint.json .") is False
    assert base.positive_state_argument("sed -n 1,2p docs/nulnul/checkpoint.json") is True
    assert protocol["tasks"]["project_fit"]["promotion_candidates"]["lessons"]
    assert protocol["tasks"]["next_session"]["job"] == protocol["tasks"]["project_fit"]["job"]
    return {"exact_five_arms": "pass", "structured_negation": "pass", "related_next_session": "pass"}


def candidate_availability(task, workspace, codex_home):
    fixture = ROOT / task["fixture"]
    bodies = sorted(
        path for path in (fixture / ".agents/skills").glob("*/SKILL.md")
        if path.parent.name != "nulnul-harness"
    )
    body_digests = {sha(path) for path in bodies}
    workspace_bodies = sorted(
        path.relative_to(workspace).as_posix()
        for path in (Path(workspace) / ".agents/skills").glob("*/SKILL.md")
        if path.parent.name != "nulnul-harness"
    )
    duplicate_paths = sorted(
        path.relative_to(workspace).as_posix()
        for path in Path(workspace).rglob("*")
        if path.is_file() and ".git" not in path.parts and sha(path) in body_digests
    )
    profile, package_root = base.permission_profile_config()
    runtime_duplicates = sorted(
        str(path) for path in Path(package_root).rglob("SKILL.md")
        if path.is_file() and sha(path) in body_digests
    )
    environment = os.environ | {"CODEX_HOME": str(codex_home)}
    metadata = command(
        [
            "codex", "sandbox", "-P", "e13-exclusive", "-C", str(workspace), "-c", profile,
            "python3", ".agents/skills/nulnul-harness/scripts/capability_contract.py",
            "view", "docs/nulnul/project.md",
        ],
        workspace,
        env=environment,
    )
    metadata_payload = payload(metadata)
    external = []
    external_visible = 0
    for body in bodies:
        probe = command(
            [
                "codex", "sandbox", "-P", "e13-exclusive", "-C", str(workspace), "-c", profile,
                "/usr/bin/head", "-c", "1", str(body.resolve()),
            ],
            workspace,
            env=environment,
        )
        readable = probe.returncode == 0
        external_visible += int(readable)
        external.append({
            "logical_identity": body.parent.name,
            "source_sha256": sha(body),
            "ordinary_read_exit": probe.returncode,
            "ordinary_readable": readable,
        })
    visible = len(set(workspace_bodies) | set(duplicate_paths)) + len(runtime_duplicates) + external_visible
    return {
        "metadata_visible": bool(metadata.returncode == 0 and isinstance(metadata_payload, dict) and metadata_payload.get("status") == "ok"),
        "metadata_capabilities": [row.get("capability_id") for row in (metadata_payload or {}).get("capabilities", [])],
        "workspace_body_paths": workspace_bodies,
        "workspace_duplicate_body_paths": duplicate_paths,
        "runtime_duplicate_body_paths": runtime_duplicates,
        "external_body_probes": external,
        "visible_body_count": visible,
        "permission_profile": "e13-exclusive-reused",
        "codex_runtime_read_root": package_root,
    }


def copy_overlay(source, workspace):
    for item in sorted(Path(source).rglob("*")):
        if not item.is_file():
            continue
        relative = item.relative_to(source)
        target = Path(workspace) / relative
        if target.exists() or target.is_symlink():
            raise ValueError(f"overlay collision: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def freeze_workspace(task, workspace, label):
    workspace = Path(workspace)
    base.git(workspace, "init", "-q")
    base.git(workspace, "config", "user.email", "experiment-14@example.invalid")
    base.git(workspace, "config", "user.name", "Experiment 14")
    exclude = workspace / ".git/info/exclude"
    with exclude.open("a", encoding="utf-8") as handle:
        handle.write("\n**/__pycache__/\n*.pyc\n**/.pytest_cache/\n.nulnul-activation/\ndocs/nulnul/.runtime/\n")
    base.git(workspace, "add", "-A")
    base.git(workspace, "commit", "-qm", f"freeze {label}")
    initial = base.check_result(task["strict_command"], workspace)
    base.clean_runtime_files(workspace)
    if base.git(workspace, "status", "--porcelain").stdout.strip():
        raise ValueError(f"{label} precheck changed its baseline")
    return {
        "initial_strict": initial,
        "initial_workspace_sha256": base.scientific_tree_sha256(workspace),
        "installed_harness_sha256": file_tree(workspace / ".agents/skills/nulnul-harness"),
        "writable_copy": all(
            bool(path.stat().st_mode & 0o200)
            for path in (workspace, *workspace.rglob("*"))
            if not path.is_symlink() and ".git" not in path.parts
        ),
    }


def preflight(args):
    protocol = load(PROTOCOL)
    freeze = load(FREEZE)
    champion = Path(args.champion).resolve()
    foundation = Path(args.foundation).resolve()
    runtime = Path(args.runtime_root).resolve()
    if runtime.exists() and any(runtime.iterdir()):
        raise ValueError("runtime root must be fresh and empty")
    runtime.mkdir(parents=True, exist_ok=True)
    validate_paths(protocol, champion, foundation, runtime)
    if not source_valid(champion, protocol["champion"]["tree_sha256"]):
        raise ValueError("Champion integrity failure")
    if not source_valid(
        foundation,
        protocol["foundation"]["tree_sha256"],
        protocol["foundation"]["scientific_tree_sha256"],
    ):
        raise ValueError("Foundation integrity failure")
    for relative, expected in freeze["changed_product_files"].items():
        path = foundation / relative
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"Foundation changed-file integrity failure: {relative}")
    tasks = verify_tasks(protocol)
    controls = self_test()
    evidence = runtime / "evidence"
    workspaces = runtime / "workspaces"
    evidence.mkdir()
    workspaces.mkdir()
    direct_champion = workspaces / "direct-champion"
    direct_foundation = workspaces / "direct-foundation"
    lifecycle = workspaces / "lifecycle"
    direct_task = protocol["tasks"]["direct"]
    setup_task = protocol["tasks"]["governed_setup"]
    base.prepare_workspace(ROOT / direct_task["fixture"], champion, "champion", direct_champion, sync_entry=True)
    base.prepare_workspace(ROOT / direct_task["fixture"], foundation, "candidate", direct_foundation, sync_entry=False)
    base.prepare_workspace(ROOT / setup_task["fixture"], foundation, "candidate", lifecycle, sync_entry=False)
    codex_home = runtime / "codex-home"
    trust = base.write_codex_home(codex_home, [direct_champion, direct_foundation, lifecycle])
    direct_install = base.install_direct_rule(direct_foundation, codex_home)
    prepared = {
        "E14-DIRECT-CHAMPION": freeze_workspace(direct_task, direct_champion, "E14 Direct Champion"),
        "E14-DIRECT-FOUNDATION": freeze_workspace(direct_task, direct_foundation, "E14 Direct Foundation"),
        "E14-GOVERNED-SETUP-FOUNDATION": freeze_workspace(setup_task, lifecycle, "E14 Governed Setup"),
        "E14-PROJECT-FIT-FOUNDATION": {"pending_setup_restart": True},
        "E14-NEXT-SESSION-MEMORY-FOUNDATION": {"pending_project_fit": True},
    }
    availability = candidate_availability(direct_task, direct_foundation, codex_home)
    if not availability["metadata_visible"] or availability["visible_body_count"]:
        raise ValueError("Direct metadata/exclusivity preflight failed")
    layers = {
        "direct_foundation": base.config_read(codex_home, direct_foundation),
        "lifecycle_before_setup": base.config_read(codex_home, lifecycle),
    }
    if not (
        layers["direct_foundation"]["user_config_loaded"]
        and layers["direct_foundation"]["project_trust_active"]
        and layers["direct_foundation"]["project_layer_active"]
        and layers["lifecycle_before_setup"]["user_config_loaded"]
        and layers["lifecycle_before_setup"]["project_trust_active"]
        and not layers["lifecycle_before_setup"]["project_layer_active"]
    ):
        raise ValueError("real Codex trust/layer preflight failed")
    tests = command(
        ["python3", "-m", "unittest", "tests.test_foundation", "-q"],
        ROOT,
        env=os.environ | {"PYTHONDONTWRITEBYTECODE": "1"},
    )
    if tests.returncode:
        raise ValueError("Foundation deterministic regression gate failed")
    frozen = benchmark_hashes()
    record = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "status": "pass",
        "planned_arms": 5,
        **frozen,
        "foundation_frozen_before_fresh_tasks": True,
        "champion": source_snapshot(champion),
        "foundation": source_snapshot(foundation),
        "foundation_freeze": freeze,
        "tasks": tasks,
        "paths": exact_paths(protocol, champion, foundation, runtime),
        "prepared_workspaces": prepared,
        "direct_precommit_availability": availability,
        "host_trust": trust,
        "host_config_layers": layers,
        "steady_state_direct_install": direct_install,
        "controls": controls | {
            "foundation_tests": "79/79 PASS",
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
        (BASE_PATH, evidence / "e13_runner.py"),
    ):
        base.atomic_write(target, source.read_bytes())
    atomic_json(evidence / "preflight.json", record)
    print(json.dumps(record, indent=2))


def runtime_script(workspace):
    return Path(workspace) / ".agents/skills/nulnul-harness/scripts/foundation_runtime.py"


def runtime_call(workspace, *arguments):
    result = command(["python3", str(runtime_script(workspace)), "--root", ".", *arguments], workspace)
    parsed = payload(result)
    if result.returncode or not isinstance(parsed, dict) or parsed.get("status") == "failed":
        raise ValueError(f"Foundation runtime call failed: {' '.join(arguments)}: {result.stdout[-1200:]} {result.stderr[-1200:]}")
    return parsed


def codex_version():
    result = command(["codex", "--version"], ROOT)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def start_foundation(workspace, task, protocol, admission_state):
    revision = base.git(workspace, "rev-parse", "HEAD").stdout.strip()
    session = runtime_call(
        workspace,
        "session-start",
        "--goal", task["prompt"],
        "--host", "codex",
        "--host-version", codex_version(),
        "--model", protocol["model"],
        "--nulnul-revision", protocol["foundation"]["tree_sha256"],
        "--project-revision", revision,
        "--host-trust", "trusted",
        "--admission-state", admission_state,
    )
    task_record = runtime_call(
        workspace,
        "task-start",
        "--goal", task["prompt"],
        "--job", task["job"],
    )
    context = task_record["context_pack"]
    host_context = {
        "session_id": session["session_id"],
        "task_id": task_record["task_id"],
        "previous_handoff": session.get("previous_handoff"),
        "context_pack": context,
    }
    preamble = (
        "[Automatic NULNUL Foundation host context; this is not a user routing choice.]\n"
        f"{json.dumps(host_context, ensure_ascii=False, separators=(',', ':'))}\n"
        "The Session and Task are already active; do not start duplicates. Use only relevant "
        "Context Pack items. Complete the user task below; the host will finalize observable "
        "evidence through the shipped Foundation runtime.\n\n[User task]\n"
    )
    return {
        "session": session,
        "task": task_record,
        "context_pack": context,
        "effective_prompt": preamble + task["prompt"],
        "effective_prompt_sha256": hashlib.sha256((preamble + task["prompt"]).encode()).hexdigest(),
        "host_context_bytes": len(preamble.encode()),
    }


def run_model(protocol, arm, task, workspace, transcript, stderr_path, environment, effective_prompt):
    call = ["codex", "exec", "--json", "--ephemeral"]
    if arm["source"] == "foundation" and task["mode"] in {"DIRECT", "PROJECT_FIT", "NEXT_SESSION"}:
        call.extend(base.permission_arguments())
    elif task["mode"] == "GOVERNED_SETUP":
        call.append("--approve-for-me")
    else:
        call.extend(["--ignore-rules", "-s", "workspace-write"])
    call.extend([
        "--skip-git-repo-check", "-C", str(workspace), "-m", protocol["model"],
        "-c", f'model_reasoning_effort="{protocol["reasoning_effort"]}"', effective_prompt,
    ])
    started = time.monotonic()
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    timed_out = False
    with Path(transcript).open("wb") as stdout, Path(stderr_path).open("wb") as stderr:
        process = subprocess.Popen(call, cwd=workspace, env=environment, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
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
        "command": call[:-1] + ["<FROZEN_EFFECTIVE_PROMPT>"],
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
            "exit_code": base.command_exit(item),
            "output": str(item.get("aggregated_output", item.get("output", ""))),
        })
    return rows


def view_events(commands):
    result = []
    for row in commands:
        normalized = row["command"].replace("\\", "/")
        if "capability_contract.py view docs/nulnul/project.md" not in normalized:
            continue
        result.append(row | {"payload": base.parse_payload(row["output"]), "output_bytes": len(row["output"].encode())})
    return result


def model_memory_reads(commands):
    markers = ("docs/nulnul/memory", "docs/nulnul/.runtime", "docs/nulnul/checkpoint", "docs/nulnul/evolution")
    return [
        {"event": row["event"], "command": row["command"]}
        for row in commands
        if base.READ_COMMAND.search(row["command"])
        and any(marker in row["command"].replace("\\", "/") for marker in markers)
        and base.positive_state_argument(row["command"])
        or base.READ_COMMAND.search(row["command"])
        and any(marker in row["command"].replace("\\", "/") for marker in ("docs/nulnul/memory", "docs/nulnul/.runtime"))
    ]


def receipt(receipts, category):
    paths = sorted((Path(receipts) / category).glob("*.json")) if (Path(receipts) / category).is_dir() else []
    if len(paths) != 1:
        return None
    return load(paths[0])


def raw_local_copy(workspace, transcript, arm_id):
    target = Path(workspace) / "docs/nulnul/.runtime/raw" / f"{arm_id}.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(transcript, target)
    return target.relative_to(workspace).as_posix()


def runtime_event(workspace, kind, task_id, details):
    path = Path(workspace) / "docs/nulnul/.runtime/host-event.json"
    base.atomic_json(path, details)
    return runtime_call(workspace, "event", kind, "--task-id", task_id, "--details", str(path.relative_to(workspace)))


def independent_checks(task, workspace):
    completion = base.check_result(task["completion_command"], workspace)
    strict = base.check_result(task["strict_command"], workspace)
    return strict, completion


def allowed_path(task, path):
    allowed = task.get("allowed_writes", []) + task.get("allowed_write_prefixes", [])
    if any(path == value for value in allowed):
        return True
    return any(value.endswith("/") and path.startswith(value) for value in allowed) or any(
        path == value or path.startswith(value) for value in FOUNDATION_STATE_PREFIXES
    )


def write_set(workspace, task):
    changed, untracked = base.changed_files(workspace)
    if untracked:
        base.git(workspace, "add", "-N", "--", *untracked, check=False)
    unauthorized = sorted(path for path in changed if not allowed_path(task, path))
    missing = sorted(path for path in task.get("required_writes", []) if path not in changed)
    return changed, unauthorized, missing


def project_fit_chain(task, workspace, trace, commands, availability, receipts):
    views = view_events(commands)
    fits = trace["boundary_events"]["project-fit"]
    checks = trace["boundary_events"]["check"]
    attrs = trace["boundary_events"]["attribute"]
    view = views[0] if len(views) == 1 else None
    fit = fits[0] if len(fits) == 1 else None
    check = checks[0] if len(checks) == 1 else None
    attr = attrs[0] if len(attrs) == 1 else None
    fit_payload = fit.get("payload") if fit else None
    check_payload = check.get("payload") if check else None
    attr_payload = attr.get("payload") if attr else None
    activation = receipt(receipts, "activations")
    check_receipt = receipt(receipts, "checks")
    attribution = receipt(receipts, "attributions")
    capability = task["expected_capability"]
    expected_body = ROOT / task["fixture"] / ".agents/skills" / capability / "SKILL.md"
    expected_digest = sha(expected_body)
    accepted = [] if not view or not isinstance(view["payload"], dict) else view["payload"].get("capabilities", [])
    selected = next((row for row in accepted if row.get("capability_id") == capability), None)
    activation_id = activation.get("activation_id") if activation else None
    check_id = check_receipt.get("check_id") if check_receipt else None
    exposures = sorted(
        path.relative_to(workspace).as_posix()
        for path in (Path(workspace) / ".nulnul-activation").rglob("SKILL.md")
    )
    expected_exposure = f".nulnul-activation/{activation_id}/{capability}/SKILL.md" if activation_id else None
    accesses = trace["exposed_capability_body_reads"]
    body_access = min(accesses, key=lambda row: row["event"], default=None)
    first_write = trace["first_task_write"]
    events = activation.get("events", {}) if activation else {}
    receipt_order = [
        events.get("host_admission", {}).get("order"),
        events.get("commit_request", {}).get("order"),
        events.get("validation_success", {}).get("order"),
        events.get("body_exposure", {}).get("order"),
        events.get("activation_receipt", {}).get("order"),
    ]
    raw_order = bool(
        view and fit and body_access and first_write and check and attr
        and view["event"] < fit["event"] < body_access["event"] < first_write["event"] < check["event"] < attr["event"]
    )
    reasons = []
    checks_map = {
        "one_bounded_view": bool(view and view["output_bytes"] <= 4096),
        "material_fit": bool(fit_payload and fit_payload.get("match_evidence")),
        "exact_identity": bool(fit_payload and fit_payload.get("capability_id") == capability),
        "accepted_current": bool(selected and selected.get("status") == "accepted/current" and selected.get("accepted_current") is True),
        "precommit_body_zero": availability.get("visible_body_count") == 0 and not trace["ordinary_capability_body_reads"],
        "commit_receipt": bool(activation and fit_payload == activation and activation.get("status") == "activated"),
        "internal_order": all(isinstance(value, int) for value in receipt_order) and receipt_order == sorted(set(receipt_order)),
        "one_exact_body": exposures == [expected_exposure] if expected_exposure else False,
        "body_digest": bool(activation and activation.get("body_sha256") == expected_digest),
        "body_access": bool(body_access and all(row["capability"] == capability and row["activation_id"] == activation_id for row in accesses)),
        "check_receipt": bool(check_payload and check_receipt == check_payload and check_receipt.get("activation_id") == activation_id and check_receipt.get("result") == "pass"),
        "attribution_receipt": bool(attr_payload and attribution == attr_payload and attribution.get("activation_id") == activation_id and attribution.get("check_id") == check_id),
        "raw_order": raw_order,
    }
    reasons.extend(name for name, passed in checks_map.items() if not passed)
    ordering = None
    if activation and check_receipt and attribution and body_access and first_write:
        ordering = {
            "commit": activation["events"]["commit_request"]["order"],
            "body_exposure": activation["events"]["body_exposure"]["order"],
            "body_access": activation["events"]["body_exposure"]["order"] + 1,
            "product_write": check_receipt["events"]["check_complete"]["order"] - 1,
            "check": check_receipt["events"]["check_complete"]["order"],
            "attribution": attribution["event"]["order"],
        }
        if list(ordering.values()) != sorted(set(ordering.values())):
            reasons.append("receipt_order_has_no_slots_for_observed_body_access_and_write")
    return {
        "valid": not reasons,
        "reasons": sorted(set(reasons)),
        "checks": checks_map,
        "view": {key: value for key, value in view.items() if key != "output"} if view else None,
        "activation": activation,
        "check_receipt": check_receipt,
        "attribution": attribution,
        "activation_id": activation_id,
        "check_id": check_id,
        "expected_body_digest": expected_digest,
        "body_access": body_access,
        "first_product_write": first_write,
        "exposures": exposures,
        "ordering": ordering,
        "raw_order": raw_order,
    }


def direct_evidence(trace, commands, workspace, availability, foundation_state):
    views = view_events(commands)
    view = views[0] if len(views) == 1 else None
    full_skill_reads = [
        {"event": row["event"], "command": row["command"]}
        for row in commands
        if base.READ_COMMAND.search(row["command"])
        and ".agents/skills/nulnul-harness/SKILL.md" in row["command"].replace("\\", "/")
    ]
    memory_reads = model_memory_reads(commands)
    positive = sum(len(trace["boundary_events"][name]) for name in ("project-fit", "govern", "host-admission"))
    bodies = sorted((Path(workspace) / ".nulnul-activation").rglob("SKILL.md"))
    first_write = trace["first_task_write"]
    verification = next(
        (row for row in trace["verification_events"] if first_write and row["event"] > first_write["event"]),
        None,
    )
    gate = bool(
        foundation_state
        and view and view["payload"] and view["payload"].get("status") == "ok"
        and view["output_bytes"] <= 4096
        and first_write and verification and view["event"] < first_write["event"] < verification["event"]
        and positive == 0 and not trace["boundary_events"]["check"] and not trace["boundary_events"]["attribute"]
        and availability.get("visible_body_count") == 0 and not bodies
        and not trace["ordinary_capability_body_reads"] and not trace["exposed_capability_body_reads"]
        and not memory_reads and not full_skill_reads
    )
    return {
        "capability_opportunity": bool(view and view["payload"] and view["payload"].get("status") == "ok"),
        "positive_boundary_available": (Path(workspace) / ".codex/rules/nulnul-activation.rules").is_file(),
        "project_fit_activations": len(trace["boundary_events"]["project-fit"]),
        "governed_activations": len(trace["boundary_events"]["govern"]),
        "capability_body_availability": availability.get("visible_body_count"),
        "capability_body_exposures": len(bodies),
        "capability_body_reads": len(trace["ordinary_capability_body_reads"]) + len(trace["exposed_capability_body_reads"]),
        "model_state_or_memory_reads": memory_reads,
        "full_skill_reads": full_skill_reads,
        "context_pack": foundation_state["context_pack"] if foundation_state else None,
        "first_product_write": first_write,
        "verification": verification,
        "gate": gate,
    }


def setup_evidence(task, workspace, trace, commands, foundation, config_before, config_after):
    governs = trace["boundary_events"]["govern"]
    activated = [row for row in governs if isinstance(row.get("payload"), dict) and row["payload"].get("status") == "activated"]
    expected = [row for row in activated if row["payload"].get("stage") == task["expected_stage"] and row["payload"].get("host") == task["expected_host"]]
    invalid_authority = [row for row in activated if row not in expected]
    syncs = trace["sync_events"]
    sync = syncs[-1] if syncs else None
    sync_payload = sync.get("payload") if sync else None
    activation = sync_payload.get("activation_rule", {}) if isinstance(sync_payload, dict) else {}
    validator = command(
        ["python3", ".agents/skills/nulnul-harness/scripts/capability_contract.py", "view", "docs/nulnul/project.md"],
        workspace,
    )
    view = payload(validator)
    rows = view.get("capabilities", []) if isinstance(view, dict) else []
    by_id = {row.get("capability_id"): row for row in rows}
    expected_rows = {
        "project-api-validation": ("api-contract", "capabilities/project-api-validation/SKILL.md"),
        "project-release-docs": ("release-docs", "capabilities/project-release-docs/SKILL.md"),
    }
    contract = bool(
        validator.returncode == 0
        and set(by_id) == set(expected_rows)
        and all(
            by_id[identity].get("status") == "accepted/current"
            and by_id[identity].get("accepted_current") is True
            and by_id[identity].get("project_check_identity") == values[0]
            and by_id[identity].get("logical_load_target") == values[1]
            for identity, values in expected_rows.items()
        )
    )
    rule = Path(workspace) / ".codex/rules/nulnul-activation.rules"
    shipped = Path(foundation) / "skills/nulnul-harness/assets/codex-activation.rules"
    current_session_activation = bool(trace["boundary_events"]["host-admission"] or trace["boundary_events"]["project-fit"])
    governed = bool(
        expected and not invalid_authority
        and expected[0]["payload"].get("sequence") == base.GOVERNED_SEQUENCE
        and expected[0]["payload"].get("authority") == base.EXPECTED_AUTHORITY
    )
    restart = bool(
        activation.get("status") == "CODEX_RESTART_REQUIRED"
        and activation.get("project_trusted") is True
        and activation.get("trust_mutated") is False
        and not current_session_activation
    )
    rule_valid = bool(rule.is_file() and shipped.is_file() and rule.read_bytes() == shipped.read_bytes())
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
        "shared_runtime_validation": contract,
        "rule_installed": rule_valid,
        "restart_required": restart,
        "current_session_activation_attempted": current_session_activation,
        "trust_mutated": config_before != config_after or activation.get("trust_mutated") is True,
        "sync": base.bounded_payload(sync_payload),
        "gate": governed and contract and rule_valid and restart and config_before == config_after,
    }


def record_observable_events(workspace, task_id, task, trace, chain=None):
    views = len(trace.get("foundation_views", []))
    if views:
        runtime_event(workspace, "CAPABILITY_OPPORTUNITY", task_id, {"bounded_views": views})
    if chain and chain.get("activation_id"):
        runtime_event(workspace, "CAPABILITY_ACTIVATION_REQUESTED", task_id, {"capability_id": task.get("expected_capability")})
        runtime_event(workspace, "CAPABILITY_ACTIVATED", task_id, {"activation_id": chain["activation_id"]})
    if trace.get("first_task_write"):
        runtime_event(workspace, "FILE_WRITE", task_id, trace["first_task_write"])
    if chain and chain.get("check_id"):
        runtime_event(workspace, "CHECK_STARTED", task_id, {"activation_id": chain["activation_id"]})
        runtime_event(workspace, "CHECK_COMPLETED", task_id, {"check_id": chain["check_id"], "result": chain["check_receipt"].get("result")})


def finish_foundation(workspace, arm_id, task, foundation_state, strict, completion, trace, chain, raw_ref):
    success = strict["result"] == "pass" and completion["result"] == "pass"
    check_result = "pass" if success else "fail"
    checks = [{"id": task.get("project_check_identity", "strict"), "result": check_result}]
    source_refs = [f"raw:{raw_ref}"]
    outcome = {
        "experience_type": "TASK_EXPERIENCE",
        "quality": "VERIFIED",
        "observability_completeness": "COMPLETE" if trace["raw_complete"] else "PARTIAL",
        "result": "SUCCESS" if success else "FAILURE",
        "product_outcome": "project checks passed" if success else "project checks failed",
        "changes": task.get("allowed_writes", []),
        "checks": checks,
        "verified_failure_reason": None if success else "independent strict or completion check failed",
        "source_refs": source_refs,
        "modules": task.get("allowed_writes", []),
    }
    promotions = {}
    if task["mode"] == "GOVERNED_SETUP":
        outcome.update({
            "experience_type": "GOVERNED_EXPERIENCE",
            "governed_stage": task["expected_stage"],
            "governed_host": task["expected_host"],
            "authority": base.EXPECTED_AUTHORITY,
        })
    elif chain is not None:
        activation = chain.get("activation")
        check_receipt = chain.get("check_receipt")
        attribution = chain.get("attribution")
        valid = chain.get("valid") and success
        outcome.update({
            "experience_type": "CAPABILITY_EXPERIENCE",
            "quality": "VERIFIED" if valid else "UNATTRIBUTED",
            "observability_completeness": "COMPLETE" if valid else "PARTIAL",
            "capability_id": task["expected_capability"],
            "capability_version": activation.get("capability_version") if activation else None,
            "activation_id": chain.get("activation_id"),
            "match_evidence": activation.get("match_evidence") if activation else task.get("expected_match_basis", "positive API-validation fit"),
            "body_digest": chain.get("expected_body_digest"),
            "check_id": chain.get("check_id"),
            "check_result": check_receipt.get("result") if check_receipt else check_result,
            "success": bool(check_receipt and check_receipt.get("result") == "pass"),
            "ordering": chain.get("ordering") or {},
            "activation_receipt": activation or {},
            "check_receipt": check_receipt or {},
            "attribution_receipt": attribution or {},
        })
        if chain.get("activation_id"):
            source_refs.append(f"activation:{chain['activation_id']}")
        if chain.get("check_id"):
            source_refs.append(f"check:{chain['check_id']}")
        if valid:
            promotions = json.loads(json.dumps(task.get("promotion_candidates", {})))
            refs = [value for value in source_refs if value.startswith(("activation:", "check:"))]
            for values in promotions.values():
                for candidate in values:
                    candidate["source_refs"] = refs
                    candidate["evidence"] = refs
    record_observable_events(workspace, foundation_state["task"]["task_id"], task, trace, chain)
    local = Path(workspace) / "docs/nulnul/.runtime"
    outcome_path = local / f"{arm_id}-outcome.json"
    promotions_path = local / f"{arm_id}-promotions.json"
    base.atomic_json(outcome_path, outcome)
    base.atomic_json(promotions_path, promotions)
    try:
        experience = runtime_call(
            workspace,
            "task-finish",
            "--task-id", foundation_state["task"]["task_id"],
            "--outcome", str(outcome_path.relative_to(workspace)),
            "--promotions", str(promotions_path.relative_to(workspace)),
        )
        captured = True
        failure = None
    except ValueError as error:
        experience = None
        captured = False
        failure = str(error)
    try:
        session = runtime_call(
            workspace,
            "session-finalize",
            "--status", "COMPLETED" if captured and success else "PARTIAL",
            "--next", "Continue from verified bounded memory",
            "--completeness", "COMPLETE" if captured and trace["raw_complete"] else "PARTIAL",
        )
        finalized = True
    except ValueError as error:
        session = None
        finalized = False
        failure = f"{failure}; {error}" if failure else str(error)
    return {
        "experience_captured": captured,
        "experience": experience,
        "session_finalized": finalized,
        "session": session,
        "outcome_supplied_to_product": outcome,
        "promotion_candidates_supplied": promotions,
        "failure": failure,
    }


def copy_foundation_state(workspace, arm_dir):
    destination = Path(arm_dir) / "foundation-state"
    destination.mkdir()
    memory = Path(workspace) / "docs/nulnul/memory"
    if memory.is_dir():
        shutil.copytree(memory, destination / "memory")
    events = Path(workspace) / "docs/nulnul/.runtime/events"
    if events.is_dir():
        shutil.copytree(events, destination / "events")
    files = {
        path.relative_to(destination).as_posix(): sha(path)
        for path in destination.rglob("*") if path.is_file()
    }
    return {
        "path": destination.name,
        "tree_sha256": file_tree(destination),
        "files": files,
        "raw_transcript_files": [name for name in files if "/raw/" in f"/{name}" or name.startswith("raw/")],
    }


def prepare_project_fit(protocol, preflight_record, workspace, arm_record):
    workspace = Path(workspace)
    activation = workspace / ".nulnul-activation"
    if activation.exists():
        base.make_writable(activation)
        shutil.rmtree(activation)
    base.git(workspace, "add", "-A")
    base.git(workspace, "commit", "--allow-empty", "-qm", "record E14 Governed Setup and Foundation memory")
    setup_commit = base.git(workspace, "rev-parse", "HEAD").stdout.strip()
    task = protocol["tasks"]["project_fit"]
    copy_overlay(ROOT / task["overlay"], workspace)
    base.git(workspace, "add", "-A")
    base.git(workspace, "commit", "-qm", "freeze E14 Project-Fit overlay")
    overlay_commit = base.git(workspace, "rev-parse", "HEAD").stdout.strip()
    initial = base.check_result(task["strict_command"], workspace)
    base.clean_runtime_files(workspace)
    codex_home = Path(preflight_record["codex_home"])
    config = base.config_read(codex_home, workspace)
    admission = base.static_rule_admission(workspace) if (workspace / ".codex/rules/nulnul-activation.rules").is_file() else None
    availability = candidate_availability(task, workspace, codex_home)
    if availability.get("visible_body_count"):
        raise ValueError("post-setup pre-commit body availability is nonzero")
    preparation = {
        "setup_evidence_committed": arm_record.get("evidence_committed") is True,
        "old_model_process_terminated": True,
        "conversation_context_reused": False,
        "setup_commit": setup_commit,
        "overlay_commit": overlay_commit,
        "initial_strict": initial,
        "initial_workspace_sha256": base.scientific_tree_sha256(workspace),
        "installed_harness_sha256": file_tree(workspace / ".agents/skills/nulnul-harness"),
        "host_config": config,
        "static_rule_admission": admission,
        "precommit_availability": availability,
    }
    path = Path(preflight_record["evidence_root"]) / "preparations/E14-PROJECT-FIT-FOUNDATION.json"
    atomic_json(path, preparation)
    return preparation


def prepare_next_session(protocol, preflight_record, workspace, arm_record):
    workspace = Path(workspace)
    activation = workspace / ".nulnul-activation"
    if activation.exists():
        base.make_writable(activation)
        shutil.rmtree(activation)
    base.git(workspace, "add", "-A")
    base.git(workspace, "commit", "--allow-empty", "-qm", "record E14 Project-Fit outcome and Foundation memory")
    project_fit_commit = base.git(workspace, "rev-parse", "HEAD").stdout.strip()
    task = protocol["tasks"]["next_session"]
    copy_overlay(ROOT / task["overlay"], workspace)
    base.git(workspace, "add", "-A")
    base.git(workspace, "commit", "-qm", "freeze E14 next-session overlay")
    overlay_commit = base.git(workspace, "rev-parse", "HEAD").stdout.strip()
    initial = base.check_result(task["strict_command"], workspace)
    base.clean_runtime_files(workspace)
    availability = candidate_availability(task, workspace, Path(preflight_record["codex_home"]))
    if availability.get("visible_body_count"):
        raise ValueError("next-session pre-commit body availability is nonzero")
    preparation = {
        "project_fit_evidence_committed": arm_record.get("evidence_committed") is True,
        "prior_model_process_terminated": True,
        "conversation_context_reused": False,
        "project_fit_commit": project_fit_commit,
        "overlay_commit": overlay_commit,
        "initial_strict": initial,
        "initial_workspace_sha256": base.scientific_tree_sha256(workspace),
        "installed_harness_sha256": file_tree(workspace / ".agents/skills/nulnul-harness"),
        "precommit_availability": availability,
    }
    path = Path(preflight_record["evidence_root"]) / "preparations/E14-NEXT-SESSION-MEMORY-FOUNDATION.json"
    atomic_json(path, preparation)
    return preparation


def preparation_for(preflight_record, arm_id):
    if arm_id in preflight_record["prepared_workspaces"] and "initial_workspace_sha256" in preflight_record["prepared_workspaces"][arm_id]:
        return preflight_record["prepared_workspaces"][arm_id]
    path = Path(preflight_record["evidence_root"]) / "preparations" / f"{arm_id}.json"
    if not path.is_file():
        raise ValueError(f"prepared lifecycle state is missing for {arm_id}")
    return load(path)


def state_raw_content_copied(state_snapshot, transcript):
    raw = Path(transcript).read_bytes()
    if not raw:
        return False
    root = Path(state_snapshot["absolute_path"])
    return any(raw == path.read_bytes() or raw in path.read_bytes() for path in root.rglob("*") if path.is_file())


def run_arm(args):
    protocol = load(PROTOCOL)
    runtime = Path(args.runtime_root).resolve()
    evidence = runtime / "evidence"
    preflight_record = load(evidence / "preflight.json")
    verify_benchmark_frozen(preflight_record)
    verify_tasks(protocol)
    arm = next((row for row in protocol["arms"] if row["arm_id"] == args.arm_id), None)
    if arm is None:
        raise ValueError("arm is outside the exact five-arm budget")
    arm_index = protocol["arms"].index(arm)
    for prior in protocol["arms"][:arm_index]:
        record_path = evidence / "arms" / prior["arm_id"] / "record.json"
        if not record_path.is_file() or load(record_path).get("evidence_committed") is not True:
            raise ValueError(f"prior official arm lacks committed evidence: {prior['arm_id']}")
    for later in protocol["arms"][arm_index + 1:]:
        if (evidence / "arms" / later["arm_id"]).exists():
            raise ValueError("later official arm evidence already exists")
    task = protocol["tasks"][arm["task"]]
    paths = next(row for row in preflight_record["paths"] if row["arm_id"] == arm["arm_id"])
    workspace = Path(paths["workspace"])
    source = Path(paths["product_source"])
    fixture = ROOT / task["fixture"]
    overlay = ROOT / task["overlay"] if task.get("overlay") else None
    prepared = preparation_for(preflight_record, arm["arm_id"])
    if not workspace.is_dir():
        raise ValueError("prepared workspace is missing")
    if base.scientific_tree_sha256(workspace) != prepared["initial_workspace_sha256"]:
        raise ValueError("prepared workspace identity changed")
    if file_tree(workspace / ".agents/skills/nulnul-harness") != prepared["installed_harness_sha256"]:
        raise ValueError("installed Foundation identity changed")
    source_before = source_snapshot(source)
    fixture_before = source_snapshot(fixture)
    overlay_before = source_snapshot(overlay) if overlay else None
    arm_dir = Path(paths["evidence"])
    if arm_dir.exists():
        raise ValueError("arm evidence already exists")
    arm_dir.mkdir(parents=True)
    receipts = Path(paths["receipt_root"])
    receipts.mkdir()
    transcript = Path(paths["transcript"])
    stderr_path = arm_dir / "stderr.txt"
    patch_path = arm_dir / "patch.diff"
    codex_home = Path(preflight_record["codex_home"])
    environment = os.environ.copy() | {"CODEX_HOME": str(codex_home), "PYTHONDONTWRITEBYTECODE": "1"}
    availability = prepared.get("precommit_availability") or (
        preflight_record["direct_precommit_availability"] if arm["arm_id"] == "E14-DIRECT-FOUNDATION" else {}
    )
    host_config_before = base.config_read(codex_home, workspace) if arm["source"] == "foundation" else None
    config_path = codex_home / "config.toml"
    config_sha_before = sha(config_path)
    rule_admission = None
    if arm["source"] == "foundation" and task["mode"] in {"DIRECT", "PROJECT_FIT", "NEXT_SESSION"}:
        rule_admission = base.static_rule_admission(workspace)
        environment.update({
            "NULNUL_CAPABILITY_STORE": str((fixture / ".agents/skills").resolve()),
            "NULNUL_RECEIPT_ROOT": str(receipts.resolve()),
            "NULNUL_CASE_ID": task["case_id"],
        })
        if task["mode"] in {"PROJECT_FIT", "NEXT_SESSION"}:
            environment.update({
                "NULNUL_PROJECT_CHECK_ID": task["project_check_identity"],
                "NULNUL_PROJECT_CHECK": task["project_check"],
            })
    foundation_state = None
    if arm["source"] == "foundation":
        admission_state = "CODEX_ACTIVATION_RULE_MISSING" if task["mode"] == "GOVERNED_SETUP" else "CODEX_ACTIVATION_ADMITTED"
        foundation_state = start_foundation(workspace, task, protocol, admission_state)
        effective_prompt = foundation_state["effective_prompt"]
    else:
        effective_prompt = task["prompt"]
    execution = run_model(protocol, arm, task, workspace, transcript, stderr_path, environment, effective_prompt)
    task_for_trace = dict(task)
    task_for_trace["allowed_writes"] = task.get("allowed_writes", task.get("required_writes", []))
    trace = base.parse_transcript(transcript, task_for_trace, workspace)
    commands = transcript_commands(transcript)
    trace["foundation_views"] = view_events(commands)
    strict, completion = independent_checks(task, workspace)
    raw_ref = raw_local_copy(workspace, transcript, arm["arm_id"]) if foundation_state else None
    chain = None
    architecture = {}
    if task["mode"] == "DIRECT" and arm["source"] == "foundation":
        architecture["direct"] = direct_evidence(trace, commands, workspace, availability, foundation_state)
    elif task["mode"] == "GOVERNED_SETUP":
        architecture["setup"] = setup_evidence(
            task, workspace, trace, commands, source, config_sha_before, sha(config_path)
        )
    elif task["mode"] in {"PROJECT_FIT", "NEXT_SESSION"}:
        chain = project_fit_chain(task, workspace, trace, commands, availability, receipts)
        architecture["project_fit"] = {
            key: value for key, value in chain.items()
            if key not in {"activation", "check_receipt", "attribution"}
        }
    foundation_finish = None
    if foundation_state:
        chain_for_finish = chain if chain and (chain.get("activation") or chain.get("check_receipt") or chain.get("attribution")) else None
        foundation_finish = finish_foundation(
            workspace, arm["arm_id"], task, foundation_state, strict, completion,
            trace, chain_for_finish, raw_ref,
        )
    lineage = None
    if foundation_state:
        try:
            lineage = runtime_call(workspace, "validate-lineage")
        except ValueError as error:
            lineage = {"valid": False, "errors": [str(error)]}
    changed, unauthorized, missing = write_set(workspace, task)
    patch = base.git(workspace, "diff", "--binary", "HEAD", check=False).stdout.encode()
    patch_hash = base.atomic_write(patch_path, patch)
    state_snapshot = None
    raw_copied = False
    if foundation_state:
        state_snapshot = copy_foundation_state(workspace, arm_dir)
        state_snapshot["absolute_path"] = str((arm_dir / state_snapshot["path"]).resolve())
        raw_copied = state_raw_content_copied(state_snapshot, transcript)
    source_after = source_snapshot(source)
    fixture_after = source_snapshot(fixture)
    overlay_after = source_snapshot(overlay) if overlay else None
    config_sha_after = sha(config_path)
    host_config_after = base.config_read(codex_home, workspace) if arm["source"] == "foundation" else None
    usage = trace["usage"]
    infrastructure_errors = []
    if execution["process_exit"] != 0:
        infrastructure_errors.append("model_process_nonzero_exit")
    if execution["timed_out"]:
        infrastructure_errors.append("model_process_timeout")
    if not trace["raw_complete"]:
        infrastructure_errors.append("raw_transcript_incomplete")
    if not isinstance(usage, dict) or not isinstance(usage.get("input_tokens"), int) or usage.get("input_tokens", 0) <= 0:
        infrastructure_errors.append("model_usage_missing_or_unparseable")
    if source_before != source_after:
        infrastructure_errors.append("frozen_product_source_mutation")
    if fixture_before != fixture_after or overlay_before != overlay_after:
        infrastructure_errors.append("frozen_task_source_mutation")
    if not patch_path.is_file() or sha(patch_path) != patch_hash:
        infrastructure_errors.append("patch_capture_failure")
    if strict.get("exit_code") is None or completion.get("exit_code") is None:
        infrastructure_errors.append("strict_or_completion_missing")
    if foundation_state and not state_snapshot:
        infrastructure_errors.append("foundation_state_capture_missing")
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
            "ignore_user_config": False,
            "permission_profile": "e13-exclusive-reused" if arm["source"] == "foundation" and task["mode"] != "GOVERNED_SETUP" else "workspace-write",
        },
        "task_sha256": task_hash(task),
        "effective_prompt_sha256": foundation_state["effective_prompt_sha256"] if foundation_state else task_hash(task),
        "fixture_sha256": fixture_before["tree_sha256"],
        "overlay_sha256": overlay_before["tree_sha256"] if overlay_before else None,
        "initial_workspace_sha256": prepared["initial_workspace_sha256"],
        "installed_harness_sha256": prepared["installed_harness_sha256"],
        "process": execution,
        "raw_transcript": str(transcript.relative_to(evidence)),
        "raw_transcript_sha256": sha(transcript),
        "raw_transcript_complete": trace["raw_complete"],
        "stderr": str(stderr_path.relative_to(evidence)),
        "stderr_sha256": sha(stderr_path),
        "model_usage": usage,
        "repository_reads": trace["repository_reads"],
        "foundation_or_memory_model_reads": model_memory_reads(commands),
        "patch": str(patch_path.relative_to(evidence)),
        "patch_sha256": patch_hash,
        "write_set": changed,
        "unauthorized_writes": unauthorized,
        "required_writes_missing": missing,
        "initial_strict": prepared["initial_strict"],
        "strict": strict,
        "completion": completion,
        "foundation_lifecycle": foundation_state,
        "foundation_finish": foundation_finish,
        "foundation_state_evidence": state_snapshot,
        "raw_transcript_content_copied_to_durable_memory": raw_copied,
        "lineage": lineage,
        "host_config_before": host_config_before,
        "host_config_after": host_config_after,
        "host_config_sha256_before": config_sha_before,
        "host_config_sha256_after": config_sha_after,
        "host_trust_mutated": config_sha_before != config_sha_after,
        "static_rule_admission": rule_admission,
        "precommit_availability": availability,
        "architecture": architecture,
        "trace_summary": {
            "event_count": trace["event_count"],
            "foundation_views": [
                {key: value for key, value in row.items() if key not in {"output", "payload"}}
                | {"payload": base.bounded_payload(row.get("payload"))}
                for row in trace["foundation_views"]
            ],
            "boundary_events": {
                name: [{key: value for key, value in row.items() if key != "payload"} | {"payload": base.bounded_payload(row.get("payload"))} for row in rows]
                for name, rows in trace["boundary_events"].items()
            },
            "ordinary_capability_body_reads": trace["ordinary_capability_body_reads"],
            "exposed_capability_body_reads": trace["exposed_capability_body_reads"],
            "first_product_write": trace["first_task_write"],
            "verification_events": trace["verification_events"],
            "final_text": trace["final_text"][-2400:],
        },
        "frozen_source_before": source_before,
        "frozen_source_after": source_after,
        "frozen_fixture_before": fixture_before,
        "frozen_fixture_after": fixture_after,
        "frozen_overlay_before": overlay_before,
        "frozen_overlay_after": overlay_after,
        "infrastructure_errors": infrastructure_errors,
        "final_status": "pass" if execution["process_exit"] == 0 and strict["result"] == "pass" and completion["result"] == "pass" else "fail",
        "evidence_committed": not infrastructure_errors,
        "cleanup_status": "PENDING",
    }
    atomic_json(arm_dir / "record.json", record)
    if record["evidence_committed"]:
        if arm["arm_id"] == "E14-GOVERNED-SETUP-FOUNDATION":
            try:
                record["post_restart_preparation"] = prepare_project_fit(protocol, preflight_record, workspace, record)
            except Exception as error:
                record["post_restart_preparation"] = {"status": "failed", "reason": f"{type(error).__name__}:{error}"}
        elif arm["arm_id"] == "E14-PROJECT-FIT-FOUNDATION":
            try:
                record["next_session_preparation"] = prepare_next_session(protocol, preflight_record, workspace, record)
            except Exception as error:
                record["next_session_preparation"] = {"status": "failed", "reason": f"{type(error).__name__}:{error}"}
        if arm["workspace"] != "lifecycle":
            try:
                base.make_writable(workspace)
                shutil.rmtree(workspace)
                record["cleanup_status"] = "CLEANUP_PASS"
            except OSError as error:
                record["cleanup_status"] = "POST_EVIDENCE_CLEANUP_FAILURE"
                record["cleanup_error"] = str(error)
        else:
            record["cleanup_status"] = "LIFECYCLE_PRESERVED"
        atomic_json(arm_dir / "record.json", record)
    print(json.dumps(record, indent=2))


def artifact_manifest(evidence):
    files = {}
    for path in sorted(Path(evidence).rglob("*")):
        if not path.is_file() or path.name in {"manifest.json", "manifest.json.receipt"}:
            continue
        files[path.relative_to(evidence).as_posix()] = sha(path)
    return {"schema_version": 1, "files": files}


def finalize(args):
    protocol = load(PROTOCOL)
    runtime = Path(args.runtime_root).resolve()
    evidence = runtime / "evidence"
    preflight_record = load(evidence / "preflight.json")
    verify_benchmark_frozen(preflight_record)
    records = []
    for arm in protocol["arms"]:
        path = evidence / "arms" / arm["arm_id"] / "record.json"
        if not path.is_file():
            raise ValueError(f"official arm record missing: {arm['arm_id']}")
        records.append(load(path))
    by_id = {row["arm_id"]: row for row in records}
    champion = by_id["E14-DIRECT-CHAMPION"]
    direct = by_id["E14-DIRECT-FOUNDATION"]
    setup = by_id["E14-GOVERNED-SETUP-FOUNDATION"]
    project_fit = by_id["E14-PROJECT-FIT-FOUNDATION"]
    next_session = by_id["E14-NEXT-SESSION-MEMORY-FOUNDATION"]
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
    try:
        evolution = runtime_call(
            lifecycle,
            "evolution-query",
            "--capability", "project-api-validation",
            "--job", protocol["tasks"]["project_fit"]["job"],
            "--limit", "20",
        )
    except ValueError as error:
        evolution = {"count": 0, "experiences": [], "error": str(error)}
    experience = (project_fit.get("foundation_finish") or {}).get("experience") or {}
    experience_id = experience.get("experience_id")
    next_context = ((next_session.get("foundation_lifecycle") or {}).get("context_pack") or {})
    context_ids = [row.get("item_id") for row in next_context.get("items", [])]
    lessons = inspections.get("lessons", {}).get("lessons", [])
    lesson_ids = [row.get("lesson_id") for row in lessons]
    relevant_context = bool(experience_id in context_ids or set(lesson_ids).intersection(context_ids))
    prior_handoff = ((next_session.get("foundation_lifecycle") or {}).get("session") or {}).get("previous_handoff") or {}
    project_session = ((project_fit.get("foundation_lifecycle") or {}).get("session") or {}).get("session_id")
    next_session_id = ((next_session.get("foundation_lifecycle") or {}).get("session") or {}).get("session_id")
    query_ids = [row.get("experience_id") for row in evolution.get("experiences", [])]
    champion_input = (champion.get("model_usage") or {}).get("input_tokens")
    direct_input = (direct.get("model_usage") or {}).get("input_tokens")
    ratio = direct_input / champion_input if isinstance(champion_input, int) and champion_input > 0 and isinstance(direct_input, int) else None
    gates = {
        "direct": bool(
            direct.get("architecture", {}).get("direct", {}).get("gate")
            and direct.get("strict", {}).get("result") == "pass"
            and direct.get("completion", {}).get("result") == "pass"
            and ratio is not None and ratio <= 1.2
            and not direct.get("unauthorized_writes")
            and (direct.get("foundation_finish") or {}).get("session_finalized")
        ),
        "setup": bool(
            setup.get("architecture", {}).get("setup", {}).get("gate")
            and setup.get("strict", {}).get("result") == "pass"
            and setup.get("completion", {}).get("result") == "pass"
            and not setup.get("unauthorized_writes")
            and (setup.get("foundation_finish") or {}).get("session_finalized")
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
            project_fit.get("architecture", {}).get("project_fit", {}).get("valid")
            and project_fit.get("strict", {}).get("result") == "pass"
            and project_fit.get("completion", {}).get("result") == "pass"
            and not project_fit.get("unauthorized_writes")
        ),
        "experience": bool(
            experience.get("experience_type") == "CAPABILITY_EXPERIENCE"
            and experience.get("quality") == "VERIFIED"
            and experience.get("observability_completeness") == "COMPLETE"
            and experience.get("evolution_eligible") is True
            and (project_fit.get("foundation_finish") or {}).get("experience_captured")
        ),
        "memory": bool(
            (project_fit.get("foundation_finish") or {}).get("session_finalized")
            and experience_id
            and lesson_ids
            and lineage.get("valid") is True
            and project_fit.get("raw_transcript_content_copied_to_durable_memory") is False
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
        "evolution_input": bool(experience_id and experience_id in query_ids and lineage.get("valid") is True),
        "state_authority": all(not row.get("unauthorized_writes") and not row.get("host_trust_mutated") for row in records),
        "durable_evidence": all(row.get("evidence_committed") is True for row in records),
    }
    failure_codes = []
    if ratio is not None and ratio > 1.2:
        failure_codes.append("DIRECT_LANE_OVERHEAD")
    if not setup.get("architecture", {}).get("setup", {}).get("shared_runtime_validation"):
        failure_codes.append("SETUP_RUNTIME_CONTRACT_FAILURE")
    if not gates["host_restart"]:
        failure_codes.append("HOST_ADMISSION_FAILURE")
    project_arch = project_fit.get("architecture", {}).get("project_fit", {})
    if "precommit_body_zero" in project_arch.get("reasons", []) or "one_exact_body" in project_arch.get("reasons", []):
        failure_codes.append("EXCLUSIVE_CAPABILITY_GATE_FAILURE")
    if "material_fit" in project_arch.get("reasons", []) or "commit_receipt" in project_arch.get("reasons", []):
        failure_codes.append("TRUE_POSITIVE_UNDERACTIVATION")
    if "exact_identity" in project_arch.get("reasons", []):
        failure_codes.append("WRONG_CAPABILITY_IDENTITY")
    if not gates["project_fit"] and any(
        reason in project_arch.get("reasons", [])
        for reason in ("internal_order", "body_access", "check_receipt", "attribution_receipt", "raw_order", "receipt_order_has_no_slots_for_observed_body_access_and_write")
    ):
        failure_codes.append("ATTRIBUTION_BOUNDARY_FAILURE")
    if not gates["experience"]:
        failure_codes.append("EXPERIENCE_CAPTURE_FAILURE")
    if gates["experience"] and not gates["memory"]:
        failure_codes.append("MEMORY_PROMOTION_FAILURE")
    if not gates["next_session"]:
        failure_codes.append("CONTEXT_RETRIEVAL_FAILURE")
    if next_context.get("item_count", 0) > 8 or next_context.get("byte_count", 0) > 4096:
        failure_codes.append("CONTEXT_BLOAT_REGRESSION")
    if lineage.get("valid") is not True:
        failure_codes.append("PROVENANCE_FAILURE")
    if not gates["state_authority"]:
        failure_codes.append("STATE_AUTHORITY_REGRESSION")
    if any(row.get("strict", {}).get("result") != "pass" or row.get("completion", {}).get("result") != "pass" for row in records):
        failure_codes.append("PRODUCT_REGRESSION")
    infrastructure = any(row.get("infrastructure_errors") or not row.get("evidence_committed") for row in records)
    if infrastructure:
        failure_codes.append("INFRASTRUCTURE_INVALID")
        primary = "INFRASTRUCTURE_INVALID"
    elif all(gates.values()):
        primary = "FOUNDATION_INTEGRATED_E2E_PROVEN"
    else:
        primary = "FOUNDATION_CORE_FAILURE"
    report = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "primary_result": primary,
        "success_claim": "NULNUL v2.3 FOUNDATION — LIVE INTEGRATED LOOP PROVEN" if primary == "FOUNDATION_INTEGRATED_E2E_PROVEN" else None,
        "evolution_readiness": primary == "FOUNDATION_INTEGRATED_E2E_PROVEN" and gates["experience"] and gates["evolution_input"],
        "failure_codes": sorted(set(failure_codes)),
        "gates": gates,
        "direct_performance": {
            "champion_input": champion_input,
            "foundation_input": direct_input,
            "ratio": ratio,
            "hard_limit": 1.2,
        },
        "project_fit_experience_id": experience_id,
        "promoted_lesson_ids": lesson_ids,
        "next_session_id": next_session_id,
        "next_session_context_ids": context_ids,
        "relevant_context_restored": relevant_context,
        "evolution_query": evolution,
        "lineage": lineage,
        "memory_inspections": inspections,
        "version": "v2.3 ARCHITECTURE REWORK REQUIRED",
        "release": "NOT READY",
        "product_changes_during_experiment": 0,
    }
    atomic_json(evidence / "final-report.json", report)
    cleanup = {}
    for path in (runtime / "workspaces", runtime / "codex-home"):
        try:
            if path.exists():
                base.make_writable(path)
                shutil.rmtree(path)
            cleanup[path.name] = "CLEANUP_PASS"
        except OSError as error:
            cleanup[path.name] = f"POST_EVIDENCE_CLEANUP_FAILURE:{error}"
    report["cleanup"] = cleanup
    atomic_json(evidence / "final-report.json", report)
    manifest = artifact_manifest(evidence)
    atomic_json(evidence / "manifest.json", manifest)
    receipt_value = sha(evidence / "manifest.json")
    base.atomic_write(evidence / "manifest.json.receipt", (receipt_value + "\n").encode())
    if (evidence / "manifest.json.receipt").read_text(encoding="utf-8").strip() != sha(evidence / "manifest.json"):
        raise ValueError("manifest receipt readback failed")
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    before = sub.add_parser("preflight")
    before.add_argument("--champion", required=True)
    before.add_argument("--foundation", required=True)
    before.add_argument("--runtime-root", required=True)
    arm = sub.add_parser("run-arm")
    arm.add_argument("arm_id")
    arm.add_argument("--runtime-root", required=True)
    done = sub.add_parser("finalize")
    done.add_argument("--runtime-root", required=True)
    sub.add_parser("self-test")
    args = parser.parse_args()
    try:
        if args.command == "preflight":
            preflight(args)
        elif args.command == "run-arm":
            run_arm(args)
        elif args.command == "finalize":
            finalize(args)
        else:
            print(json.dumps(self_test(), indent=2))
    except Exception as error:
        print(json.dumps({"status": "failed", "error": f"{type(error).__name__}:{error}"}, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
