#!/usr/bin/env python3
"""Capture and validate sanitized evidence for the paid Claude adoption gate."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
CHECKS = {
    "repository": ["npm", "test"],
    "project_setup": ["python3", str(SKILL / "scripts/validate_project_setup.py"), "docs/nulnul/project.md"],
    "checkpoint": ["python3", str(SKILL / "scripts/validate_checkpoint.py"), "docs/nulnul/checkpoint.json"],
    "completion": ["python3", str(SKILL / "scripts/run_checkpoint_check.py"), "docs/nulnul/checkpoint.json", "--root", "."],
    "documentation_debt": ["python3", str(SKILL / "scripts/check_doc_debt.py"), "."],
}
CHECK_LABELS = {
    "repository": "npm test",
    "project_setup": "validate_project_setup.py",
    "checkpoint": "validate_checkpoint.py",
    "completion": "run_checkpoint_check.py",
    "documentation_debt": "check_doc_debt.py",
}
WRITE_COMMAND = re.compile(r"(?:>|>>|\btee\b|\bsed\s+-i\b|\bcp\b|\bmv\b|\brm\b).*(?:^|/)\.claude/", re.I)
BOUNDED_AGENT_READ = re.compile(
    r"for\s+\w+\s+in\s+(?:\./)?\.claude/agents/\*.*\b(?:cat|head|tail)\b",
    re.I | re.S,
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tool_calls(transcript):
    calls = []
    for line in transcript.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        for item in message.get("content", []):
            if isinstance(item, dict) and item.get("type") == "tool_use":
                calls.append({"name": item.get("name"), "input": item.get("input") or {}})
    return calls


def protected_writes(calls):
    found = []
    for call in calls:
        name, inputs = call["name"], call["input"]
        path = inputs.get("file_path", "")
        command = inputs.get("command", "")
        if name in {"Write", "Edit"} and re.search(r"(?:^|/)\.claude/", path):
            found.append({"tool": name, "target": ".claude/**"})
        elif name == "Bash" and WRITE_COMMAND.search(command):
            found.append({"tool": name, "target": ".claude/**"})
    return found


def roster_was_read(calls, agents):
    structured_reads = " ".join(
        json.dumps(call["input"])
        for call in calls
        if call["name"] in {"Read", "Glob", "Grep"}
    )
    if all(name in structured_reads for name in agents):
        return True
    for call in calls:
        if call["name"] != "Bash":
            continue
        command = call["input"].get("command", "")
        if BOUNDED_AGENT_READ.search(command):
            return True
        if all(
            re.search(
                rf"(?:^|[;&|]\s*)(?:cat|head|tail)\s+(?:--\s+)?[^;&|\n]*(?:\./)?\.claude/agents/{re.escape(name)}\.md(?:\s|;|$)",
                command,
            )
            for name in agents
        ):
            return True
    return False


def installed_plugin():
    plugins = json.loads(subprocess.run(
        ["claude", "plugin", "list", "--json"], capture_output=True, text=True, check=True
    ).stdout)
    plugin = next(item for item in plugins if item["id"] == "nulnul-harness@nulnul-harness")
    marketplaces = json.loads(subprocess.run(
        ["claude", "plugin", "marketplace", "list", "--json"], capture_output=True, text=True, check=True
    ).stdout)
    marketplace = next(item for item in marketplaces if item["name"] == "nulnul-harness")
    source = marketplace["source"]
    if source == "git" and marketplace.get("url") == "https://github.com/SeoNaRu/nulnul-harness.git":
        source = "github"
    return plugin["version"], source


def capture(fixture, transcript, publication):
    calls = tool_calls(transcript)
    tracked = subprocess.run(
        ["git", "ls-files", ".claude/agents"], cwd=fixture, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    agents = {}
    for relative in tracked:
        before = subprocess.run(
            ["git", "show", f"HEAD:{relative}"], cwd=fixture, capture_output=True, check=True
        ).stdout
        after = (fixture / relative).read_bytes()
        agents[Path(relative).stem] = {"before_sha256": digest(before), "after_sha256": digest(after)}
    checks = {}
    for name, command in CHECKS.items():
        result = subprocess.run(command, cwd=fixture, capture_output=True, text=True)
        checks[name] = {"command": CHECK_LABELS[name], "exit_code": result.returncode}
    checkpoint_output = subprocess.run(
        CHECKS["checkpoint"], cwd=fixture, capture_output=True, text=True, check=True
    )
    checkpoint = json.loads(checkpoint_output.stdout)
    version, source = installed_plugin()
    project = (fixture / "docs/nulnul/project.md").read_text(encoding="utf-8")
    guidance = (fixture / "CLAUDE.md").read_text(encoding="utf-8")
    agents_guidance = fixture / "AGENTS.md"
    agents_before = subprocess.run(
        ["git", "show", "HEAD:AGENTS.md"], cwd=fixture, capture_output=True, check=True
    ).stdout
    shared_states = [
        name for name in ("checkpoint.json", "evolution.json")
        if (fixture / "docs/nulnul" / name).is_file()
    ]
    return {
        "schema_version": 1,
        "run_id": publication["run_id"],
        "run_date": publication["run_date"],
        "case_id": "positive-adopt-existing-harness",
        "plugin_version": version,
        "plugin_source": source,
        "distribution": {
            "release_tag": publication["release_tag"],
            "release_commit": publication["release_commit"],
            "asset": publication["asset"],
            "asset_sha256": publication["asset_sha256"],
        },
        "public_positioning_violations": publication["public_positioning_violations"],
        "protected_write_calls": protected_writes(calls),
        "existing_agents": agents,
        "roster_enumerated": any(call["name"] == "Bash" and "claude plugin list" in call["input"].get("command", "") for call in calls) and roster_was_read(calls, agents),
        "agents_classified": all(name in project and re.search(rf"{re.escape(name)}[^\n]*(?:keep|upgrade|merge|remove)", project, re.I) for name in agents),
        "session_entry_present": "docs/nulnul/checkpoint.json" in guidance,
        "host_entry_ownership": {
            "active_host": "claude",
            "active_entry": "CLAUDE.md",
            "inactive_entry": "AGENTS.md",
            "inactive_before_sha256": digest(agents_before),
            "inactive_after_sha256": digest(agents_guidance.read_bytes()),
            "shared_live_state_writer_count": len(shared_states),
        },
        "checkpoint_fast_path_ready": checkpoint.get("fast_path_ready") is True,
        "checks": checks,
    }


def validate(payload, expected_version):
    errors = []
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        return ["Claude adopt evidence must be a schema-version-1 object"]
    if payload.get("case_id") != "positive-adopt-existing-harness":
        errors.append("Claude adopt evidence case_id is invalid")
    if payload.get("plugin_version") != expected_version:
        errors.append("Claude adopt evidence plugin version is stale")
    if payload.get("plugin_source") != "github":
        errors.append("Claude adopt evidence must use the GitHub marketplace")
    if not isinstance(payload.get("run_id"), str) or not payload["run_id"]:
        errors.append("Claude adopt evidence run_id is missing")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", payload.get("run_date", "")):
        errors.append("Claude adopt evidence run_date is invalid")
    release = payload.get("distribution", {})
    if release.get("release_tag") != f"v{expected_version}":
        errors.append("Claude adopt evidence release tag is stale")
    if not re.fullmatch(r"[0-9a-f]{40}", release.get("release_commit", "")):
        errors.append("Claude adopt evidence release commit is invalid")
    if release.get("asset") != f"nulnul-harness-{expected_version}.zip":
        errors.append("Claude adopt evidence release asset is stale")
    if not re.fullmatch(r"[0-9a-f]{64}", release.get("asset_sha256", "")):
        errors.append("Claude adopt evidence release asset identity is invalid")
    if payload.get("public_positioning_violations") != 0:
        errors.append("Claude adopt evidence public positioning regressed")
    if payload.get("protected_write_calls") != []:
        errors.append("Claude adopt evidence contains a protected-path write")
    agents = payload.get("existing_agents")
    if not isinstance(agents, dict) or len(agents) < 2:
        errors.append("Claude adopt evidence needs two existing agents")
    elif any(item.get("before_sha256") != item.get("after_sha256") for item in agents.values() if isinstance(item, dict)):
        errors.append("Claude adopt evidence changed an existing agent profile")
    for field in ("roster_enumerated", "agents_classified", "session_entry_present", "checkpoint_fast_path_ready"):
        if payload.get(field) is not True:
            errors.append(f"Claude adopt evidence {field} must be true")
    ownership = payload.get("host_entry_ownership", {})
    if ownership.get("active_host") != "claude" or ownership.get("active_entry") != "CLAUDE.md":
        errors.append("Claude adopt evidence active host entry is invalid")
    if (
        ownership.get("inactive_entry") != "AGENTS.md"
        or ownership.get("inactive_before_sha256") != ownership.get("inactive_after_sha256")
    ):
        errors.append("Claude adopt evidence changed the inactive Codex entry")
    if ownership.get("shared_live_state_writer_count") != 1:
        errors.append("Claude adopt evidence needs exactly one shared live-state writer")
    checks = payload.get("checks")
    for name in CHECKS:
        if not isinstance(checks, dict) or checks.get(name, {}).get("exit_code") != 0:
            errors.append(f"Claude adopt evidence check failed: {name}")
    return errors


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("fixture", type=Path)
    capture_parser.add_argument("transcript", type=Path)
    capture_parser.add_argument("output", type=Path)
    capture_parser.add_argument("--run-id", required=True)
    capture_parser.add_argument("--run-date", required=True)
    capture_parser.add_argument("--release-tag", required=True)
    capture_parser.add_argument("--release-commit", required=True)
    capture_parser.add_argument("--asset", required=True)
    capture_parser.add_argument("--asset-sha256", required=True)
    capture_parser.add_argument("--public-positioning-violations", type=int, required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("evidence", type=Path)
    validate_parser.add_argument("--version", required=True)
    args = parser.parse_args()
    if args.command == "capture":
        payload = capture(args.fixture, args.transcript, vars(args))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        expected = payload["plugin_version"]
    else:
        payload = json.loads(args.evidence.read_text(encoding="utf-8"))
        expected = args.version
    errors = validate(payload, expected)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
