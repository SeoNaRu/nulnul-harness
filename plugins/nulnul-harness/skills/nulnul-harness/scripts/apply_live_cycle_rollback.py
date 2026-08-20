#!/usr/bin/env python3
"""Confirm healthy provisional versions or apply live-cycle rollback atomically."""

import argparse
import json
import operator
import os
import tempfile
from pathlib import Path

import validate_evolution_state


OPERATORS = {
    "lt": operator.lt,
    "lte": operator.le,
    "gt": operator.gt,
    "gte": operator.ge,
    "eq": operator.eq,
    "ne": operator.ne,
}


def apply(payload):
    errors = validate_evolution_state.validate(payload)
    if errors:
        raise ValueError("; ".join(errors))
    if payload.get("schema_version") not in (3, 4):
        raise ValueError("automatic rollback requires schema_version 3 or 4")

    proposals = {row["id"]: row for row in payload["proposals"]}
    confirmed = []
    rolled_back = []
    for promotion in payload["promotions"]:
        if promotion["decision"] not in ("provisional", "accepted"):
            continue
        live_cycle = promotion["live_cycle"]
        if live_cycle["status"] != "observed":
            continue
        compare = OPERATORS[live_cycle["rollback_operator"]]
        proposal = proposals[promotion["proposal_id"]]
        agent = payload["agents"][proposal["target_agent"]]
        breached = compare(live_cycle["metric_value"], live_cycle["rollback_value"])

        if promotion["decision"] == "provisional":
            if (
                agent["version"] != proposal["from_version"]
                or agent.get("trial_version") != proposal["to_version"]
                or agent.get("trial_promotion_id") != promotion["id"]
            ):
                raise ValueError(f"promotion {promotion['id']} is not the active provisional version")
            agent["trial_version"] = None
            agent["trial_promotion_id"] = None
            if breached:
                proposal["status"] = "rolled_back"
                promotion["decision"] = "rolled_back"
                live_cycle["status"] = "rolled_back"
                rolled_back.append(promotion["id"])
            else:
                proposal["status"] = "accepted"
                promotion["decision"] = "accepted"
                agent["version"] = proposal["to_version"]
                agent["last_promotion_id"] = promotion["id"]
                confirmed.append(promotion["id"])
            continue

        if not breached:
            continue
        if agent["version"] != proposal["to_version"] or agent["last_promotion_id"] != promotion["id"]:
            raise ValueError(f"promotion {promotion['id']} is not the active target version")

        previous = next(
            (
                row
                for row in reversed(payload["promotions"])
                if row["id"] != promotion["id"]
                and row["decision"] == "accepted"
                and proposals[row["proposal_id"]]["target_agent"] == proposal["target_agent"]
                and proposals[row["proposal_id"]]["to_version"] == proposal["from_version"]
            ),
            None,
        )
        proposal["status"] = "rolled_back"
        promotion["decision"] = "rolled_back"
        live_cycle["status"] = "rolled_back"
        agent["version"] = proposal["from_version"]
        agent["last_promotion_id"] = previous["id"] if previous else None
        rolled_back.append(promotion["id"])

    errors = validate_evolution_state.validate(payload)
    if errors:
        raise ValueError("rollback produced invalid state: " + "; ".join(errors))
    return {"confirmed": confirmed, "rolled_back": rolled_back}


def write_atomic(path, payload):
    path = Path(path)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", text=True)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as output:
            json.dump(payload, output, ensure_ascii=False, indent=2)
            output.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.state.read_text(encoding="utf-8"))
    result = apply(payload)
    if result["confirmed"] or result["rolled_back"]:
        write_atomic(args.state, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
