#!/usr/bin/env python3
"""Verify that every machine-readable nonpass verdict entered the Coach loop."""

import argparse
import json
from pathlib import Path


NONPASS = {"rejected", "regressed", "failed", "not-established"}
STATUSES = NONPASS | {"passed", "accepted"}


def validate(results, evolution):
    if not isinstance(results, dict) or not isinstance(evolution, dict):
        return ["results and evolution must be objects"]
    verdicts = results.get("learning_verdicts")
    if not isinstance(verdicts, list):
        return ["learning_verdicts must be an array"]
    feedback = {
        item.get("id")
        for item in evolution.get("feedback", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    proposals = {
        item.get("id"): item
        for item in evolution.get("proposals", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    errors = []
    seen = set()
    for index, verdict in enumerate(verdicts):
        if not isinstance(verdict, dict):
            errors.append(f"verdict {index} must be an object")
            continue
        verdict_id = verdict.get("id")
        status = verdict.get("status")
        if not isinstance(verdict_id, str) or not verdict_id:
            errors.append(f"verdict {index}.id must be a non-empty string")
            continue
        if verdict_id in seen:
            errors.append(f"duplicate verdict id: {verdict_id}")
        seen.add(verdict_id)
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f"verdict {verdict_id}.status is invalid")
            continue
        if status not in NONPASS:
            continue
        feedback_id = verdict.get("feedback_id")
        proposal_ids = verdict.get("proposal_ids")
        if not isinstance(feedback_id, str) or feedback_id not in feedback:
            errors.append(f"verdict {verdict_id} has no linked feedback")
        if not isinstance(proposal_ids, list) or not proposal_ids:
            errors.append(f"verdict {verdict_id} has no linked proposal")
            continue
        for proposal_id in proposal_ids:
            if not isinstance(proposal_id, str):
                errors.append(f"verdict {verdict_id} has an invalid proposal id")
                continue
            proposal = proposals.get(proposal_id)
            links = proposal.get("feedback_ids") if proposal else None
            if not isinstance(links, list) or feedback_id not in links:
                errors.append(
                    f"verdict {verdict_id} proposal {proposal_id} does not link its feedback"
                )
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("evolution", type=Path)
    args = parser.parse_args()
    try:
        results = json.loads(args.results.read_text(encoding="utf-8"))
        evolution = json.loads(args.evolution.read_text(encoding="utf-8"))
        if "archive" in evolution:
            import compact_evolution_state
            evolution = compact_evolution_state.read_full(args.evolution)
        errors = validate(results, evolution)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors = [f"cannot read learning loop: {error}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
