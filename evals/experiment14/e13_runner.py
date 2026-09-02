#!/usr/bin/env python3
"""Exact four-arm runner for NULNUL Experiment 13."""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import select
import shlex
import shutil
import stat
import subprocess
import tempfile
import time
import tomllib
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROTOCOL_PATH = HERE / "protocol.json"
PREREG_PATH = HERE / "preregistration.md"
BOUNDARY = re.compile(r"activation_boundary\.py(?:['\"])?\s+(view|host-admission|project-fit|check|attribute|govern)\b")
SYNC_ENTRY = re.compile(r"sync_host_entry\.py(?:['\"])?\s+codex\b")
PROJECT_SKILL = re.compile(r"\.agents/skills/(?!nulnul-harness/)([a-z0-9-]+)/SKILL\.md")
EXPOSED_SKILL = re.compile(r"\.nulnul-activation/([a-f0-9]{64})/([a-z0-9-]+)/SKILL\.md")
READ_COMMAND = re.compile(r"\b(?:cat|sed|head|tail|rg|grep|find|ls)\b|\bgit\s+(?:show|diff)\b")
WRITE_COMMAND = re.compile(r"\bapply_patch\b|\bsed\s+-i\b|(?:^|\s)>\s*")
GOVERNED_SEQUENCE = ["STAGE_REQUESTED", "STAGE_VALIDATED", "GOVERNED_ACTIVATED"]
EXPECTED_AUTHORITY = [
    "AGENTS.md",
    "docs/nulnul/project.md",
    "docs/nulnul/checkpoint.json",
    "docs/nulnul/checkpoint.verification.json",
]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256(path):
    return sha256_bytes(path.read_bytes())


def tree_sha256(root):
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def scientific_tree_sha256(root):
    """Hash content, relative path, executable semantics, and symlink policy."""
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if ".git" not in p.parts):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError(f"scientific input contains symlink: {relative}")
        if not path.is_file():
            continue
        executable = bool(path.stat().st_mode & 0o111)
        digest.update(relative.encode())
        digest.update(b"\0x" if executable else b"\0-")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def task_sha256(task):
    return sha256_bytes(task["prompt"].encode())


def atomic_write(path, data):
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return sha256(path)


