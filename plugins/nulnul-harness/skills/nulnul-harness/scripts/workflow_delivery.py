#!/usr/bin/env python3
"""Plan scoped workflow reruns and check development observations, without promotion."""

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from graphlib import TopologicalSorter, CycleError
from pathlib import Path

from validate_checkpoint import verification_fingerprint


ASSETS = Path(__file__).resolve().parents[1] / "assets"
IDENTITY = re.compile(r"[a-z][a-z0-9-]{0,63}")
DIGEST = re.compile(r"[a-f0-9]{64}")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_json(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
        raise ValueError("expected one bounded regular JSON file")
    return json.loads(path.read_text(encoding="utf-8"))


def strings(values, field, *, required=False, unique=True):
    if (not isinstance(values, list) or len(values) > 64
            or any(not isinstance(v, str) or not v.strip() or len(v) > 1024 for v in values)
            or (unique and len(set(values)) != len(values)) or (required and not values)):
        raise ValueError(f"invalid {field}")
    return values


def relative(name):
    path = Path(name)
    if (path.is_absolute() or path.as_posix() != name or ".." in path.parts
            or not path.parts or "\\" in name or any(ord(c) < 32 for c in name)):
        raise ValueError("workflow paths must be normalized relative files")
    return path


def workflow(specification):
    if not isinstance(specification, dict) or specification.get("schema_version") != 1:
        raise ValueError("unsupported workflow schema")
    rows = specification.get("steps")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 32:
        raise ValueError("workflow needs 1-32 steps")
    steps, producers = {}, {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "needs", "inputs", "outputs", "check"}:
            raise ValueError("incomplete workflow step")
        identity = row["id"]
        if not isinstance(identity, str) or not IDENTITY.fullmatch(identity) or identity in steps:
            raise ValueError("invalid or duplicate step identity")
        for field in ("needs", "inputs", "outputs", "check"):
            strings(row[field], field, required=field != "needs", unique=field != "check")
        for name in row["inputs"] + row["outputs"]:
            relative(name)
        for name in row["outputs"]:
            if name in producers:
                raise ValueError("one producer must own each output")
            producers[name] = identity
        steps[identity] = row
    if any(set(row["needs"]) - set(steps) for row in rows):
        raise ValueError("unknown workflow dependency")
    try:
        order = tuple(TopologicalSorter({key: row["needs"] for key, row in steps.items()}).static_order())
    except CycleError as error:
        raise ValueError("workflow dependency cycle") from error
    ancestors = {}
    for key in order:
        ancestors[key] = set(steps[key]["needs"])
        for parent in steps[key]["needs"]:
            ancestors[key].update(ancestors[parent])
        for name in steps[key]["inputs"]:
            owner = producers.get(name)
            if owner and owner != key and owner not in ancestors[key]:
                raise ValueError("consumed output lacks a producer dependency")
    return steps, order, ancestors


def safe_paths(root, names):
    for name in names:
        path = root / relative(name)
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            raise ValueError("workflow file escapes its root or is a symlink")


def fingerprint(root, step):
    names = sorted(set(step["inputs"] + step["outputs"]))
    safe_paths(root, names)
    return verification_fingerprint(root, names)


def plan(root, specification, receipts=(), only=()):
    root = Path(root).resolve()
    steps, order, ancestors = workflow(specification)
    if set(only) - set(steps):
        raise ValueError("unknown requested step")
    previous = {}
    for receipt in receipts:
        if (not isinstance(receipt, dict) or receipt.get("schema_version") != 1
                or receipt.get("step_id") not in steps or receipt["step_id"] in previous
                or receipt.get("verification_status") not in {"verified", "failed", "unknown"}):
            raise ValueError("invalid or duplicate workflow receipt")
        previous[receipt["step_id"]] = receipt
    fresh = {}
    for key in order:
        step = steps[key]
        safe_paths(root, step["inputs"] + step["outputs"])
        try:
            current = fingerprint(root, step)
        except (OSError, ValueError):
            current = None
        old = previous.get(key, {})
        fresh[key] = bool(current and old.get("verification_status") == "verified"
                          and old.get("exit_code") == 0 and old.get("contract_digest") == digest(step)
                          and old.get("fingerprint") == current
                          and all(fresh[parent] for parent in step["needs"]))
    run = set(only) if only else {key for key in order if not fresh[key]}
    # ponytail: at most 32 stages; use a scheduler only if real workflows outgrow this closure.
    while True:
        expanded = run | {parent for key in run for parent in ancestors[key] if not fresh[parent]}
        expanded |= {key for key in order if set(steps[key]["needs"]) & expanded}
        if expanded == run:
            break
        run = expanded
    return {
        "schema_version": 1, "authority": "advisory-only", "promotion_eligible": False,
        "steps": [{"id": key, "action": "RUN" if key in run else "REUSE" if fresh[key] else "SKIP",
                   "verified_unchanged": fresh[key]} for key in order],
    }


def verify(root, specification, identity, timeout=120):
    root = Path(root).resolve()
    steps, _, _ = workflow(specification)
    if identity not in steps or not 0 < timeout <= 3600:
        raise ValueError("invalid verification step or timeout")
    step = steps[identity]
    receipt = {"schema_version": 1, "step_id": identity, "contract_digest": digest(step),
               "verification_status": "unknown", "fingerprint": "", "exit_code": None}
    safe_paths(root, step["inputs"] + step["outputs"])
    try:
        before = verification_fingerprint(root, step["inputs"])
        result = subprocess.run(step["check"], cwd=root, timeout=timeout, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        receipt["exit_code"] = result.returncode
        if result.returncode:
            receipt["verification_status"] = "failed"
        elif before == verification_fingerprint(root, step["inputs"]):
            receipt["fingerprint"] = fingerprint(root, step)
            receipt["verification_status"] = "verified"
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass  # Missing execution or unstable evidence stays unknown, never a successful check.
    return receipt


def score_cases(bundle, observations):
    if (not isinstance(bundle, dict) or bundle.get("schema_version") != 1
            or not isinstance(bundle.get("candidate_digest"), str)
            or not DIGEST.fullmatch(bundle["candidate_digest"]) or bundle["candidate_digest"] == "0" * 64):
        raise ValueError("skill cases need an exact candidate digest")
    cases = bundle.get("cases")
    if not isinstance(cases, list) or not 3 <= len(cases) <= 20:
        raise ValueError("skill cases need 3-20 development requests")
    identities, prompts, kinds = set(), set(), set()
    for case in cases:
        if (not isinstance(case, dict) or not isinstance(case.get("id"), str)
                or not IDENTITY.fullmatch(case["id"]) or case["id"] in identities
                or not isinstance(case.get("prompt"), str) or not case["prompt"].strip()
                or len(case["prompt"]) > 4096 or case["prompt"] in prompts
                or case.get("kind") not in {"use", "skip", "followup"}
                or type(case.get("expected_use")) is not bool
                or case["expected_use"] != (case["kind"] != "skip")):
            raise ValueError("invalid skill use, near-miss, or followup case")
        identities.add(case["id"])
        prompts.add(case["prompt"])
        kinds.add(case["kind"])
    if kinds != {"use", "skip", "followup"}:
        raise ValueError("include use, near-miss skip, and followup cases")
    if not isinstance(observations, list) or len(observations) > 20:
        raise ValueError("observations must be a bounded list")
    actual = {}
    for row in observations:
        if not isinstance(row, dict) or row.get("case_id") not in identities or row["case_id"] in actual:
            raise ValueError("unknown or duplicate observation")
        actual[row["case_id"]] = row
    results = []
    for case in cases:
        row = actual.get(case["id"], {})
        passed = (row.get("candidate_digest") == bundle["candidate_digest"]
                  and type(row.get("used_capability")) is bool
                  and row["used_capability"] == case["expected_use"]
                  and row.get("check_status") == "verified"
                  and isinstance(row.get("check_id"), str) and bool(DIGEST.fullmatch(row["check_id"])))
        results.append({"case_id": case["id"], "passed": passed})
    return {"schema_version": 1, "evidence_scope": "development-observations",
            "promotion_eligible": False, "passed": all(row["passed"] for row in results), "cases": results}


def demo():
    specification = read_json(ASSETS / "workflow-example.json")
    with tempfile.TemporaryDirectory(prefix="nulnul-workflow-") as directory:
        root = Path(directory)
        for name, value in {"api.json": "[1, 2]", "view.json": '{"count": 2}', "notes.txt": "approved"}.items():
            (root / name).write_text(value, encoding="utf-8")
        receipts = [verify(root, specification, row["id"]) for row in specification["steps"]]
        assert all(row["verification_status"] == "verified" for row in receipts)
        (root / "api.json").write_text('{"projects": [1, 2]}', encoding="utf-8")
        negative = verify(root, specification, "api")
        assert negative["verification_status"] == "failed"
        rerun = [row["id"] for row in plan(root, specification, receipts)["steps"] if row["action"] == "RUN"]
        assert rerun == ["api", "view"]
        return {"passed": True, "negative_control": "failed", "invalidated": rerun,
                "evidence_scope": "deterministic-development-fixture", "promotion_eligible": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    sub = parser.add_subparsers(dest="command", required=True)
    planning = sub.add_parser("plan")
    planning.add_argument("workflow", type=Path)
    planning.add_argument("--receipt", type=Path, action="append", default=[])
    planning.add_argument("--only", action="append", default=[])
    checking = sub.add_parser("verify")
    checking.add_argument("workflow", type=Path)
    checking.add_argument("step")
    checking.add_argument("--timeout", type=int, default=120)
    scoring = sub.add_parser("score-cases")
    scoring.add_argument("bundle", type=Path)
    scoring.add_argument("observations", type=Path)
    sub.add_parser("demo")
    args = parser.parse_args()
    try:
        if args.command == "plan":
            result = plan(args.root, read_json(args.workflow), [read_json(p) for p in args.receipt], args.only)
        elif args.command == "verify":
            result = verify(args.root, read_json(args.workflow), args.step, args.timeout)
        elif args.command == "score-cases":
            result = score_cases(read_json(args.bundle), read_json(args.observations))
        else:
            result = demo()
        failed = result.get("passed") is False or result.get("verification_status", "verified") != "verified"
    except (OSError, ValueError, AssertionError) as error:
        result, failed = {"passed": False, "error": str(error)}, True
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
