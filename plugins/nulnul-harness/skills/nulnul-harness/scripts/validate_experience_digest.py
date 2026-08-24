#!/usr/bin/env python3
"""Validate bounded process evidence without accepting traces or machine paths."""

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT_FIELDS = {
    "schema_version", "run_id", "case_id", "arm", "stages", "signals",
    "verification_result", "input_tokens", "output_tokens",
}
STAGE_FIELDS = {
    "stage", "owner", "elapsed_ms", "tool_invocations", "repository_reads",
    "validator_invocations", "test_invocations", "completion_check_invocations",
}
STAGES = {"activation", "resume", "verification"}
RESULTS = {"verified", "failed", "unknown"}
PROHIBITED_KEYS = {
    "raw_prompt", "raw_response", "raw_transcript", "tool_log", "commands", "command",
    "absolute_path", "secret", "secrets", "credential", "credentials", "api_key",
}
SAFE_LABEL = re.compile(r"^[A-Za-z0-9_.:-]{1,160}$")


def validate(payload):
    if not isinstance(payload, dict):
        return ["digest must be an object"]
    errors = []

    def reject_prohibited(value, label="digest"):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.lower() in PROHIBITED_KEYS:
                    errors.append(f"{label}.{key} is prohibited")
                reject_prohibited(item, f"{label}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                reject_prohibited(item, f"{label}[{index}]")

    reject_prohibited(payload)
    missing = sorted(ROOT_FIELDS - payload.keys())
    if missing:
        errors.append("digest missing: " + ", ".join(missing))
        return errors
    unexpected = sorted(payload.keys() - ROOT_FIELDS)
    if unexpected:
        errors.append("digest fields are not allowed: " + ", ".join(unexpected))
    if payload["schema_version"] != 1:
        errors.append("schema_version must be 1")
    for field in ("run_id", "case_id", "arm"):
        if not isinstance(payload[field], str) or not SAFE_LABEL.fullmatch(payload[field]):
            errors.append(f"{field} must be a bounded identifier")
    for field in ("input_tokens", "output_tokens"):
        value = payload[field]
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
            errors.append(f"{field} must be null or a non-negative integer")
    if payload["verification_result"] not in RESULTS:
        errors.append("verification_result is invalid")
    signals = payload["signals"]
    if not isinstance(signals, list) or any(
        not isinstance(signal, str) or not SAFE_LABEL.fullmatch(signal) for signal in signals
    ):
        errors.append("signals must contain bounded identifiers")
    stages = payload["stages"]
    if not isinstance(stages, list) or not stages:
        errors.append("stages must be a non-empty array")
        return errors
    seen = set()
    for index, stage in enumerate(stages):
        label = f"stages[{index}]"
        if not isinstance(stage, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = sorted(STAGE_FIELDS - stage.keys())
        if missing:
            errors.append(f"{label} missing: " + ", ".join(missing))
            continue
        unexpected = sorted(stage.keys() - STAGE_FIELDS)
        if unexpected:
            errors.append(f"{label} fields are not allowed: " + ", ".join(unexpected))
        if stage["stage"] not in STAGES:
            errors.append(f"{label}.stage is invalid")
        elif stage["stage"] in seen:
            errors.append(f"duplicate stage: {stage['stage']}")
        seen.add(stage["stage"])
        if not isinstance(stage["owner"], str) or not SAFE_LABEL.fullmatch(stage["owner"]):
            errors.append(f"{label}.owner must be a bounded identifier")
        for field in STAGE_FIELDS - {"stage", "owner"}:
            value = stage[field]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                errors.append(f"{label}.{field} must be a non-negative integer")
    return errors


def feedback_capsule(payload, plugin_version):
    errors = validate(payload)
    if errors:
        raise ValueError("invalid Experience Digest: " + "; ".join(errors))
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    tokens = lambda value: "unknown" if value is None else str(value)
    rows = [
        "| Stage | Owner | Elapsed ms | Tools | Reads | Validators | Tests | Completion checks |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    rows.extend(
        "| {stage} | {owner} | {elapsed_ms} | {tool_invocations} | "
        "{repository_reads} | {validator_invocations} | {test_invocations} | "
        "{completion_check_invocations} |".format(**stage)
        for stage in payload["stages"]
    )
    signals = "\n".join(f"- `{signal}`" for signal in payload["signals"]) or "- None"
    pretty_digest = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    return "\n".join((
        "# NULNUL feedback capsule",
        "",
        "> Review before sharing. This was generated locally from a validated, bounded "
        "Experience Digest; do not add private code, credentials, personal data, or raw conversations.",
        "",
        f"- Plugin version: `{plugin_version}`",
        f"- Run: `{payload['run_id']}`",
        f"- Case: `{payload['case_id']}`",
        f"- Arm: `{payload['arm']}`",
        f"- Verification: `{payload['verification_result']}`",
        f"- Tokens: input `{tokens(payload['input_tokens'])}`, output `{tokens(payload['output_tokens'])}`",
        f"- Digest SHA-256: `{digest_sha}`",
        "",
        "## User review (fill before sharing)",
        "",
        "- Request: <!-- sanitized summary; never paste the raw prompt -->",
        "- Expected: <!-- sanitized expected outcome -->",
        "- Observed: <!-- sanitized uncomfortable behavior -->",
        "",
        "## Stage summary",
        "",
        *rows,
        "",
        "## Signals",
        "",
        signals,
        "",
        "<details>",
        "<summary>Validated Experience Digest</summary>",
        "",
        "```json",
        pretty_digest,
        "```",
        "</details>",
    ))


def plugin_version():
    try:
        manifest = Path(__file__).resolve().parents[3] / ".codex-plugin/plugin.json"
        return json.loads(manifest.read_text(encoding="utf-8"))["version"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
        return "unknown"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("digest", type=Path)
    parser.add_argument(
        "--feedback-capsule",
        action="store_true",
        help="print reviewable Markdown from a valid digest without saving or uploading it",
    )
    args = parser.parse_args()
    try:
        payload = json.loads(args.digest.read_text(encoding="utf-8"))
        errors = validate(payload)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors = [f"cannot read digest: {error}"]
    if args.feedback_capsule and not errors:
        print(feedback_capsule(payload, plugin_version()))
    else:
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