def atomic_json(path, payload):
    return atomic_write(path, (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode())


def canonical(path):
    return Path(os.path.normcase(str(Path(path).expanduser().resolve(strict=False))))


def overlap(first, second):
    first, second = canonical(first), canonical(second)
    return first == second or first.is_relative_to(second) or second.is_relative_to(first)


def read_only_tree(root):
    return root.is_dir() and not any(
        path.stat().st_mode & 0o222
        for path in (root, *root.rglob("*"))
        if not path.is_symlink()
    )


def make_writable(root):
    for path in (root, *root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"writable copy contains symlink: {path}")
        mode = stat.S_IMODE(path.stat().st_mode)
        path.chmod(mode | (0o700 if path.is_dir() else 0o600))


def clean_runtime_files(root):
    for path in sorted(root.rglob("__pycache__"), reverse=True):
        shutil.rmtree(path)
    for path in sorted(root.rglob(".pytest_cache"), reverse=True):
        shutil.rmtree(path)
    for path in root.rglob("*.pyc"):
        path.unlink()


def run(command, cwd, *, shell=False, timeout=120, env=None):
    return subprocess.run(
        command,
        cwd=cwd,
        shell=shell,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def git(cwd, *args, check=True):
    result = run(["git", *args], cwd)
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result


def changed_files(workspace):
    output = git(workspace, "status", "--porcelain=v1", "--untracked-files=all").stdout
    changed, untracked = [], []
    for line in output.splitlines():
        if not line:
            continue
        status, name = line[:2], line[3:]
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        changed.append(name)
        if status == "??":
            untracked.append(name)
    return sorted(set(changed)), sorted(set(untracked))


def check_result(command, workspace):
    started = time.monotonic()
    result = run(command, workspace, shell=True)
    return {
        "command": command,
        "exit_code": result.returncode,
        "result": "pass" if result.returncode == 0 else "fail",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
        "stdout_sha256": sha256_bytes(result.stdout.encode()),
        "stderr_sha256": sha256_bytes(result.stderr.encode()),
    }


def parse_payload(output):
    decoder = json.JSONDecoder()
    for offset, character in enumerate(output):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(output[offset:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def command_exit(item):
    value = item.get("exit_code")
    return value if isinstance(value, int) else None


def normalize_path(value, workspace):
    value = str(value).replace("\\", "/")
    candidate = Path(value)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(workspace.resolve()).as_posix()
        except ValueError:
            return value
    return value.removeprefix("./")


def bounded_payload(payload):
    if not isinstance(payload, dict):
        return payload
    return {key: value for key, value in payload.items() if key != "body"}


def positive_state_argument(command):
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    skip_next_glob = False
    for token in tokens:
        if skip_next_glob:
            skip_next_glob = False
            continue
        if token in {"-g", "--glob"}:
            skip_next_glob = True
            continue
        if token.startswith("--glob=") or token.startswith("-g!") or token.startswith("!"):
            continue
        normalized = token.replace("\\", "/").removeprefix("./")
        if "docs/nulnul/checkpoint" in normalized or "docs/nulnul/evolution" in normalized:
            return True
    return False


def parse_transcript(path, task, workspace):
    data = path.read_bytes()
    raw_complete = bool(data) and data.endswith(b"\n")
    events = []
    for line_number, line in enumerate(data.decode("utf-8", errors="strict").splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            raw_complete = False
            continue
        if isinstance(event, dict):
            events.append((line_number, event))

    usage = None
    commands = []
    writes = []
    boundary = {name: [] for name in ("view", "host-admission", "project-fit", "check", "attribute", "govern")}
    sync_events = []
    ordinary_body_reads = []
    exposed_body_reads = []
    state_reads = []
    stage_context_reads = []
    reads = 0
    final_text = ""

    for line_number, event in events:
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
        if event.get("type") != "item.completed" or not isinstance(event.get("item"), dict):
            continue
        item = event["item"]
        kind = item.get("type")
        if kind == "agent_message" and isinstance(item.get("text"), str):
            final_text = item["text"]
        if kind == "command_execution":
            command = str(item.get("command", ""))
            output = str(item.get("aggregated_output", item.get("output", "")))
            commands.append({"event": line_number, "command": command, "exit_code": command_exit(item)})
            normalized = command.replace("\\", "/")
            match = BOUNDARY.search(normalized)
            operation = match.group(1) if match else None
            if match:
                payload = parse_payload(output)
                boundary[operation].append({
                    "event": line_number,
                    "command": command,
                    "exit_code": command_exit(item),
                    "payload": payload,
                    "summary": bounded_payload(payload),
                    "output_bytes": len(output.encode()),
                })
            if SYNC_ENTRY.search(normalized):
                sync_events.append({
                    "event": line_number,
                    "command": command,
                    "exit_code": command_exit(item),
                    "payload": parse_payload(output),
                })
            is_read = bool(READ_COMMAND.search(command))
            if is_read or operation:
                reads += 1
            if is_read:
                for name in PROJECT_SKILL.findall(normalized):
                    ordinary_body_reads.append({"event": line_number, "capability": name, "command": command})
                for activation_id, name in EXPOSED_SKILL.findall(normalized):
                    exposed_body_reads.append({
                        "event": line_number,
                        "activation_id": activation_id,
                        "capability": name,
                        "command": command,
                    })
            if is_read and positive_state_argument(command):
                state_reads.append({"event": line_number, "command": command})
            if (
                ".agents/skills/nulnul-harness/references/" in normalized
                or "docs/nulnul/" in normalized
                or ".agents/skills/nulnul-harness/scripts/sync_host_entry.py" in normalized
            ) and is_read:
                stage_context_reads.append({"event": line_number, "command": command})
            if WRITE_COMMAND.search(command):
                for target in task["allowed_writes"]:
                    if target in normalized:
                        writes.append({"event": line_number, "path": target, "source": "command"})
        elif kind == "file_change":
            for change in item.get("changes", []):
                if isinstance(change, dict) and change.get("path"):
                    writes.append({
                        "event": line_number,
                        "path": normalize_path(change["path"], workspace),
                        "source": "file_change",
                    })

    target_writes = [event for event in writes if event["path"] in task["allowed_writes"]]
    first_write = min(target_writes, key=lambda event: event["event"]) if target_writes else None
    verification = [event for event in commands if "python3 -m unittest" in event["command"]]
    return {
        "raw_complete": raw_complete,
        "event_count": len(events),
        "usage": usage,
        "commands": commands,
        "repository_reads": reads,
        "boundary_events": boundary,
        "sync_events": sync_events,
        "ordinary_capability_body_reads": ordinary_body_reads,
        "exposed_capability_body_reads": exposed_body_reads,
        "live_or_evolution_state_reads": state_reads,
        "stage_context_reads": stage_context_reads,
        "write_events": writes,
        "first_task_write": first_write,
        "verification_events": verification,
        "final_text": final_text,
    }


def direct_evidence(trace, workspace, availability):
    views = trace["boundary_events"]["view"]
    view = views[0] if len(views) == 1 else None
    payload = view["payload"] if view else None
    first_write = trace["first_task_write"]
    verification = next(
        (event for event in trace["verification_events"] if first_write and event["event"] > first_write["event"]),
        None,
    )
    positive = (
        len(trace["boundary_events"]["host-admission"])
        + len(trace["boundary_events"]["project-fit"])
        + len(trace["boundary_events"]["govern"])
    )
    passed = bool(
        (workspace / ".agents/skills/nulnul-harness/scripts/activation_boundary.py").is_file()
        and view and payload and payload.get("status") == "ok"
        and view["output_bytes"] <= 4096
        and first_write and verification
        and view["event"] < first_write["event"] < verification["event"]
        and positive == 0
        and not trace["boundary_events"]["attribute"]
        and availability.get("visible_body_count") == 0
        and not trace["ordinary_capability_body_reads"]
        and not trace["exposed_capability_body_reads"]
        and not trace["live_or_evolution_state_reads"]
        and not list((workspace / ".nulnul-activation").rglob("SKILL.md"))
    )
    return {
        "capability_opportunity": bool(view and payload and payload.get("status") == "ok"),
        "positive_boundary_available": bool(
            (workspace / ".agents/skills/nulnul-harness/scripts/activation_boundary.py").is_file()
            and (workspace / ".codex/rules/nulnul-activation.rules").is_file()
        ),
        "project_fit_activations": len(trace["boundary_events"]["project-fit"]),
        "governed_activations": len(trace["boundary_events"]["govern"]),
        "host_admissions": len(trace["boundary_events"]["host-admission"]),
        "precommit_body_availability": availability.get("visible_body_count"),
        "capability_body_exposures": len(list((workspace / ".nulnul-activation").rglob("SKILL.md"))),
        "capability_body_reads": len(trace["ordinary_capability_body_reads"]) + len(trace["exposed_capability_body_reads"]),
        "state_reads": len(trace["live_or_evolution_state_reads"]),
        "ordered": passed,
    }


def external_receipt(receipts, category, identity):
    if not isinstance(identity, str) or not re.fullmatch(r"[a-f0-9]{64}", identity):
        return None
    path = receipts / category / f"{identity}.json"
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(receipts.resolve()):
        return None
    try:
        return load_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def project_fit_evidence(trace, task, workspace, availability, receipts):
    views = trace["boundary_events"]["view"]
    admissions = trace["boundary_events"]["host-admission"]
    fits = trace["boundary_events"]["project-fit"]
    checks = trace["boundary_events"]["check"]
    attrs = trace["boundary_events"]["attribute"]
    view = views[0] if len(views) == 1 else None
    admission = admissions[0] if len(admissions) == 1 else None
    fit = fits[0] if len(fits) == 1 else None
    check = checks[0] if len(checks) == 1 else None
    attr = attrs[0] if len(attrs) == 1 else None
    view_payload = view["payload"] if view else None
    admission_payload = admission["payload"] if admission else None
    fit_payload = fit["payload"] if fit else None
    check_payload = check["payload"] if check else None
    attr_payload = attr["payload"] if attr else None
    capability = task["expected_capability"]
    expected_source = REPO / task["fixture"] / ".agents/skills" / capability / "SKILL.md"
    expected_digest = sha256(expected_source) if expected_source.is_file() else None
    first_write = trace["first_task_write"]
    accepted_rows = view_payload.get("capabilities", []) if isinstance(view_payload, dict) else []
    accepted = next((row for row in accepted_rows if row.get("capability_id") == capability), None)
    activation_id = fit_payload.get("activation_id") if isinstance(fit_payload, dict) else None
    admission_id = admission_payload.get("admission_id") if isinstance(admission_payload, dict) else None
    body_relative = (
        f".nulnul-activation/{activation_id}/{capability}/SKILL.md"
        if isinstance(activation_id, str) else None
    )
    body_path = workspace / body_relative if body_relative else None
    exposed = sorted(
        path.relative_to(workspace).as_posix()
        for path in (workspace / ".nulnul-activation").rglob("SKILL.md")
    )
    activation_receipt = external_receipt(receipts, "activations", activation_id)
    admission_receipt = external_receipt(receipts, "admissions", admission_id)
    check_id = check_payload.get("check_id") if isinstance(check_payload, dict) else None
    check_receipt = external_receipt(receipts, "checks", check_id)
    attribution_id = attr_payload.get("attribution_id") if isinstance(attr_payload, dict) else None
    attribution_receipt = external_receipt(receipts, "attributions", attribution_id)
    fit_events = fit_payload.get("events", {}) if isinstance(fit_payload, dict) else {}
    request = fit_events.get("commit_request", {})
    admitted = fit_events.get("host_admission", {})
    validation = fit_events.get("validation_success", {})
    exposure = fit_events.get("body_exposure", {})
    activated = fit_events.get("activation_receipt", {})
    internal_order = bool(
        admitted.get("kind") == "CODEX_ACTIVATION_ADMITTED"
        and request.get("kind") == "PROJECT_FIT_COMMIT_REQUESTED"
        and validation.get("kind") == "PROJECT_FIT_COMMIT_VALIDATED"
        and exposure.get("kind") == "CAPABILITY_BODY_EXPOSED"
        and activated.get("kind") == "PROJECT_FIT_ACTIVATED"
        and admitted.get("order", 0) < request.get("order", 0) < validation.get("order", 0)
        < exposure.get("order", 0) < activated.get("order", 0)
    )
    body_accesses = trace["exposed_capability_body_reads"]
    first_body_access = min(body_accesses, key=lambda event: event["event"], default=None)
    exact_body_access = bool(
        first_body_access
        and all(
            item["activation_id"] == activation_id and item["capability"] == capability
            for item in body_accesses
        )
    )
    raw_order = bool(
        admission and fit and first_body_access and first_write and check and attr
        and admission["event"] < fit["event"] < first_body_access["event"] < first_write["event"]
        < check["event"] < attr["event"]
    )
    expected_command_hash = sha256_bytes(task["project_check"].encode())
    check_valid = bool(
        check and check["exit_code"] in (None, 0)
        and check_payload and check_payload == check_receipt
        and check_payload.get("status") == "checked"
        and check_payload.get("activation_id") == activation_id
        and check_payload.get("project_check_identity") == task["project_check_identity"]
        and check_payload.get("command") == task["project_check"]
        and check_payload.get("command_hash") == expected_command_hash
        and check_payload.get("result") == "pass"
        and check_payload.get("exit_code") == 0
        and isinstance(check_payload.get("product_state_id"), str)
        and re.fullmatch(r"[a-f0-9]{64}", check_payload.get("output_digest", ""))
    )
    commit_valid = bool(
        view and admission and admission_payload == admission_receipt
        and admission_payload.get("status") == "CODEX_ACTIVATION_ADMITTED"
        and admission_payload.get("body_exposure") == 0
        and accepted and accepted.get("accepted_status") == "current"
        and fit and fit_payload and fit_payload.get("status") == "activated"
        and fit_payload.get("activation") == "PROJECT_FIT"
        and fit_payload.get("admission_id") == admission_id
        and fit_payload.get("capability_id") == capability
        and fit_payload.get("accepted_status") == "current"
        and fit_payload.get("logical_source") == f".agents/skills/{capability}/SKILL.md"
        and fit_payload.get("source_contained") is True
        and fit_payload.get("successful_exposure") is True
        and fit_payload.get("body_path") == body_relative
        and fit_payload.get("body_sha256") == expected_digest
        and isinstance(fit_payload.get("match_evidence"), str)
        and 0 < len(fit_payload["match_evidence"].encode()) <= 1024
        and isinstance(activation_id, str) and re.fullmatch(r"[a-f0-9]{64}", activation_id)
        and isinstance(fit_payload.get("activation_receipt"), str)
        and re.fullmatch(r"[a-f0-9]{64}", fit_payload["activation_receipt"])
        and activation_receipt == fit_payload
        and internal_order
        and availability.get("visible_body_count") == 0
        and not trace["ordinary_capability_body_reads"]
        and exposed == [body_relative]
        and body_path and body_path.is_file() and sha256(body_path) == expected_digest
        and exact_body_access
        and fit["event"] < first_body_access["event"]
        and not trace["boundary_events"]["govern"]
    )
    attribution_valid = bool(
        commit_valid and check_valid and attr and attr_payload and first_write and raw_order
        and attribution_receipt == attr_payload
        and attr_payload.get("status") == "attributed"
        and attr_payload.get("capability_id") == capability
        and attr_payload.get("body_sha256") == expected_digest
        and attr_payload.get("activation_id") == activation_id
        and attr_payload.get("admission_id") == admission_id
        and attr_payload.get("check_id") == check_id
        and attr_payload.get("match_evidence") == fit_payload.get("match_evidence")
        and "command" not in attr_payload and "project_check" not in attr_payload
        and attr_payload.get("product_outcome") == "success"
        and attr_payload.get("check_result") == "pass"
        and attr_payload.get("success") is True
        and attr_payload.get("body_exposure_order") == exposure.get("order")
        and attr_payload.get("event", {}).get("order", 0)
        > check_payload.get("events", {}).get("check_complete", {}).get("order", 0)
    )
    causal_record = {
        "task_job": attr_payload.get("task_job") if isinstance(attr_payload, dict) else None,
        "match_evidence": attr_payload.get("match_evidence") if isinstance(attr_payload, dict) else None,
        "capability_id": capability if commit_valid else None,
        "admission_id": admission_id,
        "activation_id": activation_id,
        "host_admission": bounded_payload(admission_receipt),
        "commit_before_body": bool(commit_valid and internal_order),
        "body_sha256": expected_digest if commit_valid else None,
        "body_exposure_before_work": bool(raw_order),
        "first_product_write": first_write,
        "product_outcome": attr_payload.get("product_outcome") if isinstance(attr_payload, dict) else None,
        "check_id": check_id,
        "check_result": check_payload.get("result") if isinstance(check_payload, dict) else None,
        "success": attr_payload.get("success") if isinstance(attr_payload, dict) else None,
    }
    return {
        "material_fit": fit_payload.get("match_evidence") if isinstance(fit_payload, dict) else None,
        "capability_id": fit_payload.get("capability_id") if isinstance(fit_payload, dict) else None,
        "accepted_current": bool(accepted and accepted.get("accepted_status") == "current"),
        "logical_path_valid": bool(
            isinstance(fit_payload, dict)
            and fit_payload.get("logical_source") == f".agents/skills/{capability}/SKILL.md"
        ),
        "precommit_body_availability": availability.get("visible_body_count"),
        "precommit_body_reads": len(trace["ordinary_capability_body_reads"]),
        "postcommit_body_path": body_relative,
        "postcommit_body_exposures": exposed,
        "first_body_access": first_body_access,
        "body_sha256": fit_payload.get("body_sha256") if isinstance(fit_payload, dict) else None,
        "expected_body_sha256": expected_digest,
        "activation_id": activation_id,
        "activation_receipt": bounded_payload(activation_receipt),
        "first_product_write": first_write,
        "check_id": check_id,
        "check_receipt": bounded_payload(check_receipt),
        "commit_valid": commit_valid,
        "attribution": bounded_payload(attr_payload),
        "causal_record": causal_record,
        "attribution_complete": attribution_valid,
        "ordered": attribution_valid,
        "wrong_or_irrelevant_body_loads": sum(
            item["activation_id"] != activation_id or item["capability"] != capability
            for item in body_accesses
        ),
    }


def governed_evidence(trace, task, workspace):
    governs = trace["boundary_events"]["govern"]
    activated = [
        event for event in governs
        if isinstance(event.get("payload"), dict) and event["payload"].get("status") == "activated"
    ]
    governed = activated[0] if len(activated) == 1 else None
    payload = governed["payload"] if governed else None
    first_write = trace["first_task_write"]
    first_context = min(
        trace["stage_context_reads"], key=lambda event: event["event"], default=None
    )
    receipt = payload.get("activation_receipt") if isinstance(payload, dict) else None
    valid = bool(
        governed and payload and payload.get("status") == "activated"
        and payload.get("activation") == "GOVERNED"
        and payload.get("sequence") == GOVERNED_SEQUENCE
        and payload.get("stage") == task["expected_stage"]
        and payload.get("host") == task["expected_host"]
        and payload.get("authority") == EXPECTED_AUTHORITY
        and isinstance(receipt, str) and re.fullmatch(r"[a-f0-9]{64}", receipt)
        and first_write and governed["event"] < first_write["event"]
        and (first_context is None or governed["event"] < first_context["event"])
        and not any(
            isinstance(event.get("payload"), dict)
            and event["payload"].get("status") == "activated"
            and event["payload"].get("stage") != task["expected_stage"]
            for event in governs
        )
        and not trace["boundary_events"]["project-fit"]
    )
    return {
        "structural_intent": True,
        "stage": payload.get("stage") if isinstance(payload, dict) else None,
        "host": payload.get("host") if isinstance(payload, dict) else None,
        "authority": payload.get("authority") if isinstance(payload, dict) else None,
        "activation_receipt": receipt,
        "rejected_attempts": len(governs) - len(activated),
        "invalid_attempts_granted_authority": False if valid else None,
        "first_stage_context": first_context,
        "first_stage_write": first_write,
        "ordered": valid,
    }


def setup_lifecycle_evidence(trace, task, workspace, candidate, config_before, config_after):
    governed = governed_evidence(trace, task, workspace)
    syncs = trace["sync_events"]
    sync = syncs[-1] if syncs else None
    payload = sync.get("payload") if sync else None
    activation = payload.get("activation_rule", {}) if isinstance(payload, dict) else {}
    rule = workspace / ".codex/rules/nulnul-activation.rules"
    expected = candidate / "skills/nulnul-harness/assets/codex-activation.rules"
    valid = bool(
        governed.get("ordered")
        and sync and sync.get("exit_code") in (None, 0)
        and isinstance(payload, dict) and payload.get("host") == "codex"
        and activation.get("status") == "CODEX_RESTART_REQUIRED"
        and activation.get("project_trusted") is True
        and activation.get("trust_mutated") is False
        and activation.get("rule_path") == ".codex/rules/nulnul-activation.rules"
        and activation.get("rule_changed") is True
        and config_before == config_after
        and rule.is_file() and not rule.is_symlink()
        and expected.is_file() and rule.read_bytes() == expected.read_bytes()
        and not trace["boundary_events"]["host-admission"]
        and not trace["boundary_events"]["project-fit"]
        and sync["event"] > min(
            event["event"] for event in trace["boundary_events"]["govern"]
            if isinstance(event.get("payload"), dict)
            and event["payload"].get("status") == "activated"
        )
    )
    return {
        "governed": governed,
        "project_trust_preexisting": config_before == config_after,
        "trust_mutated": activation.get("trust_mutated") if activation else None,
        "rule_installed": bool(rule.is_file() and expected.is_file() and rule.read_bytes() == expected.read_bytes()),
        "rule_sha256": sha256(rule) if rule.is_file() else None,
        "rule_scope": "exact protected NULNUL activation helper",
        "current_session_rule_active": False,
        "restart_required": activation.get("status") == "CODEX_RESTART_REQUIRED",
        "sync": bounded_payload(payload),
        "ordered": valid,
    }


def validate_sources(protocol, champion, candidate):
    failures = []
    for label, root, expected in (
        ("champion", champion, protocol["champion"]["tree_sha256"]),
        ("candidate", candidate, protocol["candidate"]["tree_sha256"]),
    ):
        if not root.is_dir():
            failures.append(f"{label} source missing")
        elif tree_sha256(root) != expected:
            failures.append(f"{label} tree mismatch")
        elif not read_only_tree(root):
            failures.append(f"{label} source is not read-only")
        else:
            scientific_tree_sha256(root)
    if candidate.is_dir():
        for relative, expected in protocol["candidate"]["per_file_sha256"].items():
            path = candidate / relative
            if not path.is_file() or sha256(path) != expected:
                failures.append(f"Candidate file mismatch: {relative}")
    return failures


def exact_paths(protocol, champion, candidate, evidence, workspaces):
    source = {"champion": champion, "candidate": candidate}
    arms = []
    for item in protocol["arms"]:
        arms.append({
            **item,
            "product_source": str(source[item["source"]]),
            "fixture": str(REPO / protocol["tasks"][item["task"]]["fixture"]),
            "workspace": str(workspaces / item["workspace"]),
            "evidence": str(evidence / "arms" / item["arm_id"]),
            "receipts": str(evidence / "arms" / item["arm_id"] / "receipts"),
            "transcript": str(evidence / "arms" / item["arm_id"] / "transcript.jsonl"),
            "patch": str(evidence / "arms" / item["arm_id"] / "patch.diff"),
        })
    return arms


def validate_paths(protocol, champion, candidate, evidence, workspaces, codex_home):
    failures = []
    if overlap(champion, evidence) or overlap(candidate, evidence):
        failures.append("scientific source overlaps evidence")
    if overlap(workspaces, evidence) or overlap(codex_home, evidence) or overlap(codex_home, workspaces):
        failures.append("workspace root overlaps evidence")
    if evidence.is_relative_to(REPO) or workspaces.is_relative_to(REPO) or codex_home.is_relative_to(REPO):
        failures.append("mutable runtime roots must be outside benchmark source")
    seen = {}
    for arm in exact_paths(protocol, champion, candidate, evidence, workspaces):
        workspace = canonical(arm["workspace"])
        fixture = canonical(arm["fixture"])
        prior = seen.get(workspace)
        if prior and {prior, arm["arm_id"]} != {
            "E13-GOVERNED-SETUP-CANDIDATE",
            "E13-PROJECT-FIT-POST-RESTART-CANDIDATE",
        }:
            failures.append("unplanned arm workspace overlap")
        seen[workspace] = arm["arm_id"]
        if overlap(workspace, evidence):
            failures.append(f"{arm['arm_id']} workspace overlaps evidence")
        if overlap(fixture, evidence) or overlap(fixture, champion) or overlap(fixture, candidate):
            failures.append(f"{arm['arm_id']} fixture is not isolated")
    return failures


def source_snapshot(root):
    return {
        "tree_sha256": tree_sha256(root),
        "scientific_tree_sha256": scientific_tree_sha256(root),
        "read_only": read_only_tree(root),
    }


def permission_profile_config():
    executable = Path(shutil.which("codex") or "").resolve()
    package_root = executable.parents[1]
    root = str(package_root).replace("\\", "\\\\").replace('"', '\\"')
    value = (
        '{extends=":workspace",filesystem={":root"="deny",":minimal"="read",'
        '":tmpdir"="deny",":slash_tmp"="deny",'
        f'"{root}"="read"}}}}'
    )
    return f'permissions.e13-exclusive={value}', str(package_root)


def permission_arguments():
    profile, _ = permission_profile_config()
    return ["-c", profile, "-c", 'default_permissions="e13-exclusive"']


def candidate_availability(task, workspace, codex_home):
    fixture = REPO / task["fixture"]
    bodies = sorted(
        path for path in (fixture / ".agents/skills").glob("*/SKILL.md")
        if path.parent.name != "nulnul-harness"
    )
    visible_workspace = sorted(
        path.relative_to(workspace).as_posix()
        for path in (workspace / ".agents/skills").glob("*/SKILL.md")
        if path.parent.name != "nulnul-harness"
    )
    body_digests = {sha256(path) for path in bodies}
    duplicate_paths = sorted(
        path.relative_to(workspace).as_posix()
        for path in workspace.rglob("*")
        if path.is_file() and ".git" not in path.parts and sha256(path) in body_digests
    )
    profile, package_root = permission_profile_config()
    runtime_duplicate_paths = sorted(
        str(path)
        for path in Path(package_root).rglob("SKILL.md")
        if path.is_file() and sha256(path) in body_digests
    )
    environment = os.environ | {"CODEX_HOME": str(codex_home)}
    metadata = run(
        [
            "codex", "sandbox", "-P", "e13-exclusive", "-C", str(workspace),
            "-c", profile,
            "python3", ".agents/skills/nulnul-harness/scripts/activation_boundary.py",
            "view", "docs/nulnul/project.md", "--skills-root", ".agents/skills",
        ],
        workspace,
        env=environment,
    )
    metadata_payload = parse_payload(metadata.stdout)
    external = []
    visible_external = 0
    for body in bodies:
        probe = run(
            [
                "codex", "sandbox", "-P", "e13-exclusive", "-C", str(workspace),
                "-c", profile, "/usr/bin/head", "-c", "1", str(body.resolve()),
            ],
            workspace,
            env=environment,
        )
        readable = probe.returncode == 0
        visible_external += int(readable)
        external.append({
            "logical_identity": body.parent.name,
            "source_sha256": sha256(body),
            "ordinary_read_exit": probe.returncode,
            "ordinary_readable": readable,
        })
    visible = (
        len(set(visible_workspace) | set(duplicate_paths))
        + len(runtime_duplicate_paths)
        + visible_external
    )
    return {
        "metadata_visible": bool(
            metadata.returncode == 0
            and isinstance(metadata_payload, dict)
            and metadata_payload.get("status") == "ok"
        ),
        "metadata_capabilities": [
            row.get("capability_id") for row in (metadata_payload or {}).get("capabilities", [])
        ],
        "workspace_body_paths": visible_workspace,
        "workspace_duplicate_body_paths": duplicate_paths,
        "runtime_duplicate_body_paths": runtime_duplicate_paths,
        "external_body_probes": external,
        "visible_body_count": visible,
        "permission_profile": "e13-exclusive",
        "codex_runtime_read_root": package_root,
    }


def write_codex_home(codex_home, trusted_roots):
    if codex_home.exists():
        raise ValueError("isolated Codex home must be fresh")
    codex_home.mkdir(parents=True)
    auth = Path.home() / ".codex/auth.json"
    if not auth.is_file():
        raise ValueError("existing Codex authentication is unavailable")
    (codex_home / "auth.json").symlink_to(auth)
    lines = []
    for root in trusted_roots:
        value = str(root.resolve()).replace("\\", "\\\\").replace('"', '\\"')
        lines.extend([f'[projects."{value}"]', 'trust_level = "trusted"', ""])
    config = codex_home / "config.toml"
    atomic_write(config, ("\n".join(lines) + "\n").encode())
    return {
        "established_by": "host/test operator",
        "storage": str(config),
        "config_sha256": sha256(config),
        "trusted_projects": [str(root.resolve()) for root in trusted_roots],
        "real_user_config_modified": False,
        "auth_reused_by_symlink": True,
    }


def project_trust_active(codex_home, cwd):
    config = tomllib.loads((codex_home / "config.toml").read_text(encoding="utf-8"))
    project = config.get("projects", {}).get(str(cwd.resolve()), {})
    return project.get("trust_level") == "trusted"


def config_read(codex_home, cwd):
    environment = os.environ | {"CODEX_HOME": str(codex_home)}
    process = subprocess.Popen(
        ["codex", "app-server", "--stdio"], cwd=cwd, env=environment,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
    )
    messages = (
        {"id": 1, "method": "initialize", "params": {
            "clientInfo": {"name": "nulnul-experiment-13", "version": "1"},
            "capabilities": {},
        }},
        {"method": "initialized", "params": {}},
        {"id": 2, "method": "config/read", "params": {
            "cwd": str(cwd.resolve()), "includeLayers": True,
        }},
    )
    for message in messages:
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()
    response = None
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline and response is None:
        for stream in select.select([process.stdout, process.stderr], [], [], 0.2)[0]:
            line = stream.readline()
            if stream is process.stdout and line:
                payload = json.loads(line)
                if payload.get("id") == 2:
                    response = payload
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    if not response or response.get("error"):
        raise ValueError("Codex effective-config read failed")
    result = response.get("result", {})
    layers = result.get("layers", [])
    sources = [item.get("name") or item.get("source") for item in layers]
    user_loaded = any(
        isinstance(source, dict)
        and source.get("type") == "user"
        and canonical(source.get("file", "")) == canonical(codex_home / "config.toml")
        for source in sources
    )
    project_loaded = any(
        isinstance(source, dict)
        and source.get("type") == "project"
        and canonical(source.get("dotCodexFolder", "")) == canonical(cwd / ".codex")
        for source in sources
    )
    return {
        "user_config_loaded": user_loaded,
        "project_trust_active": project_trust_active(codex_home, cwd),
        "project_layer_active": project_loaded,
        "layer_sources": sources,
    }


def prepare_workspace(fixture, source, source_label, workspace, *, sync_entry):
    if workspace.exists():
        raise ValueError(f"workspace already exists: {workspace}")
    shutil.copytree(fixture, workspace)
    if source_label == "candidate":
        skills = workspace / ".agents/skills"
        for path in list(skills.iterdir()) if skills.is_dir() else []:
            if path.name != "nulnul-harness":
                shutil.rmtree(path)
    harness_source = source / "skills/nulnul-harness"
    harness_target = workspace / ".agents/skills/nulnul-harness"
    shutil.copytree(harness_source, harness_target)
    make_writable(workspace)
    if sync_entry:
        synced = run(
            ["python3", str(harness_target / "scripts/sync_host_entry.py"), "codex", "--root", "."],
            workspace,
        )
        if synced.returncode:
            raise RuntimeError(f"host-entry preparation failed: {synced.stderr}")
    return harness_target


def install_direct_rule(workspace, codex_home):
    helper = workspace / ".agents/skills/nulnul-harness/scripts/activation_boundary.py"
    sync = workspace / ".agents/skills/nulnul-harness/scripts/sync_host_entry.py"
    environment = os.environ | {"CODEX_HOME": str(codex_home)}
    governed = run(
        ["python3", str(helper), "govern", "adopt-upgrade", "--host", "codex", "--root", "."],
        workspace, env=environment,
    )
    payload = parse_payload(governed.stdout)
    if governed.returncode or not payload:
        raise ValueError("steady-state Direct governed setup preparation failed")
    installed = run(
        [
            "python3", str(sync), "codex", "--root", ".",
            "--codex-activation", "install",
            "--governed-stage", payload["stage"],
            "--governed-receipt", payload["activation_receipt"],
        ],
        workspace, env=environment,
    )
    result = parse_payload(installed.stdout)
    if (
        installed.returncode
        or not result
        or result.get("activation_rule", {}).get("status") != "CODEX_RESTART_REQUIRED"
        or result.get("activation_rule", {}).get("trust_mutated")
    ):
        raise ValueError("steady-state Direct rule installation failed")
    return result


def freeze_workspace(task, workspace):
    git(workspace, "init", "-q")
    git(workspace, "config", "user.email", "experiment-13@example.invalid")
    git(workspace, "config", "user.name", "Experiment 13")
    exclude = workspace / ".git/info/exclude"
    with exclude.open("a", encoding="utf-8") as handle:
        handle.write("\n**/__pycache__/\n*.pyc\n**/.pytest_cache/\n.nulnul-activation/\n")
    git(workspace, "add", "-A")
    git(workspace, "commit", "-qm", "frozen Experiment 13 input")
    initial_strict = check_result(task["strict_command"], workspace)
    clean_runtime_files(workspace)
    if git(workspace, "status", "--porcelain").stdout.strip():
        raise ValueError("fixture precheck changed the prepared workspace")
    harness = workspace / ".agents/skills/nulnul-harness"
    return {
        "initial_strict": initial_strict,
        "initial_workspace_sha256": scientific_tree_sha256(workspace),
        "installed_harness_sha256": tree_sha256(harness),
        "writable_copy": all(
            bool(path.stat().st_mode & 0o200)
            for path in (workspace, *workspace.rglob("*"))
            if not path.is_symlink() and ".git" not in path.parts
        ),
    }


def preflight(args):
    protocol = load_json(PROTOCOL_PATH)
    champion, candidate = canonical(args.champion), canonical(args.candidate)
    evidence, workspaces = canonical(args.evidence_root), canonical(args.workspace_root)
    codex_home = canonical(args.codex_home)
    failures = validate_sources(protocol, champion, candidate)
    failures.extend(validate_paths(protocol, champion, candidate, evidence, workspaces, codex_home))
    if len(protocol.get("arms", [])) != 4:
        failures.append("protocol is not the exact four-arm schedule")
    if evidence.exists():
        failures.append("fresh evidence root already exists")
    if workspaces.exists() and any(workspaces.iterdir()):
        failures.append("workspace root is not empty")
    if codex_home.exists():
        failures.append("isolated Codex home already exists")
    if git(REPO, "status", "--porcelain", check=False).stdout.strip():
        failures.append("benchmark source is not frozen in Git")
    tasks = {}
    for name, task in protocol["tasks"].items():
        fixture = REPO / task["fixture"]
        actual_task = task_sha256(task)
        actual_fixture = tree_sha256(fixture)
        tasks[name] = {"task_sha256": actual_task, "fixture_sha256": actual_fixture}
        if task["task_sha256"] != actual_task or task["fixture_sha256"] != actual_fixture:
            failures.append(f"{name} task or fixture hash mismatch")
        scientific_tree_sha256(fixture)
        if task.get("overlay"):
            overlay = REPO / task["overlay"]
            actual_overlay = tree_sha256(overlay)
            tasks[name]["overlay_sha256"] = actual_overlay
            if actual_overlay != task["overlay_sha256"]:
                failures.append(f"{name} overlay hash mismatch")
            scientific_tree_sha256(overlay)
    if failures:
        raise ValueError("; ".join(failures))
    evidence.mkdir(parents=True)
    workspaces.mkdir(parents=True, exist_ok=True)
    source = {"champion": champion, "candidate": candidate}
    direct_task = protocol["tasks"]["direct"]
    setup_task = protocol["tasks"]["governed_setup"]
    fit_task = protocol["tasks"]["project_fit"]
    direct_champion = workspaces / "direct-champion"
    direct_candidate = workspaces / "direct-candidate"
    lifecycle = workspaces / "lifecycle"
    prepare_workspace(REPO / direct_task["fixture"], champion, "champion", direct_champion, sync_entry=True)
    prepare_workspace(REPO / direct_task["fixture"], candidate, "candidate", direct_candidate, sync_entry=False)
    prepare_workspace(REPO / setup_task["fixture"], candidate, "candidate", lifecycle, sync_entry=False)
    host_trust = write_codex_home(codex_home, [direct_champion, direct_candidate, lifecycle])
    direct_install = install_direct_rule(direct_candidate, codex_home)
    prepared = {
        "E13-DIRECT-CHAMPION": freeze_workspace(direct_task, direct_champion),
        "E13-DIRECT-CANDIDATE": freeze_workspace(direct_task, direct_candidate),
        "E13-GOVERNED-SETUP-CANDIDATE": freeze_workspace(setup_task, lifecycle),
        "E13-PROJECT-FIT-POST-RESTART-CANDIDATE": {"pending_setup_lifecycle": True},
    }
    availability = {
        "E13-DIRECT-CANDIDATE": candidate_availability(direct_task, direct_candidate, codex_home),
        "E13-PROJECT-FIT-POST-RESTART-CANDIDATE": candidate_availability(fit_task, lifecycle, codex_home),
    }
    for arm_id, proof in availability.items():
        if not proof["metadata_visible"]:
            raise ValueError(f"{arm_id} metadata opportunity is unavailable")
        if proof["visible_body_count"]:
            raise ValueError(f"{arm_id} has pre-commit body availability")
    config_layers = {
        "direct_candidate": config_read(codex_home, direct_candidate),
        "lifecycle_before_setup": config_read(codex_home, lifecycle),
    }
    direct_config = config_layers["direct_candidate"]
    lifecycle_config = config_layers["lifecycle_before_setup"]
    if not (
        direct_config["user_config_loaded"]
        and direct_config["project_trust_active"]
        and direct_config["project_layer_active"]
        and lifecycle_config["user_config_loaded"]
        and lifecycle_config["project_trust_active"]
        and not lifecycle_config["project_layer_active"]
    ):
        raise ValueError("Codex trust or expected pre-setup project-layer state is invalid")
    candidate_test = run(
        ["python3", "-m", "unittest", "experiments/13/test_candidate.py", "-v"],
        REPO,
        env=os.environ | {
            "E13_CANDIDATE": str(candidate),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )
    if candidate_test.returncode:
        raise ValueError(f"Candidate deterministic gate failed: {candidate_test.stderr[-2000:]}")
    runner_test = run(
        ["python3", "-m", "unittest", "experiments/13/test_run.py", "-v"],
        REPO,
        env=os.environ | {"PYTHONDONTWRITEBYTECODE": "1"},
    )
    if runner_test.returncode:
        raise ValueError(f"runner deterministic gate failed: {runner_test.stderr[-2000:]}")
    after_preparation = validate_sources(protocol, champion, candidate)
    if after_preparation:
        raise ValueError("; ".join(after_preparation))
    record = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "status": "pass",
        "planned_arms": 4,
        "benchmark_revision": git(REPO, "rev-parse", "HEAD").stdout.strip(),
        "runner_sha256": sha256(Path(__file__)),
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "preregistration_sha256": sha256(PREREG_PATH),
        "candidate_created_before_fresh_tasks": True,
        "champion": source_snapshot(champion),
        "candidate": source_snapshot(candidate),
        "tasks": tasks,
        "paths": exact_paths(protocol, champion, candidate, evidence, workspaces),
        "prepared_workspaces": prepared,
        "precommit_availability": availability,
        "host_trust": host_trust,
        "host_config_layers": config_layers,
        "steady_state_direct_install": direct_install,
        "codex_home": str(codex_home),
        "rejected_commit_controls": {
            "unknown_id_no_exposure": "pass",
            "noncurrent_id_no_exposure": "pass",
            "path_escape_no_exposure": "pass",
            "second_unrelated_id_no_exposure": "pass",
            "test_exit": candidate_test.returncode,
            "test_stdout_sha256": sha256_bytes(candidate_test.stdout.encode()),
            "test_stderr_sha256": sha256_bytes(candidate_test.stderr.encode()),
        },
        "runner_controls": {
            "structured_state_exclusion_negative_control": "pass",
            "exact_four_arm_lifecycle": "pass",
            "user_config_retained": "pass",
            "test_exit": runner_test.returncode,
            "test_stdout_sha256": sha256_bytes(runner_test.stdout.encode()),
            "test_stderr_sha256": sha256_bytes(runner_test.stderr.encode()),
        },
        "evidence_root": str(evidence),
        "workspace_root": str(workspaces),
    }
    atomic_write(evidence / "preregistration.md", PREREG_PATH.read_bytes())
    atomic_write(evidence / "protocol.json", PROTOCOL_PATH.read_bytes())
    atomic_json(evidence / "preflight.json", record)
    if load_json(evidence / "preflight.json") != record:
        raise ValueError("preflight readback failed")
    print(json.dumps(record, ensure_ascii=False, indent=2))


def run_model(protocol, arm, task, workspace, transcript, stderr_path, env):
    command = ["codex", "exec", "--json", "--ephemeral"]
    if arm["source"] == "candidate" and task["mode"] in {"DIRECT", "PROJECT_FIT"}:
        command.extend(permission_arguments())
    elif task["mode"] == "GOVERNED_SETUP":
        command.append("--approve-for-me")
    else:
        command.extend(["--ignore-rules", "-s", "workspace-write"])
    command.extend([
        "--skip-git-repo-check", "-C", str(workspace), "-m", protocol["model"],
        "-c", f'model_reasoning_effort="{protocol["reasoning_effort"]}"', task["prompt"],
    ])
    started = time.monotonic()
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    timed_out = False
    with transcript.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            command, cwd=workspace, env=env, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr
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
        "command": command[:-1] + ["<FROZEN_TASK_PROMPT>"],
    }


def static_rule_admission(workspace):
    rule = workspace / ".codex/rules/nulnul-activation.rules"
    helper = ".agents/skills/nulnul-harness/scripts/activation_boundary.py"
    checks = {}
    for operation, suffix in {
        "host-admission": ["host-admission", "--root", "."],
        "project-fit": ["project-fit", "docs/nulnul/project.md", "--id", "project-api-validation", "--admission-id", "0" * 64],
        "check": ["check", "--activation-id", "0" * 64],
        "attribute": ["attribute", "--activation-id", "0" * 64, "--check-id", "1" * 64],
    }.items():
        result = run(
            ["codex", "execpolicy", "check", "--rules", str(rule), "--", "python3", helper, *suffix],
            workspace,
        )
        payload = parse_payload(result.stdout)
        checks[operation] = {
            "exit_code": result.returncode,
            "decision": payload.get("decision") if payload else None,
        }
    return {
        "rule_sha256": sha256(rule) if rule.is_file() else None,
        "operations": checks,
        "all_exact_operations_allowed": all(
            item["exit_code"] == 0 and item["decision"] == "allow"
            for item in checks.values()
        ),
    }


def prepare_project_fit_lifecycle(protocol, workspace):
    git(workspace, "add", "-A")
    git(workspace, "commit", "-qm", "record E13 governed setup lifecycle")
    setup_commit = git(workspace, "rev-parse", "HEAD").stdout.strip()
    overlay = REPO / protocol["tasks"]["project_fit"]["overlay"]
    for source in sorted(path for path in overlay.rglob("*") if path.is_file()):
        relative = source.relative_to(overlay)
        target = workspace / relative
        if target.exists() or target.is_symlink():
            raise ValueError(f"Project-Fit overlay collides with lifecycle state: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    git(workspace, "add", "-A")
    git(workspace, "commit", "-qm", "freeze E13 Project-Fit task overlay")
    overlay_commit = git(workspace, "rev-parse", "HEAD").stdout.strip()
    task = protocol["tasks"]["project_fit"]
    initial_strict = check_result(task["strict_command"], workspace)
    clean_runtime_files(workspace)
    if git(workspace, "status", "--porcelain").stdout.strip():
        raise ValueError("Project-Fit lifecycle preparation changed its frozen baseline")
    return {
        "setup_commit": setup_commit,
        "overlay_commit": overlay_commit,
        "overlay_sha256": tree_sha256(overlay),
        "initial_strict": initial_strict,
        "initial_workspace_sha256": scientific_tree_sha256(workspace),
        "installed_harness_sha256": tree_sha256(workspace / ".agents/skills/nulnul-harness"),
    }


def run_arm(args):
    protocol = load_json(PROTOCOL_PATH)
    preflight_record = load_json(canonical(args.evidence_root) / "preflight.json")
    arm = next((item for item in protocol["arms"] if item["arm_id"] == args.arm_id), None)
    if arm is None:
        raise ValueError("arm is outside the exact four-arm budget")
    expected_index = [item["arm_id"] for item in protocol["arms"]].index(args.arm_id)
    prior = protocol["arms"][:expected_index]
    evidence = canonical(args.evidence_root)
    for item in prior:
        record = evidence / "arms" / item["arm_id"] / "record.json"
        if not record.is_file():
            raise ValueError(f"prior official arm is missing: {item['arm_id']}")
        if not load_json(record).get("evidence_committed"):
            raise ValueError(f"prior official arm lacks committed evidence: {item['arm_id']}")
    for later in protocol["arms"][expected_index + 1:]:
        if (evidence / "arms" / later["arm_id"]).exists():
            raise ValueError("later arm evidence already exists")

    task = protocol["tasks"][arm["task"]]
    candidate_path = next(item["product_source"] for item in preflight_record["paths"] if item["source"] == "candidate")
    champion_path = next(item["product_source"] for item in preflight_record["paths"] if item["source"] == "champion")
    sources = {"champion": Path(champion_path), "candidate": Path(candidate_path)}
    source = sources[arm["source"]]
    workspace = Path(preflight_record["workspace_root"]) / arm["workspace"]
    arm_dir = evidence / "arms" / arm["arm_id"]
    if arm_dir.exists():
        raise ValueError(f"arm evidence already exists: {arm['arm_id']}")
    arm_dir.mkdir(parents=True)
    transcript = arm_dir / "transcript.jsonl"
    stderr_path = arm_dir / "stderr.txt"
    patch_path = arm_dir / "patch.diff"
    record_path = arm_dir / "record.json"
    fixture = REPO / task["fixture"]
    overlay = REPO / task["overlay"] if task.get("overlay") else None
    source_before = source_snapshot(source)
    fixture_before = source_snapshot(fixture)
    overlay_before = source_snapshot(overlay) if overlay else None
    infrastructure_errors = []
    cleanup_status = "NOT_ATTEMPTED"
    try:
        if git(REPO, "status", "--porcelain", check=False).stdout.strip():
            raise ValueError("benchmark source changed after preflight")
        if git(REPO, "rev-parse", "HEAD").stdout.strip() != preflight_record["benchmark_revision"]:
            raise ValueError("benchmark revision changed after preflight")
        for path, key in (
            (Path(__file__), "runner_sha256"),
            (PROTOCOL_PATH, "protocol_sha256"),
            (PREREG_PATH, "preregistration_sha256"),
        ):
            if sha256(path) != preflight_record[key]:
                raise ValueError(f"frozen benchmark input changed: {path.name}")
        source_errors = validate_sources(protocol, sources["champion"], sources["candidate"])
        if source_errors:
            raise ValueError("; ".join(source_errors))
        if task_sha256(task) != task["task_sha256"] or tree_sha256(REPO / task["fixture"]) != task["fixture_sha256"]:
            raise ValueError("frozen task or fixture changed after preflight")
        if overlay and tree_sha256(overlay) != task["overlay_sha256"]:
            raise ValueError("frozen Project-Fit overlay changed after preflight")
        if task["mode"] == "PROJECT_FIT":
            setup_record = load_json(
                evidence / "arms/E13-GOVERNED-SETUP-CANDIDATE/record.json"
            )
            prepared = setup_record.get("project_fit_preparation", {})
        else:
            prepared = preflight_record["prepared_workspaces"][arm["arm_id"]]
        if not workspace.is_dir() or git(workspace, "status", "--porcelain").stdout.strip():
            raise ValueError("prepared workspace is absent or changed")
        initial_workspace_hash = scientific_tree_sha256(workspace)
        if initial_workspace_hash != prepared["initial_workspace_sha256"]:
            raise ValueError("prepared workspace identity changed")
        installed_harness_hash = tree_sha256(workspace / ".agents/skills/nulnul-harness")
        if installed_harness_hash != prepared["installed_harness_sha256"]:
            raise ValueError("installed harness identity changed")
        receipts = arm_dir / "receipts"
        receipts.mkdir()
        environment = os.environ.copy()
        codex_home = Path(preflight_record["codex_home"])
        environment["CODEX_HOME"] = str(codex_home)
        config_path = codex_home / "config.toml"
        config_before = sha256(config_path)
        host_config = config_read(codex_home, workspace)
        expected_project_layer = task["mode"] != "GOVERNED_SETUP"
        if arm["source"] == "candidate" and (
            not host_config["user_config_loaded"]
            or not host_config["project_trust_active"]
            or host_config["project_layer_active"] != expected_project_layer
        ):
            raise ValueError("Candidate trust or expected project-layer state is inactive")
        rule_admission = (
            static_rule_admission(workspace)
            if arm["source"] == "candidate" and task["mode"] in {"DIRECT", "PROJECT_FIT"}
            else None
        )
        availability = preflight_record["precommit_availability"].get(arm["arm_id"], {})
        if task["mode"] == "PROJECT_FIT":
            availability = candidate_availability(task, workspace, codex_home)
            if not availability.get("metadata_visible") or availability.get("visible_body_count"):
                raise ValueError("post-setup pre-commit availability gate failed")
        if arm["source"] == "candidate" and task["mode"] in {"DIRECT", "PROJECT_FIT"}:
            environment.update({
                "NULNUL_CAPABILITY_STORE": str((fixture / ".agents/skills").resolve()),
                "NULNUL_RECEIPT_ROOT": str(receipts.resolve()),
                "NULNUL_CASE_ID": task["case_id"],
            })
            if task["mode"] == "PROJECT_FIT":
                environment.update({
                    "NULNUL_PROJECT_CHECK_ID": task["project_check_identity"],
                    "NULNUL_PROJECT_CHECK": task["project_check"],
                })
        execution = run_model(protocol, arm, task, workspace, transcript, stderr_path, environment)
        config_after = sha256(config_path)
        trace = parse_transcript(transcript, task, workspace)
        completion = check_result(task["completion_command"], workspace)
        strict = check_result(task["strict_command"], workspace)
        changed, untracked = changed_files(workspace)
        if untracked:
            git(workspace, "add", "-N", "--", *untracked, check=False)
        patch = git(workspace, "diff", "--binary", "HEAD", check=False).stdout.encode()
        patch_hash = atomic_write(patch_path, patch)
        source_after = source_snapshot(source)
        fixture_after = source_snapshot(fixture)
        allowed = sorted(set(task["allowed_writes"]))
        required = sorted(set(task["required_writes"]))
        unauthorized = sorted(set(changed) - set(allowed))
        missing = sorted(set(required) - set(changed))
        strict_pass = strict["result"] == "pass" and not unauthorized and not missing
        if arm["source"] == "champion":
            architecture = {}
        elif task["mode"] == "DIRECT":
            architecture = {"direct": direct_evidence(trace, workspace, availability)}
        elif task["mode"] == "PROJECT_FIT":
            architecture = {
                "project_fit": project_fit_evidence(trace, task, workspace, availability, receipts)
            }
        else:
            architecture = {
                "governed_setup": setup_lifecycle_evidence(
                    trace, task, workspace, sources["candidate"], config_before, config_after
                )
            }

        usage = trace["usage"]
        if not execution["process_started"]:
            infrastructure_errors.append("model_process_never_started")
        if execution["timed_out"]:
            infrastructure_errors.append("model_process_timeout")
        if execution["process_exit"] != 0:
            infrastructure_errors.append("model_process_nonzero_exit")
        if not trace["raw_complete"]:
            infrastructure_errors.append("raw_transcript_incomplete")
        if not isinstance(usage, dict) or not isinstance(usage.get("input_tokens"), int) or usage.get("input_tokens", 0) <= 0:
            infrastructure_errors.append("model_usage_missing_or_unparseable")
        if source_before != source_after:
            infrastructure_errors.append("frozen_source_mutation")
        if fixture_before != fixture_after:
            infrastructure_errors.append("frozen_fixture_mutation")
        if not patch_path.is_file() or sha256(patch_path) != patch_hash:
            infrastructure_errors.append("patch_capture_failure")
        if completion.get("exit_code") is None or strict.get("exit_code") is None:
            infrastructure_errors.append("strict_or_completion_missing")

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
                "permission_profile": (
                    "e13-exclusive"
                    if arm["source"] == "candidate" and task["mode"] in {"DIRECT", "PROJECT_FIT"}
                    else "workspace-write"
                ),
                "timeout_seconds": protocol["timeout_seconds"],
                "retries": 0,
                "ignore_user_config": False,
                "ignore_rules": arm["source"] == "champion",
            },
            "task_sha256": task_sha256(task),
            "fixture_sha256": tree_sha256(REPO / task["fixture"]),
            "scientific_input_tree_sha256": source_before["tree_sha256"],
            "initial_workspace_sha256": initial_workspace_hash,
            "installed_harness_sha256": installed_harness_hash,
            "process": execution,
            "final_status": "pass" if execution["process_exit"] == 0 and strict_pass and completion["result"] == "pass" else "fail",
            "raw_transcript": str(transcript.relative_to(evidence)),
            "raw_transcript_sha256": sha256(transcript),
            "raw_transcript_complete": trace["raw_complete"],
            "stderr": str(stderr_path.relative_to(evidence)),
            "stderr_sha256": sha256(stderr_path),
            "model_usage": usage,
            "patch": str(patch_path.relative_to(evidence)),
            "patch_sha256": patch_hash,
            "write_set": changed,
            "unauthorized_writes": unauthorized,
            "required_writes_missing": missing,
            "initial_strict": prepared["initial_strict"],
            "strict": strict | {"result": "pass" if strict_pass else "fail"},
            "completion": completion,
            "project_invariant": (
                {"command": task["project_check"], "result": strict["result"]}
                if task["mode"] == "PROJECT_FIT" else None
            ),
            "frozen_source_before": source_before,
            "frozen_source_after": source_after,
            "frozen_fixture_before": fixture_before,
            "frozen_fixture_after": fixture_after,
            "frozen_overlay_before": overlay_before,
            "frozen_overlay_after": source_snapshot(overlay) if overlay else None,
            "host_config": host_config,
            "host_config_sha256_before": config_before,
            "host_config_sha256_after": config_after,
            "host_trust_mutated": config_before != config_after,
            "static_rule_admission": rule_admission,
            "precommit_availability": availability,
            "trace_summary": {
                "event_count": trace["event_count"],
                "repository_reads": trace["repository_reads"],
                "boundary_events": {
                    name: [{key: value for key, value in event.items() if key != "payload"} for event in events]
                    for name, events in trace["boundary_events"].items()
                },
                "sync_events": [
                    {key: value for key, value in event.items() if key != "payload"}
                    for event in trace["sync_events"]
                ],
                "ordinary_capability_body_reads": trace["ordinary_capability_body_reads"],
                "exposed_capability_body_reads": trace["exposed_capability_body_reads"],
                "live_or_evolution_state_reads": trace["live_or_evolution_state_reads"],
                "first_task_write": trace["first_task_write"],
                "verification_events": trace["verification_events"],
                "final_text": trace["final_text"][-2000:],
            },
            "receipt_artifacts": {
                path.relative_to(receipts).as_posix(): sha256(path)
                for path in sorted(receipts.rglob("*")) if path.is_file()
            },
            "architecture": architecture,
            "infrastructure_errors": infrastructure_errors,
            "evidence_committed": not infrastructure_errors,
            "cleanup_status": "PENDING" if not infrastructure_errors else "NOT_ATTEMPTED",
            "raw_transcript_retained": True,
        }
    except Exception as error:
        infrastructure_errors.append(f"runner_failure:{type(error).__name__}:{error}")
        record = {
            "schema_version": 1,
            "experiment_id": protocol["experiment_id"],
            "case_id": task["case_id"],
            "arm_id": arm["arm_id"],
            "arm": arm["source"],
            "host": "codex",
            "model": protocol["model"],
            "final_status": "invalid",
            "frozen_source_before": source_before,
            "frozen_source_after": source_snapshot(source),
            "frozen_fixture_before": fixture_before,
            "frozen_fixture_after": source_snapshot(fixture),
            "frozen_overlay_before": overlay_before,
            "frozen_overlay_after": source_snapshot(overlay) if overlay else None,
            "infrastructure_errors": infrastructure_errors,
            "evidence_committed": False,
            "cleanup_status": "NOT_ATTEMPTED",
            "raw_transcript_retained": transcript.is_file(),
        }

    atomic_json(record_path, record)
    if load_json(record_path) != record:
        raise ValueError("external arm-record readback failed")
    if record["evidence_committed"]:
        if task["mode"] == "GOVERNED_SETUP":
            try:
                record["project_fit_preparation"] = prepare_project_fit_lifecycle(protocol, workspace)
                cleanup_status = "SESSION_RESTART_READY"
            except Exception as error:
                cleanup_status = "POST_EVIDENCE_LIFECYCLE_PREPARATION_FAILURE"
                record["project_fit_preparation_error"] = f"{type(error).__name__}:{error}"
                record["preserved_workspace"] = str(workspace)
        else:
            try:
                make_writable(workspace)
                shutil.rmtree(workspace)
                cleanup_status = "CLEANUP_PASS"
            except Exception:
                cleanup_status = "POST_EVIDENCE_CLEANUP_FAILURE"
                record["preserved_workspace"] = str(workspace)
        record["cleanup_status"] = cleanup_status
        atomic_json(record_path, record)
        if load_json(record_path) != record:
            raise ValueError("post-cleanup arm-record readback failed")
    print(json.dumps({
        "arm_id": arm["arm_id"],
        "evidence_committed": record["evidence_committed"],
        "final_status": record["final_status"],
        "cleanup_status": record["cleanup_status"],
        "infrastructure_errors": record["infrastructure_errors"],
    }, ensure_ascii=False, indent=2))


def validate_artifact_hashes(evidence, record):
    for path_key, hash_key in (("raw_transcript", "raw_transcript_sha256"), ("stderr", "stderr_sha256"), ("patch", "patch_sha256")):
        path = evidence / record[path_key]
        if not path.is_file() or sha256(path) != record[hash_key]:
            return False
    receipts = evidence / "arms" / record["arm_id"] / "receipts"
    for relative, expected in record.get("receipt_artifacts", {}).items():
        path = receipts / relative
        if not path.is_file() or sha256(path) != expected:
            return False
    return True


def finalize(args):
    protocol = load_json(PROTOCOL_PATH)
    evidence = canonical(args.evidence_root)
    records = []
    for arm in protocol["arms"]:
        path = evidence / "arms" / arm["arm_id"] / "record.json"
        if not path.is_file():
            raise ValueError(f"official arm record missing: {arm['arm_id']}")
        record = load_json(path)
        if record.get("arm_id") != arm["arm_id"]:
            raise ValueError("arm identity mismatch")
        records.append(record)
    by_id = {record["arm_id"]: record for record in records}
    infrastructure_errors = [
        error
        for record in records
        for error in record.get("infrastructure_errors", [])
    ]
    for record in records:
        if record.get("evidence_committed") and not validate_artifact_hashes(evidence, record):
            infrastructure_errors.append(f"artifact_readback_failure:{record['arm_id']}")

    direct_champion = by_id["E13-DIRECT-CHAMPION"]
    direct_candidate = by_id["E13-DIRECT-CANDIDATE"]
    governed = by_id["E13-GOVERNED-SETUP-CANDIDATE"]
    fit_candidate = by_id["E13-PROJECT-FIT-POST-RESTART-CANDIDATE"]
    champion_input = (direct_champion.get("model_usage") or {}).get("input_tokens")
    candidate_input = (direct_candidate.get("model_usage") or {}).get("input_tokens")
    direct_ratio = candidate_input / champion_input if champion_input and candidate_input is not None else None
    direct_arch = direct_candidate.get("architecture", {}).get("direct", {})
    direct_gate = bool(
        direct_candidate.get("evidence_committed")
        and direct_candidate.get("strict", {}).get("result") == "pass"
        and direct_candidate.get("completion", {}).get("result") == "pass"
        and not direct_candidate.get("unauthorized_writes")
        and direct_arch.get("ordered")
        and direct_candidate.get("static_rule_admission", {}).get("all_exact_operations_allowed")
        and direct_candidate.get("host_config", {}).get("user_config_loaded")
        and direct_candidate.get("host_config", {}).get("project_trust_active")
        and direct_candidate.get("host_config", {}).get("project_layer_active")
        and direct_ratio is not None and direct_ratio <= 1.2
    )
    governed_arch = governed.get("architecture", {}).get("governed_setup", {})
    governed_gate = bool(
        governed.get("evidence_committed")
        and governed.get("strict", {}).get("result") == "pass"
        and governed.get("completion", {}).get("result") == "pass"
        and not governed.get("unauthorized_writes")
        and not governed.get("host_trust_mutated")
        and governed_arch.get("ordered")
        and governed_arch.get("restart_required")
        and governed.get("host_config", {}).get("user_config_loaded")
        and governed.get("host_config", {}).get("project_trust_active")
        and not governed.get("host_config", {}).get("project_layer_active")
        and governed.get("cleanup_status") == "SESSION_RESTART_READY"
    )
    fit_arch = fit_candidate.get("architecture", {}).get("project_fit", {})
    fit_gate = bool(
        fit_candidate.get("evidence_committed")
        and fit_candidate.get("strict", {}).get("result") == "pass"
        and fit_candidate.get("completion", {}).get("result") == "pass"
        and not fit_candidate.get("unauthorized_writes")
        and fit_arch.get("commit_valid")
        and fit_arch.get("attribution_complete")
        and fit_arch.get("wrong_or_irrelevant_body_loads") == 0
        and fit_candidate.get("static_rule_admission", {}).get("all_exact_operations_allowed")
        and fit_candidate.get("host_config", {}).get("user_config_loaded")
        and fit_candidate.get("host_config", {}).get("project_trust_active")
        and fit_candidate.get("host_config", {}).get("project_layer_active")
        and not fit_candidate.get("host_trust_mutated")
    )

    failures = []
    if (
        direct_arch.get("precommit_body_availability") not in (None, 0)
        or direct_arch.get("capability_body_exposures")
        or direct_arch.get("capability_body_reads")
    ):
        failures.append("EXCLUSIVE_CAPABILITY_GATE_FAILURE")
    if direct_ratio is not None and direct_ratio > 1.2:
        failures.append("DIRECT_LANE_OVERHEAD")
    if (
        direct_candidate.get("strict", {}).get("result") != "pass"
        or direct_candidate.get("completion", {}).get("result") != "pass"
        or not direct_arch.get("ordered")
    ):
        failures.append("PRODUCT_REGRESSION")
    if (
        not governed_arch.get("ordered")
        or not governed_arch.get("restart_required")
        or governed.get("unauthorized_writes")
    ):
        failures.append("GOVERNED_REGRESSION")
    if (
        not fit_candidate.get("host_config", {}).get("user_config_loaded")
        or not fit_candidate.get("host_config", {}).get("project_trust_active")
        or not fit_candidate.get("host_config", {}).get("project_layer_active")
        or not fit_candidate.get("static_rule_admission", {}).get("all_exact_operations_allowed")
        or not fit_candidate.get("trace_summary", {}).get("boundary_events", {}).get("host-admission")
    ):
        failures.append("HOST_ADMISSION_FAILURE")
    if not fit_arch.get("material_fit") or not fit_candidate.get("trace_summary", {}).get("boundary_events", {}).get("project-fit"):
        failures.append("TRUE_POSITIVE_UNDERACTIVATION")
    elif fit_arch.get("capability_id") != "project-api-validation":
        failures.append("WRONG_CAPABILITY_IDENTITY")
    elif (
        fit_arch.get("precommit_body_availability") not in (None, 0)
        or fit_arch.get("precommit_body_reads")
        or not fit_arch.get("postcommit_body_exposures")
    ):
        failures.append("EXCLUSIVE_CAPABILITY_GATE_FAILURE")
    elif not fit_arch.get("commit_valid") or not fit_arch.get("attribution_complete"):
        failures.append("ATTRIBUTION_BOUNDARY_FAILURE")
    if (
        fit_candidate.get("strict", {}).get("result") != "pass"
        or fit_candidate.get("completion", {}).get("result") != "pass"
    ):
        failures.append("PRODUCT_REGRESSION")
    if (
        direct_candidate.get("unauthorized_writes")
        or fit_candidate.get("unauthorized_writes")
        or governed.get("unauthorized_writes")
        or direct_candidate.get("host_trust_mutated")
        or fit_candidate.get("host_trust_mutated")
        or governed.get("host_trust_mutated")
    ):
        failures.append("STATE_AUTHORITY_REGRESSION")
    if (
        governed.get("strict", {}).get("result") != "pass"
        or governed.get("completion", {}).get("result") != "pass"
    ):
        failures.append("PRODUCT_REGRESSION")
    failures = list(dict.fromkeys(failures))

    if infrastructure_errors:
        primary = "INFRASTRUCTURE_INVALID"
    elif direct_gate and fit_gate and governed_gate:
        primary = "CODEX_HOST_ADMISSION_EXCLUSIVE_ATTRIBUTION_PROVEN"
    else:
        primary = "CORE_ARCHITECTURE_FAILURE"
    attribution = fit_arch.get("causal_record") or {}
    evolution_ready = bool(
        fit_candidate.get("evidence_committed")
        and fit_arch.get("activation_id")
        and fit_arch.get("check_id")
        and fit_arch.get("attribution_complete")
        and all(attribution.get(key) is not None for key in (
            "task_job", "match_evidence", "capability_id", "activation_id",
            "admission_id",
            "commit_before_body", "body_sha256", "body_exposure_before_work",
            "first_product_write", "product_outcome", "check_id", "check_result", "success",
        ))
    )
    report = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "primary_result": primary,
        "observed_failure_codes": failures,
        "infrastructure_errors": infrastructure_errors,
        "arms_completed": len(records),
        "direct_gate": direct_gate,
        "direct_input_ratio": direct_ratio,
        "project_fit_gate": fit_gate,
        "governed_gate": governed_gate,
        "one_time_host_setup": {
            "input_tokens": (governed.get("model_usage") or {}).get("input_tokens"),
            "runtime_seconds": governed.get("process", {}).get("runtime_seconds"),
        },
        "steady_state_project_fit": {
            "input_tokens": (fit_candidate.get("model_usage") or {}).get("input_tokens"),
            "runtime_seconds": fit_candidate.get("process", {}).get("runtime_seconds"),
        },
        "product_advantage": "NOT TESTED",
        "evolution_readiness": evolution_ready,
        "success_claim": (
            "CODEX HOST ADMISSION + EXCLUSIVE PROJECT-FIT ATTRIBUTION — PROVEN"
            if primary == "CODEX_HOST_ADMISSION_EXCLUSIVE_ATTRIBUTION_PROVEN" else None
        ),
        "champion": protocol["champion"],
        "candidate": protocol["candidate"] | {"single_successor": True, "applied": False},
        "causal_attribution_record": attribution,
        "task_hashes": {
            name: {
                "task_sha256": task["task_sha256"],
                "fixture_sha256": task["fixture_sha256"],
                "overlay_sha256": task.get("overlay_sha256"),
            }
            for name, task in protocol["tasks"].items()
        },
        "records": {
            record["arm_id"]: {
                "final_status": record.get("final_status"),
                "strict": record.get("strict", {}).get("result"),
                "completion": record.get("completion", {}).get("result"),
                "input_tokens": (record.get("model_usage") or {}).get("input_tokens"),
                "runtime_seconds": record.get("process", {}).get("runtime_seconds"),
                "repository_reads": record.get("trace_summary", {}).get("repository_reads"),
                "cleanup_status": record.get("cleanup_status"),
                "evidence_committed": record.get("evidence_committed"),
            }
            for record in records
        },
        "raw_transcripts_retained": all(record.get("raw_transcript_retained") for record in records),
        "product_changes": 0,
        "version": "v2.3 ARCHITECTURE REWORK REQUIRED",
        "release": "NOT READY",
    }
    atomic_json(evidence / "final-report.json", report)
    artifacts = {}
    manifest_path = evidence / "manifest.json"
    receipt_path = evidence / "manifest.json.receipt"
    for path in sorted(p for p in evidence.rglob("*") if p.is_file() and p not in {manifest_path, receipt_path}):
        artifacts[path.relative_to(evidence).as_posix()] = sha256(path)
    manifest = {
        "schema_version": 1,
        "experiment_id": protocol["experiment_id"],
        "primary_result": primary,
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "raw_transcripts_retained": True,
    }
    manifest_hash = atomic_json(manifest_path, manifest)
    atomic_write(receipt_path, (manifest_hash + "\n").encode())
    if receipt_path.read_text(encoding="utf-8").strip() != sha256(manifest_path):
        raise ValueError("manifest receipt readback failed")
    for relative, expected in artifacts.items():
        if sha256(evidence / relative) != expected:
            raise ValueError(f"artifact manifest mismatch: {relative}")
    print(json.dumps(report | {"artifact_count": len(artifacts), "manifest_sha256": manifest_hash}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("preflight")
    prepare.add_argument("--champion", type=Path, required=True)
    prepare.add_argument("--candidate", type=Path, required=True)
    prepare.add_argument("--evidence-root", type=Path, required=True)
    prepare.add_argument("--workspace-root", type=Path, required=True)
    prepare.add_argument("--codex-home", type=Path, required=True)
    arm = sub.add_parser("arm")
    arm.add_argument("arm_id")
    arm.add_argument("--evidence-root", type=Path, required=True)
    finish = sub.add_parser("finalize")
    finish.add_argument("--evidence-root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        preflight(args)
    elif args.command == "arm":
        run_arm(args)
    else:
        finalize(args)


if __name__ == "__main__":
    main()
