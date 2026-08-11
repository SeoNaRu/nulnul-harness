#!/usr/bin/env python3
"""Validate a nulnul personal-evolution state file."""

import argparse
import json
from pathlib import Path


CHECKPOINT_FIELDS = {
    "goal",
    "milestone",
    "completion_check",
    "status",
    "last_verified",
    "next_action",
    "blockers",
    "approved_permissions",
}
AGENT_FIELDS = {"version", "job", "profile_path", "last_promotion_id"}
FEEDBACK_FIELDS = {"id", "source", "target_agent", "observed", "expected", "evidence", "scope", "status"}
PROPOSAL_FIELDS = {
    "id",
    "feedback_ids",
    "target_agent",
    "author_agent",
    "from_version",
    "to_version",
    "cause",
    "change_target",
    "regression_check",
    "primary_metric",
    "permission_delta",
    "rollback",
    "status",
}
PROMOTION_FIELDS = {"id", "proposal_id", "gate_agent", "before", "after", "regressions_passed", "decision"}
PROPOSAL_V2_FIELDS = PROPOSAL_FIELDS | {"change_level", "discovery_evidence", "transfer_check"}
PROMOTION_V2_FIELDS = PROMOTION_FIELDS | {"live_cycle"}
LIVE_CYCLE_FIELDS = {"status", "metric", "rollback_threshold", "evidence"}
PROHIBITED_KEYS = {"raw_conversation", "secret", "secrets", "credential", "credentials", "api_key", "token"}


def validate(payload):
    errors = []

    def require_fields(value, fields, label):
        if not isinstance(value, dict):
            errors.append(f"{label} must be an object")
            return False
        missing = sorted(fields - value.keys())
        if missing:
            errors.append(f"{label} missing: {', '.join(missing)}")
            return False
        return True

    def reject_sensitive_keys(value, label="root"):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.lower() in PROHIBITED_KEYS:
                    errors.append(f"{label}.{key} is prohibited")
                reject_sensitive_keys(item, f"{label}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                reject_sensitive_keys(item, f"{label}[{index}]")

    if not isinstance(payload, dict):
        return ["root must be an object"]
    reject_sensitive_keys(payload)
    schema_version = payload.get("schema_version")
    if schema_version not in (1, 2):
        errors.append("schema_version must be 1 or 2")
        schema_version = 1
    proposal_fields = PROPOSAL_V2_FIELDS if schema_version == 2 else PROPOSAL_FIELDS
    promotion_fields = PROMOTION_V2_FIELDS if schema_version == 2 else PROMOTION_FIELDS
    evolution_home = payload.get("personal_evolution_home")
    if evolution_home is not None and (not isinstance(evolution_home, str) or not evolution_home.strip()):
        errors.append("personal_evolution_home must be null or a non-empty string")

    checkpoint = payload.get("checkpoint")
    if require_fields(checkpoint, CHECKPOINT_FIELDS, "checkpoint"):
        if checkpoint["status"] not in {"active", "blocked", "complete"}:
            errors.append("checkpoint.status is invalid")
        for field in ("blockers", "approved_permissions"):
            if not isinstance(checkpoint[field], list):
                errors.append(f"checkpoint.{field} must be an array")
        if isinstance(checkpoint["approved_permissions"], list) and any(
            not isinstance(item, str) or not item for item in checkpoint["approved_permissions"]
        ):
            errors.append("checkpoint.approved_permissions must contain non-empty strings")

    agents = payload.get("agents")
    if not isinstance(agents, dict):
        errors.append("agents must be an object")
        agents = {}
    for required in ("navigator", "coach", "gate"):
        if required not in agents:
            errors.append(f"agents.{required} is required")
    for agent_id, agent in agents.items():
        if require_fields(agent, AGENT_FIELDS, f"agents.{agent_id}"):
            if not isinstance(agent["version"], int) or agent["version"] < 1:
                errors.append(f"agents.{agent_id}.version must be a positive integer")
            if not isinstance(agent["job"], str) or not agent["job"].strip():
                errors.append(f"agents.{agent_id}.job must be non-empty")

    collections = {}
    for name, fields in (("feedback", FEEDBACK_FIELDS), ("proposals", proposal_fields), ("promotions", promotion_fields)):
        rows = payload.get(name)
        if not isinstance(rows, list):
            errors.append(f"{name} must be an array")
            rows = []
        collections[name] = rows
        seen = set()
        for index, row in enumerate(rows):
            label = f"{name}[{index}]"
            if require_fields(row, fields, label):
                row_id = row["id"]
                if not isinstance(row_id, str) or not row_id:
                    errors.append(f"{label}.id must be non-empty")
                elif row_id in seen:
                    errors.append(f"{name} id is duplicated: {row_id}")
                else:
                    seen.add(row_id)

    feedback_by_id = {
        row["id"]: row
        for row in collections["feedback"]
        if isinstance(row, dict) and isinstance(row.get("id"), str) and row["id"]
    }
    proposal_by_id = {
        row["id"]: row
        for row in collections["proposals"]
        if isinstance(row, dict) and isinstance(row.get("id"), str) and row["id"]
    }
    promotions_by_proposal = {}

    for row in collections["feedback"]:
        if not isinstance(row, dict) or not FEEDBACK_FIELDS <= row.keys():
            continue
        for field in ("observed", "expected", "evidence"):
            if not isinstance(row[field], str) or not row[field].strip():
                errors.append(f"feedback {row['id']}.{field} must be non-empty")
        if not isinstance(row["source"], str) or row["source"] not in ("user", "agent", "test", "gate"):
            errors.append(f"feedback {row['id']} has invalid source")
        if not isinstance(row["scope"], str) or row["scope"] not in ("agent", "project", "personal", "core"):
            errors.append(f"feedback {row['id']} has invalid scope")
        if not isinstance(row["status"], str) or row["status"] not in ("pending", "triaged", "converted", "dismissed"):
            errors.append(f"feedback {row['id']} has invalid status")
        if not isinstance(row["target_agent"], str) or row["target_agent"] not in agents:
            errors.append(f"feedback {row['id']} targets an unknown agent")
        rejected = row.get("rejected_proposals")
        if rejected is not None and (
            not isinstance(rejected, list)
            or any(
                not isinstance(item, str)
                or proposal_by_id.get(item, {}).get("status") not in ("rejected", "rolled_back")
                for item in rejected
            )
        ):
            errors.append(f"feedback {row['id']}.rejected_proposals must reference rejected or rolled back proposals")

    for row in collections["proposals"]:
        if not isinstance(row, dict) or not proposal_fields <= row.keys():
            continue
        proposal_id = row["id"]
        if not isinstance(row["target_agent"], str) or row["target_agent"] not in agents:
            errors.append(f"proposal {proposal_id} targets an unknown agent")
            continue
        if not isinstance(row["author_agent"], str) or row["author_agent"] not in agents:
            errors.append(f"proposal {proposal_id} has an unknown author agent")
        if not isinstance(agents[row["target_agent"]], dict):
            continue
        if not isinstance(row["status"], str) or row["status"] not in ("proposed", "gated", "accepted", "rejected", "rolled_back"):
            errors.append(f"proposal {proposal_id} has invalid status")
        if not isinstance(row["feedback_ids"], list) or not row["feedback_ids"] or any(
            not isinstance(item, str) or item not in feedback_by_id for item in row["feedback_ids"]
        ):
            errors.append(f"proposal {proposal_id} references unknown feedback")
        for field in ("cause", "change_target", "regression_check", "primary_metric", "rollback"):
            if not isinstance(row[field], str) or not row[field].strip():
                errors.append(f"proposal {proposal_id}.{field} must be non-empty")
        if not isinstance(row["from_version"], int) or not isinstance(row["to_version"], int) or row["to_version"] <= row["from_version"]:
            errors.append(f"proposal {proposal_id} has invalid version transition")
        if not isinstance(row["permission_delta"], list):
            errors.append(f"proposal {proposal_id}.permission_delta must be an array")
        elif any(not isinstance(item, str) or not item for item in row["permission_delta"]):
            errors.append(f"proposal {proposal_id}.permission_delta must contain non-empty strings")
        if schema_version == 2:
            change_level = row["change_level"]
            if change_level not in ("task", "meta"):
                errors.append(f"proposal {proposal_id}.change_level must be task or meta")
            discovery_evidence = row["discovery_evidence"]
            transfer_check = row["transfer_check"]
            if discovery_evidence is not None and (
                not isinstance(discovery_evidence, str) or not discovery_evidence.strip()
            ):
                errors.append(f"proposal {proposal_id}.discovery_evidence must be null or non-empty")
            if transfer_check is not None and (
                not isinstance(transfer_check, str) or not transfer_check.strip()
            ):
                errors.append(f"proposal {proposal_id}.transfer_check must be null or non-empty")
            if change_level == "meta":
                if row["target_agent"] not in ("coach", "gate"):
                    errors.append(f"meta proposal {proposal_id} must target coach or gate")
                if not isinstance(discovery_evidence, str) or not discovery_evidence.strip():
                    errors.append(f"meta proposal {proposal_id} needs discovery evidence")
                scopes = {
                    feedback_by_id[item].get("scope")
                    for item in row["feedback_ids"]
                    if isinstance(item, str) and item in feedback_by_id
                }
                if scopes & {"personal", "core"} and (
                    not isinstance(transfer_check, str) or not transfer_check.strip()
                ):
                    errors.append(f"broad meta proposal {proposal_id} needs a transfer check")
        current_version = agents[row["target_agent"]].get("version")
        if row["status"] in ("proposed", "gated") and current_version != row["from_version"]:
            errors.append(f"proposal {proposal_id} disagrees with the target agent version")
        elif row["status"] in ("accepted", "rejected", "rolled_back") and (
            not isinstance(current_version, int) or current_version < row["from_version"]
        ):
            errors.append(f"proposal {proposal_id} disagrees with the target agent version")

    for row in collections["promotions"]:
        if not isinstance(row, dict) or not promotion_fields <= row.keys():
            continue
        promotion_id = row["id"]
        proposal_id = row["proposal_id"]
        proposal = proposal_by_id.get(proposal_id) if isinstance(proposal_id, str) else None
        if proposal is None:
            errors.append(f"promotion {promotion_id} references an unknown proposal")
            continue
        promotions_by_proposal.setdefault(row["proposal_id"], []).append(row)
        for field in ("before", "after"):
            if not isinstance(row[field], str) or not row[field].strip():
                errors.append(f"promotion {promotion_id}.{field} must be non-empty")
        gate_agent = row["gate_agent"]
        if not isinstance(gate_agent, str) or gate_agent not in agents:
            errors.append(f"promotion {promotion_id} uses an unknown gate agent")
        elif gate_agent == proposal.get("target_agent"):
            errors.append(f"promotion {promotion_id} is self-approved")
        if gate_agent == proposal.get("author_agent"):
            errors.append(f"promotion {promotion_id} is approved by its proposal author")
        if not isinstance(row["decision"], str) or row["decision"] not in ("accepted", "rejected", "rolled_back"):
            errors.append(f"promotion {promotion_id} has invalid decision")
        elif proposal.get("status") != row["decision"]:
            errors.append(f"promotion {promotion_id} disagrees with the proposal status")
        if not isinstance(row["regressions_passed"], bool):
            errors.append(f"promotion {promotion_id}.regressions_passed must be boolean")
        if row["decision"] == "accepted" and row["regressions_passed"] is not True:
            errors.append(f"promotion {promotion_id} accepted with failing regressions")
        if row["decision"] == "accepted":
            approved = checkpoint.get("approved_permissions", []) if isinstance(checkpoint, dict) else []
            permission_delta = proposal.get("permission_delta", [])
            if isinstance(permission_delta, list) and any(permission not in approved for permission in permission_delta):
                errors.append(f"promotion {promotion_id} expands permission without approval")
        if schema_version == 2:
            live_cycle = row["live_cycle"]
            if row["decision"] in ("accepted", "rolled_back"):
                if not isinstance(live_cycle, dict) or not LIVE_CYCLE_FIELDS <= live_cycle.keys():
                    errors.append(f"promotion {promotion_id} needs a complete live cycle")
                else:
                    expected_status = "observed" if row["decision"] == "accepted" else "rolled_back"
                    if live_cycle["status"] != expected_status:
                        errors.append(f"promotion {promotion_id} live cycle status must be {expected_status}")
                    for field in ("metric", "rollback_threshold", "evidence"):
                        if not isinstance(live_cycle[field], str) or not live_cycle[field].strip():
                            errors.append(f"promotion {promotion_id}.live_cycle.{field} must be non-empty")
            elif live_cycle is not None:
                errors.append(f"rejected promotion {promotion_id}.live_cycle must be null")

    accepted_by_agent = {}
    for proposal_id, proposal in proposal_by_id.items():
        if not isinstance(proposal, dict) or proposal.get("status") != "accepted":
            continue
        accepted = [row for row in promotions_by_proposal.get(proposal_id, []) if row.get("decision") == "accepted"]
        if len(accepted) != 1:
            errors.append(f"accepted proposal {proposal_id} needs exactly one accepted promotion")
        elif proposal.get("target_agent") in agents:
            accepted_by_agent.setdefault(proposal["target_agent"], []).append((proposal, accepted[0]))

    for agent_id, history in accepted_by_agent.items():
        history.sort(key=lambda item: item[0].get("to_version", 0))
        for previous, current in zip(history, history[1:]):
            if current[0].get("from_version") != previous[0].get("to_version"):
                errors.append(f"agents.{agent_id} has a broken accepted version chain")
        latest_proposal, latest_promotion = history[-1]
        agent = agents.get(agent_id, {})
        if agent.get("version") != latest_proposal.get("to_version"):
            errors.append(f"agents.{agent_id}.version does not match its latest accepted proposal")
        if agent.get("last_promotion_id") != latest_promotion.get("id"):
            errors.append(f"agents.{agent_id}.last_promotion_id does not match its latest accepted promotion")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.state.read_text(encoding="utf-8"))
    errors = validate(payload)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
